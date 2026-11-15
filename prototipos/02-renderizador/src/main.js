import * as THREE from "three";
import { MapControls } from "three/examples/jsm/controls/MapControls.js";
import { EffectComposer, RenderPass, EffectPass, BloomEffect, ToneMappingEffect, ToneMappingMode, KernelSize } from "postprocessing";
import "../../../diseno/generado/tokens.css";
import * as T from "../../../diseno/generado/tokens.js";

const params = new URLSearchParams(location.search);
const esMovil = matchMedia("(pointer: coarse)").matches || Math.min(innerWidth, innerHeight) < 700;
const PALETA = T.macrosectores.map((m) => m.oscuro.hex); // diseno/tokens.json, 1 por macrosector
const MAPEOS = { ninguno: ToneMappingMode.LINEAR, reinhard: ToneMappingMode.REINHARD2, aces: ToneMappingMode.ACES_FILMIC, agx: ToneMappingMode.AGX, neutral: ToneMappingMode.NEUTRAL };
const $ = (id) => document.getElementById(id);

const [meta, fondo, buf] = await Promise.all([
  fetch("datos/meta.json").then((r) => r.json()),
  fetch("datos/fondo.json").then((r) => r.json()),
  fetch("datos/puntos.bin").then((r) => r.arrayBuffer()),
]);
const n = meta.n;
const xs = new Uint16Array(buf, 0, n);
const ys = new Uint16Array(buf, n * 2, n);
const macro = new Uint8Array(buf, n * 4, n);
$("corte").textContent = `${n.toLocaleString("es-MX")} establecimientos · DENUE ${meta.edicion} · corte ${meta.fecha_corte}`;

// ── Renderizador ───────────────────────────────────────────────
const renderer = new THREE.WebGLRenderer({ antialias: false, powerPreference: "high-performance", alpha: false });
let dpr = Math.min(devicePixelRatio, esMovil ? 1.5 : 2);
if (params.get("dpr")) dpr = +params.get("dpr");
renderer.setPixelRatio(dpr);
renderer.setSize(innerWidth, innerHeight);
renderer.setClearColor(new THREE.Color(T.oscuro.fondo), 1);
document.body.prepend(renderer.domElement);
const gl = renderer.getContext();
const dbg = gl.getExtension("WEBGL_debug_renderer_info");
const gpu = dbg ? gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL) : "n/d";

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(40, innerWidth / innerHeight, 50, 400000);
// Mundo: x este, y norte (plano z=0 → usamos x,z con y arriba). Centro de la nube en (cx, cz).
const cx = meta.w / 2, cy = meta.h / 2;
const ALTO_INICIAL = Math.max(meta.w, meta.h) * 1.25;
camera.position.set(0, ALTO_INICIAL, 1);
const controls = new MapControls(camera, renderer.domElement);
controls.enableDamping = true; controls.dampingFactor = 0.08;
controls.screenSpacePanning = false;
controls.minDistance = 300; controls.maxDistance = ALTO_INICIAL * 1.4;
controls.maxPolarAngle = Math.PI * 0.46;
controls.target.set(0, 0, 0);

// ── Puntos: posiciones Uint16 en GPU, sin Float32 intermedio ───
const geo = new THREE.BufferGeometry();
const posAttr = new THREE.Uint16BufferAttribute(new Uint16Array(n * 2), 2);
{ const a = posAttr.array; for (let i = 0; i < n; i++) { a[2 * i] = xs[i]; a[2 * i + 1] = ys[i]; } }
geo.setAttribute("position", new THREE.BufferAttribute(new Float32Array(n * 3), 3)); // placeholder para bounding; no se usa
geo.setAttribute("q", posAttr);
geo.setAttribute("m", new THREE.Uint8BufferAttribute(macro, 1));
const fraccion = Math.min(1, Math.max(0, +(params.get("pts") ?? 1)));
geo.setDrawRange(0, Math.floor(n * fraccion));
const colores = PALETA.map((h) => new THREE.Color(h));
const mat = new THREE.ShaderMaterial({
  transparent: true, depthWrite: false, depthTest: false, blending: THREE.AdditiveBlending,
  uniforms: {
    uCentro: { value: new THREE.Vector2(cx, cy) },
    uPal: { value: colores.map((c) => new THREE.Vector3(c.r, c.g, c.b)) },
    uMask: { value: new Array(8).fill(1) },
    uPx: { value: T.luz.punto_px * dpr },
    uAlfa: { value: T.luz.alfa },
    uRev: { value: 1e9 },          // radio de revelado (m) desde el centro
    uBorde: { value: 900 },
    uResY: { value: innerHeight * dpr },
  },
  vertexShader: /* glsl */ `
    attribute vec2 q; attribute float m;
    uniform vec2 uCentro; uniform vec3 uPal[7]; uniform float uMask[8];
    uniform float uPx, uAlfa, uRev, uBorde, uResY;
    varying vec3 vC; varying float vA;
    void main(){
      vec2 p = q - uCentro;                       // metros locales, centrados
      vec4 mv = modelViewMatrix * vec4(p.x, 0.0, -p.y, 1.0);
      gl_Position = projectionMatrix * mv;
      float d = length(p);
      float rev = 1.0 - smoothstep(uRev - uBorde, uRev, d);
      int k = int(m + 0.5) - 1;
      vec3 c = vec3(1.0);
      for (int i = 0; i < 7; i++) if (i == k) c = uPal[i];
      float msk = 0.0;
      for (int i = 0; i < 8; i++) if (i == k + 1) msk = uMask[i];
      vC = c; vA = uAlfa * (${T.luz.atenuado.toFixed(3)} + ${(1 - T.luz.atenuado).toFixed(3)} * msk) * rev;
      // tamaño en pixeles constante respecto a la escena: crece al acercar, con tope
      float escala = uResY / (2.0 * tan(0.3490659) * -mv.z);   // px por metro a esa distancia
      gl_PointSize = clamp(uPx * 0.5 + escala * 7.0, uPx, uPx * 6.0);
      if (rev <= 0.001) gl_PointSize = 0.0;
    }`,
  fragmentShader: /* glsl */ `
    varying vec3 vC; varying float vA;
    void main(){
      vec2 d = gl_PointCoord - 0.5; float r = dot(d,d) * 4.0;
      float a = (1.0 - r); if (a <= 0.0) discard;
      gl_FragColor = vec4(vC * a * vA, 1.0);
    }`,
});
const puntos = new THREE.Points(geo, mat);
puntos.frustumCulled = false;
scene.add(puntos);

// ── Fondo propio: siluetas de alcaldías dibujadas desde los datos ──
const lineas = new THREE.Group();
const lmat = new THREE.LineBasicMaterial({ color: new THREE.Color(T.oscuro.alcaldia_trazo), transparent: true, opacity: 0.9 });
const fmat = new THREE.MeshBasicMaterial({ color: new THREE.Color(T.oscuro.alcaldia_relleno), transparent: true, opacity: 0.95, depthWrite: false });
for (const a of fondo) for (const ring of a.anillos) {
  const v = ring.map(([x, y]) => new THREE.Vector3(x - cx, -1, -(y - cy)));
  lineas.add(new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints(v), lmat));
  const shape = new THREE.Shape(ring.map(([x, y]) => new THREE.Vector2(x - cx, y - cy)));
  const m = new THREE.Mesh(new THREE.ShapeGeometry(shape), fmat);
  // ShapeGeometry vive en XY; se acuesta en XZ con el norte hacia -z
  m.rotation.set(-Math.PI / 2, 0, 0); m.position.y = -3;
  lineas.add(m);
}
scene.add(lineas);

// ── Posprocesado (brillo) ──────────────────────────────────────
let composer = null, bloomOn = params.get("bloom") ? params.get("bloom") === "1" : !esMovil;
function armarComposer() {
  composer = new EffectComposer(renderer, { frameBufferType: THREE.HalfFloatType });
  composer.addPass(new RenderPass(scene, camera));
  composer.addPass(new EffectPass(camera, new BloomEffect({ intensity: T.luz.brillo.intensidad, luminanceThreshold: T.luz.brillo.umbral, luminanceSmoothing: T.luz.brillo.suavizado, kernelSize: KernelSize.MEDIUM, mipmapBlur: true }), new ToneMappingEffect({ mode: MAPEOS[T.luz.mapeo_tonos] })));
}
armarComposer();
$("b-bloom").onclick = () => { bloomOn = !bloomOn; };

// ── Leyenda / selección: filtrar atenúa, nunca elimina ─────────
const activo = new Array(8).fill(true);
const leyenda = $("leyenda");
meta.macrosectores.forEach((mc, i) => {
  const b = document.createElement("button"); b.setAttribute("aria-pressed", "true");
  b.innerHTML = `<i style="background:${PALETA[i]}"></i>${mc.nombre}`;
  b.onclick = () => { activo[i + 1] = !activo[i + 1]; b.setAttribute("aria-pressed", activo[i + 1]);
    const todos = activo.slice(1, 8).every(Boolean);
    mat.uniforms.uMask.value = activo.map((v, j) => (j === 0 ? 1 : todos ? 1 : v ? 1 : 0)); };
  leyenda.appendChild(b);
});
mat.uniforms.uMask.value = new Array(8).fill(1);
mat.uniforms.uMask.value[0] = 1;

// ── Despertar: oleada de encendido desde el Zócalo ─────────────
let despertar = null;
function lanzarDespertar() { despertar = { t0: performance.now(), dur: 3200 }; mat.uniforms.uRev.value = 0; }
$("b-despertar").onclick = lanzarDespertar;
const radioMax = Math.hypot(meta.w, meta.h) * 0.7;
function pasoDespertar(now) {
  if (!despertar) return;
  const t = Math.min(1, (now - despertar.t0) / despertar.dur);
  const e = 1 - Math.pow(1 - t, 3);
  mat.uniforms.uRev.value = e * radioMax + (t >= 1 ? 1e9 : 0);
  if (t >= 1) despertar = null;
}

// ── Temporizador de GPU (mide el dibujo real, sin depender de cómo el navegador presente el cuadro) ──
const extT = gl.getExtension("EXT_disjoint_timer_query_webgl2");
const gpuMs = []; const pendientes = []; let qActiva = null;
function gpuInicio() { if (!extT || qActiva) return; qActiva = gl.createQuery(); gl.beginQuery(extT.TIME_ELAPSED_EXT, qActiva); }
function gpuFin() { if (!qActiva) return; gl.endQuery(extT.TIME_ELAPSED_EXT); pendientes.push(qActiva); qActiva = null; }
function gpuLeer() {
  while (pendientes.length) {
    const q = pendientes[0];
    if (!gl.getQueryParameter(q, gl.QUERY_RESULT_AVAILABLE)) break;
    const disjoint = gl.getParameter(extT.GPU_DISJOINT_EXT);
    if (!disjoint) { gpuMs.push(gl.getQueryParameter(q, gl.QUERY_RESULT) / 1e6); if (gpuMs.length > 600) gpuMs.shift(); if (bench) bench.gpu.push(gpuMs[gpuMs.length - 1]); }
    gl.deleteQuery(q); pendientes.shift();
  }
}

// ── Telemetría de rendimiento ──────────────────────────────────
const hud = $("hud");
const dt = []; let ultimo = performance.now(), acumHud = 0, fpsActual = 0;
let bench = null, calidadBaja = 0;
function pct(arr, p) { if (!arr.length) return 0; const s = [...arr].sort((a, b) => a - b); return s[Math.min(s.length - 1, Math.floor(p * s.length))]; }
function pintarHud() {
  const w = dt.slice(-120); if (!w.length) return;
  const avg = w.reduce((a, b) => a + b, 0) / w.length;
  fpsActual = 1000 / avg;
  hud.innerHTML = `<div><em>FPS</em><b>${fpsActual.toFixed(0)}</b></div><div><em>p95 cuadro</em>${pct(w, 0.95).toFixed(1)} ms</div>
  <div><em>puntos</em>${Math.floor(n * fraccion).toLocaleString("es-MX")}</div><div><em>dpr</em>${dpr.toFixed(2)}</div>
  <div><em>GPU/cuadro</em>${gpuMs.length ? pct(gpuMs.slice(-120), 0.5).toFixed(2) + " ms" : "n/d"}</div>
  <div><em>brillo</em>${bloomOn ? "sí" : "no"}</div><div><em>llamadas</em>${renderer.info.render.calls}</div>
  <div><em>GPU</em><span style="max-width:110px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${gpu.replace(/ANGLE \(|\)/g, "")}</span></div>`;
}
function iniciarBench() {
  bench = { t0: performance.now(), dur: 12000, muestras: [], gpu: [], cam0: camera.position.clone(), tgt0: controls.target.clone(), bloom: bloomOn };
  $("resultado").style.display = "none"; controls.enabled = false; lanzarDespertar();
}
$("b-bench").onclick = iniciarBench;
function pasoBench(now) {
  if (!bench) return;
  const t = (now - bench.t0) / bench.dur;
  if (t >= 1) {
    const m = bench.muestras.length ? bench.muestras : [1e3], avg = m.reduce((a, b) => a + b, 0) / m.length;
    const r = { dispositivo: navigator.userAgent, gpu, pantalla: `${innerWidth}x${innerHeight}@${devicePixelRatio}`, dprUsado: dpr, brillo: bench.bloom, puntos: n,
      fpsPromedio: +(1000 / avg).toFixed(1), fpsP5: +(1000 / pct(m, 0.95)).toFixed(1), cuadroP95ms: +pct(m, 0.95).toFixed(1), cuadroMaxMs: +Math.max(...m).toFixed(1), cuadros: m.length,
      gpuMedianaMs: bench.gpu.length ? +pct(bench.gpu, 0.5).toFixed(2) : null, gpuP95Ms: bench.gpu.length ? +pct(bench.gpu, 0.95).toFixed(2) : null, gpuMedidas: bench.gpu.length };
    window.__bench = r; console.log("BENCH", JSON.stringify(r));
    fetch("__bench", { method: "POST", body: JSON.stringify(r) }).catch(() => {});
    $("resultado").textContent = `Benchmark (${n.toLocaleString("es-MX")} puntos)\nFPS promedio: ${r.fpsPromedio}\nFPS p5 (peor 5%): ${r.fpsP5}\nCuadro p95: ${r.cuadroP95ms} ms\nCuadro máx: ${r.cuadroMaxMs} ms\nGPU por cuadro: mediana ${r.gpuMedianaMs ?? "n/d"} ms · p95 ${r.gpuP95Ms ?? "n/d"} ms\nDPR ${r.dprUsado} · brillo ${r.brillo ? "sí" : "no"}\nGPU: ${gpu.slice(0, 40)}`;
    $("resultado").style.display = "block"; setTimeout(() => ($("resultado").onclick = () => ($("resultado").style.display = "none")), 0);
    camera.position.copy(bench.cam0); controls.target.copy(bench.tgt0); controls.enabled = true; bench = null; return;
  }
  // recorrido: acercamiento oblicuo al centro, órbita y regreso (estresa zoom y tamaño de punto)
  const a = t * Math.PI * 2, alt = ALTO_INICIAL * (0.18 + 0.42 * (0.5 + 0.5 * Math.cos(a)));
  const ang = Math.PI * 0.28 + 0.12 * Math.sin(a * 2), rad = alt / Math.tan(1.1);
  controls.target.set(Math.sin(a) * 4000, 0, Math.cos(a) * 3000);
  camera.position.set(controls.target.x + Math.sin(a * 1.5) * rad * 0.8, alt, controls.target.z + Math.cos(a * 1.5) * rad * 0.8 * ang);
  camera.lookAt(controls.target);
}

// ── Bucle ──────────────────────────────────────────────────────
function onResize() {
  renderer.setSize(innerWidth, innerHeight); camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix();
  composer.setSize(innerWidth, innerHeight); mat.uniforms.uResY.value = innerHeight * dpr;
}
addEventListener("resize", onResize);
function bucle(now) {
  const d = now - ultimo; ultimo = now;
  if (d < 500) { dt.push(d); if (dt.length > 600) dt.shift(); if (bench) bench.muestras.push(d); }
  pasoDespertar(now); pasoBench(now); if (!bench) controls.update();
  gpuInicio();
  if (bloomOn) composer.render(); else renderer.render(scene, camera);
  gpuFin(); gpuLeer();
  acumHud += d; if (acumHud > 400) { pintarHud(); acumHud = 0; }
  // degradación automática solo en móvil sin parámetros manuales
  if (esMovil && !params.get("dpr") && !bench && dt.length > 90) {
    if (fpsActual < 40) calidadBaja++; else calidadBaja = 0;
    if (calidadBaja > 30 && dpr > 1) { dpr = Math.max(1, dpr - 0.25); renderer.setPixelRatio(dpr); mat.uniforms.uPx.value = T.luz.punto_px * dpr; mat.uniforms.uResY.value = innerHeight * dpr; composer.setSize(innerWidth, innerHeight); calidadBaja = 0; dt.length = 0; }
  }
  requestAnimationFrame(bucle);
}
requestAnimationFrame(bucle);
lanzarDespertar();
if (params.get("bench") === "1") setTimeout(iniciarBench, 2500);
window.__pulso = { n, gpu, esMovil, scene, renderer, puntos, lineas, composer, controls };

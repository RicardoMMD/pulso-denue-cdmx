// Laboratorio visual (H08): compara tres tratamientos de brillo sobre la misma ciudad y la misma cámara, con los
// tokens de diseno/. No mide rendimiento (fuera de alcance). Los colores salen de diseno/generado/tokens.js.
import * as THREE from "three";
import { MapControls } from "three/examples/jsm/controls/MapControls.js";
import { EffectComposer, RenderPass, EffectPass, BloomEffect, ToneMappingEffect, ToneMappingMode, KernelSize } from "postprocessing";
import "../../../diseno/generado/tokens.css";
import * as T from "../../../diseno/generado/tokens.js";

const $ = (id) => document.getElementById(id);
const MAPEOS = { ninguno: ToneMappingMode.LINEAR, reinhard: ToneMappingMode.REINHARD2, aces: ToneMappingMode.ACES_FILMIC, agx: ToneMappingMode.AGX, neutral: ToneMappingMode.NEUTRAL };
const PANELES = [
  { id: "sin", titulo: "Sin brillo", nota: "Solo la suma de luz de los puntos", bloom: false, halo: false },
  { id: "bloom", titulo: "Brillo por posprocesado", nota: "Desenfoque de lo más luminoso, sumado a la imagen (como el prototipo 2)", bloom: true, halo: false },
  { id: "halo", titulo: "Halo en el punto", nota: "Cada punto lleva su resplandor; sin posprocesado de brillo", bloom: false, halo: true },
];

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
const cx = meta.w / 2, cy = meta.h / 2;

// ── Estado del laboratorio (lo que se copia al elegir) ─────────
const estado = { paleta: T.paletaActiva, mapeo: T.luz.mapeo_tonos, alfa: T.luz.alfa, bloom: T.luz.brillo.intensidad, haloTamano: T.luz.halo.tamano, haloIntensidad: T.luz.halo.intensidad };
const dpr = Math.min(devicePixelRatio, 2);
const activo = new Array(8).fill(true);
const mascara = () => { const todos = activo.slice(1).every(Boolean); return activo.map((v, j) => (j === 0 || todos || v ? 1 : 0)); };
const colorDe = (hex) => { const c = new THREE.Color(hex); return new THREE.Vector3(c.r, c.g, c.b); }; // lineal: el posprocesado devuelve a sRGB
const paletaVec = () => T.paletas[estado.paleta].macrosectores.map((m) => colorDe(m.oscuro.hex));

// ── Geometría compartida por los tres paneles ──────────────────
const geo = new THREE.BufferGeometry();
const q = new Uint16Array(n * 2);
for (let i = 0; i < n; i++) { q[2 * i] = xs[i]; q[2 * i + 1] = ys[i]; }
geo.setAttribute("position", new THREE.BufferAttribute(new Float32Array(n * 3), 3));
geo.setAttribute("q", new THREE.Uint16BufferAttribute(q, 2));
geo.setAttribute("m", new THREE.Uint8BufferAttribute(macro, 1));
const fondoGeos = [];
for (const a of fondo) for (const ring of a.anillos) {
  fondoGeos.push({
    linea: new THREE.BufferGeometry().setFromPoints(ring.map(([x, y]) => new THREE.Vector3(x - cx, -1, -(y - cy)))),
    relleno: new THREE.ShapeGeometry(new THREE.Shape(ring.map(([x, y]) => new THREE.Vector2(x - cx, y - cy)))),
  });
}
const lmat = new THREE.LineBasicMaterial({ color: new THREE.Color(T.oscuro.alcaldia_trazo), transparent: true, opacity: 0.9 });
const fmat = new THREE.MeshBasicMaterial({ color: new THREE.Color(T.oscuro.alcaldia_relleno), transparent: true, opacity: 0.95, depthWrite: false });

// ── Cámara y controles compartidos ─────────────────────────────
const contenedor = $("paneles");
const camera = new THREE.PerspectiveCamera(40, 1, 50, 400000);
const ALTO = Math.max(meta.w, meta.h) * 1.25;
const controls = new MapControls(camera, contenedor);
controls.enableDamping = true; controls.dampingFactor = 0.08; controls.screenSpacePanning = false;
controls.minDistance = 300; controls.maxDistance = ALTO * 1.4; controls.maxPolarAngle = Math.PI * 0.46;

// ── Un panel = renderizador + escena + composer ────────────────
const vertex = /* glsl */ `
  attribute vec2 q; attribute float m;
  uniform vec2 uCentro; uniform vec3 uPal[7]; uniform float uMask[8];
  uniform float uPx, uAlfa, uResY, uK;
  varying vec3 vC; varying float vA;
  void main(){
    vec2 p = q - uCentro;
    vec4 mv = modelViewMatrix * vec4(p.x, 0.0, -p.y, 1.0);
    gl_Position = projectionMatrix * mv;
    int k = int(m + 0.5) - 1;
    vec3 c = vec3(1.0);
    for (int i = 0; i < 7; i++) if (i == k) c = uPal[i];
    float msk = 0.0;
    for (int i = 0; i < 8; i++) if (i == k + 1) msk = uMask[i];
    vC = c; vA = uAlfa * (${T.luz.atenuado.toFixed(3)} + ${(1 - T.luz.atenuado).toFixed(3)} * msk);
    float escala = uResY / (2.0 * tan(0.3490659) * -mv.z);
    gl_PointSize = clamp(uPx * 0.5 + escala * 7.0, uPx, uPx * 6.0) * uK;
  }`;
const fragment = /* glsl */ `
  uniform float uK, uHalo;
  varying vec3 vC; varying float vA;
  void main(){
    vec2 d = gl_PointCoord - 0.5; float r = dot(d, d) * 4.0;
    if (r >= 1.0) discard;
    float nucleo = max(0.0, 1.0 - r * uK * uK);   // con uK = 1 y uHalo = 0 es el punto del prototipo 2
    float halo = uHalo * pow(1.0 - r, 3.0);        // resplandor ancho que llega a cero en el borde del sprite
    gl_FragColor = vec4(vC * (nucleo + halo) * vA, 1.0);
  }`;

const paneles = PANELES.map((def) => {
  const caja = document.createElement("div"); caja.className = "panel";
  const renderer = new THREE.WebGLRenderer({ antialias: false, powerPreference: "high-performance", alpha: false });
  renderer.setPixelRatio(dpr);
  renderer.setClearColor(new THREE.Color(T.oscuro.fondo), 1);
  caja.appendChild(renderer.domElement);
  const rotulo = document.createElement("div"); rotulo.className = "rotulo";
  rotulo.innerHTML = `<b>${def.titulo}</b><span>${def.nota}</span>`;
  caja.appendChild(rotulo);
  contenedor.appendChild(caja);

  const scene = new THREE.Scene();
  const fondoGrupo = new THREE.Group();
  for (const g of fondoGeos) {
    fondoGrupo.add(new THREE.LineLoop(g.linea, lmat));
    const malla = new THREE.Mesh(g.relleno, fmat); malla.rotation.set(-Math.PI / 2, 0, 0); malla.position.y = -3; fondoGrupo.add(malla);
  }
  scene.add(fondoGrupo);
  const mat = new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, depthTest: false, blending: THREE.AdditiveBlending, vertexShader: vertex, fragmentShader: fragment,
    uniforms: {
      uCentro: { value: new THREE.Vector2(cx, cy) }, uPal: { value: paletaVec() }, uMask: { value: mascara() },
      uPx: { value: T.luz.punto_px * dpr }, uAlfa: { value: estado.alfa }, uResY: { value: 600 * dpr },
      uK: { value: def.halo ? estado.haloTamano : 1 }, uHalo: { value: def.halo ? estado.haloIntensidad : 0 },
    },
  });
  const puntos = new THREE.Points(geo, mat); puntos.frustumCulled = false; scene.add(puntos);

  const composer = new EffectComposer(renderer, { frameBufferType: THREE.HalfFloatType });
  composer.addPass(new RenderPass(scene, camera));
  const mapeo = new ToneMappingEffect({ mode: MAPEOS[estado.mapeo] });
  const bloom = def.bloom ? new BloomEffect({ intensity: estado.bloom, luminanceThreshold: T.luz.brillo.umbral, luminanceSmoothing: T.luz.brillo.suavizado, kernelSize: KernelSize.MEDIUM, mipmapBlur: true }) : null;
  composer.addPass(new EffectPass(camera, ...(bloom ? [bloom, mapeo] : [mapeo])));
  return { def, caja, renderer, composer, mat, mapeo, bloom };
});

function ajustarTamano() {
  const w = paneles[0].caja.clientWidth, h = paneles[0].caja.clientHeight;
  if (!w || !h) return;
  camera.aspect = w / h; camera.updateProjectionMatrix();
  for (const p of paneles) { p.renderer.setSize(w, h); p.composer.setSize(w, h); p.mat.uniforms.uResY.value = h * dpr; }
}
new ResizeObserver(ajustarTamano).observe(paneles[0].caja);

// ── Tomas fijas: el Centro denso, una periferia y la ciudad completa ──
const CELDA = 400;
const cols = Math.ceil(meta.w / CELDA) + 1, filas = Math.ceil(meta.h / CELDA) + 1;
const cuenta = new Uint32Array(cols * filas);
for (let i = 0; i < n; i++) cuenta[Math.floor(ys[i] / CELDA) * cols + Math.floor(xs[i] / CELDA)]++;
let densa = 0; for (let i = 1; i < cuenta.length; i++) if (cuenta[i] > cuenta[densa]) densa = i;
const centroCelda = (i) => [(i % cols + 0.5) * CELDA - cx, (Math.floor(i / cols) + 0.5) * CELDA - cy];
const [dx, dy] = centroCelda(densa);
let lejana = densa, mejor = 0;
for (let i = 0; i < cuenta.length; i++) if (cuenta[i] >= 60) { const [x, y] = centroCelda(i); const d = Math.hypot(x - dx, y - dy); if (d > mejor) { mejor = d; lejana = i; } }
const [lx, ly] = centroCelda(lejana);
const TOMAS = {
  centro: { objetivo: [dx, 0, -dy], posicion: [dx, 1700, -dy + 2300] },
  periferia: { objetivo: [lx, 0, -ly], posicion: [lx, 1700, -ly + 2300] },
  ciudad: { objetivo: [0, 0, 0], posicion: [0, ALTO, 1] },
};
function irA(nombre) { const t = TOMAS[nombre]; controls.target.set(...t.objetivo); camera.position.set(...t.posicion); camera.lookAt(controls.target); controls.update(); }

// ── Controles ──────────────────────────────────────────────────
const barra = $("controles");
const selector = (rotulo, valores, actual, alCambiar) => {
  const l = document.createElement("label"); l.append(rotulo + " ");
  const s = document.createElement("select");
  for (const v of valores) { const o = document.createElement("option"); o.value = v; o.textContent = v; s.appendChild(o); }
  s.value = actual; s.onchange = () => alCambiar(s.value); l.appendChild(s); barra.appendChild(l);
};
const deslizador = (rotulo, min, max, paso, clave, alCambiar) => {
  const l = document.createElement("label"); l.append(rotulo + " ");
  const r = document.createElement("input"); Object.assign(r, { type: "range", min, max, step: paso, value: estado[clave] });
  const o = document.createElement("output"); o.textContent = (+estado[clave]).toFixed(2);
  r.oninput = () => { estado[clave] = +r.value; o.textContent = (+r.value).toFixed(2); alCambiar(+r.value); salida(); };
  l.append(r, o); barra.appendChild(l);
};
const boton = (texto, alClic) => { const b = document.createElement("button"); b.textContent = texto; b.onclick = alClic; barra.appendChild(b); return b; };

selector("Paleta", Object.keys(T.paletas), estado.paleta, (v) => { estado.paleta = v; aplicarPaleta(); salida(); });
selector("Mapeo de tonos", Object.keys(MAPEOS), estado.mapeo, (v) => { estado.mapeo = v; for (const p of paneles) p.mapeo.mode = MAPEOS[v]; salida(); });
deslizador("Punto", 0.1, 1.2, 0.05, "alfa", (v) => paneles.forEach((p) => (p.mat.uniforms.uAlfa.value = v)));
deslizador("Brillo", 0, 3, 0.1, "bloom", (v) => paneles.forEach((p) => p.bloom && (p.bloom.intensity = v)));
deslizador("Halo: tamaño", 1, 4, 0.1, "haloTamano", (v) => paneles.forEach((p) => p.def.halo && (p.mat.uniforms.uK.value = v)));
deslizador("Halo: intensidad", 0, 0.6, 0.02, "haloIntensidad", (v) => paneles.forEach((p) => p.def.halo && (p.mat.uniforms.uHalo.value = v)));
boton("Centro denso", () => irA("centro"));
boton("Periferia", () => irA("periferia"));
boton("Ciudad completa", () => irA("ciudad"));
boton("Copiar parámetros", () => { const t = JSON.stringify(estado); navigator.clipboard?.writeText(t); $("salida").textContent = "Copiado: " + t; });

function salida() { $("salida").textContent = JSON.stringify(estado); }

// ── Leyenda (filtrar atenúa) y muestras en papel ───────────────
function aplicarPaleta() {
  const vec = paletaVec();
  for (const p of paneles) p.mat.uniforms.uPal.value = vec;
  const ms = T.paletas[estado.paleta].macrosectores;
  $("leyenda").replaceChildren(...ms.map((m, i) => {
    const b = document.createElement("button"); b.setAttribute("aria-pressed", String(activo[i + 1]));
    b.innerHTML = `<i style="background:${m.oscuro.hex}"></i>${m.nombre}`;
    b.onclick = () => { activo[i + 1] = !activo[i + 1]; b.setAttribute("aria-pressed", String(activo[i + 1])); const mk = mascara(); for (const p of paneles) p.mat.uniforms.uMask.value = mk; };
    return b;
  }));
  $("papel").replaceChildren(...ms.map((m) => {
    const d = document.createElement("div");
    d.innerHTML = `<i style="background:${m.claro.hex}"></i>${m.nombre}<em>${m.claro.contraste.toFixed(2)}:1</em>`;
    return d;
  }));
}
aplicarPaleta();

// ── Bucle ──────────────────────────────────────────────────────
function bucle() { controls.update(); for (const p of paneles) p.composer.render(); requestAnimationFrame(bucle); }
ajustarTamano();
irA("centro");
salida();
requestAnimationFrame(bucle);
window.__lab = { estado, irA, paneles, controls, camera };

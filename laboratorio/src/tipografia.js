// Muestra de tipografía (H08): títulos, texto de panel, cifras tabulares contando y etiquetas 3D con troika,
// en los dos temas. Todo sale de diseno/generado/tokens.*; la fuente se sirve desde diseno/fuentes/.
import * as THREE from "three";
import { Text } from "troika-three-text";
import "../../diseno/generado/tokens.css";
import * as T from "../../diseno/generado/tokens.js";
import fuente3d from "../../diseno/fuentes/Inter-latin-600.woff?url";

const $ = (id) => document.getElementById(id);
const fmt = (n) => String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, "\u00a0"); // 462 729, como en los documentos del proyecto

// Las cifras son de muestra de la tipografía (ancho de dígitos), no cifras publicables: vienen de la edición 2026-05
// solo como orden de magnitud realista; el portal las leerá de semantic.
const MUESTRA = [[T.macrosectores[0], 227775], [T.macrosectores[1], 64210], [T.macrosectores[2], 51034], [T.macrosectores[3], 38412], [T.macrosectores[4], 31080], [T.macrosectores[5], 28771], [T.macrosectores[6], 3892]];
const total = 462729;
$("tabla").tBodies[0].replaceChildren(...MUESTRA.map(([m, v]) => {
  const tr = document.createElement("tr");
  tr.innerHTML = `<td><span class="punto" style="background:var(--macro-${m.clave.replaceAll("_", "-")})"></span>${m.nombre}</td><td class="n">${fmt(v)}</td><td class="n">${(v / total * 100).toFixed(1)} %</td>`;
  return tr;
}));

let raf = 0;
function contar() {
  cancelAnimationFrame(raf);
  const t0 = performance.now(), dur = 1800;
  const paso = (t) => { const k = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - k, 3); $("cifra").textContent = fmt(total * e); if (k < 1) raf = requestAnimationFrame(paso); };
  raf = requestAnimationFrame(paso);
}
$("contar").onclick = contar; contar();

$("tema").onclick = () => {
  const claro = document.documentElement.dataset.tema !== "claro";
  document.documentElement.dataset.tema = claro ? "claro" : "oscuro";
  $("tema").textContent = "Tema: " + (claro ? "claro" : "oscuro"); $("tema").setAttribute("aria-pressed", String(claro));
};
const medir = () => ($("ancho").textContent = `ancho ${innerWidth} px · fuente ${getComputedStyle(document.body).fontFamily.split(",")[0]}`);
addEventListener("resize", medir); medir();

// ── Etiquetas 3D ───────────────────────────────────────────────
const caja = $("escena");
const renderer = new THREE.WebGLRenderer({ antialias: true }); renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setClearColor(new THREE.Color(T.oscuro.fondo), 1); caja.appendChild(renderer.domElement);
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(40, 1, 1, 5000); camera.position.set(0, 230, 330); camera.lookAt(0, 0, 0);
const sitios = [["Centro Histórico", -150, 40, 0], ["Línea 1 · Tren de luz", 40, 90, 1], ["Merced: 6 103 negocios", 150, -30, 2], ["Ñuñoa · ¿qué hay?", -60, -90, 3]];
const colores = T.macrosectores.map((m) => m.oscuro.hex);
const puntos = [];
for (const [texto, x, z, k] of sitios) {
  const t = new Text();
  Object.assign(t, { text: texto, font: fuente3d, fontSize: 24, color: T.oscuro.texto, anchorX: "center", anchorY: "bottom", outlineWidth: 0.8, outlineColor: T.oscuro.fondo });
  t.position.set(x, 18, z); t.rotation.x = -0.45; t.sync(); scene.add(t);
  puntos.push(new THREE.Vector3(x, 0, z), new THREE.Vector3(x + 6, 0, z + 5), new THREE.Vector3(x - 7, 0, z - 4));
  const g = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(x, 0, z)]);
  scene.add(new THREE.Points(g, new THREE.PointsMaterial({ color: colores[k], size: 9, sizeAttenuation: false })));
}
function ajustar() { const w = caja.clientWidth, h = caja.clientHeight; renderer.setSize(w, h); camera.aspect = w / h; camera.updateProjectionMatrix(); }
new ResizeObserver(ajustar).observe(caja); ajustar();
(function bucle() { renderer.render(scene, camera); requestAnimationFrame(bucle); })();
window.__tipografia = { Text, scene };

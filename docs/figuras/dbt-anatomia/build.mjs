// Figura "dbt build" (skill anatomy): una línea de estampado de cuatro émbolos sobre una placa.
// Todo número sale de dbt/target/manifest.json del proyecto (14 nov 2026): 18 fuentes, 17 + 33 + 18 modelos,
// 113 pruebas (12 / 85 / 16 por capa; la capa es la más alta que toca la prueba), threads: 4, todo en `table`.
// Uso: node build.mjs [--light]   (necesita la skill anatomy en ANATOMY_DIR o ~/.claude/skills/anatomy)
import { writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const SKILL = process.env.ANATOMY_DIR ?? `${process.env.HOME}/.claude/skills/anatomy`;
const k = await import(`${SKILL}/kit/iso-kit.mjs`);
const { kitScript } = await import(`${SKILL}/scripts/inline-kit.mjs`);

const HERE = dirname(fileURLToPath(import.meta.url));
const theme = process.argv.includes("--light") ? "light" : "dark";

// ---------- Verdad: el modelo del proyecto ----------
const THREADS = 4;
const SECTIONS = [
  { id: "raw", n: 18, tests: 0 }, // fuentes: las carga el pipeline, dbt no las construye
  { id: "staging", n: 17, tests: 12 },
  { id: "core", n: 33, tests: 85 },
  { id: "semantic", n: 18, tests: 16 },
];
const MODELS = SECTIONS.slice(1).reduce((sum, s) => sum + s.n, 0); // 68
const TESTS = SECTIONS.reduce((sum, s) => sum + s.tests, 0); // 113

// ---------- Mundo ----------
const WIDTH = 650;
const HEIGHT = 330;
const COLS = [-24, -8, 8, 24]; // una columna por hilo
const PITCH = 12; // una fila cada 12 unidades en x
const SLOT = { w: 9, d: 11 };
const TRAY_Z = 3; // la bandeja es una losa de 0 a 3
const BLANK_H = 1.2;
const BLOCK_H = 6;
const GAP = { raw: 22, staging: 20, core: 20, semantic: 20 };

// Disposición: bandejas de izquierda a derecha, con el medidor en el hueco que sigue a cada capa construida.
let cursor = 0;
const trays = SECTIONS.map((s) => {
  const rows = Math.ceil(s.n / THREADS);
  const tray = { ...s, rows, x: cursor, w: rows * PITCH + 8, d: 76 };
  cursor += tray.w + GAP[s.id];
  return tray;
});
const [RAW, STAGING, CORE, SEMANTIC] = trays;
const gauges = [STAGING, CORE, SEMANTIC].map((t) => ({ layer: t.id, tests: t.tests, n: t.n, x: t.x + t.w + 10, y: 0 }));

// Filas que recorre el pórtico (raw no se construye): una por fila de cada bandeja.
const ROWS = [];
for (const t of [STAGING, CORE, SEMANTIC]) {
  for (let r = 0; r < t.rows; r++) {
    ROWS.push({ layer: t.id, x: t.x + 4 + PITCH / 2 + r * PITCH, slots: Math.min(THREADS, t.n - r * THREADS) });
  }
}
const slotCenter = (t, r, c) => [t.x + 4 + PITCH / 2 + r * PITCH, COLS[c]];

const PLATE = { x: -18, y: -68, w: cursor - GAP.semantic + 20 + 18 + 12, d: 136, r: 8 };
const PLATE_H = 12;
const FOOT_H = 5;
const RAIL_Y = 54;
const RAIL_FROM = STAGING.x - 10;
const RAIL_TO = SEMANTIC.x + SEMANTIC.w + GAP.semantic + 2;

// Pórtico (se construye en x = 0 y se mueve con translateAlong)
const BEAM_Z = 33;
const BEAM_H = 8;
const PAD_UP = 15; // fondo de la almohadilla arriba (z)
const PAD_STROKE = 6; // carrera: baja hasta la cara superior del bloque (3 + 6 = 9)
const ROD_LEN = 27;

const top = (z) => z;
const P = k.fitProjection(
  [...k.boxCorners(PLATE, -PLATE_H - FOOT_H, 0), [RAIL_FROM, -RAIL_Y, 48], [RAIL_TO, RAIL_Y, 48], [RAIL_FROM, RAIL_Y, 48]],
  WIDTH,
  HEIGHT,
  { pad: 16, azimuth: 58 },
);
const at = (point) => k.iso(point, P);
const S = (paths, style) => k.solidSvg(paths, style);
const L = (d, style) => k.lineSvg(d, style);
const D = (points, style) => k.dotsSvg(points, style);
const depthXY = (x, y) => k.depthOf([x, y, 0], P);
const byDepth = (items, get = (i) => i) => [...items].sort((a, b) => depthXY(...get(a)) - depthXY(...get(b)));

// ---------- Placa ----------
function plate() {
  const out = [`<path class="iso-halo" d="${k.haloOf(PLATE, -PLATE_H - FOOT_H, PLATE_H, P)}"/>`];
  for (const [x, y] of byDepth(k.corners(PLATE, 22))) {
    out.push(S(k.cylinder(x, y, 7, -PLATE_H - FOOT_H, 1.6, P, 28), { tone: "lo" }));
    out.push(S(k.cylinder(x, y, 5.4, -PLATE_H - FOOT_H + 1.6, FOOT_H - 1.6, P, 28), { tone: "mid" }));
  }
  out.push(S(k.slabOf(PLATE, -PLATE_H, PLATE_H, P, 8, 1.6), { tone: "mid" }));
  out.push(L(k.planOutline(k.insetPlan(PLATE, 5), 0, P), { tone: "lo" }));
  const screws = k.corners(PLATE, 10);
  out.push(L(screws.map(([x, y]) => k.ring(x, y, 2.2, 0, P, 16)).join(""), { tone: "lo" }));
  out.push(D(screws.map(([x, y]) => at([x, y, 0])), { size: 0.5 }));
  // regla del frente: una marca por fila de modelos (12 unidades), mayor cada cuatro hilos... cada 5 filas
  const strip = { x: PLATE.x + 14, y: PLATE.y + PLATE.d - 15, w: PLATE.w - 28, d: 7, r: 1 };
  out.push(S(k.slabOf(strip, 0, 0.6, P, 3), { tone: "lo", crease: "none" }));
  const ticks = k.topTicks(strip.x + 4, strip.x + strip.w - 4, PITCH, 5, strip.y + 0.8, 0.6, [2, 3.6], P);
  out.push(L(ticks.minor, { tone: "lo" }), L(ticks.major, { tone: "mid" }));
  out.push(D([at([strip.x + 2, strip.y + 3.5, 0.6]), at([strip.x + strip.w - 2, strip.y + 3.5, 0.6])], { size: 0.45 }));
  // placa de datos con tres renglones, en la esquina trasera izquierda
  const label = { x: PLATE.x + 14, y: PLATE.y + 9, w: 34, d: 18, r: 2 };
  out.push(S(k.slabOf(label, 0, 0.8, P, 4, 0.3), { tone: "mid", crease: "none" }));
  [4, 9, 14].forEach((dy, index) =>
    out.push(L(k.lineOnTop([label.x + 4, label.y + dy], [label.x + label.w - (index === 2 ? 14 : 4), label.y + dy], 0.8, P), { tone: "faint", free: true })),
  );
  out.push(D([at([label.x + 2, label.y + 2, 0.8]), at([label.x + label.w - 2, label.y + 2, 0.8]), at([label.x + 2, label.y + label.d - 2, 0.8]), at([label.x + label.w - 2, label.y + label.d - 2, 0.8])], { size: 0.4 }));
  return out.join("");
}

// ---------- Rieles y topes ----------
function rails() {
  const out = [];
  for (const y of [-RAIL_Y, RAIL_Y]) {
    out.push(S(k.slabOf({ x: RAIL_FROM, y: y - 3, w: RAIL_TO - RAIL_FROM, d: 6, r: 1 }, 0, TRAY_Z, P, 3, 0.4), { tone: "mid" }));
    out.push(L(k.lineOnTop([RAIL_FROM + 3, y], [RAIL_TO - 3, y], TRAY_Z, P), { tone: "faint" }));
    const screws = [];
    for (let x = RAIL_FROM + 8; x < RAIL_TO - 4; x += 24) screws.push(at([x, y, TRAY_Z]));
    out.push(D(screws, { size: 0.4, tone: "lo" }));
  }
  for (const x of [RAIL_FROM - 6, RAIL_TO]) {
    out.push(S(k.slabOf({ x, y: -RAIL_Y - 5, w: 6, d: RAIL_Y * 2 + 10, r: 1.4 }, 0, 9, P, 3, 0.5), { tone: "mid" }));
    for (const y of [-RAIL_Y, RAIL_Y]) {
      out.push(S(k.cylinder(x + 3, y, 3.4, 9, 3, P, 20), { tone: "mid" }));
      out.push(L(k.knurl(x + 3, y, 3.4, 9, 12, 16, P), { tone: "lo" }));
    }
  }
  return out.join("");
}

// ---------- Bandejas, láminas, bloques y tambores ----------
function trayBase(t) {
  const plan = { x: t.x, y: -t.d / 2, w: t.w, d: t.d, r: 3 };
  const out = [S(k.slabOf(plan, 0, TRAY_Z, P, 4, 0.6), { tone: "mid" })];
  out.push(L(k.planOutline(k.insetPlan(plan, 2), TRAY_Z, P, 4), { tone: "faint" }));
  const screws = k.corners(plan, 4);
  out.push(D(screws.map(([x, y]) => at([x, y, TRAY_Z])), { size: 0.42, tone: "lo" }));
  // marcas de fila en el borde del frente: ahí se lee "una fila = cuatro modelos a la vez"
  const marks = [];
  for (let r = 0; r <= t.rows; r++) marks.push(k.lineOnTop([t.x + 4 + r * PITCH, t.d / 2 - 5], [t.x + 4 + r * PITCH, t.d / 2 - 2.4], TRAY_Z, P));
  out.push(L(marks.join(""), { tone: "lo" }));
  return out.join("");
}

function slotPlan([cx, cy], inset = 0) {
  return { x: cx - SLOT.w / 2 + inset, y: cy - SLOT.d / 2 + inset, w: SLOT.w - inset * 2, d: SLOT.d - inset * 2, r: 1.2 };
}

function blankSvg(c) {
  return S(k.slabOf(slotPlan(c), TRAY_Z, BLANK_H, P, 3, 0.3), { tone: "faint", crease: "none" });
}

function blockSvg(c, layer) {
  const tone = layer === "semantic" ? "hi" : "mid";
  const plan = slotPlan(c);
  const out = [S(k.slabOf(plan, TRAY_Z, BLOCK_H, P, 3, 0.5), { tone, crease: "lo" })];
  out.push(L(k.planOutline(k.insetPlan(plan, 1.8), TRAY_Z + BLOCK_H, P, 3), { tone: "faint" }));
  if (layer !== "staging") out.push(L(k.lineOnTop([c[0] - 2.4, c[1]], [c[0] + 2.4, c[1]], TRAY_Z + BLOCK_H, P), { tone: "faint" }));
  if (layer === "semantic") out.push(D([at([c[0], c[1] + 3.4, TRAY_Z + BLOCK_H])], { size: 0.45, tone: "hi" }));
  return out.join("");
}

function drumSvg(c) {
  const out = [S(k.cylinder(c[0], c[1], 4.8, TRAY_Z, 7, P, 24, 0.5), { tone: "lo" })];
  out.push(L(k.ring(c[0], c[1], 3.2, TRAY_Z + 7, P, 20), { tone: "faint" }));
  out.push(L(k.sideArc(c[0], c[1], 4.8, TRAY_Z + 3, P, 16), { tone: "faint" }));
  out.push(D([at([c[0], c[1], TRAY_Z + 7])], { size: 0.42, tone: "lo" }));
  return out.join("");
}

function section(t) {
  const out = [trayBase(t)];
  const slots = [];
  let index = 0;
  for (let r = 0; r < t.rows; r++) {
    for (let c = 0; c < THREADS && index < t.n; c++, index++) slots.push({ r, c, index, at: slotCenter(t, r, c) });
  }
  for (const s of byDepth(slots, (s) => s.at)) {
    if (t.id === "raw") out.push(drumSvg(s.at));
    else {
      const id = MODEL_OFFSET[t.id] + s.index;
      out.push(`<g data-blank="${id}">${blankSvg(s.at)}</g><g data-block="${id}" style="display:none">${blockSvg(s.at, t.id)}</g>`);
    }
  }
  return out.join("");
}
const MODEL_OFFSET = { staging: 0, core: STAGING.n, semantic: STAGING.n + CORE.n };

// Canalitos que llevan las fuentes hacia la primera bandeja: una guía por hilo
function lanes() {
  const out = [];
  for (const y of COLS) {
    out.push(S(k.slabOf({ x: RAW.x + RAW.w, y: y - 1.4, w: STAGING.x - RAW.x - RAW.w, d: 2.8, r: 0.8 }, 0, 1.4, P, 2), { tone: "lo", crease: "none" }));
  }
  return out.join("");
}

// ---------- Medidores (una capa = un medidor) ----------
const GAUGE_R = 7.6;
const GAUGE_BASE = 6;
const GAUGE_TOP = 10;
const NEEDLE_FROM = (-150 * Math.PI) / 180;
const NEEDLE_SPAN = (300 * Math.PI) / 180;
function gauge(g) {
  const out = [];
  const { x, y } = g;
  out.push(`<path class="iso-halo" d="${k.haloOf({ x: x - 9, y: y - 9, w: 18, d: 18, r: 9 }, 0, 1, P)}"/>`);
  out.push(S(k.cylinder(x, y, 8.8, 0, GAUGE_BASE, P, 32, 0.6), { tone: "lo" }));
  out.push(D([[x - 6.4, y - 6.4], [x + 6.4, y + 6.4], [x - 6.4, y + 6.4], [x + 6.4, y - 6.4]].map(([a, b]) => at([a, b, GAUGE_BASE])), { size: 0.4, tone: "lo" }));
  out.push(S(k.cylinder(x, y, GAUGE_R, GAUGE_BASE, GAUGE_TOP - GAUGE_BASE, P, 40, 0.5), { tone: "hi", crease: "lo" }));
  out.push(L(k.knurl(x, y, GAUGE_R, GAUGE_TOP - 1.8, GAUGE_TOP, 56, P, 0.3), { tone: "lo" }));
  out.push(L(k.ring(x, y, GAUGE_R - 1.4, GAUGE_TOP, P, 40), { tone: "lo" }));
  const ticks = k.radialTicks(x, y, GAUGE_R - 1.8, 30, 5, GAUGE_TOP, [0.9, 1.9], P, NEEDLE_FROM, NEEDLE_SPAN);
  out.push(L(ticks.minor, { tone: "lo" }), L(ticks.major, { tone: "mid" }));
  out.push(L(k.ring(x, y, 1, GAUGE_TOP, P, 12), { tone: "mid" }));
  return out.join("");
}
const needlePath = (g, fraction) => {
  const a = NEEDLE_FROM + fraction * NEEDLE_SPAN;
  const [sx, sy] = [Math.sin(a), -Math.cos(a)];
  return k.lineOnTop([g.x - sx * 2.4, g.y - sy * 2.4], [g.x + sx * (GAUGE_R - 2.6), g.y + sy * (GAUGE_R - 2.6)], GAUGE_TOP + 0.2, P);
};

// ---------- Pórtico ----------
const LEG = { w: 16, d: 12 };
function legBack() {
  const y = -RAIL_Y;
  const out = [S(k.slabOf({ x: -LEG.w / 2, y: y - LEG.d / 2, w: LEG.w, d: LEG.d, r: 2 }, TRAY_Z, 5, P, 3, 0.5), { tone: "mid" })];
  out.push(S(k.slabOf({ x: -4.5, y: y - 4.5, w: 9, d: 9, r: 1.4 }, TRAY_Z + 5, BEAM_Z - TRAY_Z - 5, P, 3, 0.4), { tone: "mid" }));
  out.push(D([at([-5, y, TRAY_Z + 5]), at([5, y, TRAY_Z + 5])], { size: 0.4, tone: "lo" }));
  return out.join("");
}
function legFront() {
  const y = RAIL_Y;
  const out = [`<path class="iso-halo" d="${k.haloOf({ x: -LEG.w / 2, y: y - LEG.d / 2, w: LEG.w, d: LEG.d, r: 2 }, TRAY_Z, 0.1, P)}" style="filter:blur(3px)"/>`];
  out.push(S(k.slabOf({ x: -LEG.w / 2, y: y - LEG.d / 2, w: LEG.w, d: LEG.d, r: 2 }, TRAY_Z, 5, P, 3, 0.5), { tone: "mid" }));
  out.push(S(k.slabOf({ x: -4.5, y: y - 4.5, w: 9, d: 9, r: 1.4 }, TRAY_Z + 5, BEAM_Z - TRAY_Z - 5, P, 3, 0.4), { tone: "mid" }));
  out.push(D([at([-5, y + 6, TRAY_Z + 5]), at([5, y + 6, TRAY_Z + 5])], { size: 0.4, tone: "lo" }));
  // perilla de ajuste en el frente del pie
  out.push(S(k.cylinder(0, y + 8.4, 2.6, TRAY_Z, 4, P, 18), { tone: "mid" }));
  out.push(L(k.knurl(0, y + 8.4, 2.6, TRAY_Z, TRAY_Z + 4, 16, P), { tone: "lo" }));
  return out.join("");
}
function plunger(y) {
  const out = [S(k.cylinder(0, y, 4.2, 0, 2.4, P, 28, 0.4), { tone: "hi", lit: true })];
  out.push(S(k.cylinder(0, y, 1.6, 2.4, ROD_LEN, P, 16), { tone: "hi", crease: "none", lit: true }));
  return out.join("");
}
function collars() {
  return COLS.map((y) => S(k.cylinder(0, y, 3.1, BEAM_Z - 3, 3, P, 22, 0.3), { tone: "mid" })).join("");
}
function beam() {
  const plan = { x: -6, y: -RAIL_Y - 6, w: 12, d: RAIL_Y * 2 + 12, r: 2 };
  const out = [S(k.slabOf(plan, BEAM_Z, BEAM_H, P, 4, 0.7), { tone: "mid" })];
  out.push(L(k.planOutline(k.insetPlan(plan, 2), BEAM_Z + BEAM_H, P, 4), { tone: "faint" }));
  out.push(D([at([-3.6, -RAIL_Y, BEAM_Z + BEAM_H]), at([3.6, -RAIL_Y, BEAM_Z + BEAM_H]), at([-3.6, RAIL_Y, BEAM_Z + BEAM_H]), at([3.6, RAIL_Y, BEAM_Z + BEAM_H])], { size: 0.45 }));
  for (const y of COLS) {
    out.push(S(k.cylinder(0, y, 3.4, BEAM_Z + BEAM_H, 4, P, 24, 0.3), { tone: "mid" }));
    out.push(L(k.ring(0, y, 1.8, BEAM_Z + BEAM_H + 4, P, 14), { tone: "lo" }));
  }
  // motor: caja y eje con perilla estriada, al centro de la viga
  out.push(S(k.slabOf({ x: -5, y: -9, w: 10, d: 18, r: 2 }, BEAM_Z + BEAM_H, 8, P, 4, 0.6), { tone: "mid" }));
  out.push(L(k.planOutline(k.insetPlan({ x: -5, y: -9, w: 10, d: 18, r: 2 }, 1.6), BEAM_Z + BEAM_H + 8, P, 4), { tone: "faint" }));
  out.push(S(k.cylinder(0, 0, 3.2, BEAM_Z + BEAM_H + 8, 4, P, 22), { tone: "mid" }));
  out.push(L(k.knurl(0, 0, 3.2, BEAM_Z + BEAM_H + 8, BEAM_Z + BEAM_H + 12, 20, P), { tone: "lo" }));
  return out.join("");
}

// ---------- Ensamble ----------
const g0 = ROWS[0].x;
const gaugeSvg = gauges.map(gauge).join("");
const needles = gauges.map((g, i) => `<path data-needle="${i}" class="iso-line" data-tone="hi" data-free="start" d="${needlePath(g, 0)}" style="stroke-width:1.1"/>`).join("");
const groupAt = (name, x, z, inner) => `<g data-part="${name}" transform="${k.translateAlong(P, [x, 0, z])}">${inner}</g>`;
const plungers = COLS.map((y, i) => groupAt(`plunger-${i}`, g0, PAD_UP, plunger(y))).join("");

const svg = k.figureSvg({
  width: WIDTH,
  height: HEIGHT,
  label:
    "Una línea de estampado sobre una placa. A la izquierda, 18 tambores: las fuentes de raw. Tres bandejas de láminas planas, con 17, 33 y 18 piezas: los modelos de staging, core y semantic. Un pórtico de cuatro émbolos recorre los rieles y estampa cada lámina hasta convertirla en bloque, cuatro por fila, y al final de cada bandeja un medidor cuenta las pruebas de esa capa: 12, 85 y 16.",
  body: [
    plate(),
    rails(),
    section(RAW),
    lanes(),
    groupAt("leg-back", g0, 0, legBack()),
    section(STAGING),
    section(CORE),
    section(SEMANTIC),
    gaugeSvg,
    needles,
    groupAt("leg-front", g0, 0, legFront()),
    plungers,
    groupAt("collars", g0, 0, collars()),
    groupAt("beam", g0, 0, beam()),
  ],
});

// ---------- Vida ----------
const live = `
const P = ${JSON.stringify(P)};
const ROWS = ${JSON.stringify(ROWS)};
const COLS = ${JSON.stringify(COLS)};
const GAUGES = ${JSON.stringify(gauges)};
const OFFSET = ${JSON.stringify(MODEL_OFFSET)};
const LAYERS = ${JSON.stringify(SECTIONS.slice(1).map((s) => ({ id: s.id, n: s.n, tests: s.tests })))};
const MODELS = ${MODELS}, TESTS = ${TESTS}, PAD_UP = ${PAD_UP}, PAD_STROKE = ${PAD_STROKE};
const GAUGE_R = ${GAUGE_R}, GAUGE_TOP = ${GAUGE_TOP}, FROM = ${NEEDLE_FROM}, SPAN = ${NEEDLE_SPAN};
const THREADS = ${THREADS};
const stage = document.querySelector(".iso-stage");
const svg = stage.querySelector("svg");
const readout = document.querySelector("[data-readout]");
const still = matchMedia("(prefers-reduced-motion: reduce)");
const beam = svg.querySelector('[data-part="beam"]');
const collars = svg.querySelector('[data-part="collars"]');
const legBack = svg.querySelector('[data-part="leg-back"]');
const legFront = svg.querySelector('[data-part="leg-front"]');
const plungers = [0, 1, 2, 3].map((i) => svg.querySelector('[data-part="plunger-' + i + '"]'));
const needles = GAUGES.map((_, i) => svg.querySelector('[data-needle="' + i + '"]'));
const blanks = [], blocks = [];
svg.querySelectorAll("[data-blank]").forEach((el) => { blanks[+el.dataset.blank] = el; });
svg.querySelectorAll("[data-block]").forEach((el) => { blocks[+el.dataset.block] = el; });
const built = new Array(MODELS).fill(false);
const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
const ease = (t) => t * t * (3 - 2 * t);
const needleAt = (g, fraction) => {
  const a = FROM + fraction * SPAN, sx = Math.sin(a), sy = -Math.cos(a);
  return lineOnTop([g.x - sx * 2.4, g.y - sy * 2.4], [g.x + sx * (GAUGE_R - 2.6), g.y + sy * (GAUGE_R - 2.6)], GAUGE_TOP + 0.2, P);
};
let rowOffset = [], total = 0;
for (const r of ROWS) { rowOffset.push(total); total += r.slots; }
let shown = -1, lastText = "", lastGx = NaN;
function setBuilt(count) {
  for (let i = 0; i < MODELS; i++) {
    const on = i < count;
    if (built[i] !== on) { built[i] = on; blanks[i].style.display = on ? "none" : ""; blocks[i].style.display = on ? "" : "none"; }
  }
}
// p = filas recorridas (0 a ROWS.length). Una fila: baja, estampa, sube y el pórtico pasa a la siguiente.
function draw(p, quick) {
  const n = ROWS.length;
  const row = Math.min(n - 1, Math.floor(p)), f = p >= n ? 1 : p - row;
  const stamp = f < 0.55 ? Math.sin(Math.PI * (f / 0.55)) : 0;
  const done = rowOffset[row] + (f > 0.27 ? ROWS[row].slots : 0);
  const next = ROWS[Math.min(n - 1, row + 1)];
  const gx = f > 0.55 && row < n - 1 ? ROWS[row].x + (next.x - ROWS[row].x) * ease((f - 0.55) / 0.45) : ROWS[row].x;
  const dip = quick ? 0 : stamp;
  setBuilt(Math.min(MODELS, p >= n ? MODELS : done));
  if (gx !== lastGx) {
    lastGx = gx;
    for (const part of [beam, collars, legBack, legFront]) part.setAttribute("transform", translateAlong(P, [gx, 0, 0]));
  }
  plungers.forEach((el, i) => {
    const works = i < ROWS[row].slots && !quick;
    el.setAttribute("transform", translateAlong(P, [gx, 0, PAD_UP - (works ? PAD_STROKE * dip : 0)]));
  });
  let testsDone = 0, modelsDone = 0;
  GAUGES.forEach((g, i) => {
    const L = LAYERS[i];
    let c = 0;
    for (let j = 0; j < L.n; j++) if (built[OFFSET[L.id] + j]) c++;
    modelsDone += c;
    testsDone += Math.round(L.tests * c / L.n);
    needles[i].setAttribute("d", needleAt(g, c / L.n));
  });
  const layer = ROWS[Math.min(n - 1, row)].layer;
  const text = modelsDone === 0 ? "listo para construir · " + MODELS + " modelos, " + TESTS + " pruebas"
    : layer + " · modelos " + modelsDone + " de " + MODELS + " · pruebas " + testsDone + " de " + TESTS;
  if (text !== lastText) { lastText = text; readout.textContent = text; stage.setAttribute("aria-valuetext", text); stage.setAttribute("aria-valuenow", String(modelsDone)); }
}
let p = 0, target = 0, last = 0, frame = 0, clock = 0, touring = true, visible = false, idleTimer = 0, phase = "build", hold = 0;
function tick(now) {
  const dt = last ? Math.min((now - last) / 1000, 1 / 30) : 1 / 60;
  last = now;
  const n = ROWS.length;
  let quick = false;
  if (touring) {
    if (phase === "build") { p = Math.min(n, p + dt * 1.15); if (p >= n) { phase = "hold"; hold = 2.4; } }
    else if (phase === "hold") { hold -= dt; if (hold <= 0) phase = "drop"; }
    else if (phase === "drop") { quick = true; p = Math.max(0, p - dt * 11); if (p <= 0) { phase = "rest"; hold = 1.1; } }
    else { hold -= dt; if (hold <= 0) phase = "build"; }
  } else {
    const before = p;
    p = still.matches ? target : p + (target - p) * (1 - Math.exp(-dt / 0.3));
    if (Math.abs(target - p) < 0.002) p = target;
    quick = Math.abs(p - before) / dt > 2.6;
  }
  draw(p, quick);
  const settled = !touring && p === target;
  frame = visible && !settled ? requestAnimationFrame(tick) : 0;
}
const run = () => { if (!frame && visible) { last = 0; frame = requestAnimationFrame(tick); } };
const steer = (next) => { touring = false; target = clamp(next, 0, ROWS.length); clearTimeout(idleTimer); idleTimer = setTimeout(() => { touring = !still.matches; phase = "build"; run(); }, 4200); run(); };
new IntersectionObserver((entries) => { visible = entries[entries.length - 1].isIntersecting; if (visible) run(); }, { rootMargin: "120px 0px" }).observe(stage);
if (still.matches) { touring = false; target = ROWS.length; p = target; }
stage.addEventListener("pointermove", (event) => {
  const box = svg.getBoundingClientRect();
  const share = clamp(((event.clientX - box.left) / box.width - 0.12) / 0.76, 0, 1);
  steer(share * ROWS.length);
});
stage.addEventListener("pointerleave", () => steer(target));
stage.addEventListener("keydown", (event) => {
  let to = null;
  const here = Math.round(target);
  if (event.key === "ArrowRight" || event.key === "ArrowUp") to = here + 1;
  if (event.key === "ArrowLeft" || event.key === "ArrowDown") to = here - 1;
  if (event.key === "Home") to = 0;
  if (event.key === "End") to = ROWS.length;
  if (to === null) return;
  event.preventDefault();
  steer(to);
});
draw(p, false);
`;

const body = k.plateHtml({
  fig: "Fig 1",
  title: "dbt build",
  hint: "Pasa el cursor para recorrer el build",
  readout: `listo para construir · ${MODELS} modelos, ${TESTS} pruebas`,
  keys: [
    { mark: "lit", label: `Cuatro émbolos: los ${THREADS} hilos de dbt` },
    { mark: "raised", label: "Un bloque es un modelo: una tabla recreada entera" },
    { mark: "flat", label: "Lámina plana: modelo aún sin construir" },
    { mark: "lo", label: `Tambores: las ${RAW.n} fuentes de raw` },
    { mark: "mid", label: "Medidor: las pruebas de cada capa" },
  ],
  caption: `dbt lee los ${MODELS} modelos SQL del proyecto y los construye en el orden que fijan los ref(), hasta cuatro a la vez. Cada modelo es una tabla que se borra y se vuelve a crear entera: staging (${STAGING.n}), core (${CORE.n}) y semantic (${SEMANTIC.n}), siempre en esa dirección. Cada medidor cuenta las pruebas de su capa (${STAGING.tests}, ${CORE.tests} y ${SEMANTIC.tests}); cada prueba se asigna a la capa más alta que toca.`,
  body: `<div class="iso-stage" tabindex="0" role="slider" aria-label="Recorrido del build de dbt: flechas izquierda y derecha avanzan una fila de modelos" aria-valuemin="0" aria-valuemax="${MODELS}" aria-valuenow="0">${svg}</div>`,
});

const file = theme === "light" ? "dbt-anatomia-light.html" : "dbt-anatomia.html";
writeFileSync(join(HERE, file), k.pageHtml({ title: "dbt build", theme, body, script: kitScript() + live }));
console.log("escrito", file, "· modelos", MODELS, "· pruebas", TESTS, "· filas", ROWS.length);

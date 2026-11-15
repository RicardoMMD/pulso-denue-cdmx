// Genera diseno/generado/tokens.js (motor y laboratorio) y tokens.css (interfaz y vista exacta 2D) desde tokens.json.
// No se editan a mano. Uso: node diseno/generar.mjs
// Los nombres y el orden de los macrosectores salen de dbt/seeds/ref_macrosector.csv, para que no se repitan aquí.
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const AQUI = dirname(fileURLToPath(import.meta.url));
const SEMILLA = join(AQUI, "..", "dbt", "seeds", "ref_macrosector.csv");

// ---------- Color: OKLCH → sRGB (Björn Ottosson), contraste WCAG ----------
const aLineal = (c) => (c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4);
const aSrgb = (c) => (c <= 0.0031308 ? 12.92 * c : 1.055 * c ** (1 / 2.4) - 0.055);
const rad = (h) => (h * Math.PI) / 180;

export function oklchALineal({ l, c, h }) {
  const a = c * Math.cos(rad(h));
  const b = c * Math.sin(rad(h));
  const l_ = (l + 0.3963377774 * a + 0.2158037573 * b) ** 3;
  const m_ = (l - 0.1055613458 * a - 0.0638541728 * b) ** 3;
  const s_ = (l - 0.0894841775 * a - 1.291485548 * b) ** 3;
  return [
    4.0767416621 * l_ - 3.3077115913 * m_ + 0.2309699292 * s_,
    -1.2684380046 * l_ + 2.6097574011 * m_ - 0.3413193965 * s_,
    -0.0041960863 * l_ - 0.7034186147 * m_ + 1.707614701 * s_,
  ];
}

export function linealAOklab([r, g, b]) {
  const l = Math.cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b);
  const m = Math.cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b);
  const s = Math.cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b);
  return [0.2104542553 * l + 0.793617785 * m - 0.0040720468 * s, 1.9779984951 * l - 2.428592205 * m + 0.4505937099 * s, 0.0259040371 * l + 0.7827717662 * m - 0.808675766 * s];
}

const dentro = (rgb) => rgb.every((v) => v >= -1e-9 && v <= 1 + 1e-9);

/** Lleva un color fuera de gamut al borde de sRGB bajando solo la saturación (mismo L y h). */
export function dentroDeGamut({ l, c, h }) {
  if (dentro(oklchALineal({ l, c, h }))) return { l, c, h };
  let bajo = 0;
  let alto = c;
  for (let i = 0; i < 40; i++) {
    const medio = (bajo + alto) / 2;
    if (dentro(oklchALineal({ l, c: medio, h }))) bajo = medio;
    else alto = medio;
  }
  return { l, c: bajo, h };
}

const hexDe = (lineal) => "#" + lineal.map((v) => Math.round(Math.min(1, Math.max(0, aSrgb(Math.min(1, Math.max(0, v))))) * 255).toString(16).padStart(2, "0")).join("");
const linealDeHex = (hex) => [1, 3, 5].map((i) => aLineal(parseInt(hex.slice(i, i + 2), 16) / 255));
const luminancia = (hex) => {
  const [r, g, b] = linealDeHex(hex);
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
};
export function contraste(hexA, hexB) {
  const [a, b] = [luminancia(hexA), luminancia(hexB)].sort((x, y) => y - x);
  return (a + 0.05) / (b + 0.05);
}
export const distanciaOklab = (hexA, hexB) => {
  const [a, b] = [hexA, hexB].map((h) => linealAOklab(linealDeHex(h)));
  return Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
};

export function colorOscuro(oklch) {
  const ok = dentroDeGamut(oklch);
  const hex = hexDe(oklchALineal(ok));
  return { hex, rgb: [1, 3, 5].map((i) => +(parseInt(hex.slice(i, i + 2), 16) / 255).toFixed(4)), oklch: { l: ok.l, c: +ok.c.toFixed(4), h: ok.h } };
}

/** Variante para papel: mismo tono y saturación; baja L en pasos de 0.005 hasta el contraste mínimo. */
export function colorClaro(oklch, papel, minimo) {
  for (let l = oklch.l; l >= 0.2; l -= 0.005) {
    const ok = dentroDeGamut({ l, c: oklch.c, h: oklch.h });
    const hex = hexDe(oklchALineal(ok));
    const razon = contraste(hex, papel);
    if (razon >= minimo + 0.02) return { hex, contraste: +razon.toFixed(2), oklch: { l: +l.toFixed(3), c: +ok.c.toFixed(4), h: ok.h } };
  }
  throw new Error(`No hay variante clara con contraste ${minimo} para ${JSON.stringify(oklch)}`);
}

// ---------- Lectura ----------
export function leerMacrosectores() {
  const [, ...filas] = readFileSync(SEMILLA, "utf8").trim().split("\n");
  return filas
    .map((fila) => {
      const m = fila.match(/^([a-z_]+),("([^"]+)"|[^,]+),(\d+)$/);
      if (!m) throw new Error(`Fila de ref_macrosector ilegible: ${fila}`);
      return { clave: m[1], nombre: m[3] ?? m[2], orden: +m[4] };
    })
    .sort((a, b) => a.orden - b.orden);
}

export function construir(tokens = JSON.parse(readFileSync(join(AQUI, "tokens.json"), "utf8"))) {
  const macros = leerMacrosectores();
  const claves = macros.map((m) => m.clave);
  const paletas = {};
  for (const [nombre, paleta] of Object.entries(tokens.paletas)) {
    const dadas = Object.keys(paleta.colores).sort().join();
    if (dadas !== [...claves].sort().join()) throw new Error(`La paleta "${nombre}" no tiene exactamente los macrosectores de ref_macrosector (${claves.join(", ")})`);
    paletas[nombre] = {
      descripcion: paleta.descripcion,
      macrosectores: macros.map((m) => ({
        clave: m.clave,
        nombre: m.nombre,
        oscuro: colorOscuro(paleta.colores[m.clave]),
        claro: colorClaro(paleta.colores[m.clave], tokens.claro.papel, tokens.claro.contraste_minimo),
      })),
    };
  }
  if (!paletas[tokens.paleta_activa]) throw new Error(`paleta_activa "${tokens.paleta_activa}" no existe`);
  return { version: tokens.version, estado: tokens.estado, paletaActiva: tokens.paleta_activa, paletas, oscuro: tokens.oscuro, claro: tokens.claro, luz: tokens.luz, tipografia: tokens.tipografia };
}

// ---------- Salida ----------
const CABECERA = "// Generado por diseno/generar.mjs desde diseno/tokens.json. No se edita a mano.\n";

export function generarJs(t) {
  const activa = t.paletas[t.paletaActiva];
  return `${CABECERA}export const version = ${t.version};
export const estado = ${JSON.stringify(t.estado)};
export const paletaActiva = ${JSON.stringify(t.paletaActiva)};
/** Macrosectores de la paleta activa, en el orden de ref_macrosector (el índice + 1 es el macrosector del paquete de puntos). */
export const macrosectores = ${JSON.stringify(activa.macrosectores, null, 2)};
/** Todas las paletas candidatas, con la misma forma. */
export const paletas = ${JSON.stringify(t.paletas, null, 2)};
export const oscuro = ${JSON.stringify(t.oscuro, null, 2)};
export const claro = ${JSON.stringify(t.claro, null, 2)};
export const luz = ${JSON.stringify(t.luz, null, 2)};
export const tipografia = ${JSON.stringify(t.tipografia, null, 2)};
`;
}

export function generarCss(t) {
  const activa = t.paletas[t.paletaActiva].macrosectores;
  const tipos = t.tipografia;
  const oscuro = [
    ...activa.map((m) => `  --macro-${m.clave.replaceAll("_", "-")}: ${m.oscuro.hex};`),
    `  --fondo: ${t.oscuro.fondo};`,
    `  --alcaldia-relleno: ${t.oscuro.alcaldia_relleno};`,
    `  --alcaldia-trazo: ${t.oscuro.alcaldia_trazo};`,
    `  --texto: ${t.oscuro.texto};`,
    `  --texto-tenue: ${t.oscuro.texto_tenue};`,
  ];
  const claro = [
    ...activa.map((m) => `  --macro-${m.clave.replaceAll("_", "-")}: ${m.claro.hex};`),
    `  --fondo: ${t.claro.papel};`,
    `  --texto: ${t.claro.texto};`,
    `  --texto-tenue: ${t.claro.texto_tenue};`,
    `  --trazo: ${t.claro.trazo};`,
  ];
  const fuente = [
    `  --fuente: ${tipos.pila};`,
    ...Object.entries(tipos.pesos).map(([k, v]) => `  --peso-${k}: ${v};`),
    ...Object.entries(tipos.escala_px).map(([k, v]) => `  --tam-${k.replaceAll("_", "-")}: ${v}px;`),
  ];
  return `/* Generado por diseno/generar.mjs desde diseno/tokens.json. No se edita a mano. */
:root,
[data-tema="oscuro"] {
${oscuro.join("\n")}
${fuente.join("\n")}
  color-scheme: dark;
}

[data-tema="claro"] {
${claro.join("\n")}
  color-scheme: light;
}

.cifra { font-variant-numeric: ${tipos.cifras}; }
`;
}

export function archivos() {
  const t = construir();
  return { "tokens.js": generarJs(t), "tokens.css": generarCss(t) };
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const salida = join(AQUI, "generado");
  mkdirSync(salida, { recursive: true });
  for (const [nombre, contenido] of Object.entries(archivos())) writeFileSync(join(salida, nombre), contenido);
  console.log("escrito diseno/generado/tokens.js y tokens.css");
}

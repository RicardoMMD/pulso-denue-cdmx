import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { archivos, construir, contraste, distanciaOklab, leerMacrosectores } from "../generar.mjs";

const AQUI = dirname(fileURLToPath(import.meta.url));
const tokens = construir();
const activa = tokens.paletas[tokens.paletaActiva].macrosectores;

test("lo generado está al día con tokens.json (si falla: node diseno/generar.mjs)", () => {
  for (const [nombre, esperado] of Object.entries(archivos())) {
    const enDisco = readFileSync(join(AQUI, "..", "generado", nombre), "utf8");
    assert.equal(enDisco, esperado, `diseno/generado/${nombre} está desactualizado`);
  }
});

test("cada paleta cubre exactamente los macrosectores de ref_macrosector, en su orden", () => {
  const esperados = leerMacrosectores().map((m) => m.clave);
  assert.equal(esperados.length, 7);
  for (const [nombre, paleta] of Object.entries(tokens.paletas)) {
    assert.deepEqual(paleta.macrosectores.map((m) => m.clave), esperados, nombre);
  }
});

test("los colores son hexadecimales válidos y no se repiten dentro de una paleta", () => {
  for (const [nombre, paleta] of Object.entries(tokens.paletas)) {
    for (const variante of ["oscuro", "claro"]) {
      const hexes = paleta.macrosectores.map((m) => m[variante].hex);
      assert.ok(hexes.every((h) => /^#[0-9a-f]{6}$/.test(h)), `${nombre} ${variante}`);
      assert.equal(new Set(hexes).size, hexes.length, `${nombre} ${variante} repite un color`);
    }
  }
});

test("la variante clara cumple el contraste mínimo contra el papel (todas las paletas)", () => {
  for (const [nombre, paleta] of Object.entries(tokens.paletas)) {
    for (const m of paleta.macrosectores) {
      const razon = contraste(m.claro.hex, tokens.claro.papel);
      assert.ok(razon >= tokens.claro.contraste_minimo, `${nombre}/${m.clave}: ${razon.toFixed(2)} < ${tokens.claro.contraste_minimo}`);
    }
  }
});

test("el texto cumple 4.5:1 sobre su fondo, en los dos temas", () => {
  assert.ok(contraste(tokens.oscuro.texto, tokens.oscuro.fondo) >= 4.5);
  assert.ok(contraste(tokens.claro.texto, tokens.claro.papel) >= 4.5);
  assert.ok(contraste(tokens.oscuro.texto_tenue, tokens.oscuro.fondo) >= 3);
  assert.ok(contraste(tokens.claro.texto_tenue, tokens.claro.papel) >= 4.5);
});

test("en la paleta activa, dos macrosectores nunca se parecen demasiado (a simple vista)", () => {
  for (let i = 0; i < activa.length; i++) {
    for (let j = i + 1; j < activa.length; j++) {
      const d = distanciaOklab(activa[i].oscuro.hex, activa[j].oscuro.hex);
      assert.ok(d >= 0.09, `${activa[i].clave} y ${activa[j].clave} están a ${d.toFixed(3)} (mínimo 0.09)`);
    }
  }
});

test("Comercio es el tono más sobrio: el menos luminoso y el menos saturado (todas las paletas)", () => {
  for (const [nombre, paleta] of Object.entries(tokens.paletas)) {
    const [comercio, ...otros] = paleta.macrosectores;
    assert.equal(comercio.clave, "comercio");
    for (const m of otros) {
      assert.ok(comercio.oscuro.oklch.l < m.oscuro.oklch.l, `${nombre}: ${m.clave} es menos luminoso que comercio`);
      assert.ok(comercio.oscuro.oklch.c < m.oscuro.oklch.c, `${nombre}: ${m.clave} es menos saturado que comercio`);
    }
  }
});

test("los colores oscuros no son tan claros que el brillo aditivo los vuelva blancos a la primera suma", () => {
  for (const m of activa) assert.ok(m.oscuro.oklch.l <= 0.92, `${m.clave} L=${m.oscuro.oklch.l}`);
});

test("el CSS define los siete macrosectores en los dos temas", () => {
  const css = archivos()["tokens.css"];
  for (const m of activa) {
    const variable = `--macro-${m.clave.replaceAll("_", "-")}:`;
    assert.equal(css.split(variable).length - 1, 2, `${variable} debe aparecer en oscuro y en claro`);
  }
});

test("la tipografía se sirve desde el propio sitio: los archivos existen y el CSS declara la fuente", () => {
  for (const [uso, ruta] of Object.entries(tokens.tipografia.archivos)) {
    const bytes = readFileSync(join(AQUI, "..", ruta));
    assert.ok(bytes.length > 10_000, `${uso}: ${ruta} es demasiado chico para ser una fuente`);
  }
  const licencia = readFileSync(join(AQUI, "..", "fuentes", "LICENCIA-Inter-OFL.txt"), "utf8");
  assert.match(licencia, /SIL Open Font License/);
  const css = archivos()["tokens.css"];
  assert.match(css, /@font-face/);
  assert.ok(css.includes(`url('../${tokens.tipografia.archivos.variable}')`));
});

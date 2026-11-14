// Mismo banco que pytest (contracts/casos/): Python y TS deben dar el mismo veredicto en los niveles 1 y 2 (R7)
// y exactamente los mismos bytes canónicos (R9). Los casos de nivel 3 (coherencia) los valida el backend; aquí
// deben pasar como válidos, porque Ajv no los ve.
import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import { canonico, canonicoTexto } from "../canonico.ts";
import { crearReferencias } from "../referencias.ts";
import { validar } from "../validar.ts";

const raiz = new URL("../../contracts/", import.meta.url);
const leer = (ruta: URL) => JSON.parse(fs.readFileSync(ruta, "utf8"));
const casos = (carpeta: string) =>
  fs.readdirSync(new URL(`casos/${carpeta}/`, raiz)).filter((f) => f.endsWith(".json")).sort()
    .map((f) => ({ nombre: f.replace(/\.json$/, ""), caso: leer(new URL(`casos/${carpeta}/${f}`, raiz)) }));
const refs = crearReferencias(leer(new URL("referencias/2026-05.json", raiz)));

for (const { nombre, caso } of casos("veredicto")) {
  test(`veredicto ${nombre}`, () => {
    const errores = validar(caso.estado, refs);
    const resumen = JSON.stringify(errores.map((e) => [e.nivel, e.codigo, e.ruta]));
    if (caso.valido || caso.nivel === 3) {
      assert.deepEqual(errores, [], `se esperaba válido en niveles 1 y 2: ${resumen}`);
    } else {
      assert.ok(errores.length > 0, "se esperaba inválido");
      assert.equal(Math.min(...errores.map((e) => e.nivel)), caso.nivel, resumen);
      assert.ok(errores.some((e) => e.codigo === caso.codigo), `falta el código ${caso.codigo}: ${resumen}`);
    }
  });
}

for (const { nombre, caso } of casos("canonico")) {
  test(`canónico ${nombre}`, () => {
    assert.equal(canonicoTexto(caso.estado), caso.texto);
    assert.equal(Buffer.from(canonico(caso.estado)).toString("hex"), caso.hex);
  });
}

test("el banco no está vacío", () => {
  assert.ok(casos("veredicto").length >= 40 && casos("canonico").length >= 10);
});

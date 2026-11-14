// Genera escena.v1.d.ts y validar-estructura.js (Ajv standalone) desde ../contracts/escena.v1.json.
// No se editan a mano; lo invoca `python -m contracts.generar`.
import fs from "node:fs";
import Ajv2020 from "ajv/dist/2020.js";
import standaloneCode from "ajv/dist/standalone/index.js";
import { compile } from "json-schema-to-typescript";

const esquema = JSON.parse(fs.readFileSync(new URL("../contracts/escena.v1.json", import.meta.url), "utf8"));

const ajv = new Ajv2020({ code: { source: true, esm: true }, allErrors: true, strict: true, discriminator: true });
const validar = ajv.compile(esquema);
// El código standalone usa require() para ucs2length (cuenta puntos de código en maxLength); en un módulo ESM no
// existe, así que se cambia por un import. Si Ajv cambia esa forma, el generador falla en vez de producir basura.
const REQUIRE = 'require("ajv/dist/runtime/ucs2length")';
let codigo = standaloneCode(ajv, validar);
if (codigo.split(REQUIRE).length !== 2) throw new Error("El validador generado ya no usa require(ucs2length) como se esperaba");
codigo = '"use strict";import ucs2lengthModulo from "ajv/dist/runtime/ucs2length.js";' +
  codigo.replace(/^"use strict";/, "").replace(REQUIRE, "ucs2lengthModulo");
fs.writeFileSync(new URL("./validar-estructura.js", import.meta.url), codigo);

const tipos = await compile(esquema, "Estado", {
  bannerComment: "/* GENERADO por contracts/generar.py desde escena.v1.json. No editar a mano. */",
  additionalProperties: false,
  format: true,
  ignoreMinAndMaxItems: true,
});
fs.writeFileSync(new URL("./escena.v1.d.ts", import.meta.url), tipos);
console.log("escrito contracts-ts/escena.v1.d.ts y validar-estructura.js");

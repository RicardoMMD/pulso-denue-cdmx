// Lee estados en JSON (uno por línea) de la entrada estándar y escribe su forma canónica en hexadecimal, uno por
// línea. Lo usa la prueba de paridad de pytest (tests/contracts/test_paridad_ts.py).
import fs from "node:fs";
import { canonico } from "./canonico.ts";

for (const linea of fs.readFileSync(0, "utf8").split("\n")) {
  if (linea.trim()) console.log(Buffer.from(canonico(JSON.parse(linea))).toString("hex"));
}

// Forma canónica del estado: espejo exacto de contracts/canonico.py. Base del id por contenido y de la URL #s=.
// Claves ordenadas, sin campos que valgan su predeterminado, sin espacios y con textos en NFC.
// Los predeterminados se leen del propio esquema generado (escena.v1.json): no hay una segunda lista.
import esquema from "../contracts/escena.v1.json" with { type: "json" };

type Json = null | boolean | number | string | Json[] | { [clave: string]: Json };
type Esquema = { [clave: string]: any };

function resolver(nodo: Esquema, valor: Json): Esquema {
  let actual = nodo;
  for (let vuelta = 0; vuelta < 8; vuelta++) {
    if (actual.$ref) {
      const destino = (esquema as Esquema).$defs[actual.$ref.replace("#/$defs/", "")];
      // `default`, `title`... pueden acompañar al $ref; el destino aporta propiedades y estructura.
      actual = { ...destino, ...Object.fromEntries(Object.entries(actual).filter(([k]) => k !== "$ref")) };
    } else if (actual.oneOf || actual.anyOf) {
      const opciones: Esquema[] = (actual.oneOf ?? actual.anyOf).filter((o: Esquema) => o.type !== "null");
      let elegida = opciones[0];
      if (valor !== null && typeof valor === "object" && !Array.isArray(valor)) {
        const etiqueta = actual.discriminator?.propertyName;
        elegida = opciones.find((o) => {
          const r = o.$ref ? (esquema as Esquema).$defs[o.$ref.replace("#/$defs/", "")] : o;
          if (etiqueta) return r.properties?.[etiqueta]?.const === (valor as { [k: string]: Json })[etiqueta];
          const claves = Object.keys(valor as object);
          return claves.every((k) => k in (r.properties ?? {})) && (r.required ?? []).every((k: string) => claves.includes(k));
        }) ?? opciones[0];
      }
      const { oneOf, anyOf, discriminator, ...resto } = actual;
      actual = { ...elegida, ...resto };
    } else {
      return actual;
    }
  }
  return actual;
}

function iguales(a: Json, b: Json): boolean {
  if (a === b) return true;
  if (Array.isArray(a) && Array.isArray(b)) return a.length === b.length && a.every((x, i) => iguales(x, b[i]));
  if (a && b && typeof a === "object" && typeof b === "object" && !Array.isArray(a) && !Array.isArray(b)) {
    const ka = Object.keys(a), kb = Object.keys(b);
    return ka.length === kb.length && ka.every((k) => k in b && iguales(a[k], b[k]));
  }
  return false;
}

function podar(valor: Json, nodo: Esquema): Json {
  const esq = resolver(nodo, valor);
  if (typeof valor === "string") return valor.normalize("NFC");
  if (Array.isArray(valor)) return valor.map((v) => podar(v, esq.items ?? {}));
  if (valor && typeof valor === "object") {
    const salida: { [clave: string]: Json } = {};
    for (const clave of Object.keys(valor).sort()) {
      const sub = esq.properties?.[clave] ?? {};
      const v = podar(valor[clave], sub);
      if (v === null) continue;
      const porOmision = resolver(sub, valor[clave]).default;
      if (porOmision !== undefined && iguales(v, podar(porOmision, sub))) continue;
      salida[clave] = v;
    }
    return salida;
  }
  return valor;
}

export function canonicoObjeto(estado: Json): Json {
  return podar(estado, esquema as Esquema);
}

export function canonico(estado: Json): Uint8Array {
  return new TextEncoder().encode(JSON.stringify(canonicoObjeto(estado)));
}

export function canonicoTexto(estado: Json): string {
  return JSON.stringify(canonicoObjeto(estado));
}

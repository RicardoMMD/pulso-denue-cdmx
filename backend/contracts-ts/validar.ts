// Niveles 1 y 2 en el navegador: Ajv precompilado (estructura) más las referencias de la edición.
// El nivel 3 (coherencia) lo valida el backend; el explorador solo ofrece combinaciones válidas.
import validarEstructura from "./validar-estructura.js";
import type { Referencias } from "./referencias.ts";

export interface ErrorValidacion {
  nivel: 1 | 2;
  ruta: string;
  codigo: string;
  mensaje: string;
}

type ErrorAjv = { instancePath: string; keyword: string; message?: string; params: Record<string, any> };

const CAMPOS_TEXTO = new Set(["titulo", "texto", "nota_cautela"]);

function traducir(e: ErrorAjv): ErrorValidacion {
  let ruta = e.instancePath;
  let codigo = "estructura_invalida";
  let razon = e.message ?? "no es válido";
  switch (e.keyword) {
    case "required": ruta += `/${e.params.missingProperty}`; codigo = "campo_faltante"; razon = "falta el campo obligatorio"; break;
    case "additionalProperties": ruta += `/${e.params.additionalProperty}`; codigo = "campo_no_admitido"; razon = "el campo no está permitido aquí"; break;
    case "enum": case "const": case "discriminator": codigo = "valor_no_admitido"; razon = "valor no admitido"; break;
    case "pattern":
      if (CAMPOS_TEXTO.has(ruta.split("/").pop() ?? "")) { codigo = "texto_con_cifras"; razon = "el texto no admite dígitos ni llaves fuera de los huecos {nombre}; las cifras se vinculan"; }
      else { codigo = "formato_incorrecto"; razon = "no cumple el formato esperado"; }
      break;
    case "maxLength": case "maxItems": codigo = "demasiado_largo"; razon = "excede el máximo permitido"; break;
    case "minLength": case "minItems": codigo = "demasiado_corto"; razon = "es más corto que el mínimo permitido"; break;
    case "type": codigo = "tipo_incorrecto"; razon = "el tipo de dato no es el esperado"; break;
  }
  const campo = ruta.split("/").pop() || "el estado";
  return { nivel: 1, ruta, codigo, mensaje: `${campo}: ${razon}` };
}

export function validarEstructuraEstado(estado: unknown): ErrorValidacion[] {
  if (validarEstructura(estado)) return [];
  const vistos = new Set<string>();
  const errores: ErrorValidacion[] = [];
  for (const e of (validarEstructura.errors ?? []) as ErrorAjv[]) {
    const t = traducir(e);
    const id = `${t.ruta}|${t.codigo}`;
    if (!vistos.has(id)) { vistos.add(id); errores.push(t); }
  }
  return errores.sort((a, b) => (a.ruta + a.codigo).localeCompare(b.ruta + b.codigo));
}

export function validarReferencias(estado: any, ref: Referencias): ErrorValidacion[] {
  const errores: ErrorValidacion[] = [];
  const e2 = (ruta: string, codigo: string, mensaje: string) => errores.push({ nivel: 2, ruta, codigo, mensaje });
  if (estado.edicion !== ref.edicion) e2("/edicion", "edicion_no_disponible", `edicion: la edición ${estado.edicion} no está en las referencias (solo ${ref.edicion})`);
  const territorio = (t: any, ruta: string) => {
    if (!ref.existe(t.tipo, t.clave)) e2(`${ruta}/clave`, "referencia_inexistente", `clave: ${t.tipo} '${t.clave}' no existe en la edición ${ref.edicion}`);
  };
  const seleccion = (s: any, ruta: string) => {
    (s?.scian ?? []).forEach((c: string, i: number) => {
      if (!ref.scianValido(c)) e2(`${ruta}/scian/${i}`, "scian_inexistente", `scian: el código ${c} no existe en ${ref.versionScian}`);
    });
  };
  territorio(estado.territorio, "/territorio");
  seleccion(estado.seleccion, "/seleccion");
  if (estado.comparacion?.territorio) territorio(estado.comparacion.territorio, "/comparacion/territorio");
  if (estado.comparacion?.seleccion) seleccion(estado.comparacion.seleccion, "/comparacion/seleccion");
  if (estado.escena?.tipo === "ciudades_dentro") {
    (estado.escena.tipo_conglomerado ?? []).forEach((t: string, i: number) => {
      if (!ref.tipoConglomeradoValido(t)) e2(`/escena/tipo_conglomerado/${i}`, "tipo_conglomerado_inexistente", `tipo_conglomerado: '${t}' no es un tipo de conglomerado de la edición ${ref.edicion}`);
    });
  }
  return errores;
}

/** Niveles 1 y 2. Si la estructura falla no se revisan las referencias (igual que en Python). */
export function validar(estado: unknown, ref: Referencias): ErrorValidacion[] {
  const n1 = validarEstructuraEstado(estado);
  return n1.length ? n1 : validarReferencias(estado, ref);
}

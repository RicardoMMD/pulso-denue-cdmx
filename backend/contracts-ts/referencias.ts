// Archivo de referencias (nivel 2): espejo de contracts/referencias.py. Sin base de datos.
export interface DatosReferencias {
  edicion: string;
  fecha_corte: string;
  version_scian: string;
  lugares: Record<string, Record<string, string>>;
  lineas: Record<string, { nombre: string; estaciones: string[] }>;
  scian: string[];
  tipos_conglomerado: string[];
}

export interface Referencias {
  edicion: string;
  fechaCorte: string;
  versionScian: string;
  existe(tipo: string, clave: string): boolean;
  nombre(tipo: string, clave: string): string | undefined;
  lineaPasaPor(cveLinea: string, estacion: string): boolean;
  scianValido(codigo: string): boolean;
  tipoConglomeradoValido(tipo: string): boolean;
}

export function crearReferencias(d: DatosReferencias): Referencias {
  const scian = new Set(d.scian);
  const tipos = new Set(d.tipos_conglomerado);
  return {
    edicion: d.edicion,
    fechaCorte: d.fecha_corte,
    versionScian: d.version_scian,
    existe: (tipo, clave) => (tipo === "linea_metro" ? Object.hasOwn(d.lineas, clave) : Object.hasOwn(d.lugares[tipo] ?? {}, clave)),
    nombre: (tipo, clave) => (tipo === "linea_metro" ? d.lineas[clave]?.nombre : d.lugares[tipo]?.[clave]),
    lineaPasaPor: (cve, estacion) => d.lineas[cve]?.estaciones.includes(estacion) ?? false,
    scianValido: (codigo) => scian.has(codigo),
    tipoConglomeradoValido: (tipo) => tipos.has(tipo),
  };
}

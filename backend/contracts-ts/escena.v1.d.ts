/* GENERADO por contracts/generar.py desde escena.v1.json. No editar a mano. */

/**
 * @maxItems 4
 */
export type Capas = ("alcaldias" | "lineas_metro" | "calles_principales" | "etiquetas")[];
export type Comparacion = ComparacionTerritorio | ComparacionSeleccion | null;
export type FormaComparacionTerritorio = "lado_a_lado" | "transformacion";
export type ClaveTerritorio = string;
export type RadioTerritorio = (300 | 500 | 800) | null;
export type TipoTerritorio =
  "ciudad" | "alcaldia" | "colonia" | "estacion_metro" | "linea_metro" | "conglomerado" | "calle";
export type FormaComparacionSeleccion = "lado_a_lado" | "transformacion";
export type Estratos = (1 | 2 | 3 | 4 | 5 | 6 | 7)[] | null;
export type PresenciaDigital = boolean | null;
export type CodigosScian = string[] | null;
export type TipoUnidad = ("fijo" | "semifijo") | null;
export type Contrato = 1;
export type Edicion = string;
export type Encuadre = EncuadreAjustar | EncuadreAngulo | EncuadreRecorrido;
export type ModoEncuadreAjustar = "ajustar";
export type AnguloEncuadre = "cenital" | "oblicua" | "rasante";
export type ModoEncuadreAngulo = "angulo";
export type ModoEncuadreRecorrido = "recorrido";
export type RecorridoEncuadre = "el_despertar" | "tren_de_luz" | "constelacion_estaciones" | "entrar_al_mercado";
export type Escena = CiudadDeLuz | CorredoresMetro | CiudadesDentro;
export type ModoCiudadDeLuz = "unico";
export type TipoEscenaCiudadDeLuz = "ciudad_de_luz";
export type ModoCorredoresMetro = "linea" | "ranking";
export type RadioCorredoresMetro = 300 | 500 | 800;
export type TipoEscenaCorredoresMetro = "corredores_metro";
export type ModoCiudadesDentro = "exterior" | "interior";
export type TamanoCiudadesDentro = "establecimientos" | "establecimientos_seleccion" | "locales_declarados";
export type TipoEscenaCiudadesDentro = "ciudades_dentro";
export type TiposConglomerado = string[] | null;
export type NotaCautela = string;
export type FilaCifra = ("primera" | "ultima" | "total") | FilaClave;
export type Clave = string;
export type FormatoCifra = "entero" | "porcentaje" | "decimal1" | "texto";
export type MedidaCifra =
  | "establecimientos"
  | "establecimientos_seleccion"
  | "locales_declarados"
  | "estaciones"
  | "estacion"
  | "giro_dominante"
  | "lugar"
  | "macrosector"
  | "participacion"
  | "nombre"
  | "tipo";
export type FilaCifra1 = ("primera" | "ultima" | "total") | FilaClave;
export type FormatoCifra1 = "entero" | "porcentaje" | "decimal1" | "texto";
export type MedidaCifra1 =
  | "establecimientos"
  | "establecimientos_seleccion"
  | "locales_declarados"
  | "estaciones"
  | "estacion"
  | "giro_dominante"
  | "lugar"
  | "macrosector"
  | "participacion"
  | "nombre"
  | "tipo";
export type Nombre = string;
/**
 * @maxItems 3
 */
export type Secundarias = CifraSecundaria[];
export type Texto = string;
export type Titulo = string;

/**
 * Lo que se ve. Entra al id por contenido. Origen y panel anterior van aparte, en `Metadatos`.
 */
export interface Estado {
  capas?: Capas;
  comparacion?: Comparacion;
  contrato: Contrato;
  edicion: Edicion;
  encuadre?: Encuadre;
  escena: Escena;
  narrativa: Narrativa;
  seleccion?: Seleccion1;
  territorio: Territorio;
}
export interface ComparacionTerritorio {
  forma: FormaComparacionTerritorio;
  territorio: Territorio;
}
export interface Territorio {
  clave: ClaveTerritorio;
  radio_m?: RadioTerritorio;
  tipo: TipoTerritorio;
}
export interface ComparacionSeleccion {
  forma: FormaComparacionSeleccion;
  seleccion: Seleccion;
}
/**
 * Filtrar atenúa, nunca elimina puntos. Solo giro SCIAN (de sector a clase) en v1.
 */
export interface Seleccion {
  estrato?: Estratos;
  presencia_digital?: PresenciaDigital;
  scian?: CodigosScian;
  tipo_unidad?: TipoUnidad;
}
export interface EncuadreAjustar {
  modo: ModoEncuadreAjustar;
}
export interface EncuadreAngulo {
  angulo: AnguloEncuadre;
  modo: ModoEncuadreAngulo;
}
export interface EncuadreRecorrido {
  modo: ModoEncuadreRecorrido;
  recorrido: RecorridoEncuadre;
}
export interface CiudadDeLuz {
  modo?: ModoCiudadDeLuz;
  tipo: TipoEscenaCiudadDeLuz;
}
export interface CorredoresMetro {
  modo?: ModoCorredoresMetro;
  radio_m?: RadioCorredoresMetro;
  tipo: TipoEscenaCorredoresMetro;
}
export interface CiudadesDentro {
  modo?: ModoCiudadesDentro;
  tamano?: TamanoCiudadesDentro;
  tipo: TipoEscenaCiudadesDentro;
  tipo_conglomerado?: TiposConglomerado;
}
export interface Narrativa {
  nota_cautela: NotaCautela;
  principal?: Cifra | null;
  secundarias?: Secundarias;
  texto: Texto;
  titulo: Titulo;
}
/**
 * Una cifra se nombra, no se escribe: `medida` y `fila` apuntan a la vista exacta del estado.
 */
export interface Cifra {
  fila?: FilaCifra;
  formato?: FormatoCifra;
  medida: MedidaCifra;
}
export interface FilaClave {
  clave: Clave;
}
export interface CifraSecundaria {
  fila?: FilaCifra1;
  formato?: FormatoCifra1;
  medida: MedidaCifra1;
  nombre: Nombre;
}
/**
 * Filtrar atenúa, nunca elimina puntos. Solo giro SCIAN (de sector a clase) en v1.
 */
export interface Seleccion1 {
  estrato?: Estratos;
  presencia_digital?: PresenciaDigital;
  scian?: CodigosScian;
  tipo_unidad?: TipoUnidad;
}

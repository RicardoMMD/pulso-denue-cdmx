"""Contrato de escena v1: el estado de un panel (R1–R4).

Fuente única. `escena.v1.json`, los tipos TypeScript y el validador Ajv se generan de estos modelos
(ver generar.py); no se editan a mano.

Principios (síntesis, "Contrato del estado de escena"): declarativo, referencias en vez de datos, cerrado,
parcial y heredable, determinista y cifras vinculadas. Aquí no cabe una cifra, un color, una escala, una
coordenada ni una duración: no hay campo donde escribirlos, y los textos libres no admiten dígitos fuera de
los huecos `{nombre}`.
"""
from __future__ import annotations

from typing import Annotated, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from . import catalogo as cat

# Texto sin dígitos ni llaves sueltas: solo huecos `{nombre}`. Se usa también en el JSON Schema, así que Python y
# Ajv aplican exactamente la misma regla.
PATRON_TEXTO = r"^[^0-9{}]*(\{[a-z_]+\}[^0-9{}]*)*$"
PATRON_NOMBRE_HUECO = r"^[a-z_]+$"
PATRON_EDICION = r"^[0-9]{4}-[0-9]{2}$"
PATRON_SCIAN = r"^[0-9]{2,6}$"


class Modelo(BaseModel):
    """Base cerrada y estricta: lo que no está declarado se rechaza y no se convierten tipos."""

    model_config = ConfigDict(extra="forbid", strict=True)


# --- Territorio y encuadre ---------------------------------------------------------------------------------

class Territorio(Modelo):
    tipo: Literal["ciudad", "alcaldia", "colonia", "estacion_metro", "linea_metro", "conglomerado", "calle"] = Field(
        title="TipoTerritorio")
    clave: str = Field(min_length=1, max_length=200, title="ClaveTerritorio")
    radio_m: Optional[Literal[300, 500, 800]] = Field(default=None, title="RadioTerritorio")


class EncuadreAjustar(Modelo):
    modo: Literal["ajustar"] = Field(title="ModoEncuadreAjustar")


class EncuadreAngulo(Modelo):
    modo: Literal["angulo"] = Field(title="ModoEncuadreAngulo")
    angulo: Literal["cenital", "oblicua", "rasante"] = Field(title="AnguloEncuadre")


class EncuadreRecorrido(Modelo):
    modo: Literal["recorrido"] = Field(title="ModoEncuadreRecorrido")
    recorrido: Literal["el_despertar", "tren_de_luz", "constelacion_estaciones", "entrar_al_mercado"] = Field(
        title="RecorridoEncuadre")


Encuadre = Annotated[Union[EncuadreAjustar, EncuadreAngulo, EncuadreRecorrido], Field(discriminator="modo")]


# --- Escenas de la primera versión -------------------------------------------------------------------------

class CiudadDeLuz(Modelo):
    tipo: Literal["ciudad_de_luz"] = Field(title="TipoEscenaCiudadDeLuz")
    modo: Literal["unico"] = Field(default="unico", title="ModoCiudadDeLuz")


class CorredoresMetro(Modelo):
    tipo: Literal["corredores_metro"] = Field(title="TipoEscenaCorredoresMetro")
    modo: Literal["linea", "ranking"] = Field(default="linea", title="ModoCorredoresMetro")
    radio_m: Literal[300, 500, 800] = Field(default=500, title="RadioCorredoresMetro")


class CiudadesDentro(Modelo):
    tipo: Literal["ciudades_dentro"] = Field(title="TipoEscenaCiudadesDentro")
    modo: Literal["exterior", "interior"] = Field(default="exterior", title="ModoCiudadesDentro")
    tamano: Literal["establecimientos", "establecimientos_seleccion", "locales_declarados"] = Field(
        default="establecimientos", title="TamanoCiudadesDentro")
    # None = todos los tipos. Los valores válidos son los del catálogo de referencias de la edición (nivel 2).
    tipo_conglomerado: Optional[Annotated[list[Annotated[str, Field(min_length=1, max_length=80)]],
                                          Field(min_length=1, max_length=18)]] = Field(
        default=None, title="TiposConglomerado")


Escena = Annotated[Union[CiudadDeLuz, CorredoresMetro, CiudadesDentro], Field(discriminator="tipo")]


# --- Selección, capas y comparación ------------------------------------------------------------------------

class Seleccion(Modelo):
    """Filtrar atenúa, nunca elimina puntos. Solo giro SCIAN (de sector a clase) en v1."""

    scian: Optional[Annotated[list[Annotated[str, Field(pattern=PATRON_SCIAN)]],
                              Field(min_length=1, max_length=20)]] = Field(default=None, title="CodigosScian")
    estrato: Optional[Annotated[list[Literal[1, 2, 3, 4, 5, 6, 7]], Field(min_length=1, max_length=7)]] = Field(
        default=None, title="Estratos")
    tipo_unidad: Optional[Literal["fijo", "semifijo"]] = Field(default=None, title="TipoUnidad")
    presencia_digital: Optional[bool] = Field(default=None, title="PresenciaDigital")

    def vacia(self) -> bool:
        return all(v is None for v in self.model_dump().values())


Capa = Literal["alcaldias", "lineas_metro", "calles_principales", "etiquetas"]


class ComparacionTerritorio(Modelo):
    forma: Literal["lado_a_lado", "transformacion"] = Field(title="FormaComparacionTerritorio")
    territorio: Territorio


class ComparacionSeleccion(Modelo):
    forma: Literal["lado_a_lado", "transformacion"] = Field(title="FormaComparacionSeleccion")
    seleccion: Seleccion


Comparacion = Union[ComparacionTerritorio, ComparacionSeleccion]


# --- Narrativa y cifras vinculadas -------------------------------------------------------------------------

class FilaClave(Modelo):
    clave: str = Field(min_length=1, max_length=200)


Fila = Union[Literal["primera", "ultima", "total"], FilaClave]
Medida = Literal["establecimientos", "establecimientos_seleccion", "locales_declarados", "estaciones", "estacion",
                 "giro_dominante", "lugar", "macrosector", "participacion", "nombre", "tipo"]


class Cifra(Modelo):
    """Una cifra se nombra, no se escribe: `medida` y `fila` apuntan a la vista exacta del estado."""

    medida: Medida = Field(title="MedidaCifra")
    fila: Fila = Field(default="primera", title="FilaCifra")
    formato: Literal["entero", "porcentaje", "decimal1", "texto"] = Field(default="entero", title="FormatoCifra")


class CifraSecundaria(Cifra):
    nombre: str = Field(pattern=PATRON_NOMBRE_HUECO, max_length=40)


class Narrativa(Modelo):
    titulo: str = Field(min_length=1, max_length=80, pattern=PATRON_TEXTO)
    texto: str = Field(min_length=1, max_length=400, pattern=PATRON_TEXTO)
    principal: Optional[Cifra] = None
    secundarias: list[CifraSecundaria] = Field(default=[], max_length=3)
    nota_cautela: str = Field(min_length=1, max_length=240, pattern=PATRON_TEXTO)


# --- Estado ------------------------------------------------------------------------------------------------

class Estado(Modelo):
    """Lo que se ve. Entra al id por contenido. Origen y panel anterior van aparte, en `Metadatos`."""

    contrato: Literal[1]
    edicion: str = Field(pattern=PATRON_EDICION)
    territorio: Territorio
    encuadre: Encuadre = Field(default=EncuadreAjustar(modo="ajustar"))
    escena: Escena
    seleccion: Seleccion = Field(default=Seleccion())
    capas: Annotated[list[Capa], Field(max_length=4)] = Field(default=[])
    comparacion: Optional[Comparacion] = None
    narrativa: Narrativa


class Metadatos(Modelo):
    """Quién y de dónde. No entra al id: el mismo panel tiene el mismo id venga de donde venga."""

    origen: Literal["historia", "explorador", "analista"]
    panel_anterior: Optional[str] = None
    conversacion: Optional[str] = None


# --- Estado parcial (R4) -----------------------------------------------------------------------------------
# Todos los campos son opcionales y admiten null (que borra el campo y vuelve al predeterminado). Se escriben a
# mano, bloque por bloque, para que el esquema siga legible. La combinación final se valida como `Estado`.

class TerritorioParcial(Modelo):
    tipo: Optional[Literal["ciudad", "alcaldia", "colonia", "estacion_metro", "linea_metro", "conglomerado",
                           "calle"]] = None
    clave: Optional[str] = Field(default=None, min_length=1, max_length=200)
    radio_m: Optional[Literal[300, 500, 800]] = None


class EncuadreParcial(Modelo):
    modo: Optional[Literal["ajustar", "angulo", "recorrido"]] = None
    angulo: Optional[Literal["cenital", "oblicua", "rasante"]] = None
    recorrido: Optional[Literal["el_despertar", "tren_de_luz", "constelacion_estaciones", "entrar_al_mercado"]] = None


class EscenaParcial(Modelo):
    tipo: Optional[Literal["ciudad_de_luz", "corredores_metro", "ciudades_dentro"]] = None
    modo: Optional[Literal["unico", "linea", "ranking", "exterior", "interior"]] = None
    radio_m: Optional[Literal[300, 500, 800]] = None
    tamano: Optional[Literal["establecimientos", "establecimientos_seleccion", "locales_declarados"]] = None
    tipo_conglomerado: Optional[list[str]] = None


class SeleccionParcial(Modelo):
    scian: Optional[list[str]] = None
    estrato: Optional[list[Literal[1, 2, 3, 4, 5, 6, 7]]] = None
    tipo_unidad: Optional[Literal["fijo", "semifijo"]] = None
    presencia_digital: Optional[bool] = None


class ComparacionParcial(Modelo):
    forma: Optional[Literal["lado_a_lado", "transformacion"]] = None
    territorio: Optional[TerritorioParcial] = None
    seleccion: Optional[SeleccionParcial] = None


class CifraParcial(Modelo):
    medida: Optional[Medida] = None
    fila: Optional[Fila] = None
    formato: Optional[Literal["entero", "porcentaje", "decimal1", "texto"]] = None


class NarrativaParcial(Modelo):
    titulo: Optional[str] = Field(default=None, min_length=1, max_length=80, pattern=PATRON_TEXTO)
    texto: Optional[str] = Field(default=None, min_length=1, max_length=400, pattern=PATRON_TEXTO)
    principal: Optional[CifraParcial] = None
    secundarias: Optional[list[CifraSecundaria]] = Field(default=None, max_length=3)
    nota_cautela: Optional[str] = Field(default=None, min_length=1, max_length=240, pattern=PATRON_TEXTO)


class EstadoParcial(Modelo):
    edicion: Optional[str] = Field(default=None, pattern=PATRON_EDICION)
    territorio: Optional[TerritorioParcial] = None
    encuadre: Optional[EncuadreParcial] = None
    escena: Optional[EscenaParcial] = None
    seleccion: Optional[SeleccionParcial] = None
    capas: Optional[list[Capa]] = Field(default=None, max_length=4)
    comparacion: Optional[ComparacionParcial] = None
    narrativa: Optional[NarrativaParcial] = None


def esquema_estado() -> dict:
    """JSON Schema crudo de Estado (generar.py lo ajusta para Ajv)."""
    return Estado.model_json_schema()


assert cat.VERSION == 1  # el literal de `contrato` y el catálogo cambian juntos

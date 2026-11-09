# Prototipo 3 — Resolver lugar

Herramienta del Analista que convierte formas coloquiales de nombrar un lugar de CDMX en identificadores territoriales:
"la Roma", "cerca del metro Balderas", "a 10 minutos del Zócalo", "GAM", "mercado de Sonora", "Iztapalpa".

Es determinista y no usa modelo de lenguaje: lee solo `semantic.lugar` (la superficie autorizada del Analista) y un
glosario de alias de CDMX. Cuando no puede resolver, lo dice; nunca inventa un lugar.

## Piezas

| Archivo | Qué hace |
| --- | --- |
| `dbt/models/semantic/lugar.sql` | Catálogo único: ciudad, 16 alcaldías, 1 543 colonias, 163 estaciones, 2 885 conglomerados y 9 655 calles (por alcaldía), con punto representativo |
| `resolver_lugar.py` | Interpreta la consulta y la resuelve (`resolver_lugar(conn, texto)`) |
| `glosario.json` | Alias de CDMX que el catálogo oficial no trae (La Roma, Polanco, el Centro, Tepito, CU, Eje Central…) y municipios de fuera |
| `herramienta.py` / definición | Definición para el ciclo de herramientas de la API de Claude y su ejecución |
| `casos_prueba.json`, `casos_ciegos*.json`, `evaluar.py` | Bancos de pruebas y evaluador; escribe `resultados*.md` |

## Cómo resuelve

1. **Normaliza** (mayúsculas, sin acentos ni puntuación) y quita "toda la", "en", "de".
2. **Relación espacial:** "cerca de", "junto a", "alrededor de", "por", "a N metros/km/minutos de". Los minutos se convierten a 80 m por minuto, en línea recta; el radio se limita a 100–3 000 m. Sin cantidad: 500 m para estaciones, 300 m para mercados y calles, 800 m para colonias. A una alcaldía no se le aplica "cerca de".
3. **Pista de tipo:** "metro/estación X" firme; "colonia", "alcaldía/delegación", "calle/avenida/eje…", "mercado/plaza/central" (esta última queda dentro del nombre).
4. **Búsqueda en orden:** glosario → exacto (con y sin artículo) → contención de palabras → parecido (trigramas más comparación del núcleo del nombre sin palabras genéricas).
5. **Prioridad:** si hay coincidencias territoriales (ciudad, alcaldía, colonia), mandan sobre estaciones, mercados y calles homónimos ("Coyoacán" es la alcaldía); una pista como "metro" lo invierte. Una calle que cruza alcaldías es un solo lugar; los polígonos duplicados del catálogo también.
6. **Estados:** `resuelto`, `grupo` (varios que juntos forman el lugar), `ambiguo` (hay que preguntar), `sin_resultado`, `fuera_de_cdmx`. Con `confianza` y `nota` para el usuario.

## Cómo correrlo

```bash
cd pipeline && set -a && . ../.env && set +a            # túnel SSH abierto
export PYTHONPATH=../prototipos/03-resolver-lugar
uv run python ../prototipos/03-resolver-lugar/evaluar.py                                   # banco de ajuste
uv run python ../prototipos/03-resolver-lugar/evaluar.py casos_ciegos.json resultados_ciegos.md
uv run python ../prototipos/03-resolver-lugar/evaluar.py casos_ciegos_2.json resultados_ciegos_2.md
```

## Resultados y límites

Ver "Resultado del prototipo 3" en la síntesis del proyecto. Límites conocidos:

- Las calles se guardan sin el tipo de vía y a veces con la preposición (`DE TLALPAN`); los apodos de vías ("Eje Central", ejes viales) requieren alias.
- Un nombre que existe como calle y como estación (`Insurgentes Sur`, `Balderas`) sale `ambiguo` a propósito.
- Referencias personales ("mi casa", "aquí") se rechazan; no hay geolocalización.
- La lista de municipios de fuera de CDMX es corta y manual.
- Falta el respaldo con modelo de lenguaje (Haiku) para formas que ningún método cubre, y probar con preguntas reales de usuarios.

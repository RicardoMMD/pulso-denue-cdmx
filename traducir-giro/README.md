# Traducir giro — subproyecto

Planteamiento del 15 nov 2026 · Estado: entorno listo, sin modelos descargados ni bancos · Hito que destraba: H10 (`docs/Seguimiento — Hitos del proyecto.md`)

Subproyecto independiente para responder una sola pregunta: **¿un modelo de embeddings local encuentra la clase SCIAN correcta cuando alguien nombra un giro como se habla en la calle?** Cuando el resultado sea favorable, se regresa al proyecto principal y se marca H10.

## La idea

1. **Una vez:** cada clase SCIAN se convierte en un vector y se guarda.
2. **En cada consulta:** el término del usuario ("tiendita", "donde arreglan celulares") se convierte en vector con el mismo modelo.
3. Se devuelven las clases cuyos vectores quedan más cerca.

Se comparan tres modelos, todos locales: **Qwen3-Embedding-0.6B**, **EmbeddingGemma** y **multilingual-e5-small**.

| Nombre aquí | Modelo | Disco | Memoria estimada | Licencia | Acceso |
|---|---|---|---|---|---|
| `qwen3` | Qwen/Qwen3-Embedding-0.6B | 1.2 GB | ~2.4 GB | Apache 2.0 | libre |
| `gemma` | google/embeddinggemma-300m | 1.2 GB | ~1.2 GB | Gemma, con condiciones de uso | aceptar términos y token |
| `e5-small` | intfloat/multilingual-e5-small | 0.5 GB | ~0.5 GB | MIT | libre |

La memoria es una estimación por número de parámetros, sin medir. BGE-M3 salió de la comparación el 15 nov 2026: pesa 2.3 GB y en memoria ocupa lo mismo que Qwen3, que queda como el único modelo grande de referencia. Qwen3 queda por encima del límite de C4 tal como viene; si gana, se prueba comprimido antes de aceptarlo.

## Qué entra y qué no

**Entra**
- Catálogo de clases SCIAN, exportado una vez desde `semantic.actividad` (solo lectura) y guardado en este directorio.
- Bancos de prueba de giros coloquiales con sus clases esperadas.
- Vectorización, búsqueda y evaluación de los tres modelos.
- Una página en el laboratorio visual para ver los resultados.

**No entra, por ahora**
- Escribir en la base. Nada de pgvector hasta que haya un modelo ganador.
- Servicios externos ni llaves. Todo corre en esta máquina.
- El glosario escrito a mano y el paso en que Haiku elige entre candidatos. Están en `docs/changes/2026-11-15-traducir-giro/plan.md` y se retoman después, con el modelo ya elegido.
- El ciclo del Analista (H19).

## Independencia

- Proyecto de Python propio (`uv`), con sus dependencias. Los modelos pesan y no deben entrar al entorno de `pipeline/` ni al de `backend/`.
- Después de exportar el catálogo, no necesita túnel ni base.
- No importa código del resto del repo, y el resto del repo no importa nada de aquí.
- `make ci` del proyecto principal no corre los modelos. Solo podrá revisar que los bancos tengan códigos SCIAN válidos.

## Estructura

```
traducir-giro/
  README.md              este planteamiento; al final, los resultados
  pyproject.toml, uv.lock  dependencias con versión fija (PyTorch sin tarjeta gráfica)
  Makefile               comandos del subproyecto
  comun.py               rutas, registro de modelos (revisión e instrucciones) y texto por clase
  datos/clases.json      catálogo de clases con sus palabras frecuentes (versionado; datos públicos de INEGI)
  bancos/ajuste.json     giros para afinar
  bancos/ciego.json      giros que no se miran hasta el final
  exportar_catalogo.py   lee semantic una vez, solo lectura
  descargar.py           el único script que usa la red; sin --si no baja nada
  vectorizar.py          clases → vectores, por modelo y variante de texto
  buscar.py              término → clases más cercanas
  evaluar.py             corre los bancos y escribe resultados/
  validar_bancos.py      forma de los bancos y clases válidas; lo corre `make check` del repo
  resultados/            tablas por modelo y comparación, y umbrales.json
  modelos/, vectores/    no versionados
```

## Comandos

Se corren desde `traducir-giro/`.

| Comando | Qué hace |
|---|---|
| `make catalogo` | Exporta `datos/clases.json` (solo lectura, necesita túnel) |
| `make validar` | Revisa los bancos contra el catálogo, sin base ni modelos |
| `make modelos` | Lista los modelos y si están descargados |
| `make descargar MODELO=qwen3` | Baja un modelo a `modelos/`. Para `gemma` hace falta `HF_TOKEN` en el `.env` |
| `make ajuste` | Vectores, banco de ajuste y tabla en `resultados/ajuste-simple.md`. Con `VARIANTE=palabras`, el texto enriquecido |
| `make ciego` | Banco ciego. Una sola vez: se niega a repetirse si ya existe `resultados/ciego/` |
| `uv run python buscar.py qwen3 "tiendita"` | Prueba suelta de un término |

Cargar un modelo nunca dispara una descarga: fuera de `descargar.py` todo corre sin red.

## Formato de los bancos

```json
{"casos": [
  {"termino": "tiendita", "tipo": "calle", "clases": ["461110"]},
  {"termino": "la Roma", "tipo": "no_es_giro", "clases": []}
]}
```

`tipo` es `calle`, `descripcion`, `error_dedo` o `no_es_giro`. `clases` es el conjunto de clases aceptables (SCIAN 2023); va vacío solo cuando no es un giro.

## Los bancos

Son la vara de medir, y se escriben **antes** de correr cualquier modelo.

- **Banco de ajuste:** unos 60 casos. Se usa para afinar el texto de cada clase y el umbral de parecido.
- **Banco ciego:** al menos 50 casos. No se mira al afinar. Se corre una sola vez, al final.
- Cada caso lleva el término, su tipo y el conjunto de clases aceptables, verificado a mano contra el catálogo. Un giro común puede corresponder a varias clases ("restaurante").
- Tipos de caso, todos presentes en los dos bancos:

| Tipo | Ejemplo |
|---|---|
| Palabra de la calle | "tiendita", "fonda", "estética", "tlapalería" |
| Descripción libre | "donde arreglan celulares", "lugar para cortarse el pelo" |
| Con error de dedo | "papeleria", "farmasia" |
| No es un giro | "la Roma", "barato", "cerca del metro" |

## Qué se mide

Para cada modelo, sobre cada banco:

- **Acierto entre los primeros 5:** en qué parte de los casos aparece una clase correcta entre las cinco más cercanas. Es la medida principal, porque esta pieza entrega candidatos y otra elige.
- **Acierto en el primer lugar** y **entre los primeros 10:** se reportan, pero no deciden.
- **Rechazo de lo que no es giro:** con un umbral de parecido fijado en el banco de ajuste, qué parte de los casos "no es un giro" se rechaza y qué parte de los giros reales se pierde por error.
- **Costo de operar:** memoria que ocupa el modelo, tiempo por consulta sin tarjeta gráfica y tamaño en disco.
- Todo desglosado por tipo de caso.

## Criterios de logro

El subproyecto se da por favorable cuando **al menos un modelo** cumple los cinco, medidos en el banco ciego:

| # | Criterio | Umbral propuesto |
|---|---|---|
| C1 | Acierto entre los primeros 5 | al menos 85 % de los casos que sí son giro |
| C2 | Ningún tipo de caso se queda atrás | al menos 70 % en cada tipo por separado |
| C3 | Rechazo de lo que no es giro | al menos 80 % rechazado, perdiendo como máximo 5 % de giros reales |
| C4 | Costo de operar en el VPS | menos de 2 GB de memoria y menos de 200 ms por consulta, sin tarjeta gráfica |
| C5 | Se puede repetir | un solo comando reproduce la tabla de resultados, con versiones fijas de modelo y dependencias |

Los umbrales son propuestas. Se confirman **antes** de correr el banco ciego y no se mueven después de ver el resultado.

**Regla para elegir:** entre los modelos que cumplan, gana el de mayor acierto entre los primeros 5. Si la diferencia es menor a 3 puntos, gana el más chico.

**Si ninguno cumple:**
1. Enriquecer el texto de cada clase (palabras frecuentes de los nombres comerciales, descripciones oficiales del SCIAN) y repetir sobre el banco de ajuste.
2. Los casos fallidos del banco ciego pasan al de ajuste y se escribe un banco ciego nuevo.
3. Si aun así no alcanza, se reabre el diseño: glosario ampliado sin modelo en producción, o un servicio externo como referencia.

## Reglas para que la comparación sea justa

- Los tres modelos ven **el mismo texto por clase** y los mismos bancos.
- Cada modelo se usa como lo recomienda su autor (algunos piden una instrucción distinta para la consulta y para el documento). Esa configuración se anota en los resultados.
- Lo que se afina, se afina solo con el banco de ajuste.
- La medición de tiempo se hace sin tarjeta gráfica, porque el VPS no tiene.

## Etapas

1. **Catálogo.** Hecho el 15 nov 2026: 948 clases de SCIAN 2023 (edición 2026-05), 725 con palabras frecuentes de sus nombres comerciales.
2. **Bancos.** Escribir el de ajuste y el ciego, y verificar a mano las clases esperadas.
3. **Línea base.** Correr los tres modelos sobre el banco de ajuste con el texto más simple (nombre de la clase y su jerarquía).
4. **Afinado.** Mejorar el texto por clase y fijar el umbral de parecido, solo con el banco de ajuste.
5. **Medición final.** Confirmar los umbrales, correr el banco ciego una vez y aplicar la regla para elegir.
6. **Repaso en el laboratorio.** `laboratorio/giros.html`: por cada término, las clases que devolvió cada modelo, lado a lado, con su parecido y si acertó.
7. **Regreso a H10.** Registrar el resultado en la síntesis y seguir con lo que falta del hito.

## Lo que hay que saber antes de empezar

- **Descargas.** Los tres modelos se bajan de Hugging Face: 1.2 GB, 1.2 GB y 0.5 GB. Se pide permiso antes de cada descarga.
- **EmbeddingGemma** tiene acceso restringido (verificado el 15 nov 2026): Ricardo acepta los términos de Google en la ficha del modelo con su cuenta, crea un token de lectura y lo pone en el `.env` del repo como `HF_TOKEN`. Su licencia es la de Gemma, con condiciones de uso; se lee antes de elegirlo.
- **Licencias.** Qwen3-Embedding-0.6B es Apache 2.0 y multilingual-e5-small es MIT, según la etiqueta de cada ficha en Hugging Face (15 nov 2026).

## Qué falta para marcar H10 después de este subproyecto

El hito pide más que la búsqueda por embeddings. Con un modelo elegido aquí, quedan:

- El glosario CDMX de giros y la función `traducir_giro` completa (glosario, embeddings y elección entre candidatos).
- Los vectores en pgvector, que es escribir en la base real y se hace solo con permiso.
- El acierto de la herramienta completa en un banco ciego de al menos 50 giros.

Queda por decidir si esas piezas se construyen dentro de este directorio o en el proyecto principal.

# Resultados: banco de ciego, texto «palabras»

Corrido el 2026-11-15 · 68 casos (53 giros, 15 que no lo son) · sin tarjeta gráfica, 4 hilos · generado por `evaluar.py`, no se edita a mano.

| Modelo | Primeros 5 | Primero | Primeros 10 | Rechazo de no giro | Giros perdidos | Umbral | ms por consulta | Memoria pico | C1 | C2 | C3 | C4 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gemma | 79 % | 53 % | 87 % | 47 % | 19 % | 0.286 | 110 | 1.19 GB | no | no | no | sí |
| e5-small | 70 % | 51 % | 77 % | 53 % | 11 % | 0.819 | 8 | 0.92 GB | no | no | no | sí |

## Acierto entre los primeros 5, por tipo de caso

| Modelo | Palabra de la calle | Descripción libre | Con error de dedo |
|---|---|---|---|
| gemma | 68 % de 25 | 94 % de 18 | 80 % de 10 |
| e5-small | 56 % de 25 | 72 % de 18 | 100 % de 10 |

## Configuración

- **gemma**: `google/embeddinggemma-300m` revisión `57c266a740` · consulta `'task: search result | query: '` · documento `'title: none | text: '`
- **e5-small**: `intfloat/multilingual-e5-small` revisión `614241f622` · consulta `'query: '` · documento `'passage: '`

## Fallos (ninguna clase correcta entre los primeros 5)

**gemma** (11): «changarro» → Fabricación de telas anchas de tejido de trama; «tablajería» → Fabricación de ladrillos no refractarios; «rosticería» → Fabricación de calzado con corte de piel y cuero; «lonchería» → Preparación de embutidos y otras conservas de carne de ganado, aves y otros animales comestibles; «nieves» → Elaboración de helados y paletas; «latonería» → Fabricación de otros productos metálicos; «repostería» → Panificación tradicional; «tahona» → Fabricación de ladrillos no refractarios; «quién me instala la luz en la casa» → Fabricación de focos; «nebería» → Fabricación de ladrillos no refractarios; «ferreteira» → Fabricación de productos de herrería

**e5-small** (16): «changarro» → Elaboración de alimentos para animales; «comedor» → Servicios de comedor para empresas e instituciones; «estilista» → Diseño de modas y otros diseños especializados; «tornillería» → Fabricación de tornillos, tuercas, remaches y similares; «refresquería» → Recuperación de residuos por el sector privado; «tablajería» → Aserrado de tablas y tablones; «lonchería» → Preparación de embutidos y otras conservas de carne de ganado, aves y otros animales comestibles; «botonería» → Fabricación de cierres, botones y agujas; «nieves» → Elaboración de helados y paletas; «latonería» → Reparación menor de llantas; «tahona» → Transporte por aguas interiores; «donde arreglan consolas de videojuegos» → Casas de juegos electrónicos; «donde mando una encomienda a otra ciudad» → Comercio al por menor en tiendas departamentales; «quién me instala la luz en la casa» → Comercio al por menor de electrodomésticos menores y aparatos de línea blanca; «donde dejo a mi hijo mientras trabajo» → Comercio al por menor de materiales para la construcción en tiendas de autoservicio especializadas; «donde mandan a imprimir tarjetas de presentación» → Edición de directorios y listas de correo integrada con la impresión

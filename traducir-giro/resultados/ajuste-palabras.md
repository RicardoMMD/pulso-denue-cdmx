# Resultados: banco de ajuste, texto «palabras»

Corrido el 2026-11-15 · 194 casos (153 giros, 41 que no lo son) · sin tarjeta gráfica, 4 hilos · generado por `evaluar.py`, no se edita a mano.

| Modelo | Primeros 5 | Primero | Primeros 10 | Rechazo de no giro | Giros perdidos | Umbral | ms por consulta | Memoria pico | C1 | C2 | C3 | C4 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| qwen3 | 82 % | 56 % | 87 % | 41 % | 5 % | 0.306 | 183 | 4.02 GB | no | sí | no | no |
| gemma | 92 % | 65 % | 94 % | 76 % | 5 % | 0.286 | 107 | 1.20 GB | sí | sí | no | sí |
| e5-small | 87 % | 58 % | 93 % | 32 % | 5 % | 0.819 | 8 | 0.93 GB | sí | sí | no | sí |

## Acierto entre los primeros 5, por tipo de caso

| Modelo | Palabra de la calle | Descripción libre | Con error de dedo |
|---|---|---|---|
| qwen3 | 85 % de 74 | 81 % de 52 | 78 % de 27 |
| gemma | 95 % de 74 | 96 % de 52 | 78 % de 27 |
| e5-small | 88 % de 74 | 90 % de 52 | 78 % de 27 |

## Configuración

- **qwen3**: `Qwen/Qwen3-Embedding-0.6B` revisión `97b0c614be` · consulta `'Instruct: Given a web search query, retrieve relevant passages that answer the query\nQuery:'` · documento `None`
- **gemma**: `google/embeddinggemma-300m` revisión `57c266a740` · consulta `'task: search result | query: '` · documento `'title: none | text: '`
- **e5-small**: `intfloat/multilingual-e5-small` revisión `614241f622` · consulta `'query: '` · documento `'passage: '`

## Fallos (ninguna clase correcta entre los primeros 5)

**qwen3** (27): «tiendita» → Comercio al por mayor de ropa, bisutería y accesorios de vestir; «miscelanea» → Comercio al por mayor de equipo de telecomunicaciones, fotografía y cinematografía; «ultramarinos» → Operadores de servicios de telecomunicaciones inalámbricas; «fondita» → Fondos y fideicomisos financieros; «cenaduría» → Servicios de apoyo a la educación; «pozolería» → Comercio al por menor de pisos y recubrimientos cerámicos; «dulcería» → Elaboración de dulces, chicles y productos de confitería que no sean de chocolate; «vinatería» → Elaboración de helados y paletas; «cervecería» → Cerrajerías; «hielera» → Elaboración de hielo; «donde arreglan celulares» → Comercio al por menor de teléfonos y otros aparatos de comunicación; «donde arreglan la pantalla del celular» → Comercio al por menor de teléfonos y otros aparatos de comunicación; «donde venden refrescos y botanas» → Comercio al por menor de bebidas no alcohólicas y hielo; «donde compro herramientas para la casa» → Fabricación de herramientas de mano metálicas sin motor; «donde cambian el aceite del carro» → Comercio al por menor de aceites y grasas lubricantes, aditivos y similares para vehículos de motor; «donde me sacan una muela» → Alquiler de maquinaria y equipo para mover, levantar y acomodar materiales; «donde hacen cortes de pelo para niños» → Comercio al por menor de sombreros; «farmasia» → Elaboración de botanas; «carnisería» → Servicios funerarios; «peluqeria» → Elaboración de pulque; «fonsa» → Fondos y fideicomisos financieros; «recaudería» → Recuperación de residuos por el sector privado; «donde arreglan zapatos» → Comercio al por mayor de calzado; «donde hacen portones y rejas» → Administración de puertos y muelles; «donde arreglan fugas de agua» → Captación, tratamiento y suministro de agua realizados por el sector público; «zapatreia» → Centros de planificación familiar del sector privado; «sibercafe» → Cafeterías, fuentes de sodas, neverías, refresquerías y similares

**gemma** (12): «pozolería» → Comercio al por menor de carne de aves; «bolería» → Boliches; «hielera» → Fabricación de llantas y cámaras; «donde venden refrescos y botanas» → Comercio al por mayor de botanas y frituras; «donde cambian el aceite del carro» → Comercio al por menor de aceites y grasas lubricantes, aditivos y similares para vehículos de motor; «feretería» → Fabricación de productos de herrería; «peluqeria» → Elaboración de pulque; «fonsa» → Alquiler sin intermediación de teatros, estadios, auditorios y similares; «talller mecanico» → Maquinado de piezas metálicas para maquinaria y equipo en general; «recaudería» → Agencias de cobranza; «crmeria» → Cerrajerías; «tamals» → Confección en serie de disfraces y trajes típicos

**e5-small** (20): «tiendita» → Tenedoras de acciones; «fondita» → Fondos y fideicomisos financieros; «cenaduría» → Restaurantes que preparan otro tipo de alimentos para llevar; «pozolería» → Colocación de pisos cerámicos y azulejos; «verdulería» → Congelación de frutas y verduras; «pinturería» → Realización de trabajos de carpintería en el lugar de la construcción; «hielera» → Elaboración de hielo; «donde cambian el aceite del carro» → Comercio al por menor de aceites y grasas lubricantes, aditivos y similares para vehículos de motor; «donde me sacan una muela» → Comercio al por menor de muebles para jardín; «taqeria» → Comercio al por mayor de cueros y pieles; «fonsa» → Fondos y fideicomisos financieros; «vetrinaria» → Fabricación de asientos y accesorios interiores para vehículos automotores; «recaudería» → Recuperación de residuos por el sector privado; «novedades» → Comercio al por mayor de juguetes y bicicletas; «donde hacen portones y rejas» → Comercio al por menor en ferreterías y tlapalerías; «donde arreglan fugas de agua» → Captación, tratamiento y suministro de agua realizados por el sector público; «donde compro comida corrida barata» → Comercio al por mayor de botanas y frituras; «zapatreia» → Confección de prendas de vestir sobre medida; «mueblria» → Fabricación de muebles, excepto cocinas integrales, muebles modulares de baño y muebles de oficina y estantería; «crmeria» → Cerrajerías

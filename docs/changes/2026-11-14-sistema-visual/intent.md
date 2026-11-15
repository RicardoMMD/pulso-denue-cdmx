# Intent: sistema visual v1
Autor: Ricardo (RicardoMMD) · Fecha: 2026-11-14 · Estado: aceptado
Ref: H08 en `docs/Seguimiento — Hitos del proyecto.md` · Antecedentes: `docs/Pulso DENUE CDMX — Síntesis del proyecto.md` ("Resultado del prototipo 2", "Stack y pipeline") y `docs/Core — Documentación del modelo de datos.md` (4.11 Macrosectores)

## Problema
La ciudad de luz ya se dibuja (prototipo 2), pero con decisiones provisionales que nadie tomó a propósito:
- **Color:** siete valores hexadecimales escritos a mano en `prototipos/02-renderizador/src/main.js`, uno por macrosector, elegidos solo para ver algo.
- **Luz:** tamaño de punto, halo, brillo (`BloomEffect`), fondo y atenuado son números sueltos en el mismo archivo.
- **Tipografía:** no hay ninguna definida.

Mientras esto no se decida, lo que sigue se construiría sobre valores de prueba:
- H15 (motor de escenas) y H16 (escenas) necesitan colores, parámetros de luz y estados (atenuado, resaltado, reposo) estables.
- H17 (vista exacta 2D) necesita la misma paleta sobre papel, en tema claro, para barras, coropletas y tablas.
- H18 (recorridos) y H21 (historia) necesitan tipografía para títulos, textos y cifras que cuentan hasta su valor.

Dos rasgos de los datos hacen que la paleta no se pueda elegir con muestras de color:
- **El brillo aditivo se come el tono.** Los puntos suman su luz sobre fondo oscuro. En el Centro miles de puntos se enciman y cualquier color se vuelve blanco.
- **Comercio es el 49 % de los establecimientos** (227 775 de 462 729). Si su color es intenso, la ciudad entera se lee de ese color y los macrosectores chicos desaparecen. Transporte y campo es el 0.8 %.

## Resultado propuesto
Existe un sistema visual v1 que el portal usa en todas partes, con una sola fuente:

- **Paleta por macrosector** (los 7 de `ref_macrosector`): un tono por macrosector con dos variantes:
  - **oscura:** luz para puntos aditivos sobre fondo oscuro (la ciudad de luz);
  - **clara:** color sólido para papel, solo para la vista exacta 2D y la interfaz (paneles y textos). La ciudad 3D existe solo en tema oscuro. La variante clara no se diseña aparte: se deriva de la oscura bajando la luminosidad hasta alcanzar el contraste mínimo.
  - **Comercio, el más sobrio:** tono de poca luminosidad y poca saturación, para que no domine la ciudad.
- **Neutros y estados:** fondo, trazos del fondo (alcaldías, líneas del Metro, calles), texto, y los estados de un punto (normal, atenuado por un filtro, resaltado, reposo), en ambos temas.
- **Tratamiento de la luz:** tamaño de punto por zoom, halo, brillo y mapeo de tonos, con valores que eviten que el Centro se queme a blanco.
- **Tipografía:** una sola familia, con tamaños y pesos para la interfaz, títulos, textos de panel, cifras (con dígitos de ancho fijo para los contadores) y etiquetas 3D.
- **Tokens como fuente única, en `diseno/`:** `diseno/tokens.json` genera lo que leen el motor (JS para shaders) y la interfaz y los componentes 2D (variables CSS). Ningún color ni tamaño se repite a mano en el código.
- **Laboratorio visual** (carpeta `laboratorio/` en la raíz): una página sobre el prototipo 2 para cambiar paletas y parámetros en vivo, con tomas fijas reproducibles (Centro denso, periferia, Línea 1, filtro por macrosector y una vista exacta 2D en papel). Sirve para decidir ahora y como banco visual de H15 y H16 después.
- **Aplicado:** el prototipo 2 usa los tokens, sin colores ni parámetros de luz escritos a mano.

## Usuarios y sistemas afectados
- **Visitante del portal:** lee la ciudad por macrosector, en escritorio y en celular, en tema oscuro (3D) y claro (2D).
- **Ricardo:** elige la paleta en el laboratorio. La elección final es estética y es suya.
- **Motor y escenas** (H15, H16), **vista exacta** (H17), **recorridos** (H18), **historia** (H21) y **accesibilidad** (H23): consumen los tokens.
- **Prototipo 2** (`prototipos/02-renderizador/`): primera pieza que los aplica y base del laboratorio.
- **Contrato de escena:** no cambia. El estado no lleva colores; el motor los toma de los tokens según el macrosector.

## Restricciones
- **El color no entra al contrato ni a la base.** Ni el estado de escena ni `semantic` llevan colores. El modelo solo sabe qué sectores tiene cada macrosector (4.11 del documento del modelo).
- **Stack de la síntesis:** Three.js con `postprocessing` para el brillo y `troika-three-text` para las etiquetas 3D. Interfaz en Vue 3; los componentes 2D, en SVG.
- **Tipografías de licencia abierta** (SIL OFL o similar), con acentos y ñ completos, servidas desde el propio sitio.
- **Siete macrosectores fijos.** La paleta no cambia la agrupación; si la agrupación cambia, se edita `ref_macrosector` y la paleta se ajusta.
- **Sin escribir en la base.** H08 no la necesita.

## Fuera de alcance
- **Daltonismo** (decisión del 14 nov 2026 para la primera versión). No es criterio de terminado ni se simula. El color tampoco es el único canal: filtrar por macrosector atenúa los demás puntos, la leyenda nombra cada macrosector y la vista exacta da las cifras.
- **Rendimiento** (misma decisión, que alcanza también a H24). No se mide en celular con brillo ni en gama media, y no es criterio de terminado de H08. Los parámetros de luz se eligen por cómo se ven.
- **Ciudad 3D en tema claro.** Es el caso más caro en recursos (otra técnica de dibujo y otro conjunto de tomas) y no se hace en la primera versión.
- **Referencias estéticas externas.** Las paletas candidatas salen de las restricciones de los datos (fondo oscuro, peso de Comercio, legibilidad en papel).
- **Identidad del proyecto** (logotipo, iconografía) y **duraciones de movimiento**, que ya están en la síntesis ("Coreografía").
- **Escenas de la segunda versión.** Sus colores (presencia digital, calles, rarezas) se agregan cuando lleguen, con los mismos tokens.

## Cómo sabremos que funcionó
1. **Fuente única:** existe el archivo de tokens y de él se generan el módulo JS y las variables CSS. Una prueba falla si lo generado está desactualizado. Una búsqueda en `prototipos/02-renderizador/src/` no encuentra colores hexadecimales ni parámetros de luz sueltos.
2. **Brillo aditivo:** en la toma fija del Centro, los colores de los macrosectores se siguen distinguiendo. El umbral medible (por ejemplo, la parte de píxeles quemados a blanco) se fija en la spec.
3. **Comercio no domina:** al filtrar por cada uno de los 7 macrosectores, su color se reconoce en las tomas del Centro y de la periferia, incluido Transporte y campo.
4. **Tema claro:** la vista exacta 2D de prueba (barras y coropleta) usa la variante clara, y cada color tiene un contraste de al menos 3:1 contra el fondo (WCAG 1.4.11, elementos gráficos).
5. **Tipografía:** una página de muestra en ambos temas con títulos, texto de panel, cifras tabulares contando y etiquetas 3D con troika, legible a 390 px de ancho.
6. **Elección aprobada:** Ricardo elige la paleta y los parámetros en el laboratorio, y quedan registrados en la spec con las tomas.
7. **`make verify` en verde.**

## Preguntas abiertas
Respondidas el 14 nov 2026:
1. **Alcance del tema claro** → lo menos intensivo en recursos: solo la vista exacta 2D y la interfaz; la ciudad 3D solo en oscuro.
2. **Dónde viven los tokens** → carpeta propia `diseno/` en la raíz del repo; el futuro frontend la lee.
3. **Estrategia para Comercio** → un tono sobrio y poco luminoso.
4. **Familia tipográfica** → una sola familia.
5. **Alcance de "sin rendimiento"** → también aplica a H24.

Arrastrada:
6. **Brillo** (posprocesado o halo en el punto) → se decide viendo ambos lado a lado en el laboratorio; el laboratorio también compara el mapeo de tonos (el modo que evita que el Centro se queme a blanco).

# Intent: contrato de escena v1
Autor: Ricardo (RicardoMMD) · Fecha: 2026-11-08 · Estado: aceptado
Ref: H09 en `docs/Seguimiento — Hitos del proyecto.md` · Diseño previo: `docs/Pulso DENUE CDMX — Síntesis del proyecto.md`, sección "Contrato del estado de escena"

## Problema
Tres autores distintos van a mover la misma escena: las historias editoriales, el explorador y el Analista. Lo que acordamos en la síntesis es que los tres escriban un solo "estado de escena" y que un solo motor lo interprete. Ese estado todavía no existe como código: solo está descrito en prosa.

Mientras no exista, casi todo lo que sigue está bloqueado o se construiría sobre supuestos:
- H12 (guion de "Vida comercial del Metro") no puede validar sus paneles.
- H13 (paquete estático), H14 (backend), H15 (motor) y H17 (vista exacta) no saben qué estructura leer o guardar.
- H19 (Analista) no tiene contra qué validar la herramienta "construir escena", que es su defensa contra estados inventados.

Si cada pieza inventa su propia forma del estado, se pierden las propiedades que justifican el diseño por paneles: compartir, volver atrás, heredar y abrir un panel viejo con sus cifras originales.

## Resultado propuesto
Existe un contrato de escena v1 con una sola fuente de verdad, y cualquier pieza del proyecto puede preguntar "¿este estado es válido?" y obtener la misma respuesta:

- Un estado escrito a mano (historia), generado por el explorador o propuesto por el Analista se valida en tres niveles: estructura, referencias y coherencia. El cuarto nivel de la síntesis (dispositivo) no es una validación: el estado es el mismo en celular y en escritorio, y la sustitución por agregados es trabajo del motor (H15, medido en H24). El contrato solo garantiza que cada escena declara su nivel de agregado. Si es inválido, la razón se puede leer y sirve para que el Analista corrija y reintente.
- Un estado parcial ("¿y en Cuauhtémoc?") se combina con el anterior según las reglas de herencia de la síntesis y produce un estado completo y determinista.
- El contrato cubre completas las tres escenas de la primera versión: Ciudad de luz, Corredores del Metro (modos línea y ranking) y Ciudades dentro de la ciudad (modos exterior e interior).
- El mismo contrato llega al navegador como JSON Schema versionado, tipos TypeScript y un validador Ajv, generados sin copiar nada a mano.
- Una historia inválida hace fallar la integración continua (CI: GitHub Actions ejecuta las pruebas en cada push) sin conexión a la base.
- Un cambio incompatible sube la versión y trae su migración, para que los paneles guardados sigan abriendo.

## Usuarios y sistemas afectados
- **Autor de historias** (Ricardo): escribe historias en JSON o YAML y recibe errores claros antes de publicar.
- **El Analista** (H19): la herramienta "construir escena" devuelve estados que este contrato acepta o rechaza.
- **Explorador, motor y vista exacta** (H15–H17): consumen los tipos TS y el validador del navegador.
- **Backend** (H14): valida los tres niveles y calcula el id por contenido a partir del estado canónico.
- **Paquete estático** (H13): reutiliza el catálogo de referencias por edición.
- **Base `semantic`**: es la fuente del catálogo de referencias (lugares, estaciones, líneas, conglomerados y clases SCIAN por edición). Solo se lee.
- **Repositorio**: se publica en GitHub como repositorio **público** y gana un workflow de CI.

## Restricciones
- **Fuente única:** modelos Pydantic v2 en `backend/contracts/escena.py`, dentro del proyecto del backend (FastAPI), que nace con este hito. El JSON Schema, los tipos TS y Ajv se generan; no se editan a mano.
- **Principios de la síntesis, sin excepciones:** declarativo, referencias en vez de datos (nada de coordenadas ni listas de puntos), cerrado (valores permitidos por campo), parcial y heredable, determinista, y cifras vinculadas, nunca escritas.
- **Límites del Analista:** no puede escribir cifras, colores, escalas, coordenadas de cámara ni recorridos nuevos, ni omitir la nota de cautela. El contrato debe hacer imposible expresarlo, no solo desaconsejarlo.
- **Validación sin base:** el nivel 2 usa un catálogo de referencias exportado de `semantic`, por edición, como archivo. CI no tiene acceso al VPS.
- **Versionado:** `backend/contracts/escena.v1.json`. Un cambio incompatible implica v2 más una función de migración desde v1.
- **Estado canónico estable:** claves ordenadas, sin valores predeterminados. Es la base del id SHA-256 → base62 de H14, así que no puede cambiar sin cambiar la versión.
- **Stack:** Python 3.12–3.13 con `uv` (como `pipeline/`); Node para generar y probar la parte del navegador.
- **Seguridad del repo:** el repositorio es público. Antes de crear el remoto se revisa el historial completo: no puede viajar nada de `.env`, `data/`, credenciales, la IP del VPS ni datos de la infraestructura. Un escaneo rápido del 2026-11-08 no encontró nada.
- **Selección por giro:** solo códigos SCIAN en v1; los macrosectores quedan fuera de la selección (siguen siendo codificación de color).
- **Territorio solo por referencia:** el "punto con radio" es un lugar del catálogo (estación, conglomerado, establecimiento, manzana…) más un radio permitido. No hay coordenadas libres; un clic del explorador se ajusta a la referencia más cercana.
- **Exploración bloqueable** es propiedad de la historia (con excepción por panel), no del estado, para que el mismo panel tenga el mismo id venga de donde venga.
- **`make verify`** debe incluir las pruebas del contrato.

## Fuera de alcance
- Escenas de la segunda versión (las otras ocho). Entran después como cambio compatible.
- El motor que interpreta el estado (H15), las transiciones y la coreografía.
- Endpoints, tablas `app.panel` y `app.conversacion` y el cálculo del id por contenido como servicio (H14). Aquí solo se define el estado canónico del que sale.
- El formato de los recorridos de autor (H18). El contrato solo los referencia por nombre.
- El guion completo de "Vida comercial del Metro" (H12). Aquí bastan historias de ejemplo, válidas e inválidas, para las pruebas.
- El paquete estático completo (H13). Aquí solo se exporta el catálogo de referencias.
- El proyecto frontend en Vue.

## Cómo sabremos que funcionó
- El ejemplo de la síntesis ("¿Qué mercados de Iztapalapa tienen más locales de comida?" y luego "¿Y en Cuauhtémoc?") se expresa como dos estados válidos. El segundo es parcial y, al heredar, produce el estado esperado.
- Cada regla de herencia de la síntesis tiene al menos una prueba.
- Cada uno de los tres niveles de validación tiene casos que lo rechazan con un mensaje que nombra el campo y la razón. Ejemplos: Corredores con radio de 400 m (estructura), una estación que no existe en la edición (referencias), Ciudades dentro de la ciudad sin alcaldía ni conglomerado (coherencia).
- Python y Ajv dan el mismo veredicto sobre el mismo banco de estados en los niveles 1 y 2.
- Un intento de escribir una cifra, un color o una coordenada en el estado se rechaza, incluida una coordenada en el territorio.
- Un estado v1 pasa por una migración de prueba a una v2 ficticia y sigue siendo válido.
- Un push con una historia inválida deja el workflow de GitHub Actions en rojo, y con la historia corregida en verde.
- `make verify` incluye las pruebas del contrato y termina en 0.

## Decisiones tomadas (2026-11-08)
- Escenas: solo las 3 de la primera versión.
- CI: GitHub Actions, repositorio público.
- Navegador: H09 entrega JSON Schema, tipos TS y validador Ajv.
- Nivel 2: catálogo de referencias exportado de `semantic`, como archivo.
- Nivel 4 (dispositivo): sale del contrato; es regla del motor.
- Selección por giro: solo SCIAN.
- Territorio: solo referencias del catálogo, también para el punto con radio.
- Código: `backend/contracts/`.
- Exploración bloqueable: propiedad de la historia.
- Repositorio: `RicardoMMD/pulso-denue-cdmx`, público.
- Catálogo de referencias: se versiona el de la edición vigente (también sirve a H13).
- Selección SCIAN: cualquier nivel, de sector a clase.

## Preguntas abiertas
1. **Narrativa con huecos:** sintaxis de los huecos para cifras vinculadas y cómo se declara de qué columna de la vista exacta sale cada cifra. Se propone en la spec.

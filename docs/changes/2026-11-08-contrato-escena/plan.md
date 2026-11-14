# Plan: contrato de escena v1 (de spec.md, aceptada el 2026-11-14)
Estado: borrador · Ref: H09

Quien no vio la conversación debería poder implementar H09 con este plan y la spec. Los números de requisito (R1–R15) y de sección (§1–§9) son los de `spec.md`.

## Datos de partida (consultados en `semantic` el 2026-11-14, solo lectura)

- Edición vigente: `2026-05`, corte 20 may 2026, SCIAN 2023.
- `semantic.lugar`: 14 263 filas sin claves repetidas por tipo. 1 ciudad, 16 alcaldías, 1 543 colonias, 163 estaciones, 2 885 conglomerados y 9 655 calles.
- Líneas del Metro (`metro_linea.cve_linea`): `1` a `9`, `12`, `A` y `B`. Son doce.
- Claves de ejemplo: estación `AGRICOLA ORIENTAL`; conglomerado `denue:CENTRAL DE ABASTO|PARQUE VIA VALLEJO|0`. Llevan espacios, `:` y `|`, y ninguna lleva acentos.
- Tipos de conglomerado: 18 en la edición vigente ("mercado público", "centro o plaza comercial"…). Cambian con la edición, así que se validan en el nivel 2 contra las referencias, no como lista fija del esquema.
- Estrato: 7 valores (`estrato_orden` 1 a 7). Tipo de unidad: `Fijo` y `Semifijo`.
- Clases SCIAN: 948 en la versión 2023.

## Orden de trabajo

Cada paso termina con sus pruebas en verde antes de pasar al siguiente.

### Paso 1 · Proyecto y modelos (R1–R4)
- `backend/pyproject.toml`: `uv`, Python `>=3.12,<3.14`, dependencias `pydantic>=2.9` y `pyyaml`; grupo `dev` con `pytest`; grupo `base` con `psycopg[binary]>=3.2`, que solo usa el exportador.
- `backend/contracts/catalogo.py`: un solo diccionario por escena con modos, predeterminados, territorios permitidos por modo, codificaciones, recorridos admitidos, agregado en celular y medidas de la vista exacta (tablas de §3 y §6). De aquí leen `validar`, `herencia` y `vista_exacta`; nada de esto se repite en otro archivo.
- `backend/contracts/escena.py`: `Estado` y `EstadoParcial`. Todos los modelos con `extra="forbid"`. Las escenas son unión discriminada por `tipo`. Los textos de la narrativa llevan un validador que rechaza dígitos fuera de los huecos `{nombre}`.
- `EstadoParcial` se escribe a mano, bloque por bloque, con todos los campos opcionales y `null` permitido. No se deriva por metaprogramación: son tres escenas y así el JSON Schema sale legible.
- Pruebas: los casos de R8 de nivel 1 (radio de 400 m, coordenada en el territorio) y un estado válido por escena y modo.

### Paso 2 · Generación (R1, R7)
- `backend/contracts/generar.py` escribe `escena.v1.json` desde `Estado.model_json_schema()`. Antes de escribir quita `discriminator.mapping`, añade `type: object` junto al discriminador y pone `title` propio a cada campo `tipo` y `modo`.
- `backend/contracts-ts/package.json` con `ajv`, `ajv-formats` y `json-schema-to-typescript` en versiones fijas. `generar.mjs` produce `escena.v1.d.ts` y `validar-estructura.js` (Ajv standalone, opción `discriminator: true`, modo estricto).
- Prueba: `generar.py` y `generar.mjs` corren dos veces y no cambian ningún archivo.

### Paso 3 · Referencias (R12)
- `backend/contracts/exportar_referencias.py <edicion>`: se conecta como `pulso_analista` con las variables del `.env`, igual que `prototipos/03-resolver-lugar/evaluar.py`, y abre la conexión en solo lectura.
- Escribe `referencias/2026-05.json` con claves ordenadas: edición, fecha de corte, versión SCIAN, claves de lugar por tipo (con nombre, para los mensajes de error y el hueco `{territorio}`), líneas con sus estaciones en orden (`metro_recorrido`), códigos SCIAN de sector a clase, tipos de conglomerado y estratos.
- Sin coordenadas ni geometrías: el contrato no las necesita y el archivo se queda cerca de 0.6 MB.
- `backend/contracts/referencias.py`: carga el archivo y responde `existe(tipo, clave)`, `linea_pasa_por(linea, estacion)` y `scian_valido(codigo)`. `contracts-ts/referencias.ts` hace lo mismo en el navegador.
- `referencias/LICENCIA.md` con la atribución a OpenStreetMap (ODbL) y a INEGI. `LICENSE` (MIT) en la raíz.

### Paso 4 · Validación (R6, R8)
- `backend/contracts/validar.py`: `validar(estado, referencias, contexto) -> list[ErrorValidacion]`. El nivel 1 traduce los errores de Pydantic a `nivel`, `ruta` (JSON Pointer), `codigo` y `mensaje` en español. El nivel 2 recorre las claves contra las referencias. El nivel 3 aplica las reglas de §4 leyendo `catalogo.py`.
- Si el nivel 1 falla, no se corren los niveles 2 y 3: sus mensajes sobre un estado mal formado confunden más de lo que ayudan.
- Pruebas: un caso por cada código de §4 y los cuatro casos de R8.

### Paso 5 · Herencia (R5)
- `backend/contracts/herencia.py`: `heredar(anterior, parcial) -> Estado`. Trabaja sobre diccionarios y valida el resultado al final, para que un parcial que produce un estado inválido devuelva los mismos errores que el paso 4.
- Pruebas: una por cada una de las seis reglas, más el ejemplo de la síntesis (mercados de Iztapalapa y luego "¿y en Cuauhtémoc?").

### Paso 6 · Forma canónica y migraciones (R9, R10)
- `backend/contracts/canonico.py` y `contracts-ts/canonico.ts`: quitan los campos con su valor predeterminado (leído de `catalogo.py` y del esquema), ordenan las claves por punto de código, normalizan los textos a NFC y escriben JSON sin espacios y sin escapar caracteres no ASCII.
- El estado no contiene números de punto flotante; una prueba recorre el esquema y falla si aparece un campo `number`.
- `backend/contracts/casos/canonico/`: pares de estado y bytes esperados en hexadecimal. Los leen pytest y `node --test`.
- `backend/contracts/migraciones.py`: `migrar(estado_json) -> Estado` con un registro de funciones por versión. La prueba define una v2 ficticia dentro del propio test.

### Paso 7 · Vista exacta (R11)
- `backend/contracts/vista_exacta.py`: `vista_exacta(estado) -> VistaExacta` con tabla, filtros, tipo de resultado y medidas, todo leído de `catalogo.py`. No ejecuta consultas.
- Conecta con el paso 4: `cifra_no_disponible` compara las medidas de la narrativa con las de esta vista.

### Paso 8 · Banco compartido y paridad (R7)
- `backend/contracts/casos/veredicto/`: un archivo JSON por caso con `estado`, `contexto`, `valido`, `nivel` y `codigo`.
- pytest corre los tres niveles. `node --test` corre los niveles 1 y 2 y comprueba el mismo veredicto y nivel; los casos de nivel 3 deben pasar ahí como válidos.

### Paso 9 · Historias (R13)
- `contenido/historias/ejemplo-mercados.yml`: el ejemplo de la síntesis en dos paneles.
- `backend/contracts/validar_historias.py`: aplica la herencia panel por panel, valida cada panel y termina con código distinto de cero si alguno falla. Imprime historia, número de panel, ruta y mensaje.
- `backend/tests/contracts/historias_invalidas/`: historias que deben fallar, fuera de `contenido/` para no romper el comando.

### Paso 10 · Comandos y CI (R14, R15)
- `Makefile`: `contratos`, `ci` y `referencias` según §9; `verify` pasa a ser `ci` + túnel + `dbt test`.
- `check` necesita hoy el `.env` para `dbt parse`. `ci` define variables de mentira si el `.env` no existe.
- `.github/workflows/verificar.yml`: instala `uv` y Node, y corre `make ci`. Queda escrito, pero no se ejecuta en GitHub hasta que exista el remoto.
- `CLAUDE.md`: los tres comandos nuevos en la tabla y una línea que diga que los archivos generados no se editan a mano.

### Paso 11 · Cierre
- `make verify` con la salida a la vista.
- Marcar H09 en el seguimiento y registrar el resultado en la síntesis.

## Lo que este plan no hace sin tu "adelante"
- Crear el remoto público ni hacer `push`. Antes va gitleaks sobre el historial completo.
- Escribir en la base. H09 solo lee `semantic`.

## Riesgos y cómo los atiendo

- **El paso más arriesgado es el 6.** Si Python y JS difieren en un byte, el mismo panel tiene dos ids. Por eso el banco de bytes existe antes que `canonico.ts`, e incluye claves con acentos, textos con `ñ` compuesta y descompuesta, y las claves de conglomerado con `|` y `:`.
- **Predeterminados duplicados.** La forma canónica en JS necesita los mismos predeterminados que Python. Se toman del `default` del JSON Schema generado, no de una segunda lista.
- **Mensajes de Pydantic.** Sus textos están en inglés y cambian entre versiones. El nivel 1 arma el mensaje a partir del tipo de error y la ruta, sin copiar el texto original.
- **`check` en CI.** Si `dbt parse` no arranca con variables de mentira, `ci` se queda con la sintaxis de Python y JS más `contratos`, y `dbt parse` sigue solo en `verify`.
- **Tamaño de las referencias.** Si pasa de 1 MB, se quitan los nombres de calle y se dejan solo las claves.

## Alternativas que descarté

- **Escribir el JSON Schema a mano y generar Pydantic.** La síntesis fija Pydantic como fuente, y las reglas de coherencia viven mejor en Python.
- **Derivar `EstadoParcial` automáticamente.** Ahorra unas líneas y vuelve opaco el esquema que lee el frontend.
- **Validar el nivel 3 en el navegador.** Obligaría a escribir las reglas dos veces. El explorador solo ofrece combinaciones válidas y el backend confirma.
- **RFC 8785 completo para la forma canónica.** Casi todo su peso está en los números de punto flotante, que el estado no tiene.

## Prueba de que funciona

Los ocho criterios de "Cómo sabremos que funcionó" del intent, cada uno con su comprobación:

| Criterio | Comprobación |
|---|---|
| Ejemplo de la síntesis en dos estados | prueba de herencia del paso 5 y `ejemplo-mercados.yml` |
| Una prueba por regla de herencia | `tests/contracts/test_herencia.py` |
| Rechazo en los tres niveles con mensaje claro | banco `casos/veredicto/` |
| Mismo veredicto en Python y Ajv | `node --test` sobre el mismo banco |
| Cifra, color o coordenada rechazados | casos de nivel 1 del banco |
| Migración a una v2 ficticia | `tests/contracts/test_migraciones.py` |
| Historia inválida deja CI en rojo | `make ci` con una historia de `historias_invalidas/` copiada a `contenido/`; en GitHub cuando exista el remoto |
| `make verify` incluye el contrato y termina en 0 | salida del comando al cerrar |

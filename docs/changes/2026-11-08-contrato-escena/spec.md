# Spec: contrato de escena v1 (de intent.md 2026-11-08)
Estado: aceptada (2026-11-14) · Ref: H09

Diseño previo: síntesis, secciones "Vocabulario", "Contrato del estado de escena", "Persistencia de paneles", "Recorridos de autor" y "Coreografía de transiciones". Esta spec la concreta para las tres escenas de la primera versión. Donde se aparta de la síntesis, lo dice.

## Requisitos

**Modelo**
- R1. Un modelo Pydantic v2 `Estado` describe un panel completo. Es la única fuente: el JSON Schema, los tipos TS y el validador Ajv se generan a partir de él.
- R2. Las escenas son una unión discriminada por `escena.tipo`: `ciudad_de_luz`, `corredores_metro` y `ciudades_dentro`. Cada una tiene sus modos, parámetros y codificaciones cerrados (tabla en Diseño §3).
- R3. Ningún campo del estado admite cifras de datos, colores, escalas, coordenadas, tiempos ni duraciones. Los textos libres (`titulo`, `texto`, `nota_cautela`) no admiten dígitos fuera de los huecos.
- R4. Un modelo `EstadoParcial` (todos los campos opcionales, `null` permitido) describe un cambio sobre un panel anterior.

**Herencia**
- R5. `heredar(anterior, parcial) -> Estado` aplica las seis reglas de la síntesis: fusión por bloque, listas que se reemplazan, `null` que vuelve al valor predeterminado, reinicio al cambiar de escena, narrativa heredada como plantilla y vista exacta recalculada. Cada regla tiene al menos una prueba.

**Validación**
- R6. `validar(estado, referencias, contexto) -> list[ErrorValidacion]` revisa tres niveles: 1 estructura, 2 referencias y 3 coherencia. Cada error trae `nivel`, `ruta` (JSON Pointer), `codigo` estable y `mensaje` en español que nombra el campo y la razón.
- R7. El navegador valida los niveles 1 y 2 con el JSON Schema (Ajv precompilado) y el mismo archivo de referencias. Un banco común de casos da el mismo veredicto (válido o inválido, y el mismo nivel) en Python y en TS.
- R8. Los casos del intent se rechazan en su nivel: radio de 400 m (1), estación inexistente en la edición (2), `ciudades_dentro` en modo interior sin un conglomerado como territorio (3), y una coordenada en el territorio (1).

**Identidad, forma canónica y versiones**
- R9. `canonico(estado) -> bytes`: JSON UTF-8 con claves ordenadas, sin campos con su valor predeterminado, sin espacios y con textos normalizados a NFC. Python y TS producen bytes idénticos sobre un banco de casos fijo. Esta es la base del id de H14.
- R10. El estado declara `contrato: 1`. `migrar(estado_json) -> Estado` lleva cualquier versión anterior a la vigente. Un estado v1 pasa por una migración a una v2 ficticia, solo de prueba, y sigue siendo válido.

**Vista exacta y cifras**
- R11. `vista_exacta(estado) -> VistaExacta` se deriva del estado y nadie la escribe: tabla de `semantic`, parámetros, tipo de resultado y medidas disponibles. Las cifras de la narrativa solo pueden nombrar medidas de esa vista.

**Referencias**
- R12. `exportar_referencias.py <edicion>` escribe `referencias/<edicion>.json` leyendo `semantic` con el rol `pulso_analista`. Se versiona el de la edición vigente (2026-05).

**Historias, CI y verificación**
- R13. Una historia es un archivo YAML en `contenido/historias/` (formato en Diseño §7). `validar-historias` aplica la herencia panel por panel y valida cada panel en los tres niveles.
- R14. Hay un workflow de GitHub Actions en el repo público `RicardoMMD/pulso-denue-cdmx` que, sin acceso a la base, ejecuta las pruebas del contrato, valida las historias y comprueba que los archivos generados están al día. Una historia inválida lo deja en rojo.
- R15. `make verify` incluye lo mismo que CI, más lo que ya hacía.

## Diseño

### 1. Estado y metadatos
La síntesis pone la "identidad" (origen, panel anterior) dentro del estado. Aquí la saco: si estuviera dentro, el mismo panel tendría dos ids según quién lo creara, que es el mismo problema que llevó la exploración bloqueable a la historia.

```
Estado (lo que se ve: entra al id)   Metadatos (quién y de dónde: no entra al id)
  contrato: 1                          origen: historia | explorador | analista
  edicion: "2026-05"                   panel_anterior: id | null
  territorio                           conversacion: id | null
  encuadre
  escena          (unión por tipo)
  seleccion
  capas
  comparacion     | null
  narrativa
```
`id = base62(sha256(canonico(estado)))[:10]`. La edición ya está dentro del estado; H14 lo implementa. La vista exacta no se guarda en el estado: es función de él.

### 2. Bloques comunes
| Bloque | Campos | Valores |
|---|---|---|
| `territorio` | `tipo`, `clave`, `radio_m` | `tipo` ∈ ciudad, alcaldia, colonia, estacion_metro, linea_metro, conglomerado, calle. `clave` es la de `semantic.lugar` (o `cve_linea`). `radio_m` ∈ {300, 500, 800}, solo para estacion_metro y conglomerado, y nunca dentro de `corredores_metro` (ahí el radio es el parámetro de la escena). La calle se usa completa |
| `encuadre` | `modo`, `angulo` o `recorrido` | `ajustar` (predeterminado) · `angulo` ∈ cenital, oblicua, rasante · `recorrido` ∈ el_despertar, tren_de_luz, constelacion_estaciones, entrar_al_mercado |
| `seleccion` | `scian`, `estrato`, `tipo_unidad`, `presencia_digital`, `tipo_conglomerado` | `scian`: lista de 1 a 20 códigos de 2 a 6 dígitos (sector a clase) · `estrato`: lista de 1 a 7 · `tipo_unidad` ∈ fijo, semifijo · `presencia_digital`: bool · `tipo_conglomerado`: lista del catálogo. Filtrar atenúa, nunca elimina |
| `capas` | lista | alcaldias, lineas_metro, calles_principales, etiquetas |
| `comparacion` | `forma` + exactamente uno de `territorio`, `seleccion` | `forma` ∈ lado_a_lado, transformacion |
| `narrativa` | `titulo` (≤ 80), `texto` (≤ 400), `principal`, `secundarias` (≤ 3), `nota_cautela` (obligatoria, ≤ 240) | Ver §5. Fuente y fecha de corte salen de la edición; no se escriben |

### 3. Escenas de la primera versión
| Escena | Territorio permitido | Modos | Parámetros | Codificación | Agregado en celular |
|---|---|---|---|---|---|
| `ciudad_de_luz` | cualquiera | `unico` | — | color: macrosector | AGEB |
| `corredores_metro` | linea: `linea_metro` · ranking: `ciudad` o `linea_metro` · ambos: `estacion_metro` (enfoca la estación dentro de su línea) | `linea` (pred.), `ranking` | `radio_m` ∈ {300, 500, 800} (pred. 500) | color: macrosector · tamaño: establecimientos por estación | estación |
| `ciudades_dentro` | exterior: `ciudad`, `alcaldia` o `conglomerado` · interior: solo `conglomerado` | `exterior` (pred.), `interior` | `tipo_conglomerado` (lista; pred. todos) | color: macrosector · tamaño ∈ establecimientos (pred.), establecimientos_seleccion, locales_declarados | conglomerado |

En `corredores_metro` la selección solo atenúa puntos: sus medidas no cambian con el giro y la escena no ofrece `establecimientos_seleccion`.

La columna "Agregado en celular" sustituye el nivel 4 de la síntesis: es un dato del catálogo para el motor, no una validación.

### 4. Coherencia (nivel 3)
| Código | Regla |
|---|---|
| `territorio_no_admitido` | El tipo de territorio no está entre los permitidos de la escena y el modo (§3) |
| `radio_no_admitido` | `radio_m` en un tipo de territorio que no lo admite, o en cualquier territorio dentro de `corredores_metro` |
| `estacion_fuera_de_linea` | Comparación entre una estación y una línea que no pasa por ella |
| `recorrido_no_admitido` | El recorrido no corresponde a la escena y el modo (tabla de recorridos de la síntesis) |
| `recorrido_fijo_fuera_de_historia` | `el_despertar` con `contexto.origen` distinto de historia |
| `scian_mezcla_niveles_redundantes` | Un código contiene a otro de la lista (31 y 311) |
| `cifra_no_disponible` | Un hueco o cifra nombra una medida que la vista exacta de este estado no tiene |
| `hueco_sin_declarar` | El texto usa `{x}` y `x` no es una cifra declarada en la narrativa |
| `comparacion_misma` | Se compara un territorio o una selección consigo misma |

### 5. Narrativa y cifras vinculadas
Responde la pregunta abierta del intent.
```yaml
narrativa:
  titulo: "Los mercados de {territorio} con más locales de comida"
  texto: "{lider} concentra {principal} establecimientos de preparación de alimentos."
  principal: {medida: establecimientos_seleccion, fila: primera, formato: entero}
  secundarias:
    - {nombre: lider, medida: nombre, fila: primera}
  nota_cautela: "El DENUE registra cada local como establecimiento; un puesto sin registro no aparece."
```
- Un hueco es `{nombre}`: `principal`, el `nombre` de una secundaria, o los reservados `territorio`, `fecha_corte` y `edicion` (los llena el motor).
- `medida` debe existir en la vista exacta del estado. `fila` ∈ primera, ultima, total o `{clave: ...}`. `formato` ∈ entero, porcentaje, decimal1, texto.
- **Sin dígitos fuera de los huecos.** "Línea 12" entra por `{territorio}`. Es una regla mecánica que atrapa "1,200 negocios", pero no "mil doscientos negocios". Lo demás lo cubre el banco del Analista (H11).

### 6. Vista exacta derivada
| Escena · modo | Tabla `semantic` | Tipo de resultado | Medidas |
|---|---|---|---|
| ciudad_de_luz | `resumen_territorio` / `perfil_sector` si el territorio es ciudad, alcaldía o colonia; conteo sobre `establecimiento` para estación, línea, conglomerado o calle | territorial | establecimientos, macrosector, participacion |
| corredores_metro · linea | `metro_linea`, `metro_recorrido` | serie | establecimientos, estaciones, estacion, giro_dominante |
| corredores_metro · ranking | `metro_estacion` | ranking | establecimientos, lugar (solo con territorio `ciudad`; dentro de una línea el orden se recalcula), estacion, giro_dominante |
| ciudades_dentro · exterior | `conglomerado` (+ `establecimiento` si hay selección) | ranking | establecimientos, establecimientos_seleccion, locales_declarados, nombre, tipo |
| ciudades_dentro · interior | `establecimiento` del conglomerado | perfil | establecimientos por subsector, nombre |

H09 entrega la descripción declarativa (tabla, filtros y medidas). Ejecutar la consulta y congelar resultados es trabajo de H13 y H14.

### 7. Formato de historia
```yaml
slug: vida-comercial-del-metro
titulo: Vida comercial del Metro
exploracion: bloqueada        # o libre; se puede cambiar por panel
paneles:
  - estado: {...}             # el primero es completo
  - estado: {territorio: {tipo: linea_metro, clave: "L2"}}   # los demás, parciales
    exploracion: libre
```

### 8. Archivos
```
backend/
  pyproject.toml              # uv; pydantic>=2.9, pyyaml, psycopg (solo el exportador)
  contracts/
    escena.py                 # modelos (R1–R4)
    catalogo.py               # valores por escena, predeterminados, recorridos, medidas
    herencia.py · canonico.py · validar.py · vista_exacta.py · migraciones.py
    referencias.py            # carga y consulta del archivo de referencias
    exportar_referencias.py   # semantic -> referencias/<edicion>.json
    generar.py                # escribe escena.v1.json y dispara la generación TS
    escena.v1.json            # GENERADO
    referencias/2026-05.json  # GENERADO desde la base, versionado
    casos/                    # banco compartido: estado, contexto, veredicto, nivel, codigo
  tests/contracts/            # pytest
  contracts-ts/
    package.json              # ajv, ajv-formats, json-schema-to-typescript
    escena.v1.d.ts            # GENERADO
    validar-estructura.js     # GENERADO (Ajv standalone)
    referencias.ts · canonico.ts
    test/                     # node --test sobre el mismo banco
contenido/historias/          # historias YAML (en H09, una de ejemplo)
.github/workflows/verificar.yml
```

### 9. Comandos
- `make contratos`: pytest, pruebas de Node, `validar-historias` y control de que lo generado está al día (regenera y `git diff --exit-code`).
- `make ci` = `check` (con variables de entorno de mentira para `dbt parse`) + `contratos`. Es lo que corre GitHub Actions.
- `make verify` = `ci` + túnel + `dbt test`.
- `make referencias`: vuelve a exportar el catálogo desde la base (solo lectura; requiere el túnel).

## Encaje en el código existente
- Patrones que se siguen: proyecto Python con `uv` y `pyproject.toml` como `pipeline/` (Python 3.12–3.13). La conexión, como en `prototipos/03-resolver-lugar` y el pipeline: variables del `.env`.
- `exportar_referencias.py` lee como `pulso_analista`, la misma superficie que el Analista. Si algo no está en `semantic`, el contrato no lo puede referenciar, y eso es intencional.
- Claves: las de `semantic.lugar.clave` (por ejemplo, `estacion_norm` para estaciones y `cve_municipio:calle_norm` para calles), más `metro_linea.cve_linea`. El prototipo 3 ya devuelve estas claves, así que su salida entra directo al territorio.
- `Makefile` y `CLAUDE.md` ganan `contratos`, `ci` y `referencias`.
- No se toca dbt, el pipeline ni los prototipos.

## Políticas aplicadas
- CLAUDE.md: todo en español (modelos, campos, códigos de error y mensajes); secretos solo en `.env`; las cifras salen de `semantic`; `make verify` antes de dar algo por terminado.
- Decisiones del intent: tres escenas, CI público, tipos TS y Ajv, referencias en archivo, sin nivel 4, selección solo SCIAN, territorio solo por referencia y exploración en la historia.
- Principios de la síntesis: R3 y la gramática de huecos hacen imposible escribir cifras, coordenadas o colores, no solo desaconsejarlo.

## Áreas de preocupación
- ⚠️ **Repositorio público.** Es una acción hacia fuera que no se deshace del todo: GitHub y los cachés conservan copias.
  - El escaneo del 2026-11-08 no encontró secretos, la IP del VPS ni datos de otras bases. Antes del `push` se revisa el historial completo con gitleaks.
  - El remoto se crea solo con tu "adelante" en ese momento.
- ⚠️ **Licencias de los datos publicados.**
  - El archivo de referencias incluye nombres de calles y estaciones de OpenStreetMap (ODbL, exige atribución y compartir igual) y datos de INEGI (Términos de Libre Uso).
  - Propuesta: `referencias/LICENCIA.md` con ambas atribuciones. Licencia del código: MIT (decidido el 2026-11-14).
- ⚠️ **`semantic.lugar` no tiene edición.** El catálogo de lugares es uno solo, no uno por edición, así que el nivel 2 no sabe si un conglomerado o una calle existía en 2024-11.
  - Propuesta: v1 valida referencias solo contra la edición vigente y los paneles de ediciones anteriores confían en sus resultados congelados (H14).
  - Si hace falta más, H07 puede añadir `edicion` a `lugar`.
- ⚠️ **El radio de resolver lugar es continuo y el del contrato es cerrado.** El prototipo 3 produce radios de 100 a 3 000 m ("a 10 minutos" = 800 m); el contrato admite {300, 500, 800}.
  - Propuesta: la herramienta "construir escena" redondea al valor permitido más cercano y lo dice en la nota. Los radios mayores quedan fuera de v1.
- ⚠️ **Se aparta de la síntesis en cuatro puntos**, que habría que reflejar allí al cerrar H09:
  - la identidad sale del estado (§1);
  - el nivel 4 se vuelve un dato del catálogo (§3);
  - el ranking de Corredores admite toda la ciudad, no solo una línea (para la historia de H12);
  - el parámetro "línea" de Corredores se vuelve territorio, para no tener dos fuentes de la línea.
- ⚠️ **Organización jurídica**, que la síntesis pone en la selección, no está en `semantic.establecimiento`: el DENUE la trae, pero no se cargó a `semantic`. Queda fuera de v1 y entra como cambio compatible si se agrega.
- ⚠️ **AGEB, manzana y establecimiento como territorio** quedan fuera de v1: ninguna escena v1 los necesita, y el catálogo crecería de unos 0.6 MB a más de 10 MB. El clic del explorador que se ajusta a una manzana llega cuando exista el explorador.
- ⚠️ **Paridad de la forma canónica entre Python y JS.** La URL `#s=` del explorador se arma en el navegador y el id en el backend; si difieren en un byte, el mismo panel tiene dos ids.
  - Riesgos conocidos: el orden de claves con acentos, la forma de los números y la normalización Unicode.
  - Se mitiga con el banco de bytes esperados (R9) y una regla: el estado no contiene números de punto flotante.
- ⚠️ **Cambiar de escena puede romper la narrativa heredada:** sus medidas pueden no existir en la escena nueva. La regla de la síntesis la hereda y se encuentra con `cifra_no_disponible`, así que el Analista tendrá que reescribirla. Es el comportamiento correcto, pero conviene saberlo para H19.
- ✅ **Supuesto verificado el 2026-11-14** con un esquema mínimo (pydantic 2, ajv 8, json-schema-to-typescript 15): la cadena funciona, con un ajuste.
  - Pydantic escribe `discriminator.mapping`, y Ajv lo rechaza ("mapping is not supported"). `generar.py` debe quitar `mapping` y añadir `type: object` junto al discriminador antes de escribir `escena.v1.json`. Con eso Ajv compila en modo estricto.
  - Con el discriminador, el error apunta al campo exacto (`/escena/radio_m`). Sin él, cada error llega multiplicado por las tres escenas. Se usa el discriminador.
  - Rechazó los cuatro casos de prueba: radio de 400 m, coordenada en el territorio, campo de otra escena y tipo de escena inexistente.
  - Los tipos TS salen como unión correcta (`CiudadDeLuz | Corredores | CiudadesDentro`), pero con nombres de alias numerados (`Tipo1`, `Modo2`). Se corrige poniendo `title` a cada campo de tipo y modo.
  - El validador precompilado pesa unos 21 KB para el esquema mínimo.

**Decisiones de la revisión contra `semantic` (2026-11-14)**
- **Un solo radio.** En `corredores_metro` vale el parámetro de la escena y `territorio.radio_m` se rechaza. En las otras dos escenas el radio vive en el territorio (§2, §4).
- **Selección en Corredores.** `metro_estacion` y `metro_linea` están agregadas sin giro, así que en v1 la selección solo atenúa puntos (§3). Si después se quiere la cifra por giro, hace falta una tabla establecimiento × estación × radio en `semantic`, que entra como cambio compatible.
- **Sin radio alrededor de una calle.** El punto de una calle en `lugar` es el promedio de sus establecimientos y el círculo caería a media avenida (§2).
- **Ciudad de luz fuera de ciudad, alcaldía y colonia** cuenta sobre `establecimiento` (§6).
- **`metro_estacion.lugar`** es el puesto en toda la ciudad; dentro de una línea el orden se recalcula (§6).

## Preguntas del intent
- Narrativa con huecos → respondida en §5: `{nombre}`, cifras con `medida`, `fila` y `formato` que deben existir en la vista exacta.

## Fuera de alcance
Lo mismo que el intent, más:
- La ejecución de la vista exacta y los resultados congelados (H13 y H14).
- Las referencias de ediciones anteriores.
- Las escenas de la segunda versión.
- Territorios AGEB, manzana y establecimiento.
- Organización jurídica en la selección.
- Formato y validación de los recorridos (H18): aquí solo se listan sus nombres.

# Ideas por profundizar

Lista viva. Cada idea tiene lo que ya se sabe, las preguntas abiertas y qué haría falta para trabajarla. Las ideas nuevas se agregan al final con el mismo formato.

| # | Idea | Estado | Fecha |
|---|---|---|---|
| 1 | DENUE contra Censo Económico | Datos cargados, primer análisis hecho | 2026-11-07 |

---

## 1. DENUE contra Censo Económico

**Qué es.** Usar los Censos Económicos 2024 como vara de medir del DENUE: dónde se parecen, dónde no, y qué enseña eso sobre la calidad del directorio. Después, usar el Censo para dar más sentido económico a lo que el portal muestra.

### Lo que ya se sabe

- El Censo cuenta **425 005** establecimientos en CDMX (año de referencia 2023). El DENUE, en los mismos sectores, cuenta entre 454 690 y 472 280 según la edición.
- **Razón DENUE / Censo por edición:** 1,110 (05/2024), 1,069 (11/2024), 1,075 (05/2025), 1,080 (05/2026).
- **El DENUE 11/2024 se acerca al Censo.** La razón baja de 1,11 a 1,07 justo cuando el DENUE incorporó el Censo. Es la primera evidencia numérica de que el salto de altas y bajas entre 05/2024 y 11/2024 fue una corrección de fuente.
- **Por alcaldía la razón es muy pareja** (1,06 a 1,11 en la edición vigente). No hay un sesgo geográfico visible.
- **Por sector hay diferencias grandes.** Con 2026-05:

| Sector | Razón | Lectura |
|---|---|---|
| Comercio al por menor (46) | 1,03 | El DENUE es confiable |
| Manufacturas (31-33), alimentos (72) | 1,04 a 1,05 | Confiable |
| Servicios de salud (62) | 1,13 | Probable efecto de instituciones públicas |
| Educación (61) | 2,04 | El Censo cubre solo sector privado y paraestatal; las escuelas públicas sobran en el DENUE |
| Transporte (48-49) | 1,98 | Misma hipótesis |
| Energía y agua (22) | 5,74 | Sin explicación todavía |
| Servicios financieros (52) | 2,39 (en 2024 llegaba a 6,9) | Algo cambió entre ediciones |

- El sector 93 (gobierno, 3 450 establecimientos) no está en el Censo.

### Qué ya está construido

- Datos del Censo en `raw`, `staging` y `core` (`fact_censo_economico`, `dim_ce_variable`).
- Modelo `core.validacion_denue_censo`: DENUE contra Censo por edición × alcaldía × sector.
- Prueba de aviso `denue_cercano_al_censo`: avisa si el total por alcaldía se aleja de -10 % / +25 %.
- Equivalencia entre los estratos del DENUE (7) y del Censo (4) en `dim_estrato`.
- Documentación en [Core — Documentación del modelo de datos](Core%20—%20Documentación%20del%20modelo%20de%20datos.md).

### Ideas para profundizar

1. **Aviso de calidad en el Analista.** Si alguien pregunta por educación o por energía, el Analista debe saber que el DENUE las sobrerregistra y decirlo. Podría salir de `validacion_denue_censo`.
2. **Pesar la escena por actividad económica y no solo por conteo.** Hoy "Ciudad de luz" ilumina por número de negocios. Con valor agregado por alcaldía y sector, una fonda y un corporativo dejarían de pesar igual.
3. **Valor económico por colonia (estimado).** El Censo solo llega a alcaldía. Se puede repartir el valor agregado de cada alcaldía × sector entre sus establecimientos del DENUE, ponderando por estrato. Es una estimación y habría que etiquetarla como tal.
4. **Personal ocupado real.** `dim_estrato` usa un punto medio por rango y ninguno para "251 y más". El Censo da personal ocupado por alcaldía × sector × estrato para calibrarlo.
5. **Productividad territorial.** Valor agregado por persona ocupada, por sector y alcaldía. Daría una escena o un modo nuevo: dónde se genera valor y dónde solo hay volumen.
6. **Perfil de género.** El Censo desglosa personal ocupado y remunerado por sexo. Historia posible: dónde trabajan más mujeres, por sector.
7. **Digitalización.** Variables de tecnologías de la información. Se cruza con la clase de comercio por internet que el SCIAN 2023 reparte en 84 clases.
8. **Censo 2019 contra 2024.** Antes y después de la pandemia con la misma metodología. Daría profundidad histórica que el DENUE (desde 05/2024) no tiene. INEGI tiene un archivo de CDMX de 2019 (`ce2019_cdmx_csv.zip`, comprobado que responde); falta bajarlo y revisarlo.
9. **Índice de subregistro por sector.** La razón por sector, cruzada con el estrato, dice en qué tamaño de negocio el DENUE falla más.

### Preguntas abiertas

- ¿Por qué energía y agua (22) tiene 5,7 veces más en el DENUE? ¿Son instalaciones de CFE o de SACMEX que el Censo no cuenta como establecimientos?
- ¿Qué pasó con servicios financieros (52) entre 2025-05 y 2026-05? Pasó de unos 11 000 a unos 4 000 establecimientos en toda CDMX.
- ¿Cuánto del 8 % de diferencia total es sector público, y cuánto es sobrerregistro real? Se podría estimar si el DENUE permitiera separar lo público.
- El Censo es del año 2023 y el DENUE es de 2024 a 2026. ¿Cuánto de la diferencia es crecimiento y cuánto es cobertura?
- ¿Los datos de resultado (valor agregado, ingresos) son suficientemente completos a nivel alcaldía × sector, o la confidencialidad deja muchas celdas vacías?

### Qué haría falta

- Revisar la confidencialidad: contar cuántas celdas con cifras económicas quedan vacías por nivel de actividad.
- Para la idea 8: descargar el Censo 2019 de CDMX y la tabla de correspondencia SCIAN 2013 ↔ 2018.
- Para las ideas 2 a 5: decidir la regla de reparto y cómo etiquetar los valores estimados en el portal.

### Límites conocidos

- El Censo no publica datos por establecimiento ni por AGEB o manzana en datos abiertos. Todo cruce es por alcaldía × actividad × estrato.
- No cubre comercio ambulante.
- Se publica cada cinco años.
- Usa SCIAN 2023; el DENUE usa SCIAN 2018. Para cruzar a nivel de clase hay que pasar por `scian_correspondencia`.
- Sumar el archivo sin filtrar triplica los números: cada fila repite los mismos establecimientos por nivel de actividad y de estrato.

---

## Plantilla para ideas nuevas

```
## N. Título

**Qué es.**
### Lo que ya se sabe
### Ideas para profundizar
### Preguntas abiertas
### Qué haría falta
### Límites conocidos
```

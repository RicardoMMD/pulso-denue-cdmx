# Herramienta completa: banco de ciego

Corrido el 2026-11-15 · 90 casos (66 giros, 24 que no lo son) · glosario, lugar, gemma (palabras) y claude-haiku-5-5 · generado por `evaluar_herramienta.py`, no se edita a mano.

Acierto: la herramienta devuelve al menos una clase aceptable. Limpio: además, todas las que devuelve lo son.

| Medida | Resultado | Criterio | Cumple |
|---|---|---|---|
| Acierto en giros | 91 % | C1: al menos 85 % | sí |
| Acierto por tipo | palabra de la calle 83 % de 29, descripción libre 96 % de 25, con error de dedo 100 % de 12 | C2: al menos 70 % en cada tipo | sí |
| Rechazo de lo que no es giro | 100 %, con 3 % de giros perdidos | C3: al menos 80 %, perdiendo máximo 5 % | sí |
| Respuestas limpias | 73 % | se reporta, no decide | |

## Qué resolvió cada capa

| Capa | Casos | Aciertos |
|---|---|---|
| glosario | 12 | 11 |
| lugar | 6 | 6 |
| modelo | 72 | 67 |

## Fallos

- «talachería» (calle, capa modelo): estado `sin_resultado`, devolvió nada
- «pastelería» (calle, capa glosario): estado `resuelto`, devolvió Comercio al por menor de artículos de papelería
- «maquinitas» (calle, capa modelo): estado `sin_resultado`, devolvió nada
- «materias primas» (calle, capa modelo): estado `resuelto`, devolvió Comercio al por mayor de otras materias primas para otras industrias
- «ropa de paca» (calle, capa modelo): estado `resuelto`, devolvió Comercio al por menor de ropa, excepto de bebé y lencería
- «donde componen bicicletas» (descripcion, capa modelo): estado `resuelto`, devolvió Fabricación de bicicletas y triciclos

# Herramienta completa: banco de ajuste

Corrido el 2026-11-15 · 262 casos (206 giros, 56 que no lo son) · glosario, lugar, gemma (palabras) y claude-haiku-5-5 · generado por `evaluar_herramienta.py`, no se edita a mano.

Acierto: la herramienta devuelve al menos una clase aceptable. Limpio: además, todas las que devuelve lo son.

| Medida | Resultado | Criterio | Cumple |
|---|---|---|---|
| Acierto en giros | 99 % | C1: al menos 85 % | sí |
| Acierto por tipo | palabra de la calle 100 % de 99, descripción libre 99 % de 70, con error de dedo 95 % de 37 | C2: al menos 70 % en cada tipo | sí |
| Rechazo de lo que no es giro | 98 %, con 0 % de giros perdidos | C3: al menos 80 %, perdiendo máximo 5 % | sí |
| Respuestas limpias | 91 % | se reporta, no decide | |

## Qué resolvió cada capa

| Capa | Casos | Aciertos |
|---|---|---|
| glosario | 134 | 134 |
| lugar | 12 | 12 |
| modelo | 116 | 112 |

## Fallos

- «donde venden refrescos y botanas» (descripcion, capa modelo): estado `grupo`, devolvió Comercio al por menor de bebidas no alcohólicas y hielo, Comercio al por menor de otros alimentos
- «fonsa» (error_dedo, capa modelo): estado `no_es_giro`, devolvió nada
- «talller mecanico» (error_dedo, capa modelo): estado `resuelto`, devolvió Reparación y mantenimiento de maquinaria y equipo agropecuario y forestal
- «Bosque de Chapultepec» (no_es_giro, capa modelo): estado `resuelto`, devolvió Parques de diversiones y temáticos del sector público

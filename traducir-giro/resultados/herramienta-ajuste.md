# Herramienta completa: banco de ajuste

Corrido el 2026-11-15 · 352 casos (272 giros, 80 que no lo son) · glosario, lugar, gemma (palabras) y claude-haiku-5-5 · generado por `evaluar_herramienta.py`, no se edita a mano.

Acierto: la herramienta devuelve al menos una clase aceptable. Limpio: además, todas las que devuelve lo son.

| Medida | Resultado | Criterio | Cumple |
|---|---|---|---|
| Acierto en giros | 99 % | C1: al menos 85 % | sí |
| Acierto por tipo | palabra de la calle 100 % de 128, descripción libre 98 % de 95, con error de dedo 96 % de 49 | C2: al menos 70 % en cada tipo | sí |
| Rechazo de lo que no es giro | 96 %, con 1 % de giros perdidos | C3: al menos 80 %, perdiendo máximo 5 % | sí |
| Respuestas limpias | 92 % | se reporta, no decide | |

## Qué resolvió cada capa

| Capa | Casos | Aciertos |
|---|---|---|
| glosario | 169 | 169 |
| lugar | 18 | 18 |
| modelo | 165 | 158 |

## Fallos

- «donde venden refrescos y botanas» (descripcion, capa modelo): estado `grupo`, devolvió Comercio al por menor de bebidas no alcohólicas y hielo, Comercio al por menor de otros alimentos
- «fonsa» (error_dedo, capa modelo): estado `sin_resultado`, devolvió nada
- «talller mecanico» (error_dedo, capa modelo): estado `resuelto`, devolvió Reparación y mantenimiento de maquinaria y equipo agropecuario y forestal
- «cerca del metro» (no_es_giro, capa modelo): estado `ambiguo`, devolvió Transporte colectivo urbano y suburbano de pasajeros en metro, Transporte colectivo urbano y suburbano de pasajeros en autobuses que transitan en carril exclusivo, Transporte colectivo urbano y suburbano de pasajeros en trolebuses y trenes ligeros
- «a dos cuadras del metro» (no_es_giro, capa modelo): estado `ambiguo`, devolvió Transporte colectivo urbano y suburbano de pasajeros en metro, Transporte colectivo urbano y suburbano de pasajeros en trolebuses y trenes ligeros, Transporte colectivo urbano y suburbano de pasajeros en autobuses que transitan en carril exclusivo
- «Bosque de Chapultepec» (no_es_giro, capa modelo): estado `resuelto`, devolvió Parques de diversiones y temáticos del sector público
- «donde me hacen un tatuaje» (descripcion, capa modelo): estado `sin_resultado`, devolvió nada

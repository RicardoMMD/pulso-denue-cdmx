# Resultado del banco de pruebas del resolutor de lugares

**66 de 66 casos correctos (100 %).** Tiempo por consulta: mediana 204 ms, máximo 941 ms.

| # | Consulta | Esperado | Obtenido | |
| --- | --- | --- | --- | --- |
| 1 | Iztapalapa | resuelto · alcaldia | resuelto · Iztapalapa | ✓ |
| 2 | la alcaldía Cuauhtémoc | resuelto · alcaldia | resuelto · Cuauhtémoc | ✓ |
| 3 | Delegación Coyoacán | resuelto · alcaldia | resuelto · Coyoacán | ✓ |
| 4 | GAM | resuelto · alcaldia | resuelto · Gustavo A. Madero | ✓ |
| 5 | Gustavo A. Madero | resuelto · alcaldia | resuelto · Gustavo A. Madero | ✓ |
| 6 | Magdalena Contreras | resuelto · alcaldia | resuelto · La Magdalena Contreras | ✓ |
| 7 | Benito Juárez | resuelto · alcaldia | resuelto · Benito Juárez | ✓ |
| 8 | Iztapalpa | resuelto · alcaldia | resuelto · Iztapalapa | ✓ |
| 9 | Alvaro Obregon | resuelto · alcaldia | resuelto · Álvaro Obregón | ✓ |
| 10 | Xochimilco | resuelto · alcaldia | resuelto · Xochimilco | ✓ |
| 11 | Cuahutemoc | ambiguo · alcaldia | ambiguo · Cuauhtémoc, Avenida Cuahutémoc, Calle Cuahutémoc… | ✓ |
| 12 | en Tlalpan | resuelto · alcaldia | resuelto · Tlalpan | ✓ |
| 13 | CDMX | resuelto · ciudad | resuelto · Ciudad de México | ✓ |
| 14 | toda la ciudad | resuelto · ciudad | resuelto · Ciudad de México | ✓ |
| 15 | el DF | resuelto · ciudad | resuelto · Ciudad de México | ✓ |
| 16 | la Roma | grupo · colonia | grupo · Roma Norte, Roma Sur | ✓ |
| 17 | Roma Norte | resuelto · colonia | resuelto · Roma Norte | ✓ |
| 18 | la Condesa | grupo · colonia | grupo · Condesa, Hipodromo Condesa, Hipodromo | ✓ |
| 19 | Polanco | grupo · colonia | grupo · Polanco I Seccion, Polanco Ii Seccion, Polanco Iii Seccion… | ✓ |
| 20 | la Del Valle | grupo · colonia | grupo · Del Valle Norte, Del Valle Centro, Del Valle Sur | ✓ |
| 21 | la Narvarte | grupo · colonia | grupo · Narvarte Oriente, Narvarte Poniente, Vertiz Narvarte… | ✓ |
| 22 | Santa Fe | grupo · colonia | grupo · Santa Fe, Santa Fe Centro Ciudad, Santa Fe Cuajimalpa… | ✓ |
| 23 | el Centro | resuelto · colonia | resuelto · Centro | ✓ |
| 24 | Centro Histórico | resuelto · colonia | resuelto · Centro | ✓ |
| 25 | Tepito | resuelto · colonia | resuelto · Morelos | ✓ |
| 26 | CU | resuelto · colonia | resuelto · Ciudad Universitaria | ✓ |
| 27 | la Doctores | resuelto · colonia | resuelto · Doctores | ✓ |
| 28 | la Juárez | resuelto · colonia | resuelto · Juarez | ✓ |
| 29 | colonia Narvarte Poniente | resuelto · colonia | resuelto · Narvarte Poniente | ✓ |
| 30 | Santa María la Ribera | resuelto · colonia | resuelto · Santa Maria La Ribera | ✓ |
| 31 | El Rosario | ambiguo · colonia | ambiguo · El Rosario, El Rosario, El Rosario… | ✓ |
| 32 | Morelos | ambiguo · colonia | ambiguo · Morelos, Morelos | ✓ |
| 33 | las Portales | grupo · colonia | grupo · Portales Norte, Portales Sur, Portales Oriente | ✓ |
| 34 | Escandón | grupo · colonia | grupo · Escandon Ii Seccion, Escandon I Seccion | ✓ |
| 35 | Lindavista | grupo · colonia | grupo · Lindavista Norte, Lindavista Sur, Lindavista Vallejo 2a Seccion… | ✓ |
| 36 | metro Balderas | resuelto · estacion_metro | resuelto · Balderas | ✓ |
| 37 | estación Pino Suárez | resuelto · estacion_metro | resuelto · Pino Suárez | ✓ |
| 38 | metro Polanco | resuelto · estacion_metro | resuelto · Polanco | ✓ |
| 39 | metro Tepito | resuelto · estacion_metro | resuelto · Tepito | ✓ |
| 40 | metro Zócalo | resuelto · estacion_metro | resuelto · Zócalo/Tenochtitlan | ✓ |
| 41 | estación Tacubaya | resuelto · estacion_metro | resuelto · Tacubaya | ✓ |
| 42 | metro Cuatro Caminos | resuelto · estacion_metro | resuelto · Cuatro Caminos | ✓ |
| 43 | cerca del metro Balderas | resuelto · estacion_metro | resuelto · Balderas | ✓ |
| 44 | a 5 minutos del metro Insurgentes | resuelto · estacion_metro | resuelto · Insurgentes | ✓ |
| 45 | a 300 metros del metro Hidalgo | resuelto · estacion_metro | resuelto · Hidalgo | ✓ |
| 46 | alrededor del Zócalo | resuelto · estacion_metro | resuelto · Zócalo/Tenochtitlan | ✓ |
| 47 | junto al metro Copilco | resuelto · estacion_metro | resuelto · Copilco | ✓ |
| 48 | a 10 minutos del Zócalo | resuelto · estacion_metro | resuelto · Zócalo/Tenochtitlan | ✓ |
| 49 | a 1 km de metro Pantitlán | resuelto · estacion_metro | resuelto · Pantitlán | ✓ |
| 50 | línea 7 del metro | resuelto · linea_metro | resuelto · Línea 7 | ✓ |
| 51 | metro línea B | resuelto · linea_metro | resuelto · Línea B | ✓ |
| 52 | mercado de Sonora | resuelto · conglomerado | resuelto · Mercado Sonora | ✓ |
| 53 | la Merced | resuelto · conglomerado | resuelto · MERCED NAVE MAYOR | ✓ |
| 54 | Central de Abasto | resuelto · colonia | resuelto · Central De Abasto | ✓ |
| 55 | mercado de Jamaica | grupo · conglomerado | grupo · Mercado Jamaica Vive, Mercado Jamaica Zona, Mercado De Comidas Jamaica | ✓ |
| 56 | avenida Insurgentes Sur | resuelto · calle | resuelto · Avenida Insurgentes Sur | ✓ |
| 57 | Paseo de la Reforma | resuelto · calle | resuelto · Avenida Paseo de la Reforma | ✓ |
| 58 | Insurgentes Sur | ambiguo · calle | ambiguo · Insurgentes Sur, Insurgentes Sur, Avenida Insurgentes Sur | ✓ |
| 59 | Balderas | ambiguo · estacion_metro | ambiguo · Balderas, Balderas, Avenida Balderas | ✓ |
| 60 | Naucalpan | fuera_de_cdmx | fuera_de_cdmx · — | ✓ |
| 61 | cerca de Ecatepec | fuera_de_cdmx | fuera_de_cdmx · — | ✓ |
| 62 | Toluca | fuera_de_cdmx | fuera_de_cdmx · — | ✓ |
| 63 | Narnia | sin_resultado | sin_resultado · — | ✓ |
| 64 | asdf | sin_resultado | sin_resultado · — | ✓ |
| 65 | cerca de mi casa | sin_resultado | sin_resultado · — | ✓ |
| 66 | (vacía) | sin_resultado | sin_resultado · — | ✓ |

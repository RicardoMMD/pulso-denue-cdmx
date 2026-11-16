# Laboratorio visual

Página para **ver** las propuestas de diseño aplicadas a la ciudad de luz, en lugar de leerlas en texto. Compara paletas, tratamientos de brillo y mapeo de tonos lado a lado, con la misma cámara y los mismos datos.

## Uso
```
cd laboratorio
npm install        # solo la primera vez
npm run dev        # http://localhost:5173/
```
- Lee los tokens de `../diseno/generado/` y los datos (puntos y fondo) del paquete de `../prototipos/02-renderizador/public/datos/`. No escribe en la base.
- No mide rendimiento (fuera de alcance en la primera versión).

## Páginas
- `index.html` — brillo y paleta. Selector **Comparar**: `brillo` (sin brillo, posprocesado, halo) o `mapeos` (tres paneles con brillo, cada uno con su mapeo de tonos). Tomas fijas: Centro denso, Periferia, Ciudad completa.
- `tipografia.html` — títulos, texto de panel, cifra principal con dígitos de ancho fijo contando, tabla alineada y etiquetas 3D con troika, en tema oscuro y claro. Legible a 390 px.
- `giros.html` — traducir giro (H10). Dos vistas: **Herramienta completa** (por caso: estado, capa que resolvió, clases devueltas y candidatos) y **Embeddings lado a lado** (las cinco clases más cercanas de cada modelo). Filtros por tipo, capa, solo fallos y búsqueda. Lee `../traducir-giro/resultados/`; sin base ni llaves.

## Convención del proyecto
Todo hito o cambio que tenga algo que ver debe incluir un **repaso en el laboratorio**: qué abrir, qué comparar y qué decidir. Si el cambio es visual, se agrega o actualiza ahí la comparación. El laboratorio crece con el proyecto (H15 motor, H16 escenas, H17 vista exacta).

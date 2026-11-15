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

## Convención del proyecto
Todo hito o cambio que tenga algo que ver debe incluir un **repaso en el laboratorio**: qué abrir, qué comparar y qué decidir. Si el cambio es visual, se agrega o actualiza ahí la comparación. El laboratorio crece con el proyecto (H15 motor, H16 escenas, H17 vista exacta).

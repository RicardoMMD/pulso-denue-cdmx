import { defineConfig } from "vite";

// Laboratorio visual: página de comparación de propuestas. Lee los tokens de ../diseno y los datos
// (puntos y fondo) del paquete del prototipo 2, para no duplicarlos.
export default defineConfig({
  base: "./",
  publicDir: "../prototipos/02-renderizador/public",
  build: { target: "es2022" },
  server: { host: true, fs: { allow: [".."] } },
});

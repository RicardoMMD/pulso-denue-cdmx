import { defineConfig } from "vite";

// Laboratorio visual: página de comparación de propuestas. Lee los tokens de ../diseno y los datos
// (puntos y fondo) del paquete del prototipo 2, para no duplicarlos.
export default defineConfig({
  base: "./",
  publicDir: "../prototipos/02-renderizador/public",
  build: { target: "es2022", rollupOptions: { input: { index: "index.html", tipografia: "tipografia.html" } } },
  server: { host: true, fs: { allow: [".."].map((p) => new URL(p + "/", import.meta.url).pathname) } },
});

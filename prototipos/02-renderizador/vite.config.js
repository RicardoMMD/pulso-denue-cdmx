import { defineConfig } from "vite";
import { mkdirSync, writeFileSync } from "node:fs";

// Recibe el resultado del benchmark desde cualquier dispositivo de la red y lo guarda en resultados/.
const guardarBench = () => ({
  name: "guardar-bench",
  configureServer(server) {
    server.middlewares.use("/__bench", (req, res) => {
      if (req.method !== "POST") { res.statusCode = 405; return res.end(); }
      let cuerpo = "";
      req.on("data", (c) => { cuerpo += c; if (cuerpo.length > 20000) req.destroy(); });
      req.on("end", () => {
        try {
          const r = JSON.parse(cuerpo);
          mkdirSync("resultados", { recursive: true });
          const nombre = `resultados/bench-${new Date().toISOString().replace(/[:.]/g, "-")}.json`;
          writeFileSync(nombre, JSON.stringify(r, null, 2));
          res.end("ok");
        } catch { res.statusCode = 400; res.end("json invalido"); }
      });
    });
  },
});

export default defineConfig({ base: "./", build: { target: "es2022" }, server: { host: true }, plugins: [guardarBench()] });

// Repaso de traducir giro (H10): qué devolvió la herramienta completa en cada caso y qué candidatos propuso cada
// modelo de embeddings. Lee los JSON que escriben evaluar.py y evaluar_herramienta.py en traducir-giro/resultados/;
// no usa base ni llaves. Los colores salen de los tokens: acierto y fallo se marcan con ✓/✗ y peso, no con color.
import "../../diseno/generado/tokens.css";

const HERRAMIENTA = import.meta.glob("../../traducir-giro/resultados/herramienta/*.json", { eager: true, import: "default" });
const EMBEDDINGS = import.meta.glob("../../traducir-giro/resultados/{ajuste,ciego-1}/*.json", { eager: true, import: "default" });

const $ = (id) => document.getElementById(id);
const pct = (x) => (x == null ? "—" : Math.round(x * 100) + " %");
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const TIPO = { calle: "palabra de la calle", descripcion: "descripción libre", error_dedo: "con error de dedo", no_es_giro: "no es un giro" };
const NOMBRE_BANCO = { ajuste: "banco de ajuste", ciego: "banco ciego", "ciego-1": "primer banco ciego (ya usado)" };

// Corridas disponibles por vista.
const corridas = { herramienta: {}, embeddings: {} };
for (const d of Object.values(HERRAMIENTA)) corridas.herramienta[d.banco] = d;
for (const [ruta, d] of Object.entries(EMBEDDINGS)) {
  const banco = ruta.split("/").at(-2);
  const clave = `${banco} · texto ${d.variante}`;
  (corridas.embeddings[clave] ??= { banco, variante: d.variante, modelos: {} }).modelos[d.modelo] = d;
}

let vista = "herramienta";

function tarjeta(etiqueta, cifra, nota = "") {
  return `<div class="tarjeta"><div class="cifra">${cifra}</div><div class="tenue">${etiqueta}</div>${nota ? `<div class="tenue">${nota}</div>` : ""}</div>`;
}

function llenarCorridas() {
  const nombres = Object.keys(corridas[vista]).sort();
  $("corrida").innerHTML = nombres.map((n) => `<option value="${esc(n)}">${esc(vista === "herramienta" ? NOMBRE_BANCO[n] ?? n : n.replace(/^[^ ]+/, (b) => NOMBRE_BANCO[b] ?? b))}</option>`).join("");
  // Por omisión, lo más reciente y útil: el ciego si ya se corrió; en embeddings, el texto con palabras.
  const preferida = vista === "herramienta" ? (nombres.includes("ciego") ? "ciego" : "ajuste") : nombres.find((n) => n.startsWith("ajuste") && n.endsWith("palabras"));
  if (preferida) $("corrida").value = preferida;
  $("caja-capa").style.display = vista === "herramienta" ? "" : "none";
}

function pintarHerramienta(d) {
  const m = d.metricas, c = d.cumple;
  const si = (k) => (c[k] ? "✓ cumple" : "✗ no cumple");
  $("resumen").innerHTML =
    tarjeta("acierto en giros", pct(m.acierto), `C1 (85 %): ${si("C1")}`) +
    Object.entries(m.por_tipo).map(([t, v]) => tarjeta(TIPO[t], pct(v.acierto), `${v.casos} casos`)).join("") +
    tarjeta("rechazo de lo que no es giro", pct(m.rechazo_no_giro), `C3 (80 %): ${si("C3")}`) +
    tarjeta("giros perdidos", pct(m.giros_perdidos), "máximo 5 %") +
    tarjeta("respuestas limpias", pct(m.limpio), "todas las clases devueltas son aceptables");
  const capas = Object.entries(m.por_capa).map(([k, v]) => `${k}: ${v.aciertos} de ${v.casos}`).join(" · ");
  $("aviso").textContent = `${NOMBRE_BANCO[d.banco]} · ${m.casos} casos · corrido el ${d.corrido.slice(0, 10)} · aciertos por capa — ${capas}.` +
    (d.banco === "ajuste" ? " El glosario se sembró con este mismo banco: el número que cuenta es el del banco ciego." : "");

  const tipo = $("tipo").value, capa = $("capa").value, soloFallos = $("fallos").checked, q = $("buscar").value.trim().toLowerCase();
  const casos = d.casos.filter((f) => (!tipo || f.tipo === tipo) && (!capa || f.capa === capa) && (!soloFallos || !f.acierta) && (!q || f.termino.toLowerCase().includes(q)));
  $("cuenta").textContent = `${casos.length} de ${d.casos.length}`;
  $("casos").innerHTML = casos.map((f) => {
    const devueltas = f.clases.length
      ? `<ul>${f.clases.map((k) => `<li class="${f.esperadas.includes(k.clase) ? "si" : "no"}">${f.esperadas.includes(k.clase) ? "✓" : "✗"} ${k.clase} · ${esc(k.nombre)} <span class="n">${k.establecimientos} negocios</span></li>`).join("")}</ul>`
      : `<span class="tenue">ninguna clase</span>`;
    const candidatos = f.candidatos.length
      ? `<ol>${f.candidatos.map((k) => `<li class="${f.esperadas.includes(k.clase) ? "si" : "no"}">${k.clase} · ${esc(k.nombre)} <span class="n">${k.parecido.toFixed(2)}</span></li>`).join("")}</ol>`
      : `<span class="tenue">no hizo falta: se resolvió antes</span>`;
    return `<div class="caso">
      <div><div class="termino">${esc(f.termino)}</div><div class="tenue">${TIPO[f.tipo]}</div>
        <div><span class="marca">${f.acierta ? "✓ acierta" : "✗ falla"}</span> <span class="tenue">· ${f.estado} · capa ${f.capa} · confianza ${f.confianza}</span></div>
        <div class="tenue">espera: ${f.esperadas.join(", ") || "que no sea giro"}</div></div>
      <div class="columnas">
        <div><h3>Lo que devolvió</h3>${devueltas}<div class="tenue">${esc(f.nota)}</div></div>
        <div><h3>Candidatos de embeddings</h3>${candidatos}</div>
      </div></div>`;
  }).join("") || `<p class="tenue">Ningún caso con esos filtros.</p>`;
}

function pintarEmbeddings(d) {
  const modelos = Object.keys(d.modelos).sort();
  $("resumen").innerHTML = modelos.map((n) => {
    const m = d.modelos[n].metricas;
    return tarjeta(`${n} · entre los primeros 5`, pct(m.primeros_5), `rechazo ${pct(m.rechazo_no_giro)} · ${Math.round(m.ms_mediana)} ms · ${m.memoria_pico_gb.toFixed(2)} GB`);
  }).join("");
  const primero = d.modelos[modelos[0]];
  $("aviso").textContent = `${NOMBRE_BANCO[d.banco]} · texto «${d.variante}» · ${primero.metricas.casos} casos · corrido el ${primero.corrido.slice(0, 10)}. Cada modelo muestra sus cinco clases más cercanas; ✓ marca una clase aceptable.`;

  const tipo = $("tipo").value, soloFallos = $("fallos").checked, q = $("buscar").value.trim().toLowerCase();
  const falla = (f) => (f.tipo === "no_es_giro" ? !f.rechazado : !(f.posicion && f.posicion <= 5));
  const indices = primero.casos.map((_, i) => i).filter((i) => {
    const f = primero.casos[i];
    return (!tipo || f.tipo === tipo) && (!q || f.termino.toLowerCase().includes(q)) && (!soloFallos || modelos.some((n) => falla(d.modelos[n].casos[i])));
  });
  $("cuenta").textContent = `${indices.length} de ${primero.casos.length}`;
  $("casos").innerHTML = indices.map((i) => {
    const f0 = primero.casos[i];
    const columnas = modelos.map((n) => {
      const f = d.modelos[n].casos[i];
      const veredicto = f.tipo === "no_es_giro" ? (f.rechazado ? "✓ lo rechaza" : "✗ lo deja pasar") : falla(f) ? "✗ falla" : `✓ acierta en el lugar ${f.posicion}`;
      return `<div><h3>${n} · <span class="marca">${veredicto}</span></h3><ol>${f.candidatos.slice(0, 5).map((k) => `<li class="${k.acierta ? "si" : "no"}">${k.acierta ? "✓ " : ""}${esc(k.nombre)} <span class="n">${k.parecido.toFixed(2)}</span></li>`).join("")}</ol></div>`;
    }).join("");
    return `<div class="caso"><div><div class="termino">${esc(f0.termino)}</div><div class="tenue">${TIPO[f0.tipo]}</div><div class="tenue">espera: ${f0.clases.join(", ") || "que no sea giro"}</div></div><div class="columnas">${columnas}</div></div>`;
  }).join("") || `<p class="tenue">Ningún caso con esos filtros.</p>`;
}

function pintar() {
  const d = corridas[vista][$("corrida").value];
  if (!d) { $("resumen").innerHTML = ""; $("casos").innerHTML = `<p class="tenue">Todavía no hay resultados para esta vista.</p>`; return; }
  (vista === "herramienta" ? pintarHerramienta : pintarEmbeddings)(d);
}

for (const b of document.querySelectorAll("[data-vista]")) {
  b.onclick = () => {
    vista = b.dataset.vista;
    for (const o of document.querySelectorAll("[data-vista]")) o.setAttribute("aria-pressed", String(o === b));
    llenarCorridas(); pintar();
  };
}
for (const id of ["corrida", "tipo", "capa", "fallos"]) $(id).onchange = pintar;
$("buscar").oninput = pintar;
$("tema").onclick = () => {
  const claro = document.documentElement.dataset.tema !== "claro";
  document.documentElement.dataset.tema = claro ? "claro" : "oscuro";
  $("tema").textContent = "Tema: " + (claro ? "claro" : "oscuro"); $("tema").setAttribute("aria-pressed", String(claro));
};

llenarCorridas(); pintar();

// Catálogo público de Tienda María: solo productos y precios (sin costos, sin cantidades, sin usuarios, sin ventas).
const store = require("../lib/state-store");

function validProduct(value) {
  if (!value || typeof value !== "object" || Array.isArray(value)) return false;
  const id = value.id;
  return Number.isFinite(id) || (typeof id === "string" && id.length > 0 && id.length <= 80);
}

function color(value, fallback) {
  return typeof value === "string" && /^#(?:[0-9a-f]{3}|[0-9a-f]{6})$/i.test(value) ? value : fallback;
}

function image(value) {
  if (typeof value !== "string" || value.length > 200000 || /["'<>]/.test(value)) return "";
  return /^(?:https:\/\/|data:image\/(?:png|jpeg|webp|gif)[;,])/.test(value) ? value : "";
}

module.exports = async function handler(req, res) {
  res.setHeader("Cache-Control", "public, s-maxage=15, stale-while-revalidate=60");
  if (req.method !== "GET") return res.status(405).json({ error: "metodo" });
  const storage = store();
  if (!storage.ok()) return res.status(503).json({ error: "sin_configurar" });
  try {
    const state = await storage.read("");
    if (!state || !state.data) return res.status(200).json({ empty: true });
    const d = state.data;
    const items = (Array.isArray(d.items) ? d.items : []).filter(validProduct).map((x) => ({
      id: x.id,
      n: String(x.n || "").slice(0, 80),
      c: String(x.c || "").slice(0, 40),
      p: Number(x.p) || 0,
      m: x.m === "pack" || x.m === "mayor" ? x.m : "unit",
      mq: Number(x.mq) || 0,
      mp: Number(x.mp) || 0,
      ok: Number(x.stock) > 0,
      bg: color(x.bg, "#eee"),
      fg: color(x.fg, "#333"),
      img: image(x.img),
    }));
    const s = d.settings || {};
    return res.status(200).json({ store: String(s.store || "Tienda María"), wa: String(s.wa || ""), items });
  } catch (e) {
    return res.status(500).json({ error: "interno" });
  }
};

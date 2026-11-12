// Catálogo público de Tienda María: solo productos y precios (sin costos, sin cantidades, sin usuarios, sin ventas).
const { get } = require("@vercel/blob");

const PATH = "tienda-maria/estado.json";

module.exports = async function handler(req, res) {
  res.setHeader("Cache-Control", "public, s-maxage=15, stale-while-revalidate=60");
  if (req.method !== "GET") return res.status(405).json({ error: "metodo" });
  if (!process.env.BLOB_READ_WRITE_TOKEN) return res.status(503).json({ error: "sin_configurar" });
  try {
    const r = await get(PATH, { access: "private", useCache: false });
    if (!r || r.statusCode !== 200) return res.status(200).json({ empty: true });
    const d = JSON.parse(await new Response(r.stream).text());
    const items = (Array.isArray(d.items) ? d.items : []).map((x) => ({
      id: x.id,
      n: String(x.n || "").slice(0, 80),
      c: String(x.c || "").slice(0, 40),
      p: Number(x.p) || 0,
      m: x.m === "pack" || x.m === "mayor" ? x.m : "unit",
      mq: Number(x.mq) || 0,
      mp: Number(x.mp) || 0,
      ok: Number(x.stock) > 0,
      bg: x.bg || "#eee",
      fg: x.fg || "#333",
      img: typeof x.img === "string" && x.img.length <= 200000 ? x.img : "",
    }));
    const s = d.settings || {};
    return res.status(200).json({ store: String(s.store || "Tienda María"), wa: String(s.wa || ""), items });
  } catch (e) {
    return res.status(500).json({ error: "interno" });
  }
};

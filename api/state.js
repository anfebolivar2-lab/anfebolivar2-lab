// Sincronización de Tienda María: guarda toda la información de la tienda en un archivo privado (Vercel Blob)
// para que todos los celulares vean lo mismo.
// Variables de entorno: SYNC_CODE (código de la tienda) y BLOB_READ_WRITE_TOKEN (la pone Vercel al crear el almacenamiento).
const crypto = require("crypto");
const { get, put, BlobPreconditionFailedError } = require("@vercel/blob");

const PATH = "tienda-maria/estado.json";
const MAX_BYTES = 4000000;
const hits = new Map();

function norm(s) {
  return String(s || "").toUpperCase().replace(/[^A-Z0-9]/g, "");
}
function same(a, b) {
  const x = Buffer.from(norm(a));
  const y = Buffer.from(norm(b));
  return x.length > 0 && x.length === y.length && crypto.timingSafeEqual(x, y);
}
function limited(ip) {
  const now = Date.now();
  const w = (hits.get(ip) || []).filter((t) => now - t < 60000);
  w.push(now);
  hits.set(ip, w);
  if (hits.size > 500) hits.clear();
  return w.length > 240;
}
function parseBody(req) {
  if (req.body && typeof req.body === "object") return req.body;
  try {
    return JSON.parse(req.body || "{}");
  } catch (e) {
    return {};
  }
}
async function readCurrent(rev) {
  const r = await get(PATH, { access: "private", useCache: false, ifNoneMatch: rev || undefined });
  if (!r) return null;
  if (r.statusCode === 304) return { same: true, rev: r.blob.etag };
  const text = await new Response(r.stream).text();
  return { rev: r.blob.etag, data: JSON.parse(text) };
}
function valid(d) {
  return d && typeof d === "object" && Array.isArray(d.items) && Array.isArray(d.users) && Array.isArray(d.sales);
}

module.exports = async function handler(req, res) {
  res.setHeader("Cache-Control", "no-store");
  const code = process.env.SYNC_CODE;
  if (!code || !process.env.BLOB_READ_WRITE_TOKEN) return res.status(503).json({ error: "sin_configurar" });
  const ip = String((req.headers && req.headers["x-forwarded-for"]) || "").split(",")[0].trim() || "local";
  if (limited(ip)) return res.status(429).json({ error: "limite" });
  if (!same(req.headers["x-sync-code"], code)) return res.status(401).json({ error: "codigo" });

  try {
    if (req.method === "GET") {
      const rev = String((req.query && req.query.rev) || "");
      const cur = await readCurrent(rev);
      if (!cur) return res.status(200).json({ empty: true });
      if (cur.same) return res.status(200).json({ same: true, rev: cur.rev });
      return res.status(200).json(cur);
    }
    if (req.method === "PUT") {
      const body = parseBody(req);
      if (!valid(body.data)) return res.status(400).json({ error: "datos" });
      const text = JSON.stringify(body.data);
      if (Buffer.byteLength(text) > MAX_BYTES) return res.status(413).json({ error: "grande" });
      let base = String(body.rev || "");
      if (body.force) {
        const cur = await readCurrent("");
        base = cur ? cur.rev : "";
      }
      const opts = { access: "private", contentType: "application/json", addRandomSuffix: false, cacheControlMaxAge: 60, allowOverwrite: true };
      if (!base) {
        const cur = await readCurrent("");
        if (cur) return res.status(409).json({ conflict: true, rev: cur.rev, data: cur.data });
      }
      try {
        const out = base ? await put(PATH, text, { ...opts, ifMatch: base }) : await put(PATH, text, opts);
        return res.status(200).json({ ok: true, rev: out.etag });
      } catch (e) {
        if (e instanceof BlobPreconditionFailedError) {
          const cur = await readCurrent("");
          if (!cur) return res.status(409).json({ conflict: true, empty: true });
          return res.status(409).json({ conflict: true, rev: cur.rev, data: cur.data });
        }
        throw e;
      }
    }
    return res.status(405).json({ error: "metodo" });
  } catch (e) {
    return res.status(500).json({ error: "interno", detail: String((e && e.name) || "error") });
  }
};

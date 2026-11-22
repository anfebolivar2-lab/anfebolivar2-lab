// Sincronización de Tienda María: guarda toda la información de la tienda en un archivo privado (Vercel Blob)
// para que todos los celulares vean lo mismo.
// Variables de entorno: SYNC_CODE (código de la tienda) y UNO de estos dos almacenes:
//  - FIREBASE_SERVICE_ACCOUNT (JSON de la cuenta de servicio de Firebase) -> Firestore (si existe, se usa este)
//  - BLOB_READ_WRITE_TOKEN (la pone Vercel al crear el almacenamiento) -> Vercel Blob
const crypto = require("crypto");
const store = require("../lib/state-store");

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
const MAX_LIST_LENGTH = 20000;
const MAX_TEXT_LENGTH = 100000;
const MAX_IMAGE_LENGTH = 1000000;

function isObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function sizeError(value, path, field, depth = 0) {
  if (depth > 32) return path + " supera el límite de anidación.";
  if (typeof value === "string") {
    const limit = field === "img" ? MAX_IMAGE_LENGTH : MAX_TEXT_LENGTH;
    return value.length > limit ? path + " supera el límite de " + limit + " caracteres." : null;
  }
  if (value === null || typeof value !== "object") return null;
  if (Array.isArray(value) && value.length > MAX_LIST_LENGTH) {
    return path + " supera el límite de " + MAX_LIST_LENGTH + " elementos.";
  }
  for (const [key, entry] of Object.entries(value)) {
    if (key.length > MAX_TEXT_LENGTH) return path + " contiene un nombre de campo demasiado largo.";
    const error = sizeError(entry, path + "." + key, key, depth + 1);
    if (error) return error;
  }
  return null;
}

module.exports = async function handler(req, res) {
  res.setHeader("Cache-Control", "no-store");
  const code = process.env.SYNC_CODE;
  const st = store();
  if (!code || !st.ok()) return res.status(503).json({ error: "sin_configurar" });
  const ip = String((req.headers && req.headers["x-forwarded-for"]) || "").split(",")[0].trim() || "local";
  if (limited(ip)) return res.status(429).json({ error: "limite" });
  if (!same(req.headers["x-sync-code"], code)) return res.status(401).json({ error: "codigo" });

  try {
    if (req.method === "GET") {
      const rev = String((req.query && req.query.rev) || "");
      const cur = await st.read(rev);
      if (!cur) return res.status(200).json({ empty: true });
      if (cur.same) return res.status(200).json({ same: true, rev: cur.rev });
      return res.status(200).json(cur);
    }
    if (req.method === "PUT") {
      const body = parseBody(req);
      const data = body && body.data;
      if (!isObject(data)) return res.status(400).json({ error: "El estado debe ser un objeto." });
      for (const key of ["items", "users", "sales"]) {
        const list = data[key];
        if (!Array.isArray(list)) return res.status(400).json({ error: key + " debe ser una lista." });
        if (list.length > MAX_LIST_LENGTH) {
          return res.status(400).json({ error: key + " supera el límite de " + MAX_LIST_LENGTH + " elementos." });
        }
        const index = list.findIndex((entry) => !isObject(entry));
        if (index !== -1) return res.status(400).json({ error: key + "[" + index + "] debe ser un objeto." });
      }
      const error = sizeError(data, "estado");
      if (error) return res.status(400).json({ error });
      const text = JSON.stringify(data);
      if (Buffer.byteLength(text) > MAX_BYTES) return res.status(413).json({ error: "grande" });
      let base = String(body.rev || "");
      if (body.force) {
        const cur = await st.read("");
        base = cur ? cur.rev : "";
      }
      const out = await st.write(text, base);
      if (out.conflict) return res.status(409).json(out);
      return res.status(200).json(out);
    }
    if (req.method === "DELETE") {
      await st.remove();
      return res.status(200).json({ ok: true });
    }
    return res.status(405).json({ error: "metodo" });
  } catch (e) {
    return res.status(500).json({ error: "interno", detail: String((e && e.name) || "error") });
  }
};

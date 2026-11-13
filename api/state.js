// Sincronización de Tienda María: guarda toda la información de la tienda en un archivo privado (Vercel Blob)
// para que todos los celulares vean lo mismo.
// Variables de entorno: SYNC_CODE (código de la tienda) y UNO de estos dos almacenes:
//  - FIREBASE_SERVICE_ACCOUNT (JSON de la cuenta de servicio de Firebase) -> Firestore (si existe, se usa este)
//  - BLOB_READ_WRITE_TOKEN (la pone Vercel al crear el almacenamiento) -> Vercel Blob
const crypto = require("crypto");
const { get, put, del, BlobPreconditionFailedError } = require("@vercel/blob");

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
async function blobRead(rev) {
  const r = await get(PATH, { access: "private", useCache: false, ifNoneMatch: rev || undefined });
  if (!r) return null;
  if (r.statusCode === 304) return { same: true, rev: r.blob.etag };
  const text = await new Response(r.stream).text();
  return { rev: r.blob.etag, data: JSON.parse(text) };
}
const blobStore = {
  ok: () => !!process.env.BLOB_READ_WRITE_TOKEN,
  read: blobRead,
  async write(text, base) {
    const opts = { access: "private", contentType: "application/json", addRandomSuffix: false, cacheControlMaxAge: 60, allowOverwrite: true };
    if (!base) {
      const cur = await blobRead("");
      if (cur) return { conflict: true, rev: cur.rev, data: cur.data };
    }
    try {
      const out = base ? await put(PATH, text, { ...opts, ifMatch: base }) : await put(PATH, text, opts);
      return { ok: true, rev: out.etag };
    } catch (e) {
      if (e instanceof BlobPreconditionFailedError) {
        const cur = await blobRead("");
        if (!cur) return { conflict: true, empty: true };
        return { conflict: true, rev: cur.rev, data: cur.data };
      }
      throw e;
    }
  },
  async remove() {
    await del(PATH);
  },
};

// Firestore: un documento no puede pasar de 1 MB, así que el JSON se parte en pedazos (tienda/estado/partes/N).
const CHUNK = 700000;
let fsDb = null;
function fireDb() {
  if (fsDb) return fsDb;
  const admin = require("firebase-admin");
  if (!admin.apps.length) {
    admin.initializeApp({ credential: admin.credential.cert(JSON.parse(process.env.FIREBASE_SERVICE_ACCOUNT)) });
  }
  fsDb = admin.firestore();
  return fsDb;
}
async function fireLoad(tx, db, meta) {
  const parts = [];
  for (let i = 0; i < meta.n; i++) {
    const d = await tx.get(db.doc("tienda/estado/partes/" + i));
    parts.push(d.exists ? d.data().t : "");
  }
  return JSON.parse(parts.join(""));
}
const fireStore = {
  ok: () => !!process.env.FIREBASE_SERVICE_ACCOUNT,
  async read(rev) {
    const db = fireDb();
    return db.runTransaction(async (tx) => {
      const m = await tx.get(db.doc("tienda/estado"));
      if (!m.exists || !m.data().n) return null;
      const meta = m.data();
      if (rev && rev === String(meta.rev)) return { same: true, rev: String(meta.rev) };
      return { rev: String(meta.rev), data: await fireLoad(tx, db, meta) };
    });
  },
  async write(text, base) {
    const db = fireDb();
    return db.runTransaction(async (tx) => {
      const ref = db.doc("tienda/estado");
      const m = await tx.get(ref);
      const meta = m.exists && m.data().n ? m.data() : null;
      const cur = meta ? String(meta.rev) : "";
      if (cur !== base) {
        if (!meta) return { conflict: true, empty: true };
        return { conflict: true, rev: cur, data: await fireLoad(tx, db, meta) };
      }
      const rev = Date.now() * 1000 + Math.floor(Math.random() * 1000);
      const n = Math.max(1, Math.ceil(text.length / CHUNK));
      for (let i = 0; i < n; i++) tx.set(db.doc("tienda/estado/partes/" + i), { t: text.slice(i * CHUNK, (i + 1) * CHUNK) });
      for (let i = n; meta && i < meta.n; i++) tx.delete(db.doc("tienda/estado/partes/" + i));
      tx.set(ref, { rev, n, u: new Date().toISOString() });
      return { ok: true, rev: String(rev) };
    });
  },
  async remove() {
    const db = fireDb();
    const m = await db.doc("tienda/estado").get();
    const n = m.exists ? m.data().n || 0 : 0;
    const b = db.batch();
    for (let i = 0; i < n; i++) b.delete(db.doc("tienda/estado/partes/" + i));
    b.delete(db.doc("tienda/estado"));
    await b.commit();
  },
};
function store() {
  return fireStore.ok() ? fireStore : blobStore;
}
function valid(d) {
  return d && typeof d === "object" && Array.isArray(d.items) && Array.isArray(d.users) && Array.isArray(d.sales);
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
      if (!valid(body.data)) return res.status(400).json({ error: "datos" });
      const text = JSON.stringify(body.data);
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

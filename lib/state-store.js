const { get, put, del, BlobPreconditionFailedError } = require("@vercel/blob");

const PATH = "tienda-maria/estado.json";

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

module.exports = store;

// Asistente con IA de la tienda. Función de Vercel que llama a Claude.
// Variables de entorno necesarias en Vercel:
//   ANTHROPIC_API_KEY  clave de la API de Anthropic (nunca va en la página)
//   ASSISTANT_CODE     código de acceso que escribe el administrador en Ajustes
// Opcionales: ASSISTANT_MODEL (por defecto claude-opus-5-5), ASSISTANT_EFFORT (por defecto medium)
const crypto = require("crypto");
const Anthropic = require("@anthropic-ai/sdk");

const MODEL = process.env.ASSISTANT_MODEL || "claude-opus-5-5";
const EFFORT = process.env.ASSISTANT_EFFORT || "medium";
const IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp", "image/gif"];
const hits = new Map();

const SCHEMA = {
  type: "object",
  properties: {
    answer: { type: "string" },
    charts: {
      type: "array",
      items: {
        type: "object",
        properties: {
          type: { type: "string", enum: ["bar", "hbar", "line", "donut"] },
          title: { type: "string" },
          labels: { type: "array", items: { type: "string" } },
          values: { type: "array", items: { type: "number" } },
          money: { type: "boolean" },
        },
        required: ["type", "title", "labels", "values", "money"],
        additionalProperties: false,
      },
    },
  },
  required: ["answer", "charts"],
  additionalProperties: false,
};

function systemPrompt(context) {
  return [
    "Eres el asistente de una tienda pequeña de golosinas y snacks en Colombia. Le hablas al dueño o a su equipo.",
    "Responde en español sencillo, directo y breve, sin tecnicismos. Los montos van en pesos colombianos con punto de miles, por ejemplo $12.500.",
    "Para cualquier cifra del negocio usa solo los DATOS de abajo. Si el dato no está, dilo con claridad y no inventes números. Si calculas algo, di cómo.",
    "Si el usuario envía una imagen (una factura de proveedor, un recibo, un producto, un estante, una lista de precios), descríbela y extrae lo útil: productos, cantidades, precios, totales e impuestos. Cuando se pueda, compáralos con los productos de la tienda y señala diferencias de costo o de margen.",
    "Cuando ayude a entender mejor, agrega uno o dos gráficos con datos reales (tipos: bar, hbar, line, donut; máximo 12 puntos; labels cortos; money true si son pesos). Si un gráfico no aporta, deja charts vacío.",
    "En answer puedes usar **negrita** y listas con guion. No uses tablas ni encabezados.",
    "Responde SOLO con el JSON pedido.",
    "",
    "DATOS DE LA TIENDA (JSON):",
    context,
  ].join("\n");
}

function same(a, b) {
  const x = Buffer.from(String(a));
  const y = Buffer.from(String(b));
  return x.length === y.length && crypto.timingSafeEqual(x, y);
}

function limited(ip) {
  const now = Date.now();
  const w = (hits.get(ip) || []).filter((t) => now - t < 60000);
  w.push(now);
  hits.set(ip, w);
  if (hits.size > 500) hits.clear();
  return w.length > 20;
}

function parseBody(req) {
  if (req.body && typeof req.body === "object") return req.body;
  try {
    return JSON.parse(req.body || "{}");
  } catch (e) {
    return {};
  }
}

function buildMessages(body) {
  const messages = [];
  (Array.isArray(body.history) ? body.history.slice(-8) : []).forEach((m) => {
    const role = m && m.role === "assistant" ? "assistant" : "user";
    const text = String((m && m.text) || "").slice(0, 1500).trim();
    if (!text) return;
    if (!messages.length && role === "assistant") return;
    messages.push({ role, content: text });
  });
  const question = String(body.question || "").slice(0, 2000).trim();
  const content = [];
  const img = body.image;
  if (img && IMAGE_TYPES.includes(img.mediaType) && typeof img.data === "string" && img.data.length > 100 && img.data.length <= 4000000) {
    content.push({ type: "image", source: { type: "base64", media_type: img.mediaType, data: img.data } });
  }
  content.push({ type: "text", text: question || "Describe esta imagen y dime qué información útil trae para mi tienda." });
  messages.push({ role: "user", content });
  return messages;
}

async function run(client, system, messages) {
  const base = {
    model: MODEL,
    max_tokens: 16000,
    system,
    messages,
    output_config: { effort: EFFORT, format: { type: "json_schema", schema: SCHEMA } },
  };
  // 1) con respaldo automático si el modelo rechaza la pregunta por seguridad
  try {
    return await client.beta.messages.create({ ...base, betas: ["server-side-fallback-2026-07-01"], fallbacks: "default" });
  } catch (e) {
    if (!(e instanceof Anthropic.BadRequestError)) throw e;
  }
  // 2) sin respaldo
  try {
    return await client.messages.create(base);
  } catch (e) {
    if (!(e instanceof Anthropic.BadRequestError)) throw e;
  }
  // 3) sin formato estructurado
  return client.messages.create({ ...base, output_config: { effort: EFFORT } });
}

function cleanCharts(list) {
  if (!Array.isArray(list)) return [];
  return list
    .filter((c) => c && ["bar", "hbar", "line", "donut"].includes(c.type) && Array.isArray(c.labels) && Array.isArray(c.values))
    .map((c) => {
      const n = Math.min(c.labels.length, c.values.length, 12);
      return {
        type: c.type,
        title: String(c.title || "").slice(0, 80),
        labels: c.labels.slice(0, n).map((l) => String(l).slice(0, 24)),
        values: c.values.slice(0, n).map((v) => (Number.isFinite(Number(v)) ? Number(v) : 0)),
        money: !!c.money,
      };
    })
    .filter((c) => c.labels.length > 0)
    .slice(0, 3);
}

function readReply(response) {
  if (response.stop_reason === "refusal") {
    return { answer: "No puedo ayudar con esa pregunta. Prueba con otra sobre tu tienda.", charts: [] };
  }
  const text = (response.content || [])
    .filter((b) => b.type === "text")
    .map((b) => b.text)
    .join("\n")
    .trim();
  try {
    const j = JSON.parse(text);
    return { answer: String(j.answer || "").trim() || "No encontré una respuesta.", charts: cleanCharts(j.charts) };
  } catch (e) {
    return { answer: text || "No encontré una respuesta.", charts: [] };
  }
}

module.exports = async function handler(req, res) {
  res.setHeader("Cache-Control", "no-store");
  if (req.method !== "POST") return res.status(405).json({ error: "metodo" });
  const apiKey = process.env.ANTHROPIC_API_KEY;
  const code = process.env.ASSISTANT_CODE;
  if (!apiKey || !code) return res.status(503).json({ error: "sin_configurar" });
  const body = parseBody(req);
  if (!same(body.code || "", code)) return res.status(401).json({ error: "codigo" });
  const ip = String((req.headers && req.headers["x-forwarded-for"]) || "").split(",")[0].trim() || "local";
  if (limited(ip)) return res.status(429).json({ error: "limite" });
  if (body.ping) return res.status(200).json({ ok: true, model: MODEL });

  const context = JSON.stringify(body.context || {}).slice(0, 40000);
  const messages = buildMessages(body);
  const client = new Anthropic({ apiKey, timeout: 55000, maxRetries: 1 });
  try {
    const response = await run(client, systemPrompt(context), messages);
    return res.status(200).json(readReply(response));
  } catch (e) {
    if (e instanceof Anthropic.AuthenticationError) return res.status(502).json({ error: "clave_invalida" });
    if (e instanceof Anthropic.RateLimitError) return res.status(429).json({ error: "limite_api" });
    if (e instanceof Anthropic.APIConnectionError) return res.status(504).json({ error: "conexion" });
    if (e instanceof Anthropic.APIError) return res.status(502).json({ error: "api", status: e.status });
    return res.status(500).json({ error: "interno" });
  }
};

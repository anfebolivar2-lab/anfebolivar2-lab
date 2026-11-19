#!/usr/bin/env bash
# Instala las herramientas de la guía (Codex CLI y Graphify) en tu computadora.
# Uso:  bash scripts/setup-herramientas.sh
# Los agentes y el plugin de Codex ya vienen con el repo (.claude/agents y .claude/settings.json).
set -euo pipefail

echo "== Comprobando requisitos =="
command -v node >/dev/null || { echo "Falta Node.js 18.18 o superior (nodejs.org)"; exit 1; }
node -e 'const [a,b]=process.versions.node.split(".").map(Number); if (a<18||(a===18&&b<18)) {console.error("Node demasiado viejo: necesitas 18.18 o superior"); process.exit(1)}'

echo "== Codex CLI =="
if command -v codex >/dev/null; then
  echo "Ya instalado: $(codex --version)"
else
  npm install -g @openai/codex
fi

echo "== Graphify (paquete oficial: graphifyy, con dos y) =="
if command -v graphify >/dev/null; then
  echo "Ya instalado"
elif command -v uv >/dev/null; then
  uv tool install graphifyy
elif command -v pipx >/dev/null; then
  pipx install graphifyy
else
  echo "Falta uv o pipx (necesitas Python 3.10+). Instala uv: https://docs.astral.sh/uv/"; exit 1
fi
graphify install
graphify install --platform codex

cat <<'FIN'

Listo. Falta lo único que no se puede automatizar: iniciar sesión en Codex con tu cuenta de ChatGPT.
Abre Claude Code en este proyecto y escribe:

   !codex login

Luego comprueba con /codex:setup. Si no aparecen los comandos /codex, usa /reload-plugins.
FIN

#!/usr/bin/env python3
"""Compara las respuestas de varios modelos de IA a un mismo prompt, vía OpenRouter.

Solo usa la librería estándar de Python (3.8+). No hay nada que instalar.

Requisitos:
  - Una clave de OpenRouter (openrouter.ai). Se lee de la variable de entorno
    OPENROUTER_API_KEY. Nunca la escribas dentro de este archivo ni la subas al repo.

Uso:
  export OPENROUTER_API_KEY="tu-clave"

  # Ver modelos disponibles (opcionalmente filtrando por texto)
  python3 scripts/comparar-modelos.py --listar claude
  python3 scripts/comparar-modelos.py --listar --gratis

  # Comparar modelos con un prompt
  python3 scripts/comparar-modelos.py \
      --modelos "proveedor/modelo-a,proveedor/modelo-b" \
      --prompt "Dame 3 ideas de reels para mi cafetería, con gancho y llamado a la acción."

  # Prompt desde un archivo, resultado a un archivo Markdown
  python3 scripts/comparar-modelos.py --modelos "a/b,c/d" --archivo prompt.txt --salida resultado.md

Los modelos se consultan en paralelo. El costo depende de cada modelo: probá primero con
pocos modelos, con --max-tokens bajo y con modelos gratis (--listar --gratis).
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

BASE_URL = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/")


def clave():
    k = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not k:
        sys.exit("Falta la variable de entorno OPENROUTER_API_KEY. Creá una clave en openrouter.ai "
                 'y corré: export OPENROUTER_API_KEY="tu-clave"')
    return k


def pedir(url, datos=None, k=None, timeout=120):
    headers = {"Content-Type": "application/json"}
    if k:
        headers["Authorization"] = "Bearer " + k
    cuerpo = json.dumps(datos).encode() if datos is not None else None
    req = urllib.request.Request(url, data=cuerpo, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def listar(filtro, solo_gratis):
    # La lista de modelos es pública; no hace falta clave.
    datos = pedir(BASE_URL + "/models")
    filas = []
    for m in datos.get("data", []):
        mid = m.get("id", "")
        precio = m.get("pricing", {}) or {}
        es_gratis = str(precio.get("prompt", "1")) in ("0", "0.0") and str(precio.get("completion", "1")) in ("0", "0.0")
        if filtro and filtro.lower() not in (mid + " " + (m.get("name") or "")).lower():
            continue
        if solo_gratis and not es_gratis:
            continue
        filas.append((mid, "gratis" if es_gratis else "pago"))
    for mid, tipo in sorted(filas):
        print(f"{mid}  [{tipo}]")
    print(f"\n{len(filas)} modelos.", file=sys.stderr)


def consultar(modelo, prompt, max_tokens, k):
    inicio = time.time()
    try:
        datos = pedir(
            BASE_URL + "/chat/completions",
            {"model": modelo, "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens},
            k,
        )
        texto = datos["choices"][0]["message"]["content"] or ""
        uso = datos.get("usage", {}) or {}
        return {"modelo": modelo, "ok": True, "texto": texto.strip(),
                "segundos": time.time() - inicio, "tokens": uso.get("total_tokens")}
    except urllib.error.HTTPError as e:
        detalle = ""
        try:
            detalle = json.loads(e.read().decode()).get("error", {}).get("message", "")
        except Exception:
            pass
        return {"modelo": modelo, "ok": False, "texto": f"Error HTTP {e.code}: {detalle}".strip(),
                "segundos": time.time() - inicio, "tokens": None}
    except Exception as e:  # red, JSON inesperado, timeout, etc.
        return {"modelo": modelo, "ok": False, "texto": f"Error: {e}",
                "segundos": time.time() - inicio, "tokens": None}


def a_markdown(prompt, resultados):
    out = ["# Comparación de modelos", "", "## Prompt", "", prompt, ""]
    out += ["## Resumen", "", "| Modelo | Estado | Segundos | Tokens | Caracteres |", "|---|---|---|---|---|"]
    for r in resultados:
        out.append(f"| `{r['modelo']}` | {'OK' if r['ok'] else 'ERROR'} | {r['segundos']:.1f} | "
                   f"{r['tokens'] if r['tokens'] is not None else '-'} | {len(r['texto']) if r['ok'] else '-'} |")
    out.append("")
    for r in resultados:
        out += [f"## `{r['modelo']}`", "", r["texto"] if r["texto"] else "(sin respuesta)", ""]
    out += ["---", "",
            "Puntuá cada respuesta a mano con tus criterios (claridad, tono, precisión, utilidad). "
            "Este script no califica automáticamente: el mejor modelo depende de tu tarea."]
    return "\n".join(out)


def main():
    p = argparse.ArgumentParser(description="Compara modelos de IA con un mismo prompt (OpenRouter).")
    p.add_argument("--listar", nargs="?", const="", metavar="TEXTO", help="Lista modelos (filtro opcional) y sale")
    p.add_argument("--gratis", action="store_true", help="Con --listar: solo modelos gratis")
    p.add_argument("--modelos", help="IDs separados por coma, p. ej. 'a/b,c/d'")
    p.add_argument("--prompt", help="Texto del prompt")
    p.add_argument("--archivo", help="Archivo de texto con el prompt")
    p.add_argument("--max-tokens", type=int, default=500, help="Límite de tokens por respuesta (default 500)")
    p.add_argument("--salida", help="Guarda el resultado en este archivo Markdown")
    a = p.parse_args()

    if a.listar is not None:
        return listar(a.listar, a.gratis)

    if not a.modelos:
        sys.exit("Indicá --modelos (usá --listar para ver los disponibles).")
    modelos = [m.strip() for m in a.modelos.split(",") if m.strip()]
    if len(modelos) > 12:
        sys.exit("Máximo 12 modelos por corrida, para cuidar el costo.")

    if a.archivo:
        with open(a.archivo, encoding="utf-8") as f:
            prompt = f.read().strip()
    else:
        prompt = (a.prompt or "").strip()
    if not prompt:
        sys.exit("Indicá --prompt o --archivo.")

    k = clave()
    print(f"Consultando {len(modelos)} modelo(s) en paralelo...", file=sys.stderr)
    with ThreadPoolExecutor(max_workers=len(modelos)) as ex:
        resultados = list(ex.map(lambda m: consultar(m, prompt, a.max_tokens, k), modelos))

    md = a_markdown(prompt, resultados)
    if a.salida:
        with open(a.salida, "w", encoding="utf-8") as f:
            f.write(md + "\n")
        print(f"Guardado en {a.salida}", file=sys.stderr)
    else:
        print(md)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Consulta Vapi por MCP desde Responses API. No expone herramientas de llamada.

Requiere Python 3 y las variables OPENAI_API_KEY, VAPI_PRIVATE_API_KEY y OPENAI_MODEL.
Solo usa la biblioteca estándar. No hace llamadas telefónicas.
"""

import json
import os
import sys
import urllib.error
import urllib.request


def build_request():
    required = ("OPENAI_API_KEY", "VAPI_PRIVATE_API_KEY", "OPENAI_MODEL")
    missing = [name for name in required if not os.environ.get(name, "").strip()]
    if missing:
        raise ValueError("Faltan variables: " + ", ".join(missing))

    payload = {
        "model": os.environ["OPENAI_MODEL"].strip(),
        "input": (
            "Usa Vapi para listar mis asistentes y numeros telefonicos. "
            "No hagas llamadas, no crees ni modifiques recursos. "
            "Muestra los identificadores devueltos sin inventarlos."
        ),
        "tools": [{
            "type": "mcp",
            "server_label": "vapi",
            "server_url": "https://mcp.vapi.ai/mcp",
            "authorization": os.environ["VAPI_PRIVATE_API_KEY"].strip(),
            "allowed_tools": ["list_assistants", "list_phone_numbers"],
            "require_approval": "never",
        }],
    }
    return urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + os.environ["OPENAI_API_KEY"].strip(),
            "Content-Type": "application/json",
        },
        method="POST",
    )


def main():
    try:
        request = build_request()
        with urllib.request.urlopen(request, timeout=180) as response:
            result = json.load(response)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except urllib.error.HTTPError as exc:
        print(
            f"OpenAI devolvio HTTP {exc.code}. Revisa permisos, modelo y saldo. "
            "No se imprime el cuerpo del error para evitar exponer datos.",
            file=sys.stderr,
        )
        return 1
    except (urllib.error.URLError, TimeoutError):
        print("No se pudo completar la conexion HTTPS.", file=sys.stderr)
        return 1

    output = result.get("output", [])
    print(json.dumps({"id": result.get("id"), "output": output},
                     ensure_ascii=False, indent=2))
    if result.get("error") or any(
        item.get("type") == "mcp_call" and item.get("error")
        for item in output
    ):
        print("La respuesta contiene un error; revisa el resultado.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

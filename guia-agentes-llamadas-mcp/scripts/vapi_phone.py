#!/usr/bin/env python3
"""Diagnóstico Vapi: lectura, simulación y una única llamada explícita. Python 3.10+."""
import argparse
import json
import os
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

BASE_URL = "https://api.vapi.ai"


def phone_number(value):
    if not re.fullmatch(r"\+[1-9][0-9]{6,14}", value):
        raise argparse.ArgumentTypeError("Usa E.164: +, código de país y dígitos, sin espacios.")
    return value


def request_json(method, path, key, payload=None):
    """Una solicitud; nunca reintenta POST ante un resultado incierto."""
    headers = {"Authorization": f"Bearer {key}", "Accept": "application/json"}
    body = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(payload).encode("utf-8")
    req = Request(BASE_URL + path, data=body, headers=headers, method=method)
    try:
        with urlopen(req, timeout=30) as response:
            return json.load(response)
    except HTTPError as exc:
        # No volcar respuestas que puedan contener datos o credenciales de la cuenta.
        raise RuntimeError(f"HTTP {exc.code}. Revisa el panel Vapi y la guía de diagnóstico.") from None
    except (URLError, TimeoutError, OSError, ValueError):
        message = "No se pudo confirmar la respuesta de Vapi."
        if method == "POST":
            message += " La llamada podría haberse creado: revisa Logs > Calls antes de repetir."
        raise RuntimeError(message) from None


def summarize_call(data):
    keys = ("id", "status", "startedAt", "endedAt", "endedReason", "cost")
    return {key: data[key] for key in keys if key in data}


def summarize_list(data, keys):
    # Las listas REST documentadas son arrays; aceptar también respuestas paginadas comunes.
    if isinstance(data, dict):
        data = data.get("results", data.get("data"))
    if not isinstance(data, list):
        raise RuntimeError("Formato de lista inesperado; revisa la referencia actual de la API.")
    return [{k: item[k] for k in keys if k in item} for item in data if isinstance(item, dict)]


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("list-assistants", help="Consulta IDs y nombres de asistentes; no llama.")
    sub.add_parser("list-numbers", help="Consulta IDs y números de Vapi; no llama.")
    get = sub.add_parser("get-call", help="Consulta el estado de una llamada existente.")
    get.add_argument("call_id")
    create = sub.add_parser("create-call", help="Simula por defecto; --execute solicita una llamada real.")
    create.add_argument("--assistant-id", default=os.environ.get("VAPI_ASSISTANT_ID"))
    create.add_argument("--phone-number-id", default=os.environ.get("VAPI_PHONE_NUMBER_ID"))
    create.add_argument("--to", required=True, type=phone_number)
    create.add_argument("--execute", action="store_true")
    create.add_argument("--confirm-destination", type=phone_number,
                        help="Para ejecutar, repetir exactamente el destino autorizado.")
    return p


def main(argv=None):
    p = parser()
    args = p.parse_args(argv)
    try:
        if args.command == "create-call":
            if not args.assistant_id or not args.phone_number_id:
                p.error("Faltan --assistant-id y/o --phone-number-id (o variables equivalentes).")
            payload = {"assistantId": args.assistant_id, "phoneNumberId": args.phone_number_id,
                       "customer": {"number": args.to}}
            if not args.execute:
                print(json.dumps({"mode": "SIMULACION_SIN_RED", "method": "POST", "path": "/call",
                                  "payload": payload}, ensure_ascii=False, indent=2))
                return 0
            allowed = {n.strip() for n in os.environ.get("ALLOWED_TEST_NUMBERS", "").split(",") if n.strip()}
            if args.to not in allowed:
                p.error("Destino bloqueado: agrega únicamente tu número propio/autorizado a ALLOWED_TEST_NUMBERS.")
            if args.confirm_destination != args.to:
                p.error("Para una llamada real, --confirm-destination debe coincidir exactamente con --to.")
            if any("REEMPLAZAR" in val.upper() for val in (args.assistant_id, args.phone_number_id)):
                p.error("Sustituye los identificadores de ejemplo antes de ejecutar.")
        key = os.environ.get("VAPI_PRIVATE_API_KEY", "").strip()
        if not key or "REEMPLAZAR" in key.upper():
            p.error("Configura VAPI_PRIVATE_API_KEY localmente; no la pegues en el chat.")
        if args.command == "list-assistants":
            data = summarize_list(request_json("GET", "/assistant", key), ("id", "name"))
        elif args.command == "list-numbers":
            data = summarize_list(request_json("GET", "/phone-number", key), ("id", "number", "provider"))
        elif args.command == "get-call":
            data = summarize_call(request_json("GET", "/call/" + quote(args.call_id, safe=""), key))
        else:
            data = summarize_call(request_json("POST", "/call", key, payload))
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

# Primera llamada: una prueba controlada y comprobable

Objetivo: una llamada a un teléfono que controles, con un asistente y número de salida elegidos expresamente. Este capítulo ofrece dos caminos: desde Claude/ChatGPT mediante MCP o desde la herramienta REST incluida. El segundo permite aislar errores sin depender del chat; no sustituye la conexión MCP.

## 1. Completa la ficha antes de marcar

| Campo | Tu valor local |
|---|---|
| Asistente publicado | Nombre e `assistantId` |
| Número de salida | Teléfono visible e ID Vapi `phoneNumberId` |
| Destino | Tu número real con país, por ejemplo formato `+57` más los 10 dígitos móviles |
| Objetivo | Saludar y comprobar audio en español |
| Intentos | Uno |
| Reintentos | Desactivados para esta prueba |

Los teléfonos de ejemplo de este repositorio son ilustrativos. No son destinatarios autorizados. Reemplázalos completos por tu número real. El formato E.164 tiene `+`, código de país y dígitos; no escribas espacios, paréntesis ni guiones.

## 2. Desde Claude o ChatGPT: primero consulta

Con el MCP conectado, envía:

> Lista mis asistentes y números Vapi. Muéstrame nombre, número e identificadores exactos. No crees recursos ni hagas llamadas.

Compara el resultado con el panel Vapi. Si tienes varias líneas, selecciona una por su número y proveedor; no pidas al modelo que elija «la primera». Confirma que el asistente esté publicado y que ese número admita salida.

Luego envía, con tus datos:

> Prepara una sola llamada de prueba a [MI_NUMERO_REAL_E164], desde [PHONE_NUMBER_ID_VAPI], con [ASSISTANT_ID]. El teléfono es mío y espero la prueba. El objetivo es comprobar el saludo y el audio en español. Muéstrame origen, destino y asistente antes de ejecutar. No programes reintentos.

**El objetivo escrito en el chat no cambia por sí solo lo que dirá el agente.** La llamada usa el asistente publicado en Vapi; configura allí el guion de prueba antes de llamar. El script incluido no envía cambios de prompt ni `assistantOverrides`. Si implementas personalización por llamada, usa parámetros verificados y comprueba qué versión recibirá el agente.

Después de comprobar la propuesta, autoriza esa llamada concreta. El MCP documenta `create_call` para iniciar y `get_call` para consultar. El cliente debe usar el esquema real anunciado por su servidor. [Herramientas MCP Vapi](https://docs.vapi.ai/sdk/mcp-server).

El texto del chat que dice «ya llamé» no es evidencia suficiente. Pide el ID devuelto por la herramienta, consulta esa llamada y comprueba su registro en el panel.

## 3. Alternativa de diagnóstico: herramienta local

Desde la raíz del repositorio, consulta la ayuda:

```bash
python3 scripts/vapi_phone.py --help
```

Para consultas de lectura, introduce tu clave localmente. macOS, en zsh:

```zsh
read -rs "VAPI_PRIVATE_API_KEY?Clave privada Vapi: "
echo
export VAPI_PRIVATE_API_KEY
python3 scripts/vapi_phone.py list-assistants
python3 scripts/vapi_phone.py list-numbers
```

Windows, PowerShell 7:

```powershell
$env:VAPI_PRIVATE_API_KEY = Read-Host "Clave privada Vapi" -MaskInput
py -3 scripts/vapi_phone.py list-assistants
py -3 scripts/vapi_phone.py list-numbers
```

La variable vive en esa terminal. El script no lee `.env`. La clave no se escribe en el código ni se imprime.

### Simular sin red

```bash
python3 scripts/vapi_phone.py create-call \
  --assistant-id REEMPLAZAR_ASSISTANT_ID \
  --phone-number-id REEMPLAZAR_PHONE_NUMBER_ID \
  --to +12025550123
```

Debe devolver `SIMULACION_SIN_RED` y un JSON. Esto comprueba el formato que se enviaría, no la autenticidad de IDs, acceso, telefonía ni funcionamiento del agente. Sin `--execute` no consulta Vapi y no necesita clave.

### Ejecutar cuando hayas decidido llamar

Primero carga una lista de números propios o autorizados. En los siguientes comandos, `+TU_NUMERO_REAL_E164` es un marcador: reemplázalo completo por tu teléfono real, incluyendo el `+`.

macOS zsh:

```zsh
export ALLOWED_TEST_NUMBERS="+TU_NUMERO_REAL_E164"
python3 scripts/vapi_phone.py create-call \
  --assistant-id ID_REAL_DEL_ASISTENTE \
  --phone-number-id ID_REAL_DEL_NUMERO_VAPI \
  --to "$ALLOWED_TEST_NUMBERS" \
  --execute \
  --confirm-destination "$ALLOWED_TEST_NUMBERS"
```

Windows PowerShell 7:

```powershell
$env:ALLOWED_TEST_NUMBERS = "+TU_NUMERO_REAL_E164"
py -3 scripts/vapi_phone.py create-call `
  --assistant-id ID_REAL_DEL_ASISTENTE `
  --phone-number-id ID_REAL_DEL_NUMERO_VAPI `
  --to $env:ALLOWED_TEST_NUMBERS `
  --execute `
  --confirm-destination $env:ALLOWED_TEST_NUMBERS
```

Estos ejemplos ejecutables usan **un solo número** en la variable. El script admite varios separados por coma, pero entonces `--to` y `--confirm-destination` deben recibir un único destino de la lista, no la cadena completa.

Esta acción puede generar cargos. La herramienta envía una sola petición `POST /call` con `assistantId`, `phoneNumberId` y `customer.number`. No hace lotes ni reintentos. [Referencia de crear llamada](https://docs.vapi.ai/api-reference/calls/create).

Si se agota el tiempo de espera, **la llamada podría haberse creado**. Revisa el historial antes de repetir; una segunda petición puede crear otra llamada.

## 4. Comprobar el resultado

Con el ID recibido:

```bash
python3 scripts/vapi_phone.py get-call ID_REAL_DE_LA_LLAMADA
```

O pide `get_call` desde el chat. El script muestra solo campos básicos; para transcripción y detalle revisa **Logs → Calls** en Vapi. Una grabación puede no existir si está deshabilitada o no se conserva. [Consultar una llamada](https://docs.vapi.ai/api-reference/calls/get).

Distingue tres resultados:

1. **Solicitud creada:** existe un ID y estado inicial. Todavía no demuestra que sonó.
2. **Conexión telefónica:** el registro muestra lo sucedido y los tiempos; comprueba también el teléfono y el operador.
3. **Objetivo cumplido:** escuchaste el saludo, pudiste interrumpir, te entendió y terminó correctamente. Un estado técnico finalizado no demuestra una conversación útil.

## 5. Aprobación y límites reales

La lista permitida del script y la repetición del destino son decisiones de esta implementación. No se aplican a otras herramientas, al panel ni al MCP oficial. Los prompts son instrucciones de comportamiento; para imponer límites a todos los clientes necesitas una pasarela propia que valide cada llamada.

No uses una llamada de prueba para una campaña. Antes completa la [lista de aceptación](10-lista-de-aceptacion.md).

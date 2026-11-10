# Conectar Vapi MCP mediante OpenAI Responses API

Esta alternativa crea una aplicación que usa un modelo OpenAI para consultar herramientas MCP. **No configura por sí sola la app ChatGPT** y no necesita el túnel del capítulo anterior: OpenAI puede acceder directamente al MCP remoto de Vapi.

**Estado:** ejemplo elaborado con los esquemas documentados de Responses API y Vapi MCP. No ejecutado contra servicios reales. El script incluido no expone la herramienta que crea llamadas. Usarlo sí puede consumir uso de API según tu cuenta y modelo.

## 1. Qué hace el ejemplo

El archivo [openai_mcp_readonly.py](../examples/openai_mcp_readonly.py) envía una solicitud a `https://api.openai.com/v1/responses`. Incluye la URL MCP Vapi y permite exclusivamente:

- `list_assistants`: consultar los asistentes disponibles.
- `list_phone_numbers`: consultar los números disponibles.

`allowed_tools` restringe las herramientas a esas dos consultas. `require_approval: "never"` se aplica solo a esta lista de lectura. No copies ese valor a una integración que exponga `create_call` u otras acciones sin implementar el control que necesitas.

La clave privada Vapi va en el campo `authorization` de la definición MCP. Allí se pasa el token **sin escribir `Bearer ` delante**. La clave OpenAI va en el header HTTP `Authorization: Bearer ...` de la petición a OpenAI. Son dos credenciales distintas y viajan en lugares distintos.

## 2. Requisitos

1. Python 3 instalado. El ejemplo usa únicamente su biblioteca estándar; no requiere `pip install`.
2. Acceso a OpenAI API y un modelo disponible que admita MCP remoto. Elige un ID real de tu cuenta y colócalo en `OPENAI_MODEL`. El ejemplo no inventa un modelo predeterminado.
3. Una clave OpenAI con permisos para Responses API, guardada en `OPENAI_API_KEY`.
4. Una clave privada Vapi guardada en `VAPI_PRIVATE_API_KEY`.
5. Asistente y número ya creados en Vapi para que las consultas devuelvan datos útiles.

La disponibilidad y los cargos de la API se revisan en Platform. Una suscripción o interfaz ChatGPT no determina por sí sola qué permisos, saldo o créditos tiene tu proyecto API.

## 3. Ejecutar desde macOS zsh

Desde la raíz del repositorio, introduce las credenciales sin pegarlas en un comando literal:

```zsh
read -rs "OPENAI_API_KEY?Clave OpenAI API: "
echo
export OPENAI_API_KEY

read -rs "VAPI_PRIVATE_API_KEY?Clave privada Vapi: "
echo
export VAPI_PRIVATE_API_KEY

read "OPENAI_MODEL?ID del modelo disponible en tu cuenta: "
export OPENAI_MODEL

python3 examples/openai_mcp_readonly.py
```

Los campos de claves no muestran su contenido al escribir. Los valores se conservan solo en el entorno de esta sesión y de sus procesos hijos.

## 4. Ejecutar desde Windows PowerShell 7

Desde la raíz del repositorio:

```powershell
$env:OPENAI_API_KEY = Read-Host "Clave OpenAI API" -MaskInput
$env:VAPI_PRIVATE_API_KEY = Read-Host "Clave privada Vapi" -MaskInput
$env:OPENAI_MODEL = Read-Host "ID del modelo disponible en tu cuenta"

py -3 examples/openai_mcp_readonly.py
```

Si tu instalación reconoce `python` y no `py`, cambia solo el ejecutable. `-MaskInput` requiere PowerShell 7. No subas un archivo con claves al repositorio para resolver la configuración del entorno.

## 5. Interpretar el resultado

El script imprime el ID de la respuesta y su colección `output`. Busca eventos `mcp_list_tools`, llamadas `mcp_call` a las dos herramientas permitidas y el texto final del asistente cuando se genere.

Verifica estos puntos:

- Los IDs y números provienen de tu cuenta Vapi.
- No aparece una llamada a `create_call`.
- No hay errores de autenticación o de la herramienta.
- No tomas un texto inventado por el modelo como prueba de que se ejecutó una herramienta.

El resultado puede contener información de tus asistentes y teléfonos. Antes de compartirlo, revisa los datos que incluye. El script no imprime la solicitud, headers ni claves. En fallos HTTP imprime el código sin volcar el cuerpo del error.

## 6. Habilitar llamadas en una aplicación propia

Este repositorio deja el ejemplo ejecutable en modo consulta. Para una implementación que llame necesitas ampliar su comportamiento, no solo cambiar un texto.

El flujo mínimo es:

1. Consultar el asistente y el número autorizados.
2. Validar destino E.164, consentimiento registrado, horario, presupuesto y ausencia de duplicados en tu aplicación.
3. Enviar una solicitud que exponga `create_call` y mantenga `require_approval: "always"` para acciones.
4. Leer el evento `mcp_approval_request` devuelto por Responses API.
5. Presentar el nombre de la herramienta y sus argumentos a la persona que decide. Mostrar al menos origen, destino, asistente y objetivo.
6. Solo si esa persona autoriza esa llamada, enviar un `mcp_approval_response` con `approve: true` y el `approval_request_id` exacto; continuar la respuesta con `previous_response_id`.
7. Leer el resultado y conservar el `callId` real. Consultar después `get_call` para conocer el estado.

Un evento `mcp_approval_request` significa que la acción está pendiente; todavía no demuestra que se hizo la llamada. Si el usuario la rechaza, enviar la decisión negativa o finalizar el flujo sin ejecutarla.

La documentación indica que `authorization` no se conserva en el objeto Response. Por eso debes volver a incluir la definición MCP con su `authorization` en cada nueva solicitud que necesite ese servidor, incluso en la continuación de una aprobación. No registres ese valor en logs.

## 7. Esquema de la herramienta de llamada

La forma documentada por Vapi para una llamada saliente incluye:

```json
{
  "assistantId": "ID_REAL_DEL_ASISTENTE",
  "phoneNumberId": "ID_REAL_DEL_NUMERO_EN_VAPI",
  "customer": {
    "number": "+CODIGO_PAIS_Y_NUMERO_REAL"
  }
}
```

Son marcadores de posición, no valores listos para ejecutar. El `phoneNumberId` pertenece a Vapi; no es el número E.164 ni el SID Twilio. Consulta el esquema de la herramienta que tu servidor anuncie al momento de implementar, porque las versiones pueden cambiar.

El modelo que decide usar `create_call` no tiene que ser el mismo modelo que mantiene la conversación de voz dentro de Vapi. El asistente de voz conserva su propia configuración de modelo, transcripción, voz y herramientas.

## 8. Errores frecuentes

| Error o síntoma | Revisión |
|---|---|
| Faltan variables | Cargar las tres variables en la misma terminal que ejecuta Python |
| HTTP 401 OpenAI | Clave OpenAI válida y no confundida con la clave Vapi |
| HTTP 403 / permisos | Proyecto, organización y permisos de la clave |
| Modelo no disponible | ID exacto y acceso de tu cuenta; no adivinar otro automáticamente |
| Error MCP Vapi 401 | Clave privada Vapi en `authorization`, sin prefijo `Bearer ` |
| Error 429 | Límites o saldo; revisar antes de repetir solicitudes |
| No aparecen herramientas | Endpoint MCP correcto y soporte del modelo elegido |
| Respuesta sin texto final | Inspeccionar `output`; puede contener eventos y resultados MCP |

## Fuentes

- [MCP en Responses API: autenticación, herramientas permitidas y aprobaciones](https://developers.openai.com/api/docs/guides/tools-connectors-mcp).
- [Vapi MCP: servidor oficial y esquema de llamada](https://docs.vapi.ai/sdk/mcp-server).

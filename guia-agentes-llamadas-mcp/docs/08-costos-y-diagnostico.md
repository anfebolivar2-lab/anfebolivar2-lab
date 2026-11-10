# 08. Costos, resultados y diagnóstico

## 1. Qué pagarás

Vapi documenta cobro por uso: hosting por minuto más modelo, voz, transcriptor y telefonía. Sus paquetes opcionales agregan servicios o límites y no reemplazan el cobro por uso. Recomienda la calculadora de precios y revisar **Call Cost** en una llamada terminada. [Fuente oficial: precios y paquetes Vapi](https://docs.vapi.ai/billing/pricing-and-success-packages).

Un número Twilio comprado tiene un cargo recurrente mensual; no equivale a contratar minutos ilimitados. [Fuente oficial: características y costo del número Twilio](https://help.twilio.com/articles/223135427-What-s-the-Difference-Between-a-Verified-Phone-Number-and-a-Twilio-Phone-Number).

### Fórmula de planificación propuesta

```text
Costo mensual aproximado =
  alquiler de números
  + minutos de telefonía x tarifa de la ruta
  + hosting del agente
  + transcripción
  + modelo de lenguaje
  + síntesis de voz
  + almacenamiento, infraestructura o extras que contrates
  + impuestos y conversión de moneda aplicables
```

Es una forma de organizar un presupuesto, no una cotización. Si un proveedor agrupa partidas, evita contarlas dos veces.

Ejemplo puramente aritmético: si presupuestas **200 llamadas conectadas de 3 minutos**, son **600 minutos** para estimar. Después agrega intentos, transferencias u otros conceptos según cómo facture cada proveedor. Este ejemplo no afirma que una llamada cueste una cantidad fija.

| Partida | Dónde revisar la cifra real |
|---|---|
| Número y ruta telefónica | Cuenta y tarifas del operador del número |
| Hosting, voz, modelo y transcripción | [Calculadora Vapi](https://vapi.ai/pricing) y configuración elegida |
| Gastos de llamadas finalizadas | Registro de la llamada y facturación |
| Servidor propio para tu integración | Proveedor donde lo alojes |
| Suscripción del chat o consumo API | Cuenta del producto que uses |

No asumas que pagar ChatGPT o Claude incluye los minutos telefónicos ni el consumo de tus otros proveedores.

## 2. Leer el resultado correctamente

Vapi ofrece **GET `/call/:id`** para consultar una llamada. El registro incluye estado, fechas, motivo de cierre, artefactos, análisis y costos, según la configuración y los datos disponibles. Campos útiles: `status`, `startedAt`, `endedAt`, `endedReason`, `endedMessage`, `cost` y `costBreakdown`. Una grabación desactivada no aparecerá por pedir el registro. [Fuente oficial: Get Call](https://docs.vapi.ai/api-reference/calls/get).

Para listar registros, **GET `/call`** admite filtros como `assistantId`, `phoneNumberId` y `limit`. [Fuente oficial: List Calls](https://docs.vapi.ai/api-reference/calls/list).

| Lo que sabes | Lo que puedes comunicar |
|---|---|
| Se devolvió un ID | La solicitud creó un registro |
| `queued` | La llamada está en cola |
| `ringing` | Está sonando |
| `in-progress` | La llamada está en curso |
| `ended` | Terminó; falta interpretar cómo y con qué resultado |
| Hay transcripción y respuesta explícita | Puedes resumir lo que efectivamente dijo la persona |

**Recomendación:** nunca traduzcas “se creó un ID” como “hablé con el cliente” o “la cita quedó confirmada”. Conserva el `callId` para verificar lo ocurrido.

## 3. Cuando algo falla

Vapi documenta que un error de validación **400** puede impedir crear el registro; una causa común es un destino fuera de E.164. E.164 es `+`, país y número sin espacios ni separadores. Si la telefonía rechaza el intento, `endedMessage` puede contener el motivo del operador. [Fuente oficial: diagnóstico de conexión](https://docs.vapi.ai/calls/troubleshoot-call-connection-errors).

| Problema visible | Comprobación concreta |
|---|---|
| El destino pierde el `+` | Trata el teléfono como texto desde que lo capturas; revisa la solicitud enviada |
| No aparece en Vapi | Revisa respuesta HTTP, credenciales y organización elegida antes de repetir |
| Twilio trial rechaza el destino | Verifica el destinatario en Twilio; consulta [preparación del número](01-numero-y-telefonia.md) |
| País bloqueado | Revisa Voice Dialing Geographic Permissions en la cuenta que origina la llamada |
| Importación funcionó antes y ahora falla | Comprueba si rotaste el Auth Token Twilio y actualiza la integración |
| Asistente responde con el texto anterior | Confirma versión publicada y el `assistantId` usado |
| Agente habla inglés | Revisa prompt, idioma del transcriptor y voz, y vuelve a publicar |
| Claude no ve herramientas | Diagnostica la conexión MCP antes de intentar otra llamada |
| HTTP 401 en Vapi | Comprueba clave privada y organización; no publiques la clave para pedir ayuda |
| Llamada duplicada | Revisa cuántas solicitudes se enviaron y cuál fue la respuesta de cada una |

Vapi también documenta **20003** de Twilio cuando las credenciales de la importación son rechazadas y **21211** para destino inválido. No reimportes con un número distinto para ocultar el error: corrige el dato o credencial correspondiente. [Fuente oficial: mensajes de conexión Vapi](https://docs.vapi.ai/calls/troubleshoot-call-connection-errors).

### Orden de aislamiento recomendado

1. ¿El asistente funciona con **Talk**? Si falla, corrige conversación/voz.
2. ¿Funciona una llamada desde **Test** del número importado? Si falla, corrige la telefonía.
3. ¿MCP puede listar asistentes y números? Si falla, corrige autenticación/conexión.
4. ¿Una sola llamada MCP devuelve un identificador? Conserva ese ID.
5. Consulta ese registro y los logs del operador antes de decidir un reintento.

Si una solicitud tarda o se corta, **no sabes automáticamente si se creó la llamada**. Consulta la lista y tus registros antes de repetirla. Esta medida evita duplicados por reintentos manuales.

## 4. Webhooks para automatizar el seguimiento

No necesitas un webhook para la primera prueba manual. En una implementación posterior, Vapi puede enviar solicitudes **POST** a una **Server URL**. El cuerpo tiene un objeto `message` con `type` y datos asociados. Entre sus eventos están `status-update` y `end-of-call-report`; este último puede incluir cierre y artefactos. Los estados documentados incluyen `queued`, `ringing`, `in-progress` y `ended`. [Fuente oficial: Server events](https://docs.vapi.ai/server-url/events).

Ejemplo **ilustrativo y reducido**, no una captura de una llamada real:

```json
{
  "message": {
    "type": "status-update",
    "status": "ended",
    "call": {
      "id": "IDENTIFICADOR_DE_LA_LLAMADA"
    }
  }
}
```

Diseño recomendado para una integración de producción:

1. Autenticar la recepción según la configuración del proveedor.
2. Guardar el evento asociado al `callId`.
3. Evitar procesar dos veces el mismo resultado.
4. Consultar el registro si necesitas completar datos.
5. Actualizar CRM o agenda solo cuando tengas evidencia suficiente del resultado.

Este repositorio no debe tratar un evento `ended` como confirmación comercial automática. La persona puede haber colgado o rechazado la propuesta.

## 5. Qué compartir al solicitar ayuda

Plantilla propuesta para reportar un problema:

```text
Etapa que falla: Talk / Test telefónico / MCP / consulta del resultado
Fecha y hora con zona horaria:
Proveedor telefónico:
Cuenta en trial o activa:
País de origen y destino:
Código HTTP o error:
callId si existe:
endedReason y endedMessage sin información sensible:
Último cambio realizado:
```

Oculta claves, tokens, cabeceras de autorización, teléfonos completos de clientes y contenido privado. Un identificador de llamada permite investigar sin exponer las credenciales.

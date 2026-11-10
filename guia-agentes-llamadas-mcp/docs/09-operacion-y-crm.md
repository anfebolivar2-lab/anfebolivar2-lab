# Pasar de una prueba a una operación con seguimiento

Las siguientes son recomendaciones de diseño para una implementación propia. No se incluyen un CRM desplegado, un servicio de webhooks ni un programador de campañas. La primera instalación debe funcionar con una llamada manual antes de añadir automatización.

## 1. Define responsabilidades

- **Chat / MCP:** recibe una instrucción y crea o consulta una solicitud.
- **Servicio de voz:** lleva la conversación, aplica sus instrucciones y emite resultados.
- **Capa de negocio:** decide a quién se puede llamar, cuándo, con qué presupuesto y cuántas veces.
- **CRM:** conserva intención, consentimiento registrado, intentos y resultado confirmado.

Cerrar el chat no es una orden fiable de colgar ni de cancelar una llamada creada. Detener un túnel impide nuevas peticiones por esa ruta mientras está detenido; no cancela lo que ya ejecuta el proveedor. Para detener una llamada existente usa el control de llamadas del proveedor y verifica que terminó.

## 2. Datos mínimos por intento

Una propuesta de registro para tu base de datos:

| Campo | Para qué sirve |
|---|---|
| `contact_id` | Relacionar el contacto sin usar el número como clave de negocio |
| `destination_e164` | Destino normalizado |
| `consent_reference` | Evidencia interna de autorización/contactabilidad |
| `requested_by` | Quién pidió la llamada |
| `purpose` | Objetivo permitido |
| `assistant_id` / `phone_number_id` | Recursos usados |
| `attempt_key` | Identificador propio único del intento |
| `provider_call_id` | ID real devuelto por Vapi |
| `state` | Pendiente, enviado, incierto, finalizado o fallido |
| `outcome` | Resultado comercial separado del estado técnico |
| `cost_observed` | Costo observado, con fecha y proveedor |

No uses transcripciones completas como registros públicos de diagnóstico. Aplica una retención acorde con tus necesidades y las obligaciones aplicables.

## 3. Evitar llamadas duplicadas

Diseño sugerido:

1. Normaliza y valida el destino.
2. Comprueba una lista de exclusión y el horario del destinatario.
3. Reserva de forma atómica un `attempt_key` en la base de datos.
4. Envía una única petición al proveedor.
5. Guarda su ID de llamada.
6. Si la respuesta se pierde, marca el intento como **incierto** y reconcilia el historial antes de reintentar.
7. Actualiza el resultado con eventos verificados o consulta del ID.

No se presupone que Vapi admita una cabecera de idempotencia concreta. Este patrón requiere persistencia y reglas en tu aplicación; un prompt no resuelve una carrera entre dos procesos.

## 4. Integrar resultados al CRM

Para producción, configura un endpoint HTTPS de tu propiedad para recibir eventos del servicio de voz, valida su autenticación y actualiza el registro por `provider_call_id`. Gestiona eventos repetidos o que lleguen fuera de orden. No guardes un webhook solo porque su nombre suena a «llamada terminada»: consulta el contrato actual del proveedor. [Eventos de servidor Vapi](https://docs.vapi.ai/server-url/events).

Si quieres usar Make, n8n u otro servicio, el flujo recomendado es: evento entrante autenticado → identificar llamada → consultar detalle necesario → actualizar CRM → decidir seguimiento. No hagas que cada webhook dispare otra llamada automáticamente.

## 5. Herramientas dentro de la conversación

Hay dos direcciones diferentes:

```text
Claude / ChatGPT -> MCP Vapi -> crear llamada
Agente de voz Vapi -> herramienta de agenda/CRM -> acción durante la llamada
```

Conectar la primera no conecta la segunda. Para que el agente reserve una cita necesita una herramienta de calendario configurada en Vapi, permisos y una respuesta de éxito real. Debe decir «quedó agendada» solo después de recibir confirmación. [MCP dentro de un asistente Vapi](https://docs.vapi.ai/tools/mcp).

## 6. Controles antes de ampliar

Empieza con destinos propios permitidos, una concurrencia baja y presupuesto de prueba. Para el servicio real, aplica por código límites de países, horarios, presupuesto, duración, intentos y listas de exclusión. Añade una forma de suspender nuevas llamadas y otra de revisar las existentes.

Confirma la base legal, las reglas de llamadas automatizadas y comerciales, el uso de IA y la grabación para los países implicados. El prefijo `+57` de los ejemplos no implica que esta guía determine el cumplimiento en Colombia u otro país.

Define una salida humana: qué casos transfieren, a qué destino autorizado y qué sucede si nadie responde. Transferir puede generar tramos adicionales de telefonía; mídelo en pruebas antes de prometer atención inmediata.

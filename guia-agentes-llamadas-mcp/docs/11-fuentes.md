# Fuentes oficiales y alcance de la verificación

Revisión documental: **9 de noviembre de 2026**. Los tutoriales enlazan la fuente junto a los pasos correspondientes. Los prompts, listas de aceptación, diseño de operación y herramienta local son propuestas de este repositorio.

No se hicieron compras, conexiones a las cuentas de telefonía ni llamadas reales durante la preparación. Las pruebas de código usan respuestas simuladas. La composición ChatGPT → túnel → Vapi requiere comprobarse en la cuenta donde se vaya a instalar.

## Vapi: telefonía, voz y resultados

| Fuente | Qué comprobar allí |
|---|---|
| [Importar Twilio](https://docs.vapi.ai/phone-numbers/import-twilio) | Formulario y credenciales de importación |
| [Números gratuitos](https://docs.vapi.ai/free-telephony) | Disponibilidad y límites de salida |
| [Primeras llamadas](https://docs.vapi.ai/quickstart/phone) | Prueba desde el panel |
| [Crear asistente](https://docs.vapi.ai/assistants/quickstart) | Plantillas, edición y publicación |
| [Idiomas](https://docs.vapi.ai/customization/multilingual) | Transcripción e idioma |
| [Vapi Voices](https://docs.vapi.ai/providers/voice/vapi-voices) | Opciones de voz |
| [API keys](https://docs.vapi.ai/security-and-privacy/api-keys) | Claves públicas/privadas y alcance |
| [Servidor MCP](https://docs.vapi.ai/sdk/mcp-server) | Endpoint, autenticación y herramientas |
| [Llamadas salientes](https://docs.vapi.ai/calls/outbound-calling) | Requisitos y programación REST |
| [Crear llamada](https://docs.vapi.ai/api-reference/calls/create) | Contrato de `POST /call` |
| [Consultar llamada](https://docs.vapi.ai/api-reference/calls/get) | Estado y campos disponibles |
| [Listar llamadas](https://docs.vapi.ai/api-reference/calls/list) | Búsqueda y filtros |
| [Listar números](https://docs.vapi.ai/api-reference/phone-numbers/list) | Contrato de `GET /phone-number` |
| [Diagnóstico de conexión](https://docs.vapi.ai/calls/troubleshoot-call-connection-errors) | Errores telefónicos y validación |
| [Eventos](https://docs.vapi.ai/server-url/events) | Seguimiento mediante webhooks |
| [MCP dentro del agente](https://docs.vapi.ai/tools/mcp) | Herramientas que usa el agente durante una llamada |
| [Precios y paquetes](https://docs.vapi.ai/billing/pricing-and-success-packages) | Partidas y modelo de cobro |
| [Calculadora de precios](https://vapi.ai/pricing) | Estimación según configuración |

## Claude y puente local

- [Conectar servidores MCP locales](https://modelcontextprotocol.io/docs/develop/connect-local-servers): configuración de escritorio y diagnóstico.
- [Conectores remotos de Claude](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp): alta y disponibilidad.
- [Agregar un conector fuera del directorio](https://claude.com/docs/connectors/custom/add-unlisted): autenticación y beta de headers.
- [Repositorio del autor de mcp-remote](https://github.com/punkpeye/mcp-remote): opciones del puente, referencias de entorno y particularidades de Windows. Es software de terceros utilizado en el ejemplo de Vapi.

## OpenAI: ChatGPT y API

- [MCP personalizado en ChatGPT](https://developers.openai.com/api/docs/guides/custom-mcp-server): conexión y autenticación.
- [Conectar y probar un plugin](https://developers.openai.com/plugins/deploy/connect-chatgpt): descubrimiento, pruebas y actualización.
- [Secure MCP Tunnel](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels): requisitos, permisos y cliente.
- [Configuración oficial de tunnel-client](https://github.com/openai/tunnel-client/blob/master/docs/configuration.md): YAML y headers referenciados por entorno.
- [Onboarding oficial](https://github.com/openai/tunnel-client/blob/master/docs/onboarding.md): instalación y comprobaciones.
- [MCP en Responses API](https://developers.openai.com/api/docs/guides/tools-connectors-mcp): `authorization`, lista de herramientas y aprobaciones.

## Twilio: restricciones y número existente

- [Error 21219](https://www.twilio.com/docs/api/errors/21219): destino no verificado en trial.
- [Permisos geográficos](https://www.twilio.com/docs/voice/api/dialing-permissions-resources) y [error 21215](https://www.twilio.com/docs/api/errors/21215): autorización por destino.
- [Número verificado frente a número Twilio](https://help.twilio.com/articles/223135427-What-s-the-Difference-Between-a-Verified-Phone-Number-and-a-Twilio-Phone-Number): diferencias de uso.
- [OutgoingCallerIds](https://www.twilio.com/docs/voice/api/outgoing-caller-ids): recurso de identificadores de salida.
- [Portabilidad](https://www.twilio.com/docs/phone-numbers/port-in): elegibilidad y alcance de la guía del proveedor.
- [Caller ID verificado](https://help.twilio.com/articles/223180048-How-to-Add-and-Remove-a-Verified-Phone-Number-or-Caller-ID-with-Twilio): validación y desvío.
- [WhatsApp Business Calling](https://www.twilio.com/docs/voice/whatsapp-business-calling): canal separado y requisitos.

## Al mantener esta guía

1. Comprueba fecha y vigencia de la fuente, no solo que la URL abra.
2. Distingue la API REST del esquema MCP anunciado por `tools/list`.
3. La página MCP de Vapi menciona `scheduledAt`; la guía REST describe `schedulePlan.earliestAt`. Este repositorio evita programar llamadas en sus scripts. Para añadirlo, utiliza el contrato de la interfaz concreta, sin mezclar ambos campos.
4. Prueba primero lectura y luego una llamada a tu propio teléfono.
5. Registra limitaciones de cuenta o región observadas. No conviertas un ejemplo documental en una garantía de disponibilidad.

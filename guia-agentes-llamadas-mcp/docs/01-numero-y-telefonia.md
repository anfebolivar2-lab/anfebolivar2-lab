# 01. Preparar el número y la telefonía

Esta guía usa un **número de voz de Twilio importado en Vapi**. Claude o ChatGPT darán la orden mediante MCP; Vapi ejecutará el agente de voz y Twilio conectará la llamada. El teléfono de destino puede ser un celular normal.

**Resultado que buscamos:** disponer de un número de salida, conocer su identificador dentro de Vapi y tener permitido llamar al país del destinatario. Todavía no necesitas conectar MCP.

## 1. Elegir qué número vas a usar

Para empezar, recomendamos un número separado para las pruebas. Así puedes comprobar todo antes de evaluar tu línea habitual. Esta es una recomendación de implementación de este repositorio.

Los números gratuitos propios de Vapi son estadounidenses y su documentación actual los describe como **solo entrantes**. Para agentes que realicen llamadas, utiliza un número importado de un proveedor soportado. Tampoco confundir número gratuito con minutos gratuitos. [Fuente oficial: números gratuitos Vapi](https://docs.vapi.ai/free-telephony).

Si quieres usar exactamente el número de tu SIM actual, consulta primero [Número actual y WhatsApp](07-numero-actual-y-whatsapp.md). Escribir ese número en un formulario no traslada tu línea al proveedor.

## 2. Obtener el número e importarlo

El siguiente es el procedimiento documentado por Vapi para Twilio:

1. Abre [Twilio Console](https://console.twilio.com/) y selecciona la cuenta que administrará el número.
2. Si no tienes un número Twilio, abre **Buy a number** y adquiere uno con capacidad de voz. Revisa país, requisitos y precio antes de confirmar la compra.
3. En el panel Twilio, localiza **Account Info**. Copia **Account SID** y revela **Auth Token**.
4. Abre [Vapi Dashboard](https://dashboard.vapi.ai/).
5. Entra en **Phone Numbers → Create Phone Number → Import Twilio**.
6. Completa **Twilio Phone Number** con el número internacional; **Twilio Account SID** y **Twilio Auth Token** con las credenciales correspondientes.
7. Opcionalmente agrega una etiqueta. Para este tutorial de voz puedes dejar **SMS Enabled** apagado.
8. Selecciona **Import from Twilio** y abre el número importado.

Las credenciales Twilio van en el formulario de Vapi. No hace falta pegarlas en una conversación. [Fuente oficial: importar número de Twilio](https://docs.vapi.ai/phone-numbers/import-twilio).

### Hoja de control propuesta

Lleva esta ficha en tu gestor de contraseñas o documento privado. Es un formato propuesto para organizarte; no se debe subir relleno a GitHub.

| Dato | Qué anotar |
|---|---|
| Cuenta Twilio elegida | Nombre de la cuenta o subcuenta |
| Número de salida | Número internacional real |
| País del destino de prueba | País al que llamarás |
| Etiqueta propuesta | `Pruebas de llamadas IA` |
| Organización Vapi elegida | Nombre de la organización |
| Estado de importación | Pendiente / correcto |

Si el panel cambió sus nombres, busca los campos equivalentes por su significado. No compres otro número solo porque no encuentras un botón.

## 3. Preparar el destino si Twilio está en prueba

Una cuenta **trial** de Twilio solo puede llamar a destinos verificados en esa cuenta. Para la primera prueba, verifica un número que controles en la sección de números del portal Twilio y completa la validación solicitada. Si no está verificado, puede aparecer el error **21219**. [Fuente oficial: error 21219](https://www.twilio.com/docs/api/errors/21219).

**No confundas los papeles:** el número importado es el origen. Tu celular personal puede ser el destino de prueba. Verificar el destino durante el trial no lo convierte en el número desde el que llama el agente.

## 4. Habilitar el país al que llamarás

Twilio controla por cuenta los países y tipos de destino permitidos para voz saliente. Esos permisos son distintos de comprar un número de un país. [Fuente oficial: Voice Dialing Geographic Permissions](https://www.twilio.com/docs/voice/api/dialing-permissions-resources).

Para el primer ensayo recomendamos:

1. Abre la sección **Voice Dialing Geographic Permissions** de tu cuenta Twilio. Puedes buscar ese nombre en Console.
2. Localiza el país del **destinatario**.
3. Revisa y habilita las opciones necesarias para ese destino; guarda los cambios que solicite el panel.
4. Si trabajas con una subcuenta, comprueba que estás revisando la cuenta que posee el número y que iniciará la llamada.
5. Mantén el ensayo limitado a tu número propio.

Si recibes **21215**, Twilio indica revisar la configuración de permisos geográficos del destino. [Fuente oficial: error 21215](https://www.twilio.com/docs/api/errors/21215).

## 5. Distinguir número, SID e ID

| Dato | Ejemplo ilustrativo | Dónde se usa |
|---|---|---|
| Número de salida | `+1...` o el prefijo que corresponda | Identidad telefónica del origen |
| Account SID Twilio | `AC...` | Cuenta que autoriza la importación |
| SID del número Twilio | `PN...` | Identificador del recurso en Twilio |
| `phoneNumberId` Vapi | Identificador asignado al importar | Solicitud de llamada de Vapi |
| Destino | Número real internacional del destinatario | `customer.number` |

En las solicitudes Vapi, **`phoneNumberId` es el identificador del número dentro de Vapi**, no el SID del número Twilio. [Fuente oficial: conexión de llamadas Twilio en Vapi](https://docs.vapi.ai/gpt-live/configuration).

No utilices los ejemplos de esta tabla como números marcables.

## Antes de avanzar

- [ ] Identifiqué cuál es el origen y cuál es el destino.
- [ ] El número de origen aparece importado en la organización Vapi correcta.
- [ ] Tengo su `phoneNumberId`.
- [ ] Conozco si Twilio está en trial y verifiqué el destino si corresponde.
- [ ] Revisé permisos para el país de destino.
- [ ] No publiqué claves ni fichas con datos personales.

Continúa con [02. Crear el agente de voz](02-agente-de-voz.md).

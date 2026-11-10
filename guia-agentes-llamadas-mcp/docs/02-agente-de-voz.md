# 02. Crear y probar el agente de voz

**Resultado esperado:** un asistente Vapi publicado que pueda hablar español, escuchar la respuesta y seguir un objetivo concreto. El modelo de Claude o ChatGPT que da la orden desde el chat puede ser distinto del modelo que habla durante la llamada.

## 1. Crear el asistente

En [Vapi Dashboard](https://dashboard.vapi.ai/), abre **Assistants → Create Assistant**. Puedes usar la flecha del botón para elegir una plantilla. **Customer Support**, **Lead Qualification**, **Appointment Scheduler** e **Info Collector** ya incluyen una primera frase, un prompt y una configuración de modelo.

Para configurar desde cero, elige un preset y escribe **First Message** y **System Prompt**. La primera frase se pronuncia al comenzar; el prompt define identidad, comportamiento y conversación. Al terminar, selecciona **Publish → revisar cambios → Next → Publish**. Para ensayar desde el navegador, pulsa **Talk** y permite el micrófono. [Fuente oficial: Assistants quickstart](https://docs.vapi.ai/assistants/quickstart).

**Recomendación del repositorio:** empieza con un agente que solo confirme una preferencia; agrega agenda, CRM o ventas después de que la llamada básica funcione.

## 2. Configurar el español

El idioma debe estar alineado en tres lugares: lo que escucha el transcriptor, lo que genera el modelo y lo que pronuncia la voz.

Una configuración documentada de transcripción es **Deepgram → Nova 3 → Multi**. Entra en la sección **Transcriber** del asistente y selecciona esas opciones. `Multi` permite detectar idiomas, entre ellos español; agrega el idioma deseado al prompt y vuelve a publicar. [Fuente oficial: configuración multilingüe](https://docs.vapi.ai/customization/multilingual).

Para la voz, Vapi documenta voces V2 con idioma fijo `es`. Esta configuración es un ejemplo válido de sus campos, que puedes seleccionar en el panel o aplicar desde la API si trabajas con ella:

```json
{
  "voice": {
    "provider": "vapi",
    "voiceId": "Savannah",
    "version": 2,
    "language": "es"
  }
}
```

Escucha la voz antes de elegirla. El acento indicado en una ficha no significa que solo hable ese idioma. [Fuente oficial: Vapi Voices](https://docs.vapi.ai/providers/voice/vapi-voices).

Si el preset de tu cuenta usa una arquitectura que integra voz y modelo, revisa sus opciones específicas; no fuerces los campos de una arquitectura distinta. Para seguir este ejemplo, utiliza un asistente con transcriptor y voz configurables.

## 3. Texto completo propuesto para una prueba

Lo siguiente es una **plantilla original de este repositorio**, no un prompt oficial ni una integración de agenda. Reemplaza las partes entre corchetes antes de usarla.

**Nombre propuesto:** `Agente de prueba en español`.

### First Message

```text
Hola, soy el asistente virtual de [NOMBRE DEL NEGOCIO]. Esta es una
llamada de prueba solicitada por ti. ¿Tienes un minuto para probar
una pregunta conmigo?
```

### System Prompt

```text
IDENTIDAD
Eres el asistente virtual de [NOMBRE DEL NEGOCIO]. Hablas español
claro y natural. Si preguntan si eres una persona, explica que eres
un asistente de inteligencia artificial.

OBJETIVO DE ESTA PRUEBA
Comprobar que puedes escuchar y conversar por teléfono. Pregunta
si el interlocutor prefiere recibir información por la mañana o
por la tarde. Repite la preferencia y pide confirmación.

FORMA DE HABLAR
- Usa frases breves y una pregunta por turno.
- Espera la respuesta. No hables como si leyeras una lista.
- Si no escuchas bien, pide repetir una vez.
- Si la respuesta es ambigua, aclara antes de confirmar.

LÍMITES
- No afirmes que agendaste una cita o actualizaste una base de datos.
- No prometas precios, disponibilidad ni condiciones que no conoces.
- No pidas contraseñas, códigos de verificación ni datos de pago.
- Si la persona no quiere continuar, respeta su decisión y despídete.
- Si contesta otra persona, no reveles información privada.
- Si preguntan algo ajeno a la prueba, explica el alcance y ofrece
  que una persona del negocio atienda la consulta después.

CIERRE
Después de confirmar mañana o tarde, agradece la prueba y despídete.
No prolongues la conversación con nuevas preguntas.
```

El prompt orienta al modelo. Para ejecutar una acción real como terminar la llamada, transferirla o escribir en una agenda, configura además la herramienta compatible correspondiente. Decir “ya quedó agendado” no constituye una reserva.

## 4. Publicar y probar antes de llamar a un celular

Esta secuencia de comprobación es nuestra recomendación:

1. Revisa que el saludo no conserve ningún `[MARCADOR]`.
2. Publica la versión.
3. En **Talk**, responde “por la tarde”. Debe repetir y confirmar esa preferencia.
4. Interrúmpelo cuando esté hablando. Evalúa si retoma la conversación con naturalidad.
5. Responde “no puedo hablar”. Debe aceptar la negativa.
6. Pregunta “¿ya agendaste mi cita?”. Debe explicar que esta prueba no agenda.
7. Si modificas el prompt, publica de nuevo antes de repetir.

### Registro propuesto de la prueba

| Prueba | Resultado que buscas | Tu resultado |
|---|---|---|
| Saludo | Negocio correcto y presentación como asistente | Pendiente |
| Español | Comprende y responde en español | Pendiente |
| Turnos | Hace una pregunta y espera | Pendiente |
| Preferencia | Repite sin inventar | Pendiente |
| Negativa | Cierra con respeto | Pendiente |
| Agenda | No afirma haber hecho una reserva | Pendiente |

## 5. Probar la telefonía desde el panel

Abre **Phone Numbers**, selecciona el número importado, pulsa **Test**, elige **Single Number**, introduce tu propio número de destino y selecciona este asistente. **Call** inicia la llamada; **Schedule Call** permite programarla. Después revisa **Logs → Calls**. Esta prueba utiliza telefonía y puede generar cobro. [Fuente oficial: Phone calls](https://docs.vapi.ai/quickstart/phone).

Haz esta llamada antes de conectar MCP. Si desde el panel no funciona, consulta [Costos y diagnóstico](08-costos-y-diagnostico.md); conectar Claude o ChatGPT todavía no resolverá un bloqueo del operador.

## 6. Anotar lo necesario para MCP

- `assistantId`: identificador del asistente publicado.
- `phoneNumberId`: identificador del número de origen importado en Vapi.
- Teléfono propio de prueba en formato internacional.
- Nombre de la organización Vapi donde están ambos recursos.

Guarda los identificadores en tu configuración local. Las claves privadas se configuran en el entorno seguro indicado por los siguientes capítulos y no dentro de los prompts.

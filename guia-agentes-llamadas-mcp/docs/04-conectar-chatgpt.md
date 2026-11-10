# Conectar el MCP de llamadas a ChatGPT

Esta ruta permite ordenar una llamada desde un chat de ChatGPT. El agente de voz de Vapi mantiene la conversación telefónica y Twilio suministra la línea. ChatGPT solicita acciones a través de MCP; no transporta el audio de la llamada.

**Estado de la guía:** configuración compuesta a partir de documentación oficial consultada el 9 de noviembre de 2026. No se ha probado de extremo a extremo con cuentas, claves ni llamadas reales. La disponibilidad de MCP personalizados y de Secure MCP Tunnel depende de la cuenta y de los permisos del workspace. No compres una suscripción suponiendo que una opción aparecerá: comprueba primero tu cuenta.

## 1. Por qué se utiliza un túnel

Vapi publica un MCP en `https://mcp.vapi.ai/mcp` que utiliza una clave privada como Bearer. No basta con pegar esa URL en un formulario que solo permita OAuth: una clave API y un inicio de sesión OAuth son métodos diferentes.

La solución descrita es:

```text
ChatGPT web
    -> Secure MCP Tunnel de tu organización
    -> tunnel-client ejecutándose en tu computadora
    -> MCP oficial Vapi, con Bearer añadido por tunnel-client
    -> Vapi -> número importado -> red telefónica
```

El túnel añade una ruta privada de acceso y permite configurar el header requerido por Vapi. El MCP de Vapi ya es remoto; en este caso usamos el túnel para adaptar la autenticación. No hace falta crear un servidor MCP propio ni usar `npx mcp-remote` para esta ruta.

La configuración del cliente admite headers separados para las consultas normales y para el descubrimiento inicial. Usa ambos como aparece en el archivo de ejemplo. [Configuración oficial de tunnel-client](https://github.com/openai/tunnel-client/blob/master/docs/configuration.md).

## 2. Lo que debes tener preparado

Antes de comenzar:

- Un asistente de voz creado y probado en Vapi.
- Un número importado a Vapi que admita llamadas salientes. Los números gratuitos de Vapi son solo para entrantes, según su documentación MCP.
- Tu clave **privada Vapi**. No es la clave pública del widget web.
- Acceso a la organización correcta en OpenAI Platform.
- Permiso para crear y usar un MCP personalizado en el workspace de ChatGPT.
- Una computadora con conexión a Internet que permanecerá encendida durante las pruebas.

Identifica estos valores antes de ejecutar comandos:

| Valor | Qué representa | Dónde se usa |
|---|---|---|
| `tunnel_id` | Identificador del túnel, empieza por `tunnel_` | Archivo YAML y conexión ChatGPT |
| `CONTROL_PLANE_API_KEY` | Clave runtime OpenAI con permisos de túnel | Cliente local del túnel |
| `VAPI_AUTH_HEADER` | Texto `Bearer ` seguido de la clave privada Vapi | Header que el cliente envía a Vapi |

No introduzcas la clave Vapi en el chat ni en una URL. Tampoco uses una clave administrativa OpenAI para mantener el cliente en ejecución.

## 3. Crear el túnel y descargar el cliente

1. Abre [OpenAI Platform: Tunnels](https://platform.openai.com/settings/organization/tunnels).
2. Selecciona la organización desde la que quieres gestionar esta integración.
3. Crea un túnel. Ponle un nombre reconocible, por ejemplo `vapi-llamadas-prueba`.
4. Copia el identificador generado. No inventes un ID de ejemplo.
5. Comprueba las asociaciones del túnel: debe incluir la organización Platform correcta y el workspace ChatGPT desde el que lo usarás. Asociarlo solo a Platform no garantiza que aparezca en ChatGPT.
6. Descarga `tunnel-client` desde el enlace ofrecido en Tunnels o desde las [versiones oficiales de OpenAI](https://github.com/openai/tunnel-client/releases/latest). Escoge el sistema y arquitectura que correspondan a tu equipo.
7. Extrae el paquete y conserva juntos sus archivos. Ejecuta el binario desde la carpeta extraída o agrégala al `PATH` de tu sistema.
8. Abre Terminal en macOS o PowerShell en Windows y comprueba que responde `tunnel-client help quickstart`. Si ejecutas desde su propia carpeta, usa `./tunnel-client` en Mac o `.\tunnel-client.exe` en Windows.

Quien crea o edita el túnel necesita **Tunnels Read + Manage**. Quien lo ejecuta o selecciona en ChatGPT necesita **Tunnels Read + Use**. Son permisos de la organización Platform, distintos de los permisos del workspace ChatGPT. Si Tunnels muestra un bloqueo, resolver esos permisos es el siguiente paso; cambiar el YAML no lo elimina. [Guía oficial Secure MCP Tunnel](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels).

## 4. Crear una clave runtime OpenAI

Abre [API keys de la organización](https://platform.openai.com/settings/organization/api-keys). Crea la clave runtime con los permisos necesarios para leer y usar el túnel. Si tu organización usa roles, el administrador debe asignar esos permisos al usuario o cuenta de servicio que representa la clave.

La clave runtime autentica el cliente contra OpenAI. La clave Vapi autentica las peticiones contra Vapi. No son intercambiables. Los pasos de este documento no crean ni usan una clave administrativa.

## 5. Copiar el archivo de configuración

Copia [el ejemplo YAML](../examples/vapi-tunnel.example.yaml) en una carpeta de trabajo y nómbralo `vapi-tunnel.yaml`. Edita `tunnel_REEMPLAZAR` con tu ID real:

```yaml
config_version: 1
control_plane:
  tunnel_id: tunnel_REEMPLAZAR
  api_key: env:CONTROL_PLANE_API_KEY
mcp:
  server_urls:
    - channel: main
      url: https://mcp.vapi.ai/mcp
  extra_headers:
    Authorization: env:VAPI_AUTH_HEADER
  discovery_extra_headers:
    Authorization: env:VAPI_AUTH_HEADER
health:
  listen_addr: 127.0.0.1:8080
```

Mantén la indentación con espacios. No reemplaces `env:CONTROL_PLANE_API_KEY` ni `env:VAPI_AUTH_HEADER` por secretos: el programa leerá sus valores del entorno cuando arranque.

La dirección `127.0.0.1:8080` sirve para consultar el estado local del cliente. No es la URL que debes pegar como MCP remoto en ChatGPT y no es el puerto de una llamada telefónica.

## 6. Introducir claves y arrancar en macOS

Abre Terminal, entra a la carpeta que contiene tu YAML y ejecuta este bloque en **zsh**. Los dos campos de entrada no muestran las claves ni escriben su valor literal en los comandos del historial:

```zsh
read -rs "CONTROL_PLANE_API_KEY?Clave runtime OpenAI: "
echo
export CONTROL_PLANE_API_KEY

read -rs "VAPI_PRIVATE_KEY?Clave privada Vapi: "
echo
export VAPI_AUTH_HEADER="Bearer ${VAPI_PRIVATE_KEY}"
unset VAPI_PRIVATE_KEY

tunnel-client run --config ./vapi-tunnel.yaml
```

Si el binario está en la carpeta actual y no en el PATH, cambia la última línea a `./tunnel-client run --config ./vapi-tunnel.yaml`.

No cierres esa ventana. Los valores se cargan en ese proceso y sus hijos; una nueva ventana Terminal no los recibe automáticamente. Al reiniciar el cliente en otra sesión debes introducirlos otra vez o configurar un gestor de secretos para una instalación permanente.

## 7. Introducir claves y arrancar en Windows

Abre **PowerShell 7**, entra a la carpeta que contiene el YAML y ejecuta:

```powershell
$env:CONTROL_PLANE_API_KEY = Read-Host "Clave runtime OpenAI" -MaskInput
$vapiKey = Read-Host "Clave privada Vapi" -MaskInput
$env:VAPI_AUTH_HEADER = "Bearer $vapiKey"
Remove-Variable vapiKey

tunnel-client run --config .\vapi-tunnel.yaml
```

Si el ejecutable está en la carpeta actual, usa `.\tunnel-client.exe run --config .\vapi-tunnel.yaml` en la última línea. `-MaskInput` requiere PowerShell 7; comprueba la versión con `$PSVersionTable.PSVersion`. No pegues las claves como argumentos de ejecución para resolver un problema de versión.

Las variables duran en esa sesión de PowerShell. Mantén la ventana abierta. El YAML no guarda las claves.

## 8. Comprobar el cliente antes de abrir ChatGPT

Abre `http://127.0.0.1:8080/ui` en el navegador de la misma computadora. Comprueba que el cliente está conectado, preparado para atender peticiones y realizando la comunicación con el túnel. También están disponibles `/healthz` y `/readyz` en ese mismo puerto.

Si el puerto 8080 está ocupado, cambia `health.listen_addr` por `127.0.0.1:8081`, reinicia y abre el puerto nuevo. Si aparece un error de clave, autorización o conexión, resuélvelo antes de crear el plugin.

No declares completada la integración solo porque el proceso arrancó: la prueba final es que ChatGPT pueda consultar Vapi mediante una herramienta.

## 9. Añadir el túnel a ChatGPT

Los nombres de los menús pueden cambiar. La documentación actual describe esta ruta en ChatGPT web:

1. Abre [ChatGPT Plugins](https://chatgpt.com/plugins).
2. Pulsa `+` y selecciona **Add custom MCP server**.
3. Nombre: `Llamadas Vapi`. Descripción sugerida: `Consultar asistentes y numeros Vapi; realizar una llamada solo cuando se autorice expresamente`.
4. En **Connection**, elige **Tunnel**.
5. Selecciona tu túnel o pega su `tunnel_id` real.
6. Para este diseño, elige **No authentication** como autenticación de la conexión. El cliente local añade el Bearer al comunicarse con Vapi; no se ha configurado un OAuth individual de cada usuario.
7. Revisa el aviso que muestra ChatGPT y crea el plugin.
8. Instálalo y revisa las herramientas descubiertas.

**No authentication no significa un servidor público sin protección.** El acceso a este camino depende de los permisos y asociaciones del túnel. Significa que no añadimos una segunda autenticación OAuth por usuario sobre este diseño. Si configuras OAuth, el header `Authorization` reenviado desde el conector puede prevalecer sobre el header estático del cliente y cambiar su comportamiento.

Si tu cuenta no permite esta opción, no pruebes autenticaciones al azar: usa la ruta Claude Desktop o la [ruta API](05-openai-api.md), o configura una pasarela con OAuth apropiado para un servicio compartido. [Alta oficial de MCP personalizado](https://developers.openai.com/api/docs/guides/custom-mcp-server).

## 10. Primera consulta, sin llamar

Abre una conversación nueva. Escribe `@` y selecciona `Llamadas Vapi`. Pega:

> Usa Llamadas Vapi. Ejecuta list_assistants y list_phone_numbers. Muéstrame los nombres, números e identificadores devueltos. No llames, no crees asistentes y no modifiques la configuración.

Comprueba que se ejecutaron herramientas reales y que sus IDs coinciden con tu panel Vapi. Una explicación escrita por el modelo no prueba una conexión.

Conserva el `assistantId` y `phoneNumberId` correctos. El segundo es el identificador interno del número dentro de Vapi; no es el teléfono escrito en formato `+57...` ni un SID de Twilio.

## 11. Primera llamada, cuando decidas probarla

Usa primero un número tuyo o de una persona que espera la prueba. Sustituye los campos entre corchetes antes de enviar:

> Haz una sola llamada de prueba con create_call. Usa assistantId [ID_REAL] y phoneNumberId [ID_REAL]. Destino: [NUMERO_REAL_E164]. El destinatario espera esta prueba. No hagas reintentos automáticos ni llames a otros números. Antes de ejecutar, muéstrame el origen, el destino y el objetivo. Cuando autorice esa llamada concreta, ejecútala y devuelve el callId recibido.

Después consulta `get_call` con el ID devuelto. Revisa en Vapi y Twilio el intento real, su estado y los resultados disponibles. `queued` o un `callId` significan que se creó una solicitud; no garantizan que alguien contestó.

La orden de pedir confirmación es una instrucción conversacional, no un límite técnico del proveedor. Para operación empresarial, los límites de destinos, presupuesto, horarios y repetición deben aplicarse también en una capa de servicio.

## 12. Si no funciona

| Síntoma | Qué revisar primero |
|---|---|
| No aparece **Add custom MCP server** | Permisos y disponibilidad de la cuenta/workspace; la guía no garantiza acceso por plan |
| El túnel no se lista | Asociación al workspace y permiso Tunnels Read + Use |
| El cliente arranca pero no está preparado | Conexión HTTPS, clave runtime, ID y mensajes de estado locales |
| Vapi devuelve 401/403 | Clave privada Vapi correcta; `Bearer ` con un espacio; variables presentes en la sesión que lanzó el proceso |
| La consulta funciona, la llamada no | Número importado con salida, saldo, permisos geográficos y destino E.164 |
| Las herramientas están desactualizadas | Reiniciar/desplegar el servicio correspondiente, refrescar el plugin y abrir otro chat |
| Funcionaba y ahora falla | Computadora suspendida, proceso cerrado o credencial revocada |

Detén el cliente con `Ctrl+C` cuando termines las pruebas. Esto impide nuevas acciones por ese camino mientras está detenido; no debe interpretarse como una orden de colgar llamadas ya creadas en Vapi.

## Fuentes

- [Vapi MCP oficial: endpoint, herramientas y autenticación](https://docs.vapi.ai/sdk/mcp-server).
- [Secure MCP Tunnel: instalación, permisos y conexión](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels).
- [Configuración de tunnel-client: YAML, referencias a secretos y headers](https://github.com/openai/tunnel-client/blob/master/docs/configuration.md).
- [Añadir MCP personalizado a ChatGPT](https://developers.openai.com/api/docs/guides/custom-mcp-server).
- [Conectar, probar y refrescar el plugin](https://developers.openai.com/plugins/deploy/connect-chatgpt).

# Conectar Claude con el servicio que hará las llamadas

Esta conexión permite dar órdenes desde Claude: elegir el asistente de voz y el número de salida, iniciar una llamada autorizada y consultar su resultado. El audio de la llamada lo atiende el asistente configurado en Vapi. La conversación escrita de Claude no se convierte por sí sola en el diálogo telefónico.

## Antes de configurar

Debes tener una cuenta de Vapi con un asistente de voz guardado, un número habilitado para llamadas salientes y una clave privada. Conserva los identificadores del asistente y del número: no son el nombre del asistente ni sus dígitos telefónicos. Consulta las secciones anteriores de esta guía para preparar esos elementos.

Vapi publica un servidor MCP en `https://mcp.vapi.ai/mcp`. Recibe la clave de Vapi como autenticación Bearer. Este capítulo conecta Claude con ese servidor; no necesitas desarrollar uno propio. [Documentación MCP de Vapi](https://docs.vapi.ai/sdk/mcp-server).

## Opción A. Claude Desktop mediante un puente local

Esta es la alternativa documentada cuando tu cuenta no permite configurar encabezados de autenticación en un conector web. Necesita que Claude Desktop y el proceso local estén disponibles para enviar órdenes. Una llamada ya aceptada se ejecuta en el servicio de voz.

### 1. Instala y comprueba Node.js

Instala una versión LTS vigente desde [nodejs.org](https://nodejs.org/). Abre una terminal nueva y ejecuta:

```bash
node --version
npx --version
```

Ambas órdenes deben mostrar una versión. Si aparece que no se encuentra el comando, termina la instalación y abre de nuevo la terminal y Claude. El puente necesita Node.js; su documentación indica un mínimo de 18, pero usa una LTS vigente. [Instrucciones del puente](https://github.com/punkpeye/mcp-remote).

### 2. Abre la configuración de Claude Desktop

En la aplicación de escritorio abre **Settings > Developer > Edit Config**. Las rutas del archivo son:

| Sistema | Archivo |
| --- | --- |
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |

Estos ajustes pertenecen a la aplicación de escritorio. Un archivo guardado dentro de este repositorio no cambia automáticamente Claude. [Guía oficial para servidores locales MCP](https://modelcontextprotocol.io/docs/develop/connect-local-servers).

### 3. Copia el ejemplo y coloca la clave en tu archivo local

Abre [el ejemplo de configuración](../examples/claude_desktop_config.example.json). Si tu archivo de Claude está vacío, puedes copiar su contenido completo. Si ya contiene otros servidores, incorpora únicamente el objeto `vapi-mcp` dentro del objeto `mcpServers` existente. Conserva los demás servidores y el resto de los ajustes.

En tu copia local sustituye `REEMPLAZAR_POR_CLAVE_PRIVADA_VAPI` por la clave privada. Conserva `Bearer` y el espacio que lo sigue. No reemplaces `${AUTH_HEADER}`: es la referencia que el puente resuelve usando `env`.

El encabezado se construye así:

```text
env.AUTH_HEADER = Bearer TU_CLAVE_PRIVADA
argumento del puente = Authorization:${AUTH_HEADER}
encabezado enviado = Authorization: Bearer TU_CLAVE_PRIVADA
```

La forma sin espacios en el argumento evita un problema de escape que el puente documenta para Windows. El primer argumento `-y` evita que la instalación de `mcp-remote` quede esperando una respuesta. [Opciones y encabezados de mcp-remote](https://github.com/punkpeye/mcp-remote).

### 4. Guarda sin publicar secretos

El ejemplo del repositorio lleva solo un marcador. La configuración real de Claude está en las rutas del sistema anteriores y contiene tu secreto en texto. No la subas a GitHub ni la pegues en un chat.

Si guardas una copia de trabajo en el repositorio, llámala `claude_desktop_config.local.json` y verifica que Git la ignore antes de añadir tu clave:

```bash
git check-ignore claude_desktop_config.local.json
```

El comando debe mostrar ese nombre. Si no devuelve nada, agrega `claude_desktop_config.local.json` a `.gitignore` antes de escribir la clave. Evita `git add .` si tienes dudas sobre archivos locales. Si una clave se publicó, elimínala desde Vapi y crea otra: borrar el archivo de la última versión no borra el historial.

Las claves privadas de Vapi dan acceso a su organización. Usa una organización de prueba separada cuando quieras separar sus recursos y facturación de producción. [Claves API de Vapi](https://docs.vapi.ai/security-and-privacy/api-keys).

### 5. Reinicia y verifica primero con lecturas

Cierra Claude completamente y vuelve a abrirlo. Abre una conversación y verifica que el conector aparezca entre las herramientas. Envía este mensaje:

> Comprueba la conexión con Vapi. Lista mis asistentes y mis números disponibles. Muéstrame sus nombres e identificadores. Esta comprobación es de lectura: no crees asistentes ni hagas llamadas.

El resultado correcto es una lista de los recursos de tu propia organización. Una lista vacía no demuestra que el número esté habilitado: comprueba que estés usando la organización y la clave correctas.

Después usa [el prompt del operador MCP](../prompts/operador-mcp.md). La prueba de llamada debe tener un número destino que controles o para el que tengas autorización, asistente e identificador del número de salida explícitos.

## Opción B. Conector remoto directo en Claude web

Los conectores remotos se configuran en **Customize > Connectors > + Add > Add custom connector**. En Team y Enterprise puede ser necesario que un propietario lo agregue desde **Organization settings > Connectors**. La documentación consultada incluye los planes Free, Pro, Max, Ultra, Team y Enterprise; Free admite un conector personalizado. La disponibilidad en tu cuenta y las políticas del espacio pueden limitar lo que aparece. [Ayuda de Claude para conectores remotos](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp).

**Comprueba antes si existe Request headers.** Esa función está en beta y solo está disponible para determinadas organizaciones. Si no aparece, utiliza la opción A; pegar la URL sin la autenticación no completa la conexión. [Autenticación de conectores personalizados](https://claude.com/docs/connectors/custom/add-unlisted).

Cuando la cuenta sí muestra esos campos, configura:

| Campo | Valor |
| --- | --- |
| Name | `Vapi llamadas` |
| MCP server URL | `https://mcp.vapi.ai/mcp` |
| Authentication | `No sign-in` |
| Request header name | `Authorization` |
| Request header value | `Bearer TU_CLAVE_PRIVADA_VAPI` |
| Required | Activado |

`No sign-in` indica que no usarás un flujo OAuth. La clave del encabezado sigue siendo obligatoria. Claude envía el valor exactamente como lo escribes, por lo que debes incluir el prefijo `Bearer `.

Guarda el conector y actívalo en la conversación con **+ > Connectors**. Repite primero la prueba de lectura del paso 5. No inventes un OAuth Client ID o Client Secret si la interfaz los solicita: ese formulario no sustituye el encabezado Bearer.

La conexión remota sale desde los servidores de Anthropic. No escribas `localhost` como servidor remoto ni la dirección de tu computador; Vapi ya ofrece una dirección pública. [Requisitos de red de Claude](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp).

## Si algo falla

| Síntoma | Comprobación concreta |
| --- | --- |
| No aparece el servidor | Revisa JSON válido, que editaste el archivo de Claude y que cerraste toda la aplicación. |
| No se encuentra `npx` | Comprueba la instalación de Node y su disponibilidad desde una terminal nueva. En macOS `command -v npx` y en Windows `where.exe npx` muestran su ubicación. |
| Respuesta 401 | Verifica clave privada, organización y el prefijo `Bearer `; no envíes la clave al pedir ayuda. |
| No hay Request headers | Usa la configuración local de Desktop; el acceso a esa función remota no es universal. |
| La lectura funciona, la llamada falla | Revisa el número de salida, sus permisos de destino, el saldo y el asistente en el servicio de voz. MCP conectado no implica telefonía lista. |

Para fallos de arranque, los registros de Claude están en `~/Library/Logs/Claude` en macOS y `%APPDATA%\Claude\logs` en Windows. Revisa `mcp.log` y los archivos del servidor. Comparte solo errores con secretos ocultos. [Diagnóstico de MCP local](https://modelcontextprotocol.io/docs/develop/connect-local-servers).

## Qué se ha comprobado en esta guía

La configuración se basa en las fuentes enlazadas. No representa una conexión a tu cuenta, una validación del operador telefónico ni una llamada real. La comprobación final consiste en listar tus recursos y completar una llamada de prueba autorizada, verificando después el estado y el resultado en el servicio de voz.

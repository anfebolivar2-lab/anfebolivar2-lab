# Guía: conectar Claude Code con Codex (arquitecto y obrero)

Basada en la guía gratuita de Luis Padial (@luispadialx). Claude piensa y revisa; Codex ejecuta.
Lo que ejecuta Codex se descuenta de tus límites de Codex, no de los de Claude.

## Qué necesitás
- Claude Code instalado y funcionando con tu plan de Claude.
- Una cuenta de ChatGPT (vale la gratuita) o una API key de OpenAI. Con plan de pago tenés más margen.
- Node.js 18.18 o superior. Comprobalo con `node --version`.

El conector es un plugin oficial de OpenAI, gratis y de código abierto: github.com/openai/codex-plugin-cc

## 1. Instalación (dentro de Claude Code, en el chat)

```
/plugin marketplace add openai/codex-plugin-cc
/plugin install codex@openai-codex
/reload-plugins
/codex:setup
```

`/codex:setup` te dice si Codex está instalado y con sesión iniciada. Si no, te ofrece instalarlo.

Si hace falta hacerlo a mano:

```
# instalar Codex (en la terminal)
npm install -g @openai/codex

# iniciar sesión con tu cuenta de ChatGPT (desde Claude Code, con el !)
!codex login
```

`!codex login` abre el navegador para iniciar sesión con ChatGPT. Corrélo en tu computadora, no en un
entorno remoto: el login espera un retorno a `localhost`.

Para comprobar que funciona: al escribir `/codex` tienen que aparecer los comandos del plugin, y en
`/agents` un agente nuevo llamado `codex:codex-rescue`.

## 2. Comandos

| Comando | Para qué sirve |
|---|---|
| `/codex:rescue` | Le pasás una tarea a Codex: arreglar un bug, implementar algo, investigar un fallo. Codex sí toca archivos. |
| `/codex:review` | Codex revisa tus cambios sin tocar nada. |
| `/codex:adversarial-review` | Revisión de "abogado del diablo": cuestiona el diseño y las decisiones. |
| `/codex:status` | Ves qué tareas de Codex están en marcha. |
| `/codex:result` | Ves el resultado de una tarea terminada. |
| `/codex:cancel` | Parás una tarea en segundo plano. |
| `/codex:transfer` | Pasás la conversación actual a Codex con el mismo contexto. |

Ejemplos:

```
/codex:rescue investiga por qué falla el login y arréglalo con el cambio mínimo
/codex:rescue --background implementa el formulario de contacto
/codex:review --background
/codex:adversarial-review cuestiona si esta forma de guardar los datos es segura
```

Con `--background` las tareas largas corren por detrás mientras seguís con Claude.
También podés decirle a Claude en lenguaje normal: "pásale esta tarea a Codex".

## 3. El flujo: arquitecto, obrero, inspector

1. **Claude diseña el plan.** Le explicás lo que querés y le pedís tareas pequeñas y concretas. No escribe código.
2. **Codex construye cada tarea** con `/codex:rescue`, mejor en segundo plano.
3. **Claude revisa y decide.** Si algo no cuadra, le devuelve la tarea con instrucciones.

Prompt para arrancar (cambiá lo que va en mayúsculas):

```
Vamos a trabajar en equipo: tú eres el arquitecto y Codex es el que ejecuta.

Objetivo: QUÉ QUIERES CONSTRUIR.

1. Analiza el proyecto y hazme un plan dividido en tareas pequeñas,
   cada una con qué archivos toca y cómo sabremos que está bien.
   Enséñamelo y espera a que te dé el ok.
2. Cuando lo apruebe, delega cada tarea a Codex con /codex:rescue
   en segundo plano. No escribas tú el código.
3. Cuando Codex termine, revisa el resultado contra el plan.
   Si algo falla, vuelve a pasárselo a Codex con instrucciones claras.
4. Al final, lanza /codex:review y resúmeme qué se ha hecho.
```

Cuanto más concreta sea cada tarea, mejor trabaja Codex. "Arregla la app" sale mal.
"En el archivo de login, haz que el error de contraseña se muestre debajo del campo" sale bien.

## 4. Errores típicos

| Problema | Solución |
|---|---|
| No aparecen los comandos `/codex` | `/reload-plugins`. Si sigue igual, cerrá y abrí Claude Code. |
| `/codex:setup` dice que no hay sesión | `!codex login` y entrá con ChatGPT. |
| Error de versión de Node | Instalá Node 18.18 o más (LTS) desde nodejs.org. |
| Codex tarda mucho | Es normal en tareas grandes. Lanzalas con `--background`. |
| Codex hace algo distinto a lo que querías | La tarea era demasiado vaga. Pedile a Claude que la parta en pasos más pequeños. |

## Cómo estirar tus límites
- Que Claude no escriba código largo. Si lo ves implementando, recordale que eso se lo pasa a Codex.
- Revisiones de código con `/codex:review` en vez de pedirle a Claude que lo revise todo.
- Tareas cortas y claras: menos idas y vueltas, menos consumo.
- Empezá sin subir de plan: probá una semana con los planes básicos y mirá cuál se agota antes.

Cuidado con el review gate: `/codex:setup --enable-review-gate` hace que Codex revise cada respuesta de
Claude antes de terminar. Puede entrar en bucle y consumir los límites de los dos. Activalo solo si vas
a estar mirando la sesión.

## Bonus: Graphify (que los dos lean menos)
Convierte tu proyecto (código, documentos, PDFs) en un mapa de conexiones, así el asistente consulta
el mapa en vez de abrir archivo por archivo. El mapa del código se genera en tu computadora, sin gastar
créditos de IA. No conecta Claude con Codex, pero funciona en los dos.

Necesitás Python 3.10 o más. En la terminal normal (no dentro de Claude Code):

```
# 1. instalar Graphify (el paquete lleva dos "y")
uv tool install graphifyy
# o, si no tenés uv:  pipx install graphifyy

# 2. registrarlo en Claude Code
graphify install

# 3. registrarlo también en Codex
graphify install --platform codex
```

Uso, dentro de tu proyecto:

```
/graphify .     # en Claude Code
$graphify .     # en Codex (usa $ en vez de /)
```

Crea una carpeta `graphify-out` con el mapa visual para abrir en el navegador, un informe con lo más
importante del proyecto y el grafo que usan los asistentes.

Ojo: el paquete oficial es `graphifyy`, con doble y. Otros paquetes con nombre parecido no son del
mismo equipo. Repo oficial: github.com/Graphify-Labs/graphify

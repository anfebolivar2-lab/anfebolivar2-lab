# Cómo trabajamos: Claude Code + Codex

Responde siempre al dueño en español.

## Roles

Claude Code planea el trabajo y revisa los cambios. Codex, la herramienta de OpenAI que el script del entorno ya instaló, escribe el código.
Claude Code solo escribe cambios largos de código si el dueño se lo pide o si Codex no está disponible.

## Al empezar cada chat

1. Ejecuta `codex login status`.
2. Si dice «Logged in using an API key», Codex está listo. El proxy del entorno pone la clave real.
3. Si no hay sesión, inicia sesión y comprueba que Codex responde.

   ```bash
   echo sk-proxy-injected | codex login --with-api-key
   codex exec --skip-git-repo-check "Responde solo: OK" < /dev/null
   ```

   Si devuelve un error 401, la clave guardada en el entorno no sirve. Avisa al dueño y ofrécele `codex login --device-auth` como alternativa para entrar con un código de ChatGPT.

## Cómo delegar a Codex

Escribe el encargo en `tarea.md`. Indica qué archivos y funciones debe cambiar, qué pruebas debe correr e incluye «no hagas commits».

```bash
codex exec -s workspace-write "$(cat tarea.md)" < /dev/null
```

Incluye siempre `< /dev/null`. Sin eso, Codex se queda esperando.

## Antes de subir cambios

Claude Code lee el diff completo (la lista de cambios) y corre las pruebas del repositorio. Si hay cambios visuales, prueba la pantalla en el navegador con Playwright y manda una captura al dueño.

## Reglas obligatorias del dueño

- Nunca trabajes ni hagas push en `main`. Usa una rama nueva y un PR en borrador para cada cambio. El dueño decide si lo incorpora.
- No borres archivos, datos ni historial. Si una tarea requiere borrar algo, pregunta antes.
- Solo toca la base de datos o los datos de usuarios en Supabase, o despliega funciones, si el dueño lo pide.
- Todo cambio debe poder deshacerse cerrando el PR o revirtiendo el commit.
- Explica al dueño en español sencillo qué se hizo, cuánto tardó y qué falta.

## Notas de este repositorio

- Repo del perfil de GitHub (`README.md`) y la página de la Tienda María (`index.html`, `vitrina.html`, `api/`, `sw.js`).
- No hay pruebas automáticas: revisa los cambios abriendo las páginas en el navegador.
- `guia-claude-codex.md` explica con más detalle el flujo Claude + Codex.

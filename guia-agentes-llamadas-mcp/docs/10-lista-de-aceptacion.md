# Lista de aceptación de tu instalación

Copia esta lista en tus notas privadas y registra fecha y resultado. Las casillas describen verificaciones que debes ejecutar con tus cuentas; no se afirman como completadas por este repositorio.

## Telefonía

- [ ] El número pertenece a la cuenta del proveedor y tiene capacidad de voz.
- [ ] El país destino está autorizado; saldo y restricciones de prueba revisados.
- [ ] El número está importado en Vapi y su ID corresponde al teléfono correcto.
- [ ] Mi móvil recibe una llamada desde el panel, sin intervenir Claude ni ChatGPT.

## Agente de voz

- [ ] El asistente correcto está publicado.
- [ ] Saluda en español y se presenta como asistente virtual.
- [ ] Comprende una interrupción y una petición de finalizar.
- [ ] No promete acciones para las que no tiene herramientas conectadas.
- [ ] La duración y el cierre están configurados y comprobados.

## MCP

- [ ] El cliente consulta asistentes y números mediante herramientas reales.
- [ ] Los datos devueltos coinciden con el panel.
- [ ] Se selecciona un origen explícito entre los números existentes.
- [ ] Una llamada autorizada devuelve un ID real; la consulto después.
- [ ] Una instrucción de no llamar se respeta en las pruebas de conversación.
- [ ] Si uso ChatGPT, el cliente del túnel está preparado y el workspace asociado es el correcto.

## Operación

- [ ] Ninguna clave, contacto, transcripción o grabación real está en Git.
- [ ] Conozco el costo observado de mi prueba y qué proveedores lo facturan.
- [ ] Un timeout no provoca reintentos ciegos.
- [ ] Puedo detener nuevas llamadas y gestionar una llamada existente desde el proveedor.
- [ ] Antes de campañas, implemento límites del lado del servicio y verifico requisitos aplicables.

## Evidencia mínima privada

| Prueba | Evidencia que guardar |
|---|---|
| Consulta MCP | Fecha, herramientas ejecutadas e IDs coherentes |
| Prueba telefónica | ID de llamada, destino propio y estado final |
| Audio | Resultado de saludo, comprensión, interrupción y cierre |
| Costo | Registro del costo real y fuentes de facturación |
| Suspensión | Nuevas solicitudes bloqueadas por el control previsto |

No marques «completo» solo porque el JSON es válido o el chat respondió con seguridad. Conexión, llamada y conversación son comprobaciones separadas.

# 07. Usar tu número actual y entender WhatsApp

**“Quiero que mi agente llame” puede describir varias necesidades distintas.** Decide primero cuál tienes; comprar, verificar, portar y desviar un número son operaciones diferentes.

## 1. Elegir el escenario

| Necesidad | Ruta que conviene evaluar |
|---|---|
| El agente llama a celulares normales desde un número propio del proyecto | Número con voz del proveedor, importado en Vapi; es la ruta del capítulo 01 |
| El destinatario ve el número de mi celular como origen | Caller ID verificado; confirmar compatibilidad del proveedor y de Vapi |
| Quiero mover mi número habitual a telefonía programable | Evaluación de portabilidad |
| Quiero que las llamadas que recibe mi celular lleguen al agente | Desvío de llamadas hacia un número del agente |
| Quiero llamar dentro de la aplicación WhatsApp | Integración separada de WhatsApp Business Calling |
| Quiero que una SIM física instalada en mi teléfono haga la llamada | Requiere otra solución de telefonía/dispositivo; no está implementada aquí |

La tabla es una orientación de este repositorio. No presupone que todas las opciones estén disponibles para tu país o tu operador.

## 2. Caller ID verificado: mostrar tu número

Twilio permite verificar un número que ya posees fuera de su plataforma y utilizarlo como identificador en llamadas salientes. El operador original conserva la línea; las llamadas y mensajes entrantes siguen llegando por ese operador. La verificación no habilita enviar SMS/MMS desde ese número mediante Twilio. [Fuente oficial: número verificado frente a número Twilio](https://help.twilio.com/articles/223135427-What-s-the-Difference-Between-a-Verified-Phone-Number-and-a-Twilio-Phone-Number).

Twilio administra esos identificadores con **OutgoingCallerIds** y puede iniciar una llamada de validación para comprobar el número. [Fuente oficial: OutgoingCallerIds](https://www.twilio.com/docs/voice/api/outgoing-caller-ids).

**Límite de esta guía:** no está comprobado que el flujo de importación normal de Vapi acepte cualquier SIM personal solo porque se verificó su Caller ID en Twilio. El tutorial principal emplea un número del proveedor. No sustituyas el número importado por tu celular sin validarlo antes.

### Preguntas propuestas para soporte

Antes de elegir esta ruta, confirma con el proveedor y Vapi:

```text
Soy titular de un número [PREFIJO Y PAÍS] que quiero conservar en
su operador actual. Necesito llamadas salientes PSTN de un agente
Vapi que muestren ese número como Caller ID.

¿Es compatible con mi país y los destinos que llamaré?
¿Cómo se representa ese Caller ID dentro de Vapi?
¿Necesito un número Twilio adicional o una configuración SIP?
¿Qué ocurre con las devoluciones de llamada y con el costo?
```

No envíes claves privadas en esa consulta. Estas preguntas son una plantilla propuesta para obtener una respuesta aplicable a tu cuenta.

## 3. Portabilidad: trasladar la línea

Al portar un número a Twilio, Twilio se convierte en su operador. Su documentación recomienda comprobar la elegibilidad con **Portability Checker** antes del trámite. La ruta de Porting API descrita en esa página está dirigida a números estadounidenses no gratuitos; no demuestra que un celular de otro país sea portable. [Fuente oficial: portabilidad a Twilio](https://www.twilio.com/docs/phone-numbers/port-in).

Si necesitas un número colombiano `+57`, por ejemplo, confirma expresamente **país, tipo móvil/fijo y operador actual**. No se ha verificado aquí la portabilidad de tu número concreto.

### Plan propuesto antes de portar

1. Obtén confirmación escrita de elegibilidad.
2. Define cómo conservarás datos móviles, SMS y accesos que dependan de la línea.
3. Verifica si hay otros servicios asociados al número, incluido WhatsApp.
4. Acuerda la fecha del cambio y una vía alternativa de contacto.
5. Prueba tu proyecto con un número separado antes de trasladar el habitual.

No canceles una línea por tu cuenta durante el trámite sin coordinarlo con los operadores.

## 4. Desvío: atender llamadas entrantes de tu celular

Twilio explica que un número verificado continúa recibiendo llamadas en el operador original y que, si ese operador lo permite, se puede desviar hacia un número Twilio. Verificarlo por sí solo no envía las entrantes a Twilio. [Fuente oficial: agregar o quitar un Caller ID verificado](https://help.twilio.com/articles/223180048-How-to-Add-and-Remove-a-Verified-Phone-Number-or-Caller-ID-with-Twilio).

Diagrama orientativo:

```text
Cliente llama a tu número habitual
              |
              v
Operador aplica el desvío que tú configuraste
              |
              v
Número programable del agente -> Vapi atiende
```

Consulta con tu operador qué modalidades ofrece, cuánto cuestan y cómo desactivarlas. El desvío no hace que el agente utilice los minutos de tu SIM para llamar hacia afuera.

## 5. WhatsApp: canal separado

**WhatsApp Business Calling sí tiene integración por API.** Twilio documenta llamadas entrantes y salientes para remitentes WhatsApp habilitados para voz. Requiere una cuenta/remitente de WhatsApp Business, configuración adicional y, para llamadas iniciadas por la empresa, autorización previa del consumidor. Existen restricciones por país. Los destinos WhatsApp no se pueden conectar a extremos PSTN. [Fuente oficial: WhatsApp Business Calling](https://www.twilio.com/docs/voice/whatsapp-business-calling).

Por tanto, ten claras estas diferencias prácticas:

- El tutorial principal llama al teléfono convencional del destinatario.
- Que una persona tenga WhatsApp instalado no cambia el tipo de llamada del tutorial.
- Vincular una cuenta de mensajería mediante QR no es el procedimiento de voz descrito aquí.
- Registrar un número para mensajes no prueba que la configuración de llamadas esté terminada.
- Este repositorio no implementa WhatsApp Business Calling.

**Recomendación:** completa primero una llamada telefónica convencional. Si la necesidad real es que suene WhatsApp, abre un proyecto específico para ese canal con sus requisitos, permisos y pruebas.

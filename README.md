## Hi there 👋

<!--
**anfebolivar2-lab/anfebolivar2-lab** is a ✨ _special_ ✨ repository because its `README.md` (this file) appears on your GitHub profile.

Here are some ideas to get you started:

- 🔭 I’m currently working on ...
- 🌱 I’m currently learning ...
- 👯 I’m looking to collaborate on ...
- 🤔 I’m looking for help with ...
- 💬 Ask me about ...
- 📫 How to reach me: ...
- 😄 Pronouns: ...
- ⚡ Fun fact: ...
-->
# ¡Hola! Soy Andrés Felipe Bolívar Arias 👋

* **Edad:** 21 años
* **Origen:** Neiva
* **Ocupación:** Guarda de seguridad y Emprendedor (Venta de celulares)
* **Educación:** Estudiante de Ingeniería en Inteligencia Artificial en Corhuila | Técnico en Sistemas
* **Experiencia:** Servicio Militar prestado en el año 2023

---

### Sobre mí 🚀

Mi nombre es Andrés Felipe Bolívar Arias. Tengo 21 años y soy de Neiva. Soy estudiante de Corhuila, donde estudio Ingeniería en Inteligencia Artificial. Trabajo como guarda de seguridad, estudié un Técnico en Sistemas y presté servicio militar en el año 2023. Estudio y trabajo para poder salir adelante. Además, tengo un emprendimiento de venta de celulares.

---

### Conéctate conmigo 🤝

* 💼 [Tu LinkedIn](https://linkedin.com)
* 📧 [Tu Correo Electrónico](mailto:tu-correo@email.com)


## Nube (misma información en todos los celulares)

La API `/api/state` guarda el estado de la tienda y está protegida con el código de la tienda (`SYNC_CODE`).

Variables de entorno en Vercel:

- `SYNC_CODE`: código de la tienda.
- `FIREBASE_SERVICE_ACCOUNT` (opcional): JSON de la cuenta de servicio de Firebase. Si existe, el estado se guarda en Firestore (`tienda/estado`). Dejar las reglas de Firestore cerradas (`allow read, write: if false;`), porque el servidor entra con la cuenta de servicio.
- `BLOB_READ_WRITE_TOKEN`: si no hay Firebase, se usa Vercel Blob.

## Asistente con IA

`/api/ask` usa Gemini si existe `GEMINI_API_KEY` (clave gratuita de Google AI Studio), o Claude si solo existe `ANTHROPIC_API_KEY`. En los dos casos hace falta `ASSISTANT_CODE`, el código que el administrador escribe en Ajustes.

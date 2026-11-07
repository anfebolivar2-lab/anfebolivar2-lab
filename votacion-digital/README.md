# Votación digital

Web de votación con Firebase (proyecto `votacion-digital`): Authentication (correo y contraseña),
Cloud Firestore y Hosting. Una persona, un voto, resultados en vivo.

## Despliegue
```bash
cd votacion-digital
firebase deploy --only firestore:rules,hosting
```

## Modelo de datos
- `candidates/{id}` → `{ name, votes }`. Lectura pública; solo se puede sumar 1 voto junto con el voto del usuario.
- `votes/{uid}` → `{ candidateId, createdAt }`. El ID es el UID, así que solo puede existir un voto por persona.

Los candidatos se crean/editan desde la consola de Firebase o con credenciales de administrador.

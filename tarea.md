# Encargo: rediseño realista de restaurante.html

Edita SOLO el archivo `restaurante.html` (reemplaza su diseño actual completo). No toques ningún otro archivo, no borres nada, no hagas commits.

Restaurante: "Sabor Huilense" (comida colombiana). Todo en español. Mantén los mismos platos, precios, horarios, dirección de ejemplo y el enlace de WhatsApp (https://wa.me/573000000000 con el mensaje prellenado que ya existe).

## Fotos reales (ya existen, 1920x1080, JPG)
- `imagenes/portada.jpg`: interior del restaurante al atardecer (usar en la portada).
- `imagenes/asado.jpg`: Asado huilense.
- `imagenes/tamal.jpg`: Tamal huilense.
- `imagenes/mojarra.jpg`: Mojarra frita.
Usa rutas relativas. Pon `alt` descriptivo en español, `loading="lazy"` en las que no estén en la portada y `width`/`height` para evitar saltos de diseño. No uses el emoji ni ilustraciones CSS de antes; no uses imágenes externas.

## Estilo (mezcla de tres ambientes)
- Portada oscura y elegante: foto `portada.jpg` a pantalla casi completa con una capa oscura degradada para que el texto blanco/dorado se lea bien; nombre grande en serif, frase corta y botón dorado "Reservar por WhatsApp".
- Tonos cálidos tierra (madera, terracota, dorado) en detalles y títulos.
- Resto de la página sobre fondo claro y limpio, con fotos grandes y mucho espacio.

## Secciones
1. Barra de navegación fija (transparente sobre la portada, sólida al bajar; Inicio, Menú, Visítanos, Contacto).
2. Portada.
3. "Platos de la casa": tarjetas grandes con las 3 fotos de platos (asado, tamal, mojarra), con nombre, descripción corta y precio.
4. Menú completo en 3 columnas (Entradas, Platos fuertes, Bebidas) como ahora, con precios en COP.
5. Horarios y ubicación (con la dirección de ejemplo).
6. Pie de página con botón de WhatsApp.

## Requisitos
- Responsive: se ve bien en celular (390 px) y computador (1280 px), sin scroll horizontal.
- `lang="es"`, `<meta viewport>`, buen contraste, foco visible en enlaces, `prefers-reduced-motion` respetado si usas animaciones (mínimas).
- Un solo archivo HTML con CSS y JS mínimo inline.

## Prueba
Verifica sintaxis con `xmllint --html --noout` y `node --check` si hay JS, que las 4 imágenes existan en las rutas usadas y que los enlaces internos (#inicio, #menu, #visita, #contacto) apunten a secciones existentes.

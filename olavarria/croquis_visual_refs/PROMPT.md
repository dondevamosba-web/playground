# Prompt para Gemini — Croquis Visual Ilustrado (no técnico)

Pega este prompt en Gemini junto con las 3 imágenes de esta carpeta (ref_estilo_cocina.jpg, ref_layout_planta_alta.png, ref_layout_planta_baja.png).

---

Quiero que generes un **croquis/plano ilustrado en estilo isométrico moderno** de una casa (NO un plano técnico/CAD en blanco y negro — quiero algo visual, cálido y atractivo, tipo los planos ilustrados que usan estudios de arquitectura o Airbnb para mostrar una propiedad).

**Estilo visual de referencia:**
- Vista isométrica (3/4, ángulo elevado ~30-45°), con paredes y muebles con volumen/sombra suave
- Paleta de colores cálida: madera clara, blancos, cremas, verdes suaves para plantas — igual a la imagen de referencia de la cocina (ref_estilo_cocina.jpg)
- Pisos con textura (madera clara en dormitorios/living, porcelanato claro en cocina/baños)
- Muebles dibujados con detalle simplificado pero reconocible (sofás, camas, isla de cocina, mesada, inodoros, plantas)
- Sombra suave y luz cálida, sensación acogedora — no un dibujo técnico frío
- Líneas de contorno finas en los muebles, sin grosor de plano arquitectónico

**Layout a respetar** (usar ref_layout_planta_alta.png y ref_layout_planta_baja.png como guía de distribución exacta — no cambies la posición de los ambientes, solo el estilo visual):

PLANTA ALTA (103,66 m²) — orientación: Norte = fachada/calle, Sur = patio/jardín
- Balcón (frente norte) sobre el Living
- Living 6×4,66m
- Dormitorio 1 (principal) 3,5×4m con cama doble, piso de madera clara
- Baño completo 2×2m
- Toilet 2×2m
- Pasillo central
- Escalera/Hall central
- Dormitorio 2 3,45×3,6m (esquina noreste)
- Cocina y comedor 4,66×6m — isla con horno empotrado, heladera, muebles hasta el techo en melamina clara, mesada con grifería, detalles de madera
- Lavadero
- Terraza trasera 8,66×3m con acceso a jardín

PLANTA BAJA
- Garage angosto 2,3×6m
- Escalera central de acceso
- Jardín trasero 8,66×6m con plantas distribuidas

**Formato de salida:** Dos láminas separadas (Planta Alta / Planta Baja), fondo claro, con el nombre de cada ambiente en tipografía simple y elegante. Sin grilla técnica, sin cotas en centímetros — solo el nombre del ambiente y quizás el m².

---

## Contenido de esta carpeta
- `ref_estilo_cocina.jpg` — referencia de paleta de color y materiales (madera clara, blanco, cálido)
- `ref_layout_planta_alta.png` — referencia de distribución exacta de ambientes (planta alta)
- `ref_layout_planta_baja.png` — referencia de distribución exacta de ambientes (planta baja)

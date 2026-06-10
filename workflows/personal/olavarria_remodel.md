# Workflow: Remodelación España 3175 (Olavarría)

**Objetivo:** trackear gastos y presupuestos de la remodelación (presupuesto: USD 10.000), juntar inspiración por ambiente, y documentar el antes/después con renders y fotos.

---

## Piezas del proyecto

| Pieza | Dónde vive |
|---|---|
| Gastos + presupuestos | Google Sheet "Remodel — España 3175" (`REMODEL_SHEET_ID` en `.env`) |
| Inspiración por ambiente | `olavarria_inspiration.md` |
| Galería antes/después | `olavarria/gallery.html` |

## 1. Registrar un gasto

```bash
python3 tools/add_remodel_gasto.py --room Cocina --item "Mesada granito" \
    --vendor "Marmolería Díaz" --usd 450 --pay Efectivo
```

Ambientes válidos: Living, Cocina, Baños, Terraza/Pérgola, Iluminación, Exterior/Fachada, Dormitorios, General.

La pestaña **Resumen** del sheet calcula automáticamente: gastado total vs USD 10.000 y gastado por ambiente.

## 2. Registrar/comparar presupuestos

```bash
python3 tools/add_remodel_gasto.py --quote --room "Baños" \
    --item "Cambio grifería x2" --vendor "Plomero Juan" --usd 180
```

Cuando elegís uno, cambiá su Estado a `elegido` en el sheet (y los demás a `descartado`). Al pagarlo, registralo como gasto con `--budgeted-usd` para comparar presupuestado vs pagado.

También se puede pegar el texto crudo de un presupuesto de WhatsApp en una sesión de Claude y pedir que lo normalice y cargue con el tool.

## 3. Inspiración

Cuando aparezca algo lindo (Pinterest, IG, una nota): pegar el link o descripción en la sección del ambiente en `olavarria_inspiration.md`.

## 4. Galería antes/después

`olavarria/gallery.html` — editar el array `ROOMS` con URLs públicas de las fotos (Drive direct-link o CDN). Los slots vacíos se muestran como "pendiente". Subir fotos al Drive con `tools/upload_to_drive.py` para obtener la URL.

## 5. Ángulo de contenido (opcional)

La remodelación es material de contenido local perfecto ("compré una casa en Olavarría con USD 10k de presupuesto"): reels de antes/después documentando el proceso. Sirve de portfolio vivo para Ola Digital. Si se activa, usar el flujo estándar de `workflows/ola-digital/content_calendar_autopost.md`.

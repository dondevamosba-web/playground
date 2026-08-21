#!/usr/bin/env python3
"""Agrega un batch de items nuevos a wishlist.json sin tocar los existentes."""
import json, pathlib, datetime

base = pathlib.Path(__file__).parent.parent / "wishlist"
data = json.loads((base / "wishlist.json").read_text())
existing_ids = {i["id"] for i in data["wishlist"]}
next_id = max(existing_ids) + 1

today = datetime.date.today().isoformat()

nuevos = [
  # --- OUTDOOR / TREKKING / PESCA ---
  {"nombre":"Black Diamond Spot 400 Headlamp","categoria":"Outdoor",
   "link":"https://www.amazon.com/s?k=black+diamond+spot+400+headlamp",
   "precio_estimado_usd":45,"notas":"La referencia en headlamps: 400 lumens, impermeable, modo rojo. Imprescindible para pesca de madrugada y trekking.",
   "envio_tipo":"tecno"},
  {"nombre":"Darn Tough Micro Crew Merino Socks (2-pack)","categoria":"Outdoor",
   "link":"https://www.amazon.com/s?k=darn+tough+merino+hiking+socks",
   "precio_estimado_usd":30,"notas":"Garantía de vida: si se rompen, las mandan de vuelta gratis. Las mejores medias para trekking.","envio_tipo":"ropa"},
  {"nombre":"SealLine Baja Dry Bag 10L","categoria":"Outdoor",
   "link":"https://www.amazon.com/s?k=sealline+baja+dry+bag+10l",
   "precio_estimado_usd":30,"notas":"Impermeable real. Para proteger cámara/teléfono/comida en el bote o cuando llueve pescando.","envio_tipo":"ropa"},
  {"nombre":"Osprey Daylite Plus 20L","categoria":"Outdoor",
   "link":"https://www.amazon.com/s?k=osprey+daylite+plus+backpack",
   "precio_estimado_usd":80,"notas":"La mochila de día perfecta: liviana, acolchado bueno, cabe en carry-on. Sirve para ciudad y montaña.","envio_tipo":"ropa"},
  {"nombre":"PackTowl Personal Toalla de Viaje","categoria":"Outdoor",
   "link":"https://www.amazon.com/s?k=packtowl+personal+towel",
   "precio_estimado_usd":25,"notas":"Seca en minutos, ocupa nada. La llevan todos los que hacen trekking multipdía.","envio_tipo":"ropa"},
  {"nombre":"ENO SingleNest Hammock","categoria":"Outdoor",
   "link":"https://www.amazon.com/Eagles-Nest-Outfitters-SingleNest-Hammock/dp/B001DIJ7DC",
   "precio_estimado_usd":65,"notas":"Hamaca que entra en una bolsita de puño. Pesa 400g. Para acampar, river trip, o el campo.","envio_tipo":"ropa"},
  {"nombre":"Frogg Toggs Ultralight Waders","categoria":"Outdoor",
   "link":"https://www.amazon.com/s?k=frogg+toggs+waders+fly+fishing",
   "precio_estimado_usd":120,"notas":"Los mejores waders entry-level para pesca con mosca. Livianos, aguantan bien el primer par de temporadas.","envio_tipo":"voluminoso"},
  {"nombre":"Piscifun Fly Fishing Chest Pack","categoria":"Outdoor",
   "link":"https://www.amazon.com/s?k=piscifun+fly+fishing+chest+pack",
   "precio_estimado_usd":40,"notas":"Pechera/pack para llevar flies, líderes y accesorios con las manos libres. Mejor que un vest para moverse.","envio_tipo":"ropa"},
  # extras outdoor
  {"nombre":"Hydro Flask 32oz Wide Mouth","categoria":"Outdoor",
   "link":"https://www.amazon.com/s?k=hydro+flask+32oz+wide+mouth",
   "precio_estimado_usd":45,"notas":"Mantiene frío 24h, caliente 12h. La botella que llevan todos al río y a la montaña. Dura décadas.","envio_tipo":"tecno"},
  {"nombre":"Gerber Paraframe Mini Pocket Knife","categoria":"Outdoor",
   "link":"https://www.amazon.com/s?k=gerber+paraframe+pocket+knife",
   "precio_estimado_usd":20,"notas":"Cuchillo de bolsillo ultraliviano para pesca, campo, uso diario. El más vendido de Gerber por algo.","envio_tipo":"accesorio"},

  # --- TECH / EDC ---
  {"nombre":"Kindle Paperwhite (2023, 16GB)","categoria":"Tecnología",
   "link":"https://www.amazon.com/s?k=kindle+paperwhite+2023",
   "precio_estimado_usd":160,"notas":"Pantalla sin reflejos, luz cálida, impermeable. Para leer los libros de la wishlist sin traer físicos a Argentina.","envio_tipo":"tecno"},
  {"nombre":"Leatherman Wave+","categoria":"Tecnología",
   "link":"https://www.amazon.com/s?k=leatherman+wave+plus",
   "precio_estimado_usd":110,"notas":"El multi-tool de referencia: 18 herramientas, acero inoxidable, garantía 25 años. Imprescindible en remodelación.","envio_tipo":"tecno"},
  {"nombre":"Apple AirTag (pack x4)","categoria":"Tecnología",
   "link":"https://www.amazon.com/s?k=apple+airtag+4+pack",
   "precio_estimado_usd":99,"notas":"Para equipaje, mochila, llaves, auto. Red de Find My de 2B+ dispositivos Apple. Necesita iPhone.","envio_tipo":"tecno"},
  {"nombre":"Anker Cable Organizer Pouch","categoria":"Tecnología",
   "link":"https://www.amazon.com/s?k=anker+cable+organizer+travel+pouch",
   "precio_estimado_usd":20,"notas":"Pochette para cables, cargadores y earbuds. Para no volverte loco en el bolso cuando viajás.","envio_tipo":"tecno"},
  {"nombre":"Govee LED Strip Lights 5m","categoria":"Tecnología",
   "link":"https://www.amazon.com/s?k=govee+led+strip+lights+5m",
   "precio_estimado_usd":30,"notas":"LED RGB con app, funciona con Alexa/Google. Para el escritorio o algún ambiente de la casa nueva.","envio_tipo":"tecno"},

  # --- ROPA ---
  {"nombre":"Carhartt WIP Chase Hoodie","categoria":"Ropa",
   "link":"https://www.amazon.com/s?k=carhartt+wip+chase+sweatshirt+hoodie",
   "precio_estimado_usd":80,"notas":"El hoodie clásico de Carhartt Work In Progress. Algodón pesado, logo bordado. Va con todo.","envio_tipo":"ropa"},
  {"nombre":"Fjallraven Vidda Pro Trousers","categoria":"Ropa",
   "link":"https://www.amazon.com/s?k=fjallraven+vidda+pro+trousers",
   "precio_estimado_usd":165,"notas":"El pantalón técnico más versátil: sirve para trekking exigente y también para la ciudad. G-1000, dura años.","envio_tipo":"ropa"},
  {"nombre":"Woolly Clothing Merino Wool T-Shirt","categoria":"Ropa",
   "link":"https://www.amazon.com/s?k=woolly+clothing+merino+wool+t-shirt",
   "precio_estimado_usd":55,"notas":"Merino 100%: no huele aunque la usés 3 días seguidos, regula temperatura, ideal viajes y campo.","envio_tipo":"ropa"},
  {"nombre":"Smartwool Merino Beanie","categoria":"Ropa",
   "link":"https://www.amazon.com/s?k=smartwool+merino+beanie",
   "precio_estimado_usd":30,"notas":"Merino fino, no pica, abriga sin calentarte de más. La marca de referencia en lana merino.","envio_tipo":"ropa"},
  {"nombre":"Patagonia Baggies Shorts 5\"","categoria":"Ropa",
   "link":"https://www.amazon.com/s?k=patagonia+baggies+shorts",
   "precio_estimado_usd":55,"notas":"El short más versátil del mercado: sirve de traje de baño, para correr, para la playa. Seca rápido.","envio_tipo":"ropa"},

  # --- LIBROS ---
  {"nombre":"Die with Zero – Bill Perkins","categoria":"Libros",
   "link":"https://www.amazon.com/s?k=die+with+zero+bill+perkins",
   "precio_estimado_usd":15,"notas":"Argumento para gastar las experiencias en el momento justo de tu vida, no ahorrar para siempre.","envio_tipo":"digital"},
  {"nombre":"Deep Work – Cal Newport","categoria":"Libros",
   "link":"https://www.amazon.com/s?k=deep+work+cal+newport",
   "precio_estimado_usd":14,"notas":"Para los que trabajan solos y se auto-gestionan. Cómo hacer trabajo de alta concentración sin distracciones.","envio_tipo":"digital"},
  {"nombre":"The Obstacle Is the Way – Ryan Holiday","categoria":"Libros",
   "link":"https://www.amazon.com/s?k=obstacle+is+the+way+ryan+holiday",
   "precio_estimado_usd":13,"notas":"Estoicismo práctico. Cómo convertir los problemas en ventajas. Leer antes de Can't Hurt Me.","envio_tipo":"digital"},

  # --- PERROS ---
  {"nombre":"Fi Series 3 GPS Dog Collar","categoria":"Perros",
   "link":"https://www.amazon.com/s?k=fi+series+3+gps+dog+collar",
   "precio_estimado_usd":149,"notas":"Collar con GPS en tiempo real + pedómetro. Batería 3 meses. Geofence con alertas si sale del perímetro.","envio_tipo":"tecno"},
  {"nombre":"Ruffwear Front Range Dog Harness","categoria":"Perros",
   "link":"https://www.amazon.com/s?k=ruffwear+front+range+harness",
   "precio_estimado_usd":45,"notas":"El arnés que usan todos los que llevan perros al campo. Ajuste en 4 puntos, argolla pectoral y dorsal.","envio_tipo":"ropa"},

  # --- HOGAR / OBRA ---
  {"nombre":"Victorinox Fibrox 8\" Chef's Knife","categoria":"Hogar",
   "link":"https://www.amazon.com/Victorinox-Fibrox-Pro-Chefs-Knife/dp/B008ZAE3Y8",
   "precio_estimado_usd":40,"notas":"El cuchillo que usan las cocinas profesionales. Mejor relación precio/calidad del mercado, sin discusión.","envio_tipo":"accesorio"},
  {"nombre":"Anova Culinary Nano Sous Vide","categoria":"Hogar",
   "link":"https://www.amazon.com/s?k=anova+culinary+nano+sous+vide",
   "precio_estimado_usd":100,"notas":"Cocinar carne o pollo en bolsa a temperatura exacta. Resultado perfecto sin esfuerzo, cada vez.","envio_tipo":"tecno"},
  {"nombre":"Govee Thermo-Hygrometer Smart","categoria":"Hogar",
   "link":"https://www.amazon.com/s?k=govee+thermometer+hygrometer+smart",
   "precio_estimado_usd":15,"notas":"Sensor de temperatura y humedad con app. Útil en la obra para ver si el yeso/pintura secó bien.","envio_tipo":"tecno"},
  {"nombre":"Rhino USA Ratchet Straps (4-pack)","categoria":"Hogar",
   "link":"https://www.amazon.com/s?k=rhino+usa+ratchet+straps",
   "precio_estimado_usd":30,"notas":"Para sujetar materiales en el auto/camioneta durante la obra. Más fuertes y confiables que los genéricos.","envio_tipo":"accesorio"},
]

# Asignar IDs y campos fijos
for i, item in enumerate(nuevos):
    envio = item.pop("envio_tipo", "accesorio")
    item["id"] = next_id + i
    item["fecha_agregado"] = today
    item["historial_precios"] = []
    item["alternativas"] = []
    item["_envio_tipo"] = envio  # lo usará el HTML

data["wishlist"].extend(nuevos)
data["actualizado"] = today

(base / "wishlist.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
print(f"Agregados {len(nuevos)} ítems. Total: {len(data['wishlist'])}")

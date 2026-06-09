"""
Reads .tmp/listings.json (GPS coords already embedded from JSON-LD),
filters to within 2km of Olavarría city center, and builds an
interactive Folium HTML map saved to .tmp/map_olavarria.html
"""

import json
import os
import webbrowser

import folium
from geopy.distance import geodesic

LISTINGS_PATH = os.path.join(os.path.dirname(__file__), "..", ".tmp", "listings.json")
MAP_PATH = os.path.join(os.path.dirname(__file__), "..", ".tmp", "map_olavarria.html")

# Plaza Coronel Manuel Dorrego — Olavarría city center
CENTER = (-36.8932, -60.3228)
RADIUS_KM = 2.0


def filter_by_distance(listings):
    nearby = [l for l in listings if geodesic(CENTER, (l["lat"], l["lng"])).km <= RADIUS_KM]
    print(f"Within {RADIUS_KM}km of centro: {len(nearby)}/{len(listings)}")
    return nearby


def build_map(listings):
    m = folium.Map(location=CENTER, zoom_start=14, tiles="CartoDB positron")

    folium.Marker(
        location=CENTER,
        popup="<b>Centro — Plaza Coronel Dorrego</b>",
        icon=folium.Icon(color="red", icon="star"),
    ).add_to(m)

    folium.Circle(
        location=CENTER,
        radius=RADIUS_KM * 1000,
        color="#3b82f6",
        fill=True,
        fill_opacity=0.05,
        weight=1.5,
        tooltip=f"{RADIUS_KM}km radio del centro",
    ).add_to(m)

    for l in listings:
        popup_html = f"""
        <div style="min-width:220px;font-family:sans-serif;line-height:1.5">
            <b style="font-size:15px;color:#0A215B">{l['price']}</b><br>
            <span style="color:#444;font-size:13px">{l['street'] or l['title']}</span><br>
            <a href="{l['url']}" target="_blank"
               style="color:#1a73e8;font-size:12px">Ver propiedad →</a>
        </div>
        """
        folium.Marker(
            location=(l["lat"], l["lng"]),
            popup=folium.Popup(popup_html, max_width=280),
            tooltip=f"{l['price']} — {l['street'] or l['title'][:40]}",
            icon=folium.Icon(color="green", icon="home", prefix="fa"),
        ).add_to(m)

    m.save(MAP_PATH)
    print(f"Map saved → {MAP_PATH}")
    return MAP_PATH


def run():
    if not os.path.exists(LISTINGS_PATH):
        raise FileNotFoundError(f"Run scrape_mipropiedad.py first. Not found: {LISTINGS_PATH}")

    with open(LISTINGS_PATH, encoding="utf-8") as f:
        listings = json.load(f)

    if not listings:
        print("No listings to map.")
        return

    nearby = filter_by_distance(listings)

    if not nearby:
        print(f"No listings within {RADIUS_KM}km of centro. All {len(listings)} listings are shown instead.")
        nearby = listings

    map_path = build_map(nearby)
    print(f"{len(nearby)} properties on the map.")
    webbrowser.open(f"file://{os.path.abspath(map_path)}")


if __name__ == "__main__":
    run()

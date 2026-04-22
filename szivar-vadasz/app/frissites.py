"""
Szivar Vadász – Adatfrissítő szkript
=====================================
Egy kattintással letölti az összes magyar dohányboltot az OpenStreetMap-ről
és átalakítja a Szivar Vadász adatbázis formátumára.

Használat:
    python frissites.py

Eredmény:
    tobacco_raw.json        – nyers OSM adat (backup)
    cigar_database_v1.json  – kész adatbázis, Firestore-ba tölthető
"""

import json
import uuid
import urllib.request
from datetime import datetime

# ── Beállítások ───────────────────────────────────────────────────────────────
OUTPUT_RAW  = "tobacco_raw.json"
OUTPUT_DB   = "cigar_database_v1.json"

# Overpass API lekérdezés: összes tobacco + cigar shop Magyarországon
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
OVERPASS_QUERY = """
[out:json][timeout:60];
area["ISO3166-1"="HU"][admin_level=2]->.hu;
(
  node["shop"="tobacco"](area.hu);
  way["shop"="tobacco"](area.hu);
  node["shop"="cigar"](area.hu);
  way["shop"="cigar"](area.hu);
);
out center;
"""

# ── 1. lépés: OSM letöltés ────────────────────────────────────────────────────
def download_osm():
    print("📡 OSM adatok letöltése... (ez 10-30 mp lehet)")
    data = urllib.parse.urlencode({"data": OVERPASS_QUERY}).encode()
    
    req = urllib.request.Request(
        OVERPASS_URL,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    with urllib.request.urlopen(req, timeout=90) as response:
        raw = json.loads(response.read().decode("utf-8"))
    
    with open(OUTPUT_RAW, "w", encoding="utf-8") as f:
        json.dump(raw, f, ensure_ascii=False, indent=2)
    
    count = len(raw.get("elements", []))
    print(f"✅ Letöltve: {count} elem → {OUTPUT_RAW}")
    return raw

# ── 2. lépés: Transzformálás ──────────────────────────────────────────────────
def transform(osm_data):
    print("🔄 Transzformálás...")
    cigar_db = []
    now = datetime.now().isoformat()

    for element in osm_data.get("elements", []):
        tags = element.get("tags", {})

        if tags.get("shop") not in ["tobacco", "cigar"]:
            continue

        lat = element.get("lat") or element.get("center", {}).get("lat")
        lon = element.get("lon") or element.get("center", {}).get("lon")

        if lat is None or lon is None:
            continue  # koordináta nélküli elem kihagyva

        name = tags.get("name", "Nemzeti Dohánybolt")
        shop_type = tags.get("shop")
        is_cigar = shop_type == "cigar" or "szivar" in name.lower() or "cigar" in name.lower()

        entry = {
            "store_id":     str(uuid.uuid4()),
            "name":         name,
            "type":         "Specialized Shop" if is_cigar else "Standard Trafik",
            "country":      "Hungary",
            "city":         tags.get("addr:city", "Ismeretlen"),
            "zip_code":     tags.get("addr:postcode", ""),
            "street":       tags.get("addr:street", ""),
            "house_number": tags.get("addr:housenumber", ""),
            "coordinates":  {"lat": lat, "lng": lon},
            "humidor_status": is_cigar,
            "brand_focus":    [],
            "brands_available": [],
            "contact_info": {
                "phone":   tags.get("contact:phone")   or tags.get("phone", ""),
                "website": tags.get("contact:website") or tags.get("website", ""),
                "email":   tags.get("contact:email")   or tags.get("email", ""),
            },
            "verified":     False,
            "source":       "osm_import",
            "last_updated": now,
        }

        cigar_db.append(entry)

    with open(OUTPUT_DB, "w", encoding="utf-8") as f:
        json.dump(cigar_db, f, ensure_ascii=False, indent=2)

    specialized = sum(1 for x in cigar_db if x["type"] == "Specialized Shop")
    has_city    = sum(1 for x in cigar_db if x["city"] != "Ismeretlen")
    print(f"✅ Kész: {len(cigar_db)} bolt → {OUTPUT_DB}")
    print(f"   ├─ Szivarbolt (Specialized): {specialized}")
    print(f"   ├─ Standard Trafik:          {len(cigar_db) - specialized}")
    print(f"   └─ Pontos cím (city):        {has_city}")
    return cigar_db

# ── Futtatás ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import urllib.parse
    print("=" * 50)
    print("  Szivar Vadász – Adatfrissítő")
    print("=" * 50)
    osm_data = download_osm()
    transform(osm_data)
    print("\n🎉 Minden kész! Következő lépés: Firestore feltöltés.")

"""
Szivar Vadász – Humidor Trafik Importáló
==========================================
Beolvassa a KML fájlt, geocodolja a címeket Google API-val,
és feltölti Firestore-ba Megerősítve: true jelzéssel.

Telepítés:
    pip install google-cloud-firestore requests

Használat:
    python humidor_import.py
"""

import json
import time
import uuid
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from google.cloud import firestore
from google.oauth2 import service_account

# ── Beállítások ───────────────────────────────────────────────────────────────
KML_FILE             = "A_Magyarországon_humidorral_rendelkező_trafikok_térképe__1_.kml"
SERVICE_ACCOUNT_FILE = "serviceAccountKey.json"
GOOGLE_API_KEY       = "AIzaSyCqCZBsFCKSnHm_NXAS2lcb6X860e1xMYk"
COLLECTION_NAME      = "szivarozok"
DELAY_SEC            = 0.1   # késleltetés API hívások között

# ── Firebase init ─────────────────────────────────────────────────────────────
def init_firebase():
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
    return firestore.Client(project="szivar-vadasz", database="szivarvadasz", credentials=creds)

# ── KML beolvasás ─────────────────────────────────────────────────────────────
def parse_kml(kml_file):
    tree = ET.parse(kml_file)
    root = tree.getroot()
    ns = {'kml': 'http://www.opengis.net/kml/2.2'}

    shops = []
    for p in root.findall('.//kml:Placemark', ns):
        data = {}

        name_el = p.find('kml:n', ns)
        data['nev'] = name_el.text.strip() if name_el is not None and name_el.text else ''

        addr_el = p.find('kml:address', ns)
        raw_addr = addr_el.text.strip() if addr_el is not None and addr_el.text else ''

        # Kinyerjük az ExtendedData mezőket
        zip_code = city = street = ''
        for d in p.findall('.//kml:Data', ns):
            dname = d.get('name', '')
            val_el = d.find('kml:value', ns)
            val = val_el.text.strip() if val_el is not None and val_el.text else ''
            if dname == 'Irányítószám': zip_code = val
            elif dname == 'Város': city = val
            elif dname == 'Utca': street = val

        # Ha a névben nincs adat, próbáljuk a raw_addr-ből kinyerni
        if not data['nev'] and raw_addr:
            # A raw_addr formátuma: "Bolt neve IRSZ Város Utca"
            parts = raw_addr.split(' ')
            if zip_code and zip_code in raw_addr:
                idx = raw_addr.index(zip_code)
                data['nev'] = raw_addr[:idx].strip()

        cim = f"{zip_code} {city}, {street}".strip(', ')
        data['cim'] = cim
        data['zip_code'] = zip_code
        data['city'] = city
        data['street'] = street
        data['raw_address'] = raw_addr

        shops.append(data)

    return shops

# ── Geocoding ─────────────────────────────────────────────────────────────────
def geocode(address):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address + ", Hungary", "key": GOOGLE_API_KEY, "language": "hu"}
    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        if data['status'] == 'OK':
            loc = data['results'][0]['geometry']['location']
            return loc['lat'], loc['lng']
    except Exception as e:
        print(f"    ⚠️ Geocoding hiba: {e}")
    return None, None

# ── Feltöltés ─────────────────────────────────────────────────────────────────
def upload(db, shops):
    total = len(shops)
    ok = skip = fail = 0
    now = datetime.now().isoformat()

    print(f"📤 Feltöltés indul: {total} humidoros trafik\n")

    for i, shop in enumerate(shops):
        addr = shop['raw_address'] or shop['cim']
        if not addr:
            print(f"  [{i+1}/{total}] ⚠️ Nincs cím, kihagyva")
            skip += 1
            continue

        lat, lng = geocode(addr)
        time.sleep(DELAY_SEC)

        if lat is None:
            print(f"  [{i+1}/{total}] ❌ Nem geocodolható: {addr[:50]}")
            fail += 1
            # Feltöltjük koordináta nélkül is
            lat, lng = None, None

        nev = shop['nev'] or addr.split(' ')[0]
        print(f"  [{i+1}/{total}] ✅ {nev[:35]:<35} → {lat}, {lng}")

        doc = {
            "nev":          nev,
            "cim":          shop['cim'],
            "lat":          lat,
            "lng":          lng,
            "tipus":        "Specialized Shop",
            "humidor":      True,
            "humidor_status": True,
            "Megerősítve":  True,
            "megerositve":  True,
            "nyitvatartas": "",
            "source":       "humidor_kml_import",
            "last_updated": now,
        }

        ref = db.collection(COLLECTION_NAME).document(str(uuid.uuid4()))
        ref.set(doc)
        ok += 1

    print(f"\n🎉 Kész!")
    print(f"   ├─ Sikeresen feltöltve: {ok}")
    print(f"   ├─ Nem geocodolható:    {fail} (feltöltve koordináta nélkül)")
    print(f"   └─ Kihagyva:            {skip}")

# ── Futtatás ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("  Szivar Vadász – Humidor Trafik Importáló")
    print("=" * 55)

    shops = parse_kml(KML_FILE)
    print(f"📋 KML beolvasva: {len(shops)} bolt találva\n")

    db = init_firebase()
    upload(db, shops)

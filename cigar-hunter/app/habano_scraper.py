#!/usr/bin/env python3
"""
habano_scraper.py
-----------------
Leszedi a habanolocator.com összes boltját (Habanos Specialist,
La Casa del Habano, Habanos Terrace stb.) és feltölti a
cigar-hunter Firestore cigarshops kollekcióba.

Futtatás:
  pip install requests beautifulsoup4 google-cloud-firestore
  python habano_scraper.py

Szükséges: serviceAccount.json (cigar-hunter projekt)
"""

import re
import time
import json
import requests
from bs4 import BeautifulSoup
from google.cloud import firestore

# ============================================================
# KONFIG
# ============================================================
SERVICE_ACCOUNT  = 'cigar-hunter-firebase-adminsdk-fbsvc-d508dbda17.json'
BASE_URL         = 'https://habanolocator.com'
MAX_PAGES        = 575       # Az oldalon 575 oldal van
DELAY_SEC        = 0.5       # Udvarias késleltetés kérések között
DRY_RUN          = False      # True = csak listázza, nem ír Firestore-ba
FIRESTORE_DB     = '(default)'  # cigar-hunter default DB
COLLECTION       = 'cigarshops'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}

# ============================================================
# SCRAPER
# ============================================================
def scrape_page(page_num):
    """Egy oldal boltjainak leszedése."""
    url = BASE_URL if page_num == 1 else f'{BASE_URL}?page={page_num}'
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f'  ❌ Page {page_num} error: {e}')
        return []

    soup = BeautifulSoup(resp.text, 'html.parser')
    shops = []

    for item in soup.select('.shop_item'):
        try:
            # Név
            title_el = item.select_one('.shop_title')
            name = title_el.get_text(strip=True) if title_el else ''

            # Típus (Habanos Specialist, La Casa del Habano, stb.)
            type_el = item.select_one('.shop_content > p:not(.s_location)')
            shop_type = type_el.get_text(strip=True) if type_el else ''

            # Cím
            loc_el = item.select_one('.s_location')
            address_raw = loc_el.get_text(strip=True) if loc_el else ''

            # Shop ID a linkből
            link_el = item.select_one('a[href*="shop_details"]')
            shop_id = ''
            if link_el:
                m = re.search(r'shop_details/(\d+)', link_el.get('href', ''))
                if m:
                    shop_id = m.group(1)

            if not name:
                continue

            # Ország kinyerése a cím végéről
            country = extract_country(address_raw)

            shops.append({
                'habano_id':  shop_id,
                'nev':        name,
                'cim':        address_raw,
                'leiras':     shop_type,
                'humidor':    'pro',          # Mind prémium Habanos bolt
                'megerositve': True,
                'source':     'habanolocator',
                'country':    country,
                'lat':        None,
                'lng':        None,
            })
        except Exception as e:
            print(f'  ⚠️  Parse error: {e}')
            continue

    return shops


def extract_country(address):
    """Ország kinyerése a cím utolsó részéből."""
    parts = [p.strip() for p in address.split(',')]
    if not parts:
        return ''
    last = parts[-1]
    last = re.sub(r'^[A-Z]-?\d+\s*', '', last).strip()
    last = re.sub(r'^\d+\s*', '', last).strip()
    return last if len(last) > 1 else (parts[-2].strip() if len(parts) > 1 else '')


def get_shop_coords(shop_id):
    """Egy bolt koordinatainak leszedese a detail oldalrol."""
    if not shop_id:
        return None, None
    url = f'{BASE_URL}/shop_details/{shop_id}'
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        text = resp.text

        patterns_lat = [
            r'var\s+lat\s*=\s*([\d.\-]+)',
            r'"latitude"\s*:\s*"?([\d.\-]+)"?',
            r'lat\s*:\s*([\d.\-]+)',
        ]
        patterns_lng = [
            r'var\s+lng\s*=\s*([\d.\-]+)',
            r'"longitude"\s*:\s*"?([\d.\-]+)"?',
            r'lng\s*:\s*([\d.\-]+)',
        ]
        for pl, pn in zip(patterns_lat, patterns_lng):
            lm = re.search(pl, text)
            nm = re.search(pn, text)
            if lm and nm:
                lat, lng = float(lm.group(1)), float(nm.group(1))
                if 35 < lat < 72 and -25 < lng < 50:
                    return lat, lng

        # Google Maps embed: q=48.123,16.456 or @48.123,16.456
        for pat in [r'[?&]q=([\d.\-]+),([\d.\-]+)', r'@([\d.\-]+),([\d.\-]+)', r'LatLng\(([\d.\-]+),\s*([\d.\-]+)\)']:
            m = re.search(pat, text)
            if m:
                lat, lng = float(m.group(1)), float(m.group(2))
                if 35 < lat < 72 and -25 < lng < 50:
                    return lat, lng

    except Exception:
        pass
    return None, None


# ============================================================
# FŐPROGRAM
# ============================================================
def main():
    print('=== Habanolocator Scraper ===\n')

    # 1. Scraping
    all_shops = []
    print(f'Scraping {MAX_PAGES} oldalon...')

    for page in range(1, MAX_PAGES + 1):
        shops = scrape_page(page)
        all_shops.extend(shops)
        print(f'  Oldal {page}/{MAX_PAGES}: {len(shops)} bolt | Összesen: {len(all_shops)}')
        time.sleep(DELAY_SEC)

        # Teszteléshez: csak az első 3 oldal
        if DRY_RUN and page >= 3:
            print('\n  [DRY RUN] Első 3 oldal után megáll.')
            break

    print(f'\n✅ Összesen leszedve: {len(all_shops)} bolt')

    # 2. Koordináták leszedése (opcionális - lassabb)
    print('\nKoordináták leszedése a detail oldalakról...')
    coords_found = 0
    for i, shop in enumerate(all_shops):
        if shop.get('habano_id'):
            lat, lng = get_shop_coords(shop['habano_id'])
            if lat and lng:
                shop['lat'] = lat
                shop['lng'] = lng
                coords_found += 1
        time.sleep(0.8)
        if (i + 1) % 10 == 0:
            print(f'  {i+1}/{len(all_shops)} feldolgozva, {coords_found} koordináta megvan')
        if DRY_RUN and i >= 9:
            print('  [DRY RUN] Első 10 bolt koordinátája után megáll.')
            break

    print(f'\n✅ Koordinátával: {coords_found}/{len(all_shops)}')

    # 3. Minta kimenet
    print('\nMinta boltok:')
    for s in all_shops[:5]:
        print(f"  [{s['habano_id']}] {s['nev']}")
        print(f"      Típus: {s['leiras']}")
        print(f"      Cím:   {s['cim']}")
        print(f"      Ország: {s['country']}")
        print(f"      GPS:   {s['lat']}, {s['lng']}")

    if DRY_RUN:
        print('\n🔍 DRY RUN - nem ír Firestore-ba.')
        print('Állítsd DRY_RUN = False-ra és futtasd újra!')
        return

    # 4. Firestore feltöltés
    print(f'\n📤 Feltöltés Firestore-ba ({COLLECTION})...')
    db = firestore.Client.from_service_account_json(
        SERVICE_ACCOUNT,
        database=FIRESTORE_DB
    )
    coll = db.collection(COLLECTION)

    uploaded = 0
    skipped = 0
    batch = db.batch()
    batch_count = 0

    for shop in all_shops:
        if not shop['lat'] or not shop['lng']:
            skipped += 1
            continue

        # Duplikátum ellenőrzés: habano_id alapján
        doc_id = f'habano_{shop["habano_id"]}' if shop['habano_id'] else None
        if doc_id:
            ref = coll.document(doc_id)
        else:
            ref = coll.document()

        batch.set(ref, {
            'nev':         shop['nev'],
            'cim':         shop['cim'],
            'leiras':      shop['leiras'],
            'humidor':     shop['humidor'],
            'megerositve': shop['megerositve'],
            'source':      shop['source'],
            'lat':         shop['lat'],
            'lng':         shop['lng'],
            'feltoltes':   firestore.SERVER_TIMESTAMP,
        }, merge=True)

        uploaded += 1
        batch_count += 1

        if batch_count >= 400:
            batch.commit()
            print(f'  {uploaded} feltöltve...')
            batch = db.batch()
            batch_count = 0

    batch.commit()
    print(f'\n✅ Kész! {uploaded} bolt feltöltve, {skipped} koordináta nélküli kihagyva.')


if __name__ == '__main__':
    main()

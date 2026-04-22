#!/usr/bin/env python3
"""
humidor_frissites.py
--------------------
Beolvassa a KML fájlból a 443 humidoros boltot,
és a Szivar Vadász Firestore-ban (szivarvadasz adatbázis)
a szivarozok kollekcióban beállítja humidor: 'pro'-ra
azokat a boltokat amelyek cím alapján egyeznek.

Futtatás:
  pip install google-cloud-firestore
  python humidor_frissites.py

Szükséges: serviceAccount.json a szivar-vadasz projekthez
(Firebase Console -> Projekt beállítások -> Szolgáltatásfiók -> JSON letöltés)
"""

import re
import unicodedata
from google.cloud import firestore

# ============================================================
# KONFIG
# ============================================================
KML_FILE       = 'A Magyarországon humidorral rendelkező trafikok térképe.kml'
SERVICE_ACCOUNT = 'serviceAccount.json'   # <-- ide tedd a JSON fájl nevét
DATABASE_ID    = 'szivarvadasz'
COLLECTION     = 'szivarozok'
HUMIDOR_ERTEK  = 'pro'   # 'pro' vagy 'alap'
DRY_RUN        = False   # True = csak listázza, nem ír Firestore-ba

# ============================================================
# SEGÉDFÜGGVÉNYEK
# ============================================================
def normalize(s):
    """Kisbetű, ékezet nélkül, csak alfanumerikus"""
    s = s.lower().strip()
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    s = re.sub(r'[^a-z0-9]', '', s)
    return s

def make_kml_key(irsz, utca):
    """Dupla kulcs: irsz+házszám (pontos) és csak irsz (tág)"""
    nums = re.findall(r'\d+', utca)
    hazszam = nums[-1] if nums else ''
    return irsz + '_' + hazszam

def make_fs_key(cim):
    """Firestore: '2471 Baracska Országút utca 27' -> irsz + házszám"""
    cim = cim.strip()
    m = re.match(r'^(\d{4})', cim)
    if not m: return '_'
    irsz = m.group(1)
    nums = re.findall(r'\d+', cim)
    hazszam = nums[-1] if len(nums) > 1 else ''
    return irsz + '_' + hazszam

def parse_kml(kml_file):
    with open(kml_file, 'r', encoding='utf-8') as f:
        raw = f.read()
    irsz_list  = re.findall(r'<Data name="Ir[aá]ny[ií]t[oó]sz[aá]m">\s*<value>(.*?)</value>', raw)
    varos_list = re.findall(r'<Data name="V[aá]ros">\s*<value>(.*?)</value>', raw)
    utca_list  = re.findall(r'<Data name="Utca">\s*<value>(.*?)</value>', raw)
    bolts = []
    for i in range(len(irsz_list)):
        irsz  = irsz_list[i].strip()
        varos = varos_list[i].strip() if i < len(varos_list) else ''
        utca  = utca_list[i].strip()  if i < len(utca_list)  else ''
        bolts.append({
            'irsz':  irsz,
            'varos': varos,
            'utca':  utca,
            'key': make_kml_key(varos, utca)
        })
    return bolts

# ============================================================
# FŐPROGRAM
# ============================================================
def main():
    print("=== Humidor frissítő script ===\n")

    # 1. KML beolvasás
    kml_bolts = parse_kml(KML_FILE)
    print(f"KML-ből beolvasva: {len(kml_bolts)} bolt")

    # KML kulcsok halmaza
    kml_keys = set(b['key'] for b in kml_bolts)
    print(f"Egyedi kulcsok a KML-ben: {len(kml_keys)}\n")

    # 2. Firestore kapcsolat
    db = firestore.Client.from_service_account_json(
        SERVICE_ACCOUNT,
        database=DATABASE_ID
    )
    coll = db.collection(COLLECTION)

    # 3. Összes bolt lekérése (lapozással)
    print("Firestore boltok lekérése... (ez eltarthat egy percig)")
    all_docs = []
    query = coll.limit(500)
    last_doc = None
    page = 0
    while True:
        if last_doc:
            docs = list(query.start_after(last_doc).stream())
        else:
            docs = list(query.stream())
        if not docs:
            break
        all_docs.extend(docs)
        last_doc = docs[-1]
        page += 1
        print(f"  {page}. lap: {len(docs)} bolt (összesen: {len(all_docs)})")
        if len(docs) < 500:
            break

    print(f"\nFirestore-ban összesen: {len(all_docs)} bolt\n")

    # 4. Egyeztetés és frissítés
    egyezik = []
    nem_egyezik = []

    # KML irányítószámok halmaza (tág egyeztetéshez)
    kml_irsz = set()
    raw_kml = open(KML_FILE, encoding='utf-8').read()
    import re as _re
    for irsz in _re.findall(r'<Data name="Ir[aá]ny[ií]t[oó]sz[aá]m">\s*<value>(.*?)</value>', raw_kml):
        kml_irsz.add(irsz.strip())

    for doc in all_docs:
        data = doc.to_dict()
        cim = data.get('cim', '')
        # Pontos egyezés: irsz + házszám
        key = make_fs_key(cim)
        if key in kml_keys:
            egyezik.append((doc, data, key + ' [pontos]'))
            continue
        # Tág egyezés: csak irányítószám
        m = __import__('re').match(r'^(\d{4})', cim.strip())
        if m and m.group(1) in kml_irsz:
            egyezik.append((doc, data, m.group(1) + ' [irsz]'))
        else:
            nem_egyezik.append((doc, data, key))

    print(f"Egyezés: {len(egyezik)} bolt")
    print(f"Nem egyezik: {len(nem_egyezik)} bolt")

    if not egyezik:
        print("\n⚠️  Nincs egyezés! Ellenőrizd a cim mező formátumát.")
        # Debug: mutasd az első néhány Firestore cim-et
        print("\nFirestore cim minták:")
        for doc, data, key in all_docs[:10]:
            print(f"  cim='{data.get('cim','')}' -> key='{key}'")
        print("\nKML kulcs minták:")
        for b in kml_bolts[:10]:
            print(f"  {b['irsz']} {b['varos']}, {b['utca']} -> key='{b['key']}'")
        return

    print(f"\nEgyező boltok (első 20):")
    for doc, data, key in egyezik[:20]:
        print(f"  [{key}] {data.get('nev','?')} | jelenlegi humidor: {data.get('humidor','')}")

    # 5. Írás Firestore-ba
    if DRY_RUN:
        print(f"\n🔍 DRY RUN - nem ír Firestore-ba. {len(egyezik)} boltot frissítene.")
        return

    print(f"\n✏️  Frissítés indul ({len(egyezik)} bolt -> humidor='{HUMIDOR_ERTEK}')...")
    batch_size = 400
    updated = 0
    batch = db.batch()
    for i, (doc, data, key) in enumerate(egyezik):
        if data.get('humidor') == HUMIDOR_ERTEK:
            continue  # már jó
        batch.update(doc.reference, {'humidor': HUMIDOR_ERTEK})
        updated += 1
        if updated % batch_size == 0:
            batch.commit()
            print(f"  {updated} frissítve...")
            batch = db.batch()
    batch.commit()
    print(f"\n✅ Kész! {updated} bolt frissítve -> humidor='{HUMIDOR_ERTEK}'")

if __name__ == '__main__':
    main()

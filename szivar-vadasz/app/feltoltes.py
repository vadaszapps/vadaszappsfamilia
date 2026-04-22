"""
Szivar Vadász – Firestore Feltöltő
"""

import json
from google.cloud import firestore
from google.oauth2 import service_account

SERVICE_ACCOUNT_FILE = "serviceAccountKey.json"
INPUT_FILE           = "cigar_database_v1.json"
COLLECTION_NAME      = "szivarozok"
BATCH_SIZE           = 400

def init_firebase():
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
    db = firestore.Client(project="szivar-vadasz", database="szivarvadasz", credentials=creds)
    return db

def upload(db, records):
    total    = len(records)
    uploaded = 0
    skipped  = 0

    print(f"📤 Feltöltés indul: {total} rekord → '{COLLECTION_NAME}'")
    print(f"   (Meglévő manuális adatokat NEM érinti)\n")

    for i in range(0, total, BATCH_SIZE):
        batch = db.batch()
        chunk = records[i:i + BATCH_SIZE]

        for shop in chunk:
            lat = shop.get("coordinates", {}).get("lat")
            lng = shop.get("coordinates", {}).get("lng")

            if lat is None or lng is None:
                skipped += 1
                continue

            parts = [shop.get("zip_code",""), shop.get("city",""),
                     shop.get("street",""), shop.get("house_number","")]
            cim = " ".join(p for p in parts if p and p != "Ismeretlen").strip()
            if not cim:
                cim = "Ismeretlen cím"

            doc = {
                "nev":          shop["name"],
                "cim":          cim,
                "lat":          lat,
                "lng":          lng,
                "tipus":        shop["type"],
                "humidor":      shop["humidor_status"],
                "nyitvatartas": "",
                "Megerősítve":  False,
                "source":       "osm_import",
                "last_updated": shop["last_updated"],
            }

            ref = db.collection(COLLECTION_NAME).document(shop["store_id"])
            batch.set(ref, doc)
            uploaded += 1

        batch.commit()
        print(f"   ✅ {min(i + BATCH_SIZE, total)}/{total} feltöltve...")

    print(f"\n🎉 Kész!")
    print(f"   ├─ Feltöltve:  {uploaded}")
    print(f"   └─ Kihagyva:   {skipped} (koordináta nélküli)")

if __name__ == "__main__":
    print("=" * 50)
    print("  Szivar Vadász – Firestore Feltöltő")
    print("=" * 50)

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        records = json.load(f)

    db = init_firebase()
    upload(db, records)

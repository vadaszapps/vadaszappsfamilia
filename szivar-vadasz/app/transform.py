import json
import uuid
from datetime import datetime

def transform_osm_to_cigar_db(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        osm_data = json.load(f)

    cigar_db = []
    
    for element in osm_data.get('elements', []):
        tags = element.get('tags', {})
        
        # Alapvető szűrés: Csak a dohányboltokat vesszük át
        if tags.get('shop') not in ['tobacco', 'cigar']:
            continue

        # Koordináták kezelése (Node vs Way/Relation központ)
        lat = element.get('lat') or element.get('center', {}).get('lat')
        lon = element.get('lon') or element.get('center', {}).get('lon')

        # Saját struktúra felépítése
        entry = {
            "store_id": str(uuid.uuid4()),
            "name": tags.get('name', 'Nemzeti Dohánybolt'),
            "type": "Specialized Shop" if tags.get('shop') == 'cigar' else "Standard Trafik",
            "country": "Hungary",
            "city": tags.get('addr:city', 'Ismeretlen'),
            "zip_code": tags.get('addr:postcode', ''),
            "street": tags.get('addr:street', ''),
            "house_number": tags.get('addr:housenumber', ''),
            # FIX #1: objektum lat/lng helyett string GeoPoint
            # FIX #2: "lon" -> "lng" hogy a frontend shop.coordinates.lng működjön
            "coordinates": {
                "lat": lat,
                "lng": lon
            },
            "humidor_status": True if tags.get('shop') == 'cigar' else False,
            "brand_focus": [],
            "brands_available": [],
            "contact_info": {
                "phone": tags.get('contact:phone') or tags.get('phone', ''),
                "website": tags.get('contact:website') or tags.get('website', ''),
                "email": tags.get('contact:email') or tags.get('email', '')
            },
            "verified": False,
            "source": "osm_import",
            "last_updated": datetime.now().isoformat()
        }
        
        # Speciális szűrés: ha a névben benne van a "szivar" vagy "cigar"
        if "szivar" in entry['name'].lower() or "cigar" in entry['name'].lower():
            entry['type'] = "Specialized Shop"
            entry['humidor_status'] = True

        # FIX #3: Csak akkor adjuk hozzá, ha van érvényes koordináta
        if lat is not None and lon is not None:
            cigar_db.append(entry)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cigar_db, f, ensure_ascii=False, indent=2)
    
    return len(cigar_db)

count = transform_osm_to_cigar_db('tobacco_raw.json', 'cigar_database_v1.json')
print(f"Sikeresen feldolgozva: {count} egység.")


import json, urllib.request

# Firestore REST API - első 20 bolt cim mezője
url = "https://firestore.googleapis.com/v1/projects/szivar-vadasz/databases/szivarvadasz/documents/szivarozok?pageSize=20&key=AIzaSyCqCZBsFCKSnHm_NXAS2lcb6X860e1xMYk"

req = urllib.request.urlopen(url)
data = json.loads(req.read())

print("Firestore cim minták:")
for doc in data.get('documents', []):
    f = doc.get('fields', {})
    nev = f.get('nev', {}).get('stringValue', '?')
    cim = f.get('cim', {}).get('stringValue', '?')
    print(f"  nev=\"{nev}\" | cim=\"{cim}\"")

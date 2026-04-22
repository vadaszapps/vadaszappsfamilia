# 🍕 Pizza Vadász – Deploy útmutató

## Mappastruktúra

```
pizza-vadasz/
├── public/
│   ├── index.html          ← fő app fájl
│   ├── manifest.json       ← PWA manifest
│   ├── service-worker.js   ← offline cache
│   ├── robots.txt
│   ├── sitemap.xml
│   └── icons/              ← app ikonok (lásd lentebb)
├── firebase.json           ← Firebase Hosting konfig
├── .firebaserc             ← projekt azonosító
└── README.md
```

---

## 1. Előkészítés

### Firebase CLI telepítése (ha még nincs)
```bash
npm install -g firebase-tools
```

### Bejelentkezés
```bash
firebase login
```

### Projekt létrehozása (ha még nincs)
1. Menj a https://console.firebase.google.com oldalra
2. „Add project" → Projekt neve: **pizza-vadasz**
3. A projekt ID legyen: `pizza-vadasz`

---

## 2. Fájlok előkészítése

Hozd létre a `public/` mappát és másold bele a fájlokat:
```bash
mkdir public
cp index.html public/
cp manifest.json public/
cp service-worker.js public/
cp robots.txt public/
cp sitemap.xml public/
```

### Ikonok generálása
A `public/icons/` mappába kell a következő méretű PNG fájlok:
- icon-72x72.png
- icon-96x96.png
- icon-128x128.png
- icon-144x144.png
- icon-152x152.png
- icon-192x192.png
- icon-384x384.png
- icon-512x512.png

**Gyors generálás:** Tölts fel egy 512×512-es 🍕 pizza logót a
https://realfavicongenerator.net oldalra, és töltsd le az összes méretet.

---

## 3. Service Worker regisztráció

Az `index.html` záró `</body>` tagja elé add hozzá (ha még nincs benne):

```html
<script>
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
      navigator.serviceWorker.register('/service-worker.js')
        .then(function(reg) { console.log('SW regisztrálva:', reg.scope); })
        .catch(function(err) { console.log('SW hiba:', err); });
    });
  }
</script>
```

---

## 4. Google Maps API kulcs csere

Az `index.html` alján cseréld ki a kulcsot:
```html
<!-- RÉGI: -->
<script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyCqCZBsFCKSnHm_NXAS2lcb6X860e1xMYk&...

<!-- ÚJ (saját kulcs): -->
<script src="https://maps.googleapis.com/maps/api/js?key=SAJAT_API_KULCSOD&...
```

**Google Maps API beállítások (Google Cloud Console):**
- Maps JavaScript API ✅
- Places API ✅
- Directions API ✅
- Geocoding API ✅
- HTTP referrer korlátozás: `pizza-vadasz.web.app/*`

---

## 5. Deploy

```bash
# Inicializálás (első alkalommal)
firebase init hosting

# Választások az init során:
# ✔ Use an existing project → pizza-vadasz
# ✔ Public directory → public
# ✔ Configure as SPA → Yes
# ✔ Overwrite index.html → No

# Deploy
firebase deploy
```

Az app elérhető lesz: **https://pizza-vadasz.web.app**

---

## 6. Gyors update deploy

```bash
firebase deploy --only hosting
```

---

## 7. Ellenőrző lista deploy előtt

- [ ] Saját Google Maps API kulcs beállítva
- [ ] API kulcs HTTP referrer korlátozva (`pizza-vadasz.web.app/*`)
- [ ] `public/icons/` mappa feltöltve (min. 192x192 és 512x512)
- [ ] Service Worker regisztráció az `index.html`-ben
- [ ] `firebase.json` a projekt gyökerében
- [ ] `.firebaserc` a projekt gyökerében
- [ ] `firebase login` sikeres

---

## Kapcsolódó Vadász appok

| App | URL |
|-----|-----|
| 💊 Patika Vadász | https://patika-vadasz.web.app |
| 🚬 Szivar Vadász | https://szivar-vadasz.web.app |
| 🏪 Trafik Vadász | https://trafik-vadasz.web.app |
| 🎸 Hangszerbolt Vadász | https://hangszerbolt-vadasz.web.app |

---

© 2026 Pizza Vadász – Készítette: Králik Zola

/**
 * Whiskey Vadász — Kezdő adatbázis feltöltő
 * 
 * Futtatás:
 *   npm install firebase-admin
 *   node seed.js
 * 
 * Előtte: Firebase Console → Project Settings → Service Accounts
 *   → Generate new private key → mentsd le: serviceAccountKey.json
 */

const admin = require('firebase-admin');
const serviceAccount = require('./serviceAccountKey.json');

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount)
});

const db = admin.firestore();

const shops = [
  // ── GOODSPIRIT / WHISKYNET ──────────────────────────────────────
  {
    nev: "GoodSpirit Shop Belváros",
    cim: "Budapest, Veres Pálné utca 7, 1053",
    leiras: "A WhiskyNet zászlóshajója. Hatalmas prémium whiskey, rum, gin választék. Kóstolók rendszeresen.",
    lat: 47.4916,
    lng: 19.0521,
    tipus: "shop",
    stilus: ["single_malt", "bourbon", "blended", "japanese", "irish", "scotch"],
    arkategoria: "premium",
    megerositve: true,
    jelolesek: 1,
    datum: new Date().toISOString(),
    website: "https://goodspirit.hu"
  },
  {
    nev: "GoodSpirit Shop Óbuda",
    cim: "Budapest, Szőlőkert utca 4/B, 1033",
    leiras: "C+C bolt — internetes áron vásárolhatsz személyesen. Óriási raktárkészlet.",
    lat: 47.5499,
    lng: 19.0394,
    tipus: "shop",
    stilus: ["single_malt", "bourbon", "blended", "japanese", "irish", "scotch"],
    arkategoria: "premium",
    megerositve: true,
    jelolesek: 1,
    datum: new Date().toISOString(),
    website: "https://goodspirit.hu"
  },
  {
    nev: "GoodSpirit Shop Etele Plaza",
    cim: "Budapest, Hadak útja 1, 1119 (Etele Plaza, 1. emelet)",
    leiras: "Prémium italbolt az Etele Plazában. H-Cs: 10-20, P-Szo: 10-21, V: 10-19.",
    lat: 47.4682,
    lng: 19.0213,
    tipus: "shop",
    stilus: ["single_malt", "bourbon", "blended", "japanese", "irish", "scotch"],
    arkategoria: "premium",
    megerositve: true,
    jelolesek: 1,
    datum: new Date().toISOString(),
    website: "https://goodspirit.hu"
  },
  {
    nev: "GoodSpirit Shop Árkád",
    cim: "Budapest, Örs Vezér tere 25/A, 1106 (Árkád, alsó szint)",
    leiras: "A főváros keleti részén. H-Szo: 10-21, V: 10-19.",
    lat: 47.5017,
    lng: 19.1394,
    tipus: "shop",
    stilus: ["single_malt", "bourbon", "blended", "japanese", "irish", "scotch"],
    arkategoria: "premium",
    megerositve: true,
    jelolesek: 1,
    datum: new Date().toISOString(),
    website: "https://goodspirit.hu"
  },

  // ── SPIRIT-ALL ──────────────────────────────────────────────────
  {
    nev: "Spirit-All Italszaküzlet",
    cim: "Budapest, Tátra utca 26, 1133",
    leiras: "Családias szaküzlet Újlipótvárosban. Személyes tanácsadás, kurátori whiskey válogatás. Jászai Mari tér közelében.",
    lat: 47.5196,
    lng: 19.0512,
    tipus: "shop",
    stilus: ["single_malt", "bourbon", "blended", "japanese", "irish", "scotch"],
    arkategoria: "mid",
    megerositve: true,
    jelolesek: 1,
    datum: new Date().toISOString(),
    website: "https://www.spiritall.hu"
  },

  // ── GOLDEN DRINKS ───────────────────────────────────────────────
  {
    nev: "Golden Drinks Italszaküzlet",
    cim: "Budapest, Hegedűs Gyula utca 75, 1133",
    leiras: "20+ éves tapasztalat. 1600+ féle termék 112 országból. Különleges szeszes italok és ínyenc dohányáruk.",
    lat: 47.5178,
    lng: 19.0487,
    tipus: "shop",
    stilus: ["single_malt", "bourbon", "blended", "scotch"],
    arkategoria: "premium",
    megerositve: true,
    jelolesek: 1,
    datum: new Date().toISOString(),
    website: "https://www.golden-drinks.hu"
  },

  // ── BARRIQUE ────────────────────────────────────────────────────
  {
    nev: "Barrique Italszaküzlet",
    cim: "Budapest, Akácfa utca 10, 1072",
    leiras: "Bor, kézműves sör, whiskey és exkluzív párlatok szaküzlete a VII. kerületben.",
    lat: 47.4993,
    lng: 19.0643,
    tipus: "shop",
    stilus: ["single_malt", "bourbon", "blended", "irish", "scotch"],
    arkategoria: "mid",
    megerositve: true,
    jelolesek: 1,
    datum: new Date().toISOString()
  },

  // ── WHISKY BAR ──────────────────────────────────────────────────
  {
    nev: "GoodSpirit Bar Belváros",
    cim: "Budapest, Veres Pálné utca 7, 1053",
    leiras: "A GoodSpirit Shop melletti whiskey bár. K-Cs: 17-24, P-Szo: 17-01. Kóstolók, események rendszeresen.",
    lat: 47.4915,
    lng: 19.0522,
    tipus: "bar",
    stilus: ["single_malt", "bourbon", "blended", "japanese", "irish", "scotch"],
    arkategoria: "premium",
    megerositve: true,
    jelolesek: 1,
    datum: new Date().toISOString(),
    website: "https://goodspirit.hu"
  },
  {
    nev: "Whiskynet Óbuda Bar",
    cim: "Budapest, Szőlőkert utca 4/B, 1033",
    leiras: "K-Szo: 17-22. Whiskey kóstoló bár a C+C bolt mellett.",
    lat: 47.5498,
    lng: 19.0395,
    tipus: "bar",
    stilus: ["single_malt", "blended", "scotch", "irish"],
    arkategoria: "mid",
    megerositve: true,
    jelolesek: 1,
    datum: new Date().toISOString()
  },

  // ── BALASSI UTCA ────────────────────────────────────────────────
  {
    nev: "Prémium Italszaküzlet (V. ker.)",
    cim: "Budapest, Balassi Bálint utca 25, 1055",
    leiras: "Prémium whiskey és párlat szaküzlet az V. kerületben.",
    lat: 47.5072,
    lng: 19.0468,
    tipus: "shop",
    stilus: ["single_malt", "bourbon", "scotch"],
    arkategoria: "premium",
    megerositve: false,
    jelolesek: 1,
    datum: new Date().toISOString()
  }
];

async function seed() {
  console.log('🥃 Whiskey Vadász — adatbázis feltöltés indul...\n');
  
  const col = db.collection('whiskeybolts');
  
  // Töröljük az esetleges régi tesztadatokat
  const existing = await col.get();
  if (!existing.empty) {
    console.log(`⚠️  Már van ${existing.size} dokumentum. Törlés...`);
    const batch = db.batch();
    existing.docs.forEach(doc => batch.delete(doc.ref));
    await batch.commit();
    console.log('   Törölve.\n');
  }

  let ok = 0;
  for (const shop of shops) {
    try {
      await col.add(shop);
      console.log(`  ✅ ${shop.nev} (${shop.tipus === 'bar' ? '🍸 Bár' : '🏪 Bolt'})`);
      ok++;
    } catch(e) {
      console.error(`  ❌ ${shop.nev}: ${e.message}`);
    }
  }

  console.log(`\n🎉 Kész! ${ok}/${shops.length} bejegyzés feltöltve.`);
  process.exit(0);
}

seed().catch(err => {
  console.error('Hiba:', err);
  process.exit(1);
});

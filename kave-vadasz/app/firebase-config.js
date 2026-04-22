// firebase-config.js
// © 2026 Kávé Vadász – Firebase konfiguráció
// Ez a fájl OPCIONÁLIS – csak Analytics/Firestore használathoz szükséges.
// A Firebase Hosting deploy NEM igényli ezt a fájlt.

import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";

const firebaseConfig = {
  apiKey: "AIzaSyD-s7ys1PubkPbPboN-rh1zLdMK7foCQ5o",
  authDomain: "kave-vadasz.firebaseapp.com",
  projectId: "kave-vadasz",
  storageBucket: "kave-vadasz.firebasestorage.app",
  messagingSenderId: "84542409114",
  appId: "1:84542409114:web:c8e39746535bd6ecbe1223",
  measurementId: "G-B4WGC6TLGN"
};

const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);

export { app, analytics };

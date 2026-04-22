// © 2026 Pizza Vadász – Service Worker
const CACHE_NAME = 'pizza-vadasz-v1';
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  'https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@400;500;600&display=swap'
];

// ── INSTALL: előre gyorsítótárazza a statikus fájlokat
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(STATIC_ASSETS);
    })
  );
  self.skipWaiting();
});

// ── ACTIVATE: régi cache törlése
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
      )
    )
  );
  self.clients.claim();
});

// ── FETCH: Cache-first statikushoz, Network-first API-hoz
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);

  // Overpass API és Google Maps – mindig hálózatról
  if (
    url.hostname.includes('overpass-api.de') ||
    url.hostname.includes('maps.googleapis.com') ||
    url.hostname.includes('maps.gstatic.com')
  ) {
    event.respondWith(fetch(event.request));
    return;
  }

  // OSM tile-ok – cache, ha van, különben hálózat
  if (url.hostname.includes('tile.openstreetmap.org')) {
    event.respondWith(
      caches.match(event.request).then(cached =>
        cached || fetch(event.request).then(response => {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
          return response;
        })
      )
    );
    return;
  }

  // Minden más: Cache-first
  event.respondWith(
    caches.match(event.request).then(cached => {
      if (cached) return cached;
      return fetch(event.request).then(response => {
        if (!response || response.status !== 200 || response.type === 'opaque') {
          return response;
        }
        const clone = response.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
        return response;
      });
    })
  );
});

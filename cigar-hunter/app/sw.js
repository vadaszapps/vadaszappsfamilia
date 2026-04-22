const CACHE_NAME = 'cigar-hunter-v1';
const ASSETS = [
    '/',
    '/index.html'
];

self.addEventListener('install', function(e) {
    e.waitUntil(
        caches.open(CACHE_NAME).then(function(cache) {
            return cache.addAll(ASSETS);
        })
    );
    self.skipWaiting();
});

self.addEventListener('activate', function(e) {
    e.waitUntil(
        caches.keys().then(function(keys) {
            return Promise.all(
                keys.filter(function(k) { return k !== CACHE_NAME; })
                    .map(function(k) { return caches.delete(k); })
            );
        })
    );
    self.clients.claim();
});

self.addEventListener('fetch', function(e) {
    // Csak GET kérések, ne cache-eljük az API hívásokat
    if (e.request.method !== 'GET') return;
    if (e.request.url.includes('firestore.googleapis.com')) return;
    if (e.request.url.includes('generativelanguage.googleapis.com')) return;
    if (e.request.url.includes('maps.googleapis.com')) return;

    e.respondWith(
        fetch(e.request).catch(function() {
            return caches.match(e.request).then(function(r) {
                return r || caches.match('/index.html');
            });
        })
    );
});

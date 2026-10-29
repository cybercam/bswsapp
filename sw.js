// v3: pages are fetched from the network first so site updates reach returning visitors;
// the cache is only an offline fallback. Static assets are served from cache, refreshed in the background.
const CACHE_NAME = 'bsws-bible-v3';
const PRECACHE = [
  '/bible/',
  '/bible/assets/style.css',
  '/bible/assets/reader.js',
  '/bible/manifest.json',
];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE_NAME).then((c) => c.addAll(PRECACHE)));
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(caches.keys().then((keys) =>
    Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
  ));
  self.clients.claim();
});

function cachePut(request, response) {
  if (response.ok && request.url.includes('/bible/')) {
    const copy = response.clone();
    caches.open(CACHE_NAME).then((c) => c.put(request, copy));
  }
  return response;
}

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== self.location.origin) return;
  const isPage = req.mode === 'navigate' || (req.headers.get('accept') || '').includes('text/html');
  if (isPage) {
    e.respondWith(fetch(req).then((res) => cachePut(req, res)).catch(() => caches.match(req)));
    return;
  }
  e.respondWith(caches.match(req).then((cached) => {
    const network = fetch(req).then((res) => cachePut(req, res)).catch(() => cached);
    return cached || network;
  }));
});

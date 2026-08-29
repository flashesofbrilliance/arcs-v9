const SHELL = [
  '/resume-tailor-pwa.html',
  '/resume-tailor-manifest.json',
  '/resume-tailor-icon-192.png',
  '/resume-tailor-icon-512.png',
];

const CACHE = 'resume-tailor-pwa-v1';
const STATIC = 'resume-tailor-static-v1';

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(STATIC).then(c => c.addAll(SHELL)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.filter(k => k !== CACHE && k !== STATIC).map(k => caches.delete(k))
    )).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);

  // Shell resources: cache-first
  if (SHELL.some(s => url.pathname.endsWith(s))) {
    e.respondWith(
      caches.match(e.request).then(r => r || fetch(e.request).then(resp => {
        const copy = resp.clone();
        caches.open(STATIC).then(c => c.put(e.request, copy));
        return resp;
      }))
    );
    return;
  }

  // CDN / external: network-first (MUI, fonts, GitHub)
  if (url.origin !== self.location.origin) {
    e.respondWith(
      fetch(e.request).catch(() => caches.match(e.request))
    );
    return;
  }

  // Everything else on the app origin: stale-while-revalidate
  e.respondWith(
    caches.match(e.request).then(cached => {
      const fetchPromise = fetch(e.request).then(network => {
        caches.open(STATIC).then(c => c.put(e.request, network.clone()));
        return network;
      }).catch(() => cached);
      return cached || fetchPromise;
    })
  );
});

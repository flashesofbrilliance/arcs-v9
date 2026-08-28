// resume-sw.js — service worker for Zach Harris Resume (resume.arcs.care)
// Scope: the standalone public/resume.html surface.
// Strategy: cache-first for the shell (HTML + fonts + icons), network-first
// for analytics/toolbar scripts (they're Vercel CDN, tolerate staleness).

const CACHE = 'resume-shell-v1';
const SHELL_URLS = [
  '/',
  '/resume.html',
  '/manifest.json',
  '/resume-icon-192.png',
  '/resume-icon-512.png',
  'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap',
];

async function cacheShell() {
  const cache = await caches.open(CACHE);
  await cache.addAll(SHELL_URLS);
}

async function serveFromCache(request) {
  const cached = await caches.match(request);
  if (cached) return cached;
  // fallback: fetch from network and stash
  try {
    const network = await fetch(request);
    if (network.ok) {
      const cache = await caches.open(CACHE);
      cache.put(request, new Response(network.body, { status: network.status, statusText: network.statusText, headers: network.headers }));
    }
    return network;
  } catch (e) {
    // offline: return a minimal opaque response so the page doesn't crash
    return new Response('', { status: 503, statusText: 'Offline' });
  }
}

self.addEventListener('install', (event) => {
  event.waitUntil(cacheShell());
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(
      keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))
    ))
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // Vercel analytics/toolbar: network-first, tolerate staleness.
  if (url.hostname === 'www.vercel-analytics.com' || url.pathname.startsWith('/_vercel/')) {
    event.respondWith(
      fetch(event.request).catch(() => caches.match(event.request))
    );
    return;
  }

  // Anything already in cache: serve it.
  event.respondWith(serveFromCache(event.request));
});

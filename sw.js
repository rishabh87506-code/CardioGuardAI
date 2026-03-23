/**
 * CardioGuard AI — Service Worker v4.9
 * Cache strategy:
 *   - Precache: /, /logo.png, /manifest.json
 *   - Network-first: /api/* (graceful offline message)
 *   - Cache-first + background update: everything else
 */

const CACHE_NAME = 'cgai-v4.9.1';
const PRECACHE = ['/', '/logo.png', '/manifest.json'];

// ── INSTALL ─────────────────────────────────────────────
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(PRECACHE))
      .then(() => self.skipWaiting())
  );
});

// ── ACTIVATE: clear old caches ────────────────────────
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
      )
    ).then(() => self.clients.claim())
  );
});

// ── FETCH ─────────────────────────────────────────────
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // Only handle GET requests
  if (request.method !== 'GET') return;

  // Skip non-same-origin (except Google Fonts)
  const isSameOrigin = url.origin === self.location.origin;
  const isFonts = url.hostname === 'fonts.gstatic.com' || url.hostname === 'fonts.googleapis.com';
  if (!isSameOrigin && !isFonts) return;

  // Network-first for API calls
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(request).catch(() =>
        new Response(
          JSON.stringify({ error: 'Offline — please check your connection', offline: true }),
          { status: 503, headers: { 'Content-Type': 'application/json' } }
        )
      )
    );
    return;
  }

  // Cache-first with background update for static assets
  event.respondWith(
    caches.open(CACHE_NAME).then(cache =>
      cache.match(request).then(cached => {
        const networkFetch = fetch(request).then(response => {
          if (response.ok && request.method === 'GET') {
            cache.put(request, response.clone());
          }
          return response;
        }).catch(() => cached); // fallback to cache if network fails

        // Return cache immediately if available; update in background
        return cached || networkFetch;
      })
    ).catch(() => caches.match('/'))
  );
});

// ── PUSH NOTIFICATIONS (future) ──────────────────────
self.addEventListener('push', event => {
  if (!event.data) return;
  const data = event.data.json();
  self.registration.showNotification(data.title || 'CardioGuard AI', {
    body: data.body || '',
    icon: '/logo.png',
    badge: '/logo.png',
    vibrate: [200, 100, 200],
    tag: data.tag || 'cgai',
    data: { url: data.url || '/' }
  });
});

self.addEventListener('notificationclick', event => {
  event.notification.close();
  event.waitUntil(
    clients.openWindow(event.notification.data?.url || '/')
  );
});

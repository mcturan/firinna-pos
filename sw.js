// Fırınna POS — Service Worker v1.0
// Cache adı — değişince eski cache temizlenir
const CACHE_NAME = 'firinna-pos-v1';

// Offline çalışabilmesi için önbelleğe alınacak statik dosyalar
const STATIC_ASSETS = [
  '/',
  '/static/css/style.css',
  '/static/favicon.svg',
  '/offline.html'
];

// Install: statik dosyaları önbelleğe al
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(STATIC_ASSETS).catch(() => {
        // Bazı dosyalar yoksa sessizce geç
      });
    })
  );
  self.skipWaiting();
});

// Activate: eski cache'leri temizle
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// Fetch: API isteklerini her zaman ağdan al, statikleri cache-first
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);

  // API istekleri: her zaman ağ, hata varsa JSON döndür
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(event.request).catch(() =>
        new Response(JSON.stringify({ error: 'offline', message: 'İnternet bağlantısı yok' }),
          { headers: { 'Content-Type': 'application/json' } })
      )
    );
    return;
  }

  // Statik dosyalar: önce cache, sonra ağ
  if (url.pathname.startsWith('/static/')) {
    event.respondWith(
      caches.match(event.request).then(cached => cached || fetch(event.request))
    );
    return;
  }

  // Sayfalar: ağ-first, çevrimdışıysa offline.html
  event.respondWith(
    fetch(event.request).catch(() => caches.match('/offline.html'))
  );
});

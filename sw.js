const CACHE_NAME = 'staff-app-v1';
const urlsToCache = [
  '/staff/dashboard',
  '/staff/login',
  // Мы убрали фавиконки из кэша, чтобы не вызывать ошибок, если их нет
];

self.addEventListener('install', event => {
  self.skipWaiting(); // Заставляет SW активироваться немедленно
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        return cache.addAll(urlsToCache);
      })
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(self.clients.claim()); // Захватываем контроль над клиентами немедленно
});

self.addEventListener('fetch', event => {
  // Простая стратегия: сначала сеть, если нет — то кэш (для PWA важно)
  // Или Cache First, Network Fallback
  event.respondWith(
    fetch(event.request).catch(() => {
      return caches.match(event.request);
    })
  );
});
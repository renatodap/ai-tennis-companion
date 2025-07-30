// 🎾 TENNISVIZ SERVICE WORKER - Elite PWA Functionality
const CACHE_NAME = 'tennisviz-v1.0.0';
const STATIC_CACHE = 'tennisviz-static-v1';
const DYNAMIC_CACHE = 'tennisviz-dynamic-v1';

// Files to cache immediately
const STATIC_FILES = [
  '/tennisviz-app.html',
  '/tennisviz-app.js',
  '/manifest.json',
  '/icons/icon-192.png',
  '/icons/icon-512.png'
];

// Install event - cache static files
self.addEventListener('install', event => {
  console.log('🎾 TennisViz SW: Installing...');
  
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then(cache => {
        console.log('🎾 TennisViz SW: Caching static files');
        return cache.addAll(STATIC_FILES);
      })
      .then(() => {
        console.log('🎾 TennisViz SW: Installation complete');
        return self.skipWaiting();
      })
      .catch(error => {
        console.error('🎾 TennisViz SW: Installation failed:', error);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  console.log('🎾 TennisViz SW: Activating...');
  
  event.waitUntil(
    caches.keys()
      .then(cacheNames => {
        return Promise.all(
          cacheNames.map(cacheName => {
            if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
              console.log('🎾 TennisViz SW: Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('🎾 TennisViz SW: Activation complete');
        return self.clients.claim();
      })
  );
});

// Fetch event - handle network requests
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Handle API requests
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(handleApiRequest(request));
    return;
  }
  
  // Handle static files
  if (request.destination === 'document' || 
      request.destination === 'script' || 
      request.destination === 'style' ||
      request.destination === 'image') {
    event.respondWith(handleStaticRequest(request));
    return;
  }
  
  // Default: network first
  event.respondWith(fetch(request));
});

// Handle API requests with cache-first strategy for GET, network-only for POST
async function handleApiRequest(request) {
  const cache = await caches.open(DYNAMIC_CACHE);
  
  if (request.method === 'GET') {
    // Try cache first for GET requests
    const cachedResponse = await cache.match(request);
    if (cachedResponse) {
      console.log('🎾 TennisViz SW: Serving from cache:', request.url);
      return cachedResponse;
    }
  }
  
  try {
    const response = await fetch(request);
    
    // Cache successful GET responses
    if (request.method === 'GET' && response.ok) {
      cache.put(request, response.clone());
    }
    
    return response;
  } catch (error) {
    console.error('🎾 TennisViz SW: API request failed:', error);
    
    // Return offline fallback for failed requests
    return new Response(
      JSON.stringify({
        error: 'Network unavailable',
        message: 'Please check your connection and try again',
        offline: true
      }),
      {
        status: 503,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// Handle static files with cache-first strategy
async function handleStaticRequest(request) {
  const cache = await caches.open(STATIC_CACHE);
  
  // Try cache first
  const cachedResponse = await cache.match(request);
  if (cachedResponse) {
    console.log('🎾 TennisViz SW: Serving static from cache:', request.url);
    return cachedResponse;
  }
  
  try {
    const response = await fetch(request);
    
    // Cache successful responses
    if (response.ok) {
      cache.put(request, response.clone());
    }
    
    return response;
  } catch (error) {
    console.error('🎾 TennisViz SW: Static request failed:', error);
    
    // Return offline fallback page
    if (request.destination === 'document') {
      return new Response(
        `<!DOCTYPE html>
        <html>
        <head>
          <title>TennisViz - Offline</title>
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <style>
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                   text-align: center; padding: 50px; background: #f5f5f7; }
            .offline { color: #666; }
            .logo { font-size: 2em; margin-bottom: 20px; }
          </style>
        </head>
        <body>
          <div class="logo">🎾 TennisViz</div>
          <h1>You're Offline</h1>
          <p class="offline">Please check your internet connection and try again.</p>
          <button onclick="location.reload()">Retry</button>
        </body>
        </html>`,
        {
          headers: { 'Content-Type': 'text/html' }
        }
      );
    }
    
    throw error;
  }
}

// Background sync for offline uploads
self.addEventListener('sync', (event) => {
  if (event.tag === 'background-sync') {
    event.waitUntil(doBackgroundSync());
  }
});

function doBackgroundSync() {
  // Handle offline video uploads when connection is restored
  return new Promise((resolve) => {
    // Implementation for handling queued uploads
    resolve();
  });
}

// Push notifications for analysis completion
self.addEventListener('push', (event) => {
  const data = event.data ? event.data.json() : {};
  
  const options = {
    title: data.title || '🎾 TennisViz Analysis Complete',
    body: data.body || 'Your tennis analysis results are ready!',
    icon: '/icons/icon-192.png',
    badge: '/icons/icon-192.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      analysisId: data.analysisId,
      url: data.url || '/'
    },
    actions: [
      {
        action: 'view',
        title: 'View Results',
        icon: '/icons/icon-192.png'
      },
      {
        action: 'close',
        title: 'Close'
      }
    ],
    requireInteraction: true
  };
  
  event.waitUntil(
    self.registration.showNotification(options.title, options)
  );
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  
  if (event.action === 'view') {
    const urlToOpen = event.notification.data.url || '/';
    
    event.waitUntil(
      clients.matchAll({ type: 'window' })
        .then(clientList => {
          // Check if app is already open
          for (const client of clientList) {
            if (client.url === urlToOpen && 'focus' in client) {
              return client.focus();
            }
          }
          
          // Open new window if app not open
          if (clients.openWindow) {
            return clients.openWindow(urlToOpen);
          }
        })
    );
  }
});

// Handle messages from main app
self.addEventListener('message', (event) => {
  console.log('🎾 TennisViz SW: Received message:', event.data);
  
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'GET_VERSION') {
    event.ports[0].postMessage({ version: CACHE_NAME });
  }
});

// Utility function to broadcast messages to all clients
async function broadcastMessage(message) {
  const clients = await self.clients.matchAll();
  clients.forEach(client => {
    client.postMessage(message);
  });
}

console.log('🎾 TennisViz Service Worker loaded successfully!');

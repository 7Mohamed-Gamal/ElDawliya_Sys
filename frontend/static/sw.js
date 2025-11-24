/**
 * Service Worker for ElDawliya System
 * ==================================
 * 
 * Advanced caching strategies and offline functionality
 */

const CACHE_NAME = 'eldawliya-v1.0.0';
const STATIC_CACHE = 'eldawliya-static-v1.0.0';
const DYNAMIC_CACHE = 'eldawliya-dynamic-v1.0.0';
const API_CACHE = 'eldawliya-api-v1.0.0';

// Resources to cache immediately
const STATIC_ASSETS = [
    '/',
    '/static/css/base-enhanced.css',
    '/static/css/components.css',
    '/static/css/design-system.css',
    '/static/js/components.js',
    '/static/js/theme-system.js',
    '/static/js/performance-optimizer.js',
    '/static/fonts/cairo-regular.woff2',
    '/static/fonts/cairo-bold.woff2',
    '/static/images/logo.png',
    '/offline/',
];

// API endpoints to cache
const API_ENDPOINTS = [
    '/api/v1/dashboard/stats/',
    '/api/v1/employees/',
    '/api/v1/departments/',
    '/api/v1/attendance/summary/',
];

// Cache strategies
const CACHE_STRATEGIES = {
    CACHE_FIRST: 'cache-first',
    NETWORK_FIRST: 'network-first',
    STALE_WHILE_REVALIDATE: 'stale-while-revalidate',
    NETWORK_ONLY: 'network-only',
    CACHE_ONLY: 'cache-only',
};

// Route configurations
const ROUTE_CONFIG = [
    {
        pattern: /^https:\/\/.*\.(?:png|jpg|jpeg|svg|gif|webp)$/,
        strategy: CACHE_STRATEGIES.CACHE_FIRST,
        cache: STATIC_CACHE,
        maxAge: 30 * 24 * 60 * 60 * 1000, // 30 days
    },
    {
        pattern: /^https:\/\/.*\.(?:css|js|woff|woff2|ttf|eot)$/,
        strategy: CACHE_STRATEGIES.CACHE_FIRST,
        cache: STATIC_CACHE,
        maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days
    },
    {
        pattern: /\/api\/v1\//,
        strategy: CACHE_STRATEGIES.NETWORK_FIRST,
        cache: API_CACHE,
        maxAge: 5 * 60 * 1000, // 5 minutes
    },
    {
        pattern: /\/static\//,
        strategy: CACHE_STRATEGIES.CACHE_FIRST,
        cache: STATIC_CACHE,
        maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days
    },
    {
        pattern: /\/(Hr|inventory|api|core)\//,
        strategy: CACHE_STRATEGIES.STALE_WHILE_REVALIDATE,
        cache: DYNAMIC_CACHE,
        maxAge: 60 * 60 * 1000, // 1 hour
    },
];

/**
 * Service Worker Installation
 */
self.addEventListener('install', event => {
    console.log('🔧 Service Worker installing...');
    
    event.waitUntil(
        Promise.all([
            // Cache static assets
            caches.open(STATIC_CACHE).then(cache => {
                console.log('📦 Caching static assets');
                return cache.addAll(STATIC_ASSETS);
            }),
            
            // Cache API endpoints
            caches.open(API_CACHE).then(cache => {
                console.log('🔗 Pre-caching API endpoints');
                return Promise.all(
                    API_ENDPOINTS.map(endpoint => {
                        return fetch(endpoint)
                            .then(response => {
                                if (response.ok) {
                                    return cache.put(endpoint, response);
                                }
                            })
                            .catch(error => {
                                console.warn(`Failed to cache ${endpoint}:`, error);
                            });
                    })
                );
            }),
        ]).then(() => {
            console.log('✅ Service Worker installed successfully');
            // Skip waiting to activate immediately
            return self.skipWaiting();
        })
    );
});

/**
 * Service Worker Activation
 */
self.addEventListener('activate', event => {
    console.log('🚀 Service Worker activating...');
    
    event.waitUntil(
        Promise.all([
            // Clean up old caches
            cleanupOldCaches(),
            
            // Claim all clients
            self.clients.claim(),
        ]).then(() => {
            console.log('✅ Service Worker activated successfully');
        })
    );
});

/**
 * Fetch Event Handler
 */
self.addEventListener('fetch', event => {
    const request = event.request;
    const url = new URL(request.url);
    
    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }
    
    // Skip chrome-extension and other non-http requests
    if (!url.protocol.startsWith('http')) {
        return;
    }
    
    // Find matching route configuration
    const routeConfig = findRouteConfig(request.url);
    
    if (routeConfig) {
        event.respondWith(
            handleRequest(request, routeConfig)
        );
    } else {
        // Default strategy for unmatched routes
        event.respondWith(
            handleRequest(request, {
                strategy: CACHE_STRATEGIES.NETWORK_FIRST,
                cache: DYNAMIC_CACHE,
                maxAge: 60 * 60 * 1000, // 1 hour
            })
        );
    }
});

/**
 * Background Sync
 */
self.addEventListener('sync', event => {
    console.log('🔄 Background sync triggered:', event.tag);
    
    if (event.tag === 'background-sync') {
        event.waitUntil(
            syncData()
        );
    }
});

/**
 * Push Notifications
 */
self.addEventListener('push', event => {
    console.log('📱 Push notification received');
    
    const options = {
        body: event.data ? event.data.text() : 'إشعار جديد من نظام الدولية',
        icon: '/static/images/icon-192x192.png',
        badge: '/static/images/badge-72x72.png',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        },
        actions: [
            {
                action: 'explore',
                title: 'عرض',
                icon: '/static/images/checkmark.png'
            },
            {
                action: 'close',
                title: 'إغلاق',
                icon: '/static/images/xmark.png'
            },
        ]
    };
    
    event.waitUntil(
        self.registration.showNotification('نظام الدولية', options)
    );
});

/**
 * Notification Click Handler
 */
self.addEventListener('notificationclick', event => {
    console.log('🔔 Notification clicked:', event.notification.tag);
    
    event.notification.close();
    
    if (event.action === 'explore') {
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});

/**
 * Helper Functions
 */

function findRouteConfig(url) {
    return ROUTE_CONFIG.find(config => config.pattern.test(url));
}

async function handleRequest(request, config) {
    const { strategy, cache: cacheName, maxAge } = config;
    
    switch (strategy) {
        case CACHE_STRATEGIES.CACHE_FIRST:
            return cacheFirst(request, cacheName, maxAge);
        
        case CACHE_STRATEGIES.NETWORK_FIRST:
            return networkFirst(request, cacheName, maxAge);
        
        case CACHE_STRATEGIES.STALE_WHILE_REVALIDATE:
            return staleWhileRevalidate(request, cacheName, maxAge);
        
        case CACHE_STRATEGIES.NETWORK_ONLY:
            return fetch(request);
        
        case CACHE_STRATEGIES.CACHE_ONLY:
            return caches.match(request);
        
        default:
            return networkFirst(request, cacheName, maxAge);
    }
}

async function cacheFirst(request, cacheName, maxAge) {
    const cache = await caches.open(cacheName);
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse && !isExpired(cachedResponse, maxAge)) {
        return cachedResponse;
    }
    
    try {
        const networkResponse = await fetch(request);
        
        if (networkResponse.ok) {
            // Clone the response before caching
            const responseToCache = networkResponse.clone();
            await cache.put(request, responseToCache);
        }
        
        return networkResponse;
    } catch (error) {
        console.warn('Network failed, serving from cache:', error);
        
        // Return cached response even if expired
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Return offline page for navigation requests
        if (request.mode === 'navigate') {
            return caches.match('/offline/');
        }
        
        throw error;
    }
}

async function networkFirst(request, cacheName, maxAge) {
    const cache = await caches.open(cacheName);
    
    try {
        const networkResponse = await fetch(request);
        
        if (networkResponse.ok) {
            // Clone the response before caching
            const responseToCache = networkResponse.clone();
            await cache.put(request, responseToCache);
        }
        
        return networkResponse;
    } catch (error) {
        console.warn('Network failed, trying cache:', error);
        
        const cachedResponse = await cache.match(request);
        
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Return offline page for navigation requests
        if (request.mode === 'navigate') {
            return caches.match('/offline/');
        }
        
        throw error;
    }
}

async function staleWhileRevalidate(request, cacheName, maxAge) {
    const cache = await caches.open(cacheName);
    const cachedResponse = await cache.match(request);
    
    // Always try to fetch from network in background
    const networkResponsePromise = fetch(request).then(response => {
        if (response.ok) {
            const responseToCache = response.clone();
            cache.put(request, responseToCache);
        }
        return response;
    }).catch(error => {
        console.warn('Background fetch failed:', error);
    });
    
    // Return cached response immediately if available
    if (cachedResponse) {
        return cachedResponse;
    }
    
    // If no cached response, wait for network
    return networkResponsePromise;
}

function isExpired(response, maxAge) {
    if (!maxAge) return false;
    
    const dateHeader = response.headers.get('date');
    if (!dateHeader) return false;
    
    const responseTime = new Date(dateHeader).getTime();
    const now = Date.now();
    
    return (now - responseTime) > maxAge;
}

async function cleanupOldCaches() {
    const cacheNames = await caches.keys();
    const currentCaches = [STATIC_CACHE, DYNAMIC_CACHE, API_CACHE];
    
    return Promise.all(
        cacheNames.map(cacheName => {
            if (!currentCaches.includes(cacheName)) {
                console.log('🗑️ Deleting old cache:', cacheName);
                return caches.delete(cacheName);
            }
        })
    );
}

async function syncData() {
    console.log('🔄 Syncing data in background...');
    
    try {
        // Get pending sync data from IndexedDB
        const pendingData = await getPendingSyncData();
        
        if (pendingData.length > 0) {
            for (const data of pendingData) {
                try {
                    await fetch(data.url, {
                        method: data.method,
                        headers: data.headers,
                        body: data.body,
                    });
                    
                    // Remove from pending sync after successful upload
                    await removePendingSyncData(data.id);
                } catch (error) {
                    console.error('Failed to sync data:', error);
                }
            }
        }
        
        console.log('✅ Background sync completed');
    } catch (error) {
        console.error('Background sync failed:', error);
    }
}

// IndexedDB helpers for background sync
async function getPendingSyncData() {
    // This would typically read from IndexedDB
    // For now, return empty array
    return [];
}

async function removePendingSyncData(id) {
    // This would typically remove from IndexedDB
    console.log('Removing synced data:', id);
}

// Cache management utilities
async function getCacheSize(cacheName) {
    const cache = await caches.open(cacheName);
    const keys = await cache.keys();
    
    let totalSize = 0;
    for (const key of keys) {
        const response = await cache.match(key);
        if (response) {
            const blob = await response.blob();
            totalSize += blob.size;
        }
    }
    
    return totalSize;
}

async function limitCacheSize(cacheName, maxSize) {
    const cache = await caches.open(cacheName);
    const keys = await cache.keys();
    
    let currentSize = await getCacheSize(cacheName);
    
    // Remove oldest entries if cache is too large
    while (currentSize > maxSize && keys.length > 0) {
        const oldestKey = keys.shift();
        await cache.delete(oldestKey);
        currentSize = await getCacheSize(cacheName);
    }
}

// Periodic cache cleanup
setInterval(async () => {
    try {
        // Limit cache sizes
        await limitCacheSize(DYNAMIC_CACHE, 50 * 1024 * 1024); // 50MB
        await limitCacheSize(API_CACHE, 10 * 1024 * 1024); // 10MB
        
        console.log('🧹 Cache cleanup completed');
    } catch (error) {
        console.error('Cache cleanup failed:', error);
    }
}, 60 * 60 * 1000); // Every hour
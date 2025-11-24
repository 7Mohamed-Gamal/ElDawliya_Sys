/**
 * Frontend Performance Optimizer
 * =============================
 * 
 * Advanced frontend optimization including:
 * - Lazy loading for images and content
 * - Resource preloading and prefetching
 * - Service worker for caching
 * - Performance monitoring
 * - Progressive Web App features
 */

class PerformanceOptimizer {
    constructor() {
        this.config = {
            lazyLoadOffset: 100,
            preloadDelay: 2000,
            cacheVersion: 'v1.0.0',
            enableServiceWorker: true,
            enableLazyLoading: true,
            enablePreloading: true,
            enablePerformanceMonitoring: true,
        };
        
        this.performanceMetrics = {
            pageLoadTime: 0,
            domContentLoadedTime: 0,
            firstContentfulPaint: 0,
            largestContentfulPaint: 0,
            cumulativeLayoutShift: 0,
            firstInputDelay: 0,
        };
        
        this.init();
    }
    
    init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initializeOptimizations());
        } else {
            this.initializeOptimizations();
        }
    }
    
    initializeOptimizations() {
        console.log('🚀 Initializing Performance Optimizer');
        
        // Initialize optimizations
        if (this.config.enableLazyLoading) {
            this.initLazyLoading();
        }
        
        if (this.config.enablePreloading) {
            this.initResourcePreloading();
        }
        
        if (this.config.enableServiceWorker) {
            this.initServiceWorker();
        }
        
        if (this.config.enablePerformanceMonitoring) {
            this.initPerformanceMonitoring();
        }
        
        // Initialize PWA features
        this.initPWAFeatures();
        
        // Optimize images
        this.optimizeImages();
        
        // Optimize fonts
        this.optimizeFonts();
        
        // Initialize critical resource hints
        this.initResourceHints();
        
        console.log('✅ Performance Optimizer initialized');
    }
    
    /**
     * Lazy Loading Implementation
     */
    initLazyLoading() {
        // Use Intersection Observer for modern browsers
        if ('IntersectionObserver' in window) {
            this.initIntersectionObserver();
        } else {
            // Fallback for older browsers
            this.initScrollBasedLazyLoading();
        }
    }
    
    initIntersectionObserver() {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    this.loadImage(img);
                    observer.unobserve(img);
                }
            });
        }, {
            rootMargin: `${this.config.lazyLoadOffset}px`
        });
        
        // Observe all lazy images
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
        
        // Lazy load content sections
        const contentObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const element = entry.target;
                    this.loadContent(element);
                    observer.unobserve(element);
                }
            });
        }, {
            rootMargin: `${this.config.lazyLoadOffset}px`
        });
        
        document.querySelectorAll('[data-lazy-content]').forEach(element => {
            contentObserver.observe(element);
        });
    }
    
    initScrollBasedLazyLoading() {
        const lazyImages = document.querySelectorAll('img[data-src]');
        
        const loadImagesOnScroll = () => {
            lazyImages.forEach(img => {
                if (this.isElementInViewport(img)) {
                    this.loadImage(img);
                }
            });
        };
        
        window.addEventListener('scroll', this.throttle(loadImagesOnScroll, 100));
        window.addEventListener('resize', this.throttle(loadImagesOnScroll, 100));
        
        // Initial load
        loadImagesOnScroll();
    }
    
    loadImage(img) {
        const src = img.dataset.src;
        const srcset = img.dataset.srcset;
        
        if (src) {
            // Create a new image to preload
            const newImg = new Image();
            
            newImg.onload = () => {
                img.src = src;
                if (srcset) {
                    img.srcset = srcset;
                }
                img.classList.add('loaded');
                img.classList.remove('loading');
            };
            
            newImg.onerror = () => {
                img.classList.add('error');
                img.classList.remove('loading');
            };
            
            img.classList.add('loading');
            newImg.src = src;
        }
    }
    
    loadContent(element) {
        const contentUrl = element.dataset.lazyContent;
        
        if (contentUrl) {
            element.classList.add('loading');
            
            fetch(contentUrl)
                .then(response => response.text())
                .then(html => {
                    element.innerHTML = html;
                    element.classList.add('loaded');
                    element.classList.remove('loading');
                    
                    // Re-initialize any scripts in the loaded content
                    this.initializeLoadedContent(element);
                })
                .catch(error => {
                    console.error('Error loading content:', error);
                    element.classList.add('error');
                    element.classList.remove('loading');
                });
        }
    }
    
    initializeLoadedContent(container) {
        // Re-initialize lazy loading for new images
        container.querySelectorAll('img[data-src]').forEach(img => {
            this.loadImage(img);
        });
        
        // Initialize any other components in the loaded content
        if (window.initializeComponents) {
            window.initializeComponents(container);
        }
    }
    
    /**
     * Resource Preloading
     */
    initResourcePreloading() {
        // Preload critical resources
        setTimeout(() => {
            this.preloadCriticalResources();
        }, this.config.preloadDelay);
        
        // Preload on hover for navigation links
        this.initHoverPreloading();
    }
    
    preloadCriticalResources() {
        const criticalResources = [
            '/static/css/components.css',
            '/static/js/components.js',
            '/static/fonts/cairo-regular.woff2',
        ];
        
        criticalResources.forEach(resource => {
            this.preloadResource(resource);
        });
    }
    
    preloadResource(url, type = 'fetch') {
        const link = document.createElement('link');
        link.rel = 'preload';
        link.href = url;
        
        if (type === 'style') {
            link.as = 'style';
        } else if (type === 'script') {
            link.as = 'script';
        } else if (type === 'font') {
            link.as = 'font';
            link.crossOrigin = 'anonymous';
        } else {
            link.as = 'fetch';
            link.crossOrigin = 'anonymous';
        }
        
        document.head.appendChild(link);
    }
    
    initHoverPreloading() {
        const navigationLinks = document.querySelectorAll('a[href^="/"]');
        
        navigationLinks.forEach(link => {
            let preloadTimeout;
            
            link.addEventListener('mouseenter', () => {
                preloadTimeout = setTimeout(() => {
                    this.prefetchPage(link.href);
                }, 100);
            });
            
            link.addEventListener('mouseleave', () => {
                if (preloadTimeout) {
                    clearTimeout(preloadTimeout);
                }
            });
        });
    }
    
    prefetchPage(url) {
        if (this.prefetchedPages?.has(url)) {
            return;
        }
        
        if (!this.prefetchedPages) {
            this.prefetchedPages = new Set();
        }
        
        const link = document.createElement('link');
        link.rel = 'prefetch';
        link.href = url;
        document.head.appendChild(link);
        
        this.prefetchedPages.add(url);
    }
    
    /**
     * Service Worker
     */
    initServiceWorker() {
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', () => {
                navigator.serviceWorker.register('/sw.js')
                    .then(registration => {
                        console.log('✅ Service Worker registered:', registration);
                        
                        // Check for updates
                        registration.addEventListener('updatefound', () => {
                            const newWorker = registration.installing;
                            newWorker.addEventListener('statechange', () => {
                                if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                                    this.showUpdateNotification();
                                }
                            });
                        });
                    })
                    .catch(error => {
                        console.error('❌ Service Worker registration failed:', error);
                    });
            });
        }
    }
    
    showUpdateNotification() {
        const notification = document.createElement('div');
        notification.className = 'update-notification';
        notification.innerHTML = `
            <div class="update-content">
                <span>تحديث جديد متاح</span>
                <button onclick="window.location.reload()" class="btn btn-primary btn-sm">تحديث</button>
                <button onclick="this.parentElement.parentElement.remove()" class="btn btn-secondary btn-sm">لاحقاً</button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-hide after 10 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 10000);
    }
    
    /**
     * Performance Monitoring
     */
    initPerformanceMonitoring() {
        // Monitor page load performance
        window.addEventListener('load', () => {
            this.measurePerformanceMetrics();
        });
        
        // Monitor Core Web Vitals
        this.initCoreWebVitals();
        
        // Monitor resource loading
        this.monitorResourceLoading();
    }
    
    measurePerformanceMetrics() {
        if ('performance' in window) {
            const navigation = performance.getEntriesByType('navigation')[0];
            
            this.performanceMetrics.pageLoadTime = navigation.loadEventEnd - navigation.fetchStart;
            this.performanceMetrics.domContentLoadedTime = navigation.domContentLoadedEventEnd - navigation.fetchStart;
            
            // Send metrics to server
            this.sendPerformanceMetrics();
        }
    }
    
    initCoreWebVitals() {
        // First Contentful Paint
        if ('PerformanceObserver' in window) {
            new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    if (entry.name === 'first-contentful-paint') {
                        this.performanceMetrics.firstContentfulPaint = entry.startTime;
                    }
                }
            }).observe({ entryTypes: ['paint'] });
            
            // Largest Contentful Paint
            new PerformanceObserver((list) => {
                const entries = list.getEntries();
                const lastEntry = entries[entries.length - 1];
                this.performanceMetrics.largestContentfulPaint = lastEntry.startTime;
            }).observe({ entryTypes: ['largest-contentful-paint'] });
            
            // Cumulative Layout Shift
            new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    if (!entry.hadRecentInput) {
                        this.performanceMetrics.cumulativeLayoutShift += entry.value;
                    }
                }
            }).observe({ entryTypes: ['layout-shift'] });
            
            // First Input Delay
            new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    this.performanceMetrics.firstInputDelay = entry.processingStart - entry.startTime;
                }
            }).observe({ entryTypes: ['first-input'] });
        }
    }
    
    monitorResourceLoading() {
        if ('PerformanceObserver' in window) {
            new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    if (entry.duration > 1000) { // Resources taking more than 1 second
                        console.warn(`Slow resource: ${entry.name} took ${entry.duration}ms`);
                    }
                }
            }).observe({ entryTypes: ['resource'] });
        }
    }
    
    sendPerformanceMetrics() {
        // Send metrics to server for analysis
        if (navigator.sendBeacon) {
            const data = JSON.stringify({
                url: window.location.href,
                metrics: this.performanceMetrics,
                timestamp: Date.now(),
                userAgent: navigator.userAgent,
            });
            
            navigator.sendBeacon('/api/performance-metrics/', data);
        }
    }
    
    /**
     * PWA Features
     */
    initPWAFeatures() {
        // Add to home screen prompt
        this.initInstallPrompt();
        
        // Handle offline functionality
        this.initOfflineHandling();
        
        // Background sync
        this.initBackgroundSync();
    }
    
    initInstallPrompt() {
        let deferredPrompt;
        
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
            
            // Show install button
            this.showInstallButton(deferredPrompt);
        });
        
        window.addEventListener('appinstalled', () => {
            console.log('✅ PWA installed');
            this.hideInstallButton();
        });
    }
    
    showInstallButton(deferredPrompt) {
        const installButton = document.createElement('button');
        installButton.className = 'install-button btn btn-primary';
        installButton.innerHTML = '<i class="fas fa-download"></i> تثبيت التطبيق';
        installButton.style.cssText = `
            position: fixed;
            bottom: 20px;
            left: 20px;
            z-index: 1000;
            border-radius: 25px;
            padding: 10px 20px;
        `;
        
        installButton.addEventListener('click', () => {
            deferredPrompt.prompt();
            deferredPrompt.userChoice.then((choiceResult) => {
                if (choiceResult.outcome === 'accepted') {
                    console.log('User accepted the install prompt');
                }
                deferredPrompt = null;
                installButton.remove();
            });
        });
        
        document.body.appendChild(installButton);
        
        // Auto-hide after 10 seconds
        setTimeout(() => {
            if (installButton.parentElement) {
                installButton.remove();
            }
        }, 10000);
    }
    
    hideInstallButton() {
        const installButton = document.querySelector('.install-button');
        if (installButton) {
            installButton.remove();
        }
    }
    
    initOfflineHandling() {
        window.addEventListener('online', () => {
            this.showConnectionStatus('متصل', 'success');
        });
        
        window.addEventListener('offline', () => {
            this.showConnectionStatus('غير متصل', 'warning');
        });
    }
    
    showConnectionStatus(message, type) {
        const notification = document.createElement('div');
        notification.className = `connection-status alert alert-${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 200px;
        `;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 3000);
    }
    
    initBackgroundSync() {
        if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
            // Register for background sync
            navigator.serviceWorker.ready.then(registration => {
                return registration.sync.register('background-sync');
            }).catch(error => {
                console.error('Background sync registration failed:', error);
            });
        }
    }
    
    /**
     * Image Optimization
     */
    optimizeImages() {
        // Convert images to WebP if supported
        if (this.supportsWebP()) {
            this.convertImagesToWebP();
        }
        
        // Add responsive image attributes
        this.addResponsiveImageAttributes();
        
        // Optimize image loading
        this.optimizeImageLoading();
    }
    
    supportsWebP() {
        const canvas = document.createElement('canvas');
        canvas.width = 1;
        canvas.height = 1;
        return canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0;
    }
    
    convertImagesToWebP() {
        document.querySelectorAll('img[src$=".jpg"], img[src$=".jpeg"], img[src$=".png"]').forEach(img => {
            const webpSrc = img.src.replace(/\.(jpg|jpeg|png)$/, '.webp');
            
            // Check if WebP version exists
            const testImg = new Image();
            testImg.onload = () => {
                img.src = webpSrc;
            };
            testImg.src = webpSrc;
        });
    }
    
    addResponsiveImageAttributes() {
        document.querySelectorAll('img:not([srcset])').forEach(img => {
            const src = img.src || img.dataset.src;
            if (src && !src.includes('data:')) {
                const baseSrc = src.replace(/\.(jpg|jpeg|png|webp)$/, '');
                const ext = src.match(/\.(jpg|jpeg|png|webp)$/)?.[0] || '.jpg';
                
                // Generate srcset for different screen densities
                const srcset = [
                    `${baseSrc}${ext} 1x`,
                    `${baseSrc}@2x${ext} 2x`,
                    `${baseSrc}@3x${ext} 3x`
                ].join(', ');
                
                img.srcset = srcset;
            }
        });
    }
    
    optimizeImageLoading() {
        // Add loading="lazy" to images below the fold
        document.querySelectorAll('img').forEach(img => {
            if (!this.isElementInViewport(img, 200)) {
                img.loading = 'lazy';
            }
        });
    }
    
    /**
     * Font Optimization
     */
    optimizeFonts() {
        // Preload critical fonts
        this.preloadCriticalFonts();
        
        // Use font-display: swap for better performance
        this.optimizeFontDisplay();
    }
    
    preloadCriticalFonts() {
        const criticalFonts = [
            '/static/fonts/cairo-regular.woff2',
            '/static/fonts/cairo-bold.woff2',
        ];
        
        criticalFonts.forEach(font => {
            this.preloadResource(font, 'font');
        });
    }
    
    optimizeFontDisplay() {
        const style = document.createElement('style');
        style.textContent = `
            @font-face {
                font-family: 'Cairo';
                font-display: swap;
            }
        `;
        document.head.appendChild(style);
    }
    
    /**
     * Resource Hints
     */
    initResourceHints() {
        // DNS prefetch for external domains
        this.addDNSPrefetch([
            '//fonts.googleapis.com',
            '//cdn.jsdelivr.net',
            '//cdnjs.cloudflare.com',
        ]);
        
        // Preconnect to critical origins
        this.addPreconnect([
            'https://fonts.gstatic.com',
        ]);
    }
    
    addDNSPrefetch(domains) {
        domains.forEach(domain => {
            const link = document.createElement('link');
            link.rel = 'dns-prefetch';
            link.href = domain;
            document.head.appendChild(link);
        });
    }
    
    addPreconnect(origins) {
        origins.forEach(origin => {
            const link = document.createElement('link');
            link.rel = 'preconnect';
            link.href = origin;
            link.crossOrigin = 'anonymous';
            document.head.appendChild(link);
        });
    }
    
    /**
     * Utility Functions
     */
    isElementInViewport(element, offset = 0) {
        const rect = element.getBoundingClientRect();
        return (
            rect.top >= -offset &&
            rect.left >= -offset &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) + offset &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth) + offset
        );
    }
    
    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
    
    debounce(func, wait, immediate) {
        let timeout;
        return function() {
            const context = this;
            const args = arguments;
            const later = function() {
                timeout = null;
                if (!immediate) func.apply(context, args);
            };
            const callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func.apply(context, args);
        };
    }
}

// Initialize Performance Optimizer
const performanceOptimizer = new PerformanceOptimizer();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PerformanceOptimizer;
} else if (typeof window !== 'undefined') {
    window.PerformanceOptimizer = PerformanceOptimizer;
}
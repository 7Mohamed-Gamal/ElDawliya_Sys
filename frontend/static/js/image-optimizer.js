/**
 * Image Optimization Utility
 * ==========================
 * 
 * Advanced image optimization including:
 * - WebP conversion and fallback
 * - Responsive image generation
 * - Lazy loading with intersection observer
 * - Image compression and resizing
 * - Progressive loading
 */

class ImageOptimizer {
    constructor(options = {}) {
        this.config = {
            webpSupport: null,
            lazyLoadOffset: 100,
            compressionQuality: 0.8,
            maxWidth: 1920,
            maxHeight: 1080,
            enableProgressiveLoading: true,
            enableResponsiveImages: true,
            enableWebPConversion: true,
            ...options
        };
        
        this.init();
    }
    
    init() {
        this.detectWebPSupport();
        this.initLazyLoading();
        this.optimizeExistingImages();
        this.setupImageUploadOptimization();
    }
    
    /**
     * WebP Support Detection
     */
    detectWebPSupport() {
        return new Promise((resolve) => {
            const webP = new Image();
            webP.onload = webP.onerror = () => {
                this.config.webpSupport = (webP.height === 2);
                resolve(this.config.webpSupport);
            };
            webP.src = 'data:image/webp;base64,UklGRjoAAABXRUJQVlA4IC4AAACyAgCdASoCAAIALmk0mk0iIiIiIgBoSygABc6WWgAA/veff/0PP8bA//LwYAAA';
        });
    }
    
    /**
     * Lazy Loading Implementation
     */
    initLazyLoading() {
        if ('IntersectionObserver' in window) {
            this.setupIntersectionObserver();
        } else {
            this.setupScrollBasedLazyLoading();
        }
    }
    
    setupIntersectionObserver() {
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
        this.observeLazyImages(imageObserver);
        
        // Set up mutation observer for dynamically added images
        this.setupMutationObserver(imageObserver);
    }
    
    observeLazyImages(observer) {
        document.querySelectorAll('img[data-src], img[data-srcset]').forEach(img => {
            observer.observe(img);
        });
    }
    
    setupMutationObserver(imageObserver) {
        const mutationObserver = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1) { // Element node
                        // Check if the node itself is a lazy image
                        if (node.tagName === 'IMG' && (node.dataset.src || node.dataset.srcset)) {
                            imageObserver.observe(node);
                        }
                        
                        // Check for lazy images within the added node
                        const lazyImages = node.querySelectorAll?.('img[data-src], img[data-srcset]');
                        lazyImages?.forEach(img => imageObserver.observe(img));
                    }
                });
            });
        });
        
        mutationObserver.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
    
    setupScrollBasedLazyLoading() {
        const lazyImages = document.querySelectorAll('img[data-src], img[data-srcset]');
        
        const loadImagesOnScroll = () => {
            lazyImages.forEach(img => {
                if (this.isElementInViewport(img, this.config.lazyLoadOffset)) {
                    this.loadImage(img);
                }
            });
        };
        
        window.addEventListener('scroll', this.throttle(loadImagesOnScroll, 100));
        window.addEventListener('resize', this.throttle(loadImagesOnScroll, 100));
        
        // Initial load
        loadImagesOnScroll();
    }
    
    /**
     * Image Loading with Optimization
     */
    async loadImage(img) {
        const src = img.dataset.src;
        const srcset = img.dataset.srcset;
        
        if (!src && !srcset) return;
        
        // Add loading class
        img.classList.add('loading');
        
        try {
            // Determine the best image source
            const optimizedSrc = await this.getOptimizedImageSrc(src, img);
            const optimizedSrcset = await this.getOptimizedSrcset(srcset, img);
            
            // Preload the image
            await this.preloadImage(optimizedSrc);
            
            // Apply the optimized sources
            if (optimizedSrc) {
                img.src = optimizedSrc;
            }
            
            if (optimizedSrcset) {
                img.srcset = optimizedSrcset;
            }
            
            // Add loaded class and remove loading class
            img.classList.add('loaded');
            img.classList.remove('loading');
            
            // Remove data attributes
            delete img.dataset.src;
            delete img.dataset.srcset;
            
        } catch (error) {
            console.error('Error loading image:', error);
            img.classList.add('error');
            img.classList.remove('loading');
        }
    }
    
    async getOptimizedImageSrc(src, img) {
        if (!src) return null;
        
        // Check for WebP support and convert if enabled
        if (this.config.enableWebPConversion && this.config.webpSupport) {
            const webpSrc = this.convertToWebP(src);
            if (await this.imageExists(webpSrc)) {
                return webpSrc;
            }
        }
        
        // Generate responsive image if needed
        if (this.config.enableResponsiveImages) {
            return this.getResponsiveImageSrc(src, img);
        }
        
        return src;
    }
    
    async getOptimizedSrcset(srcset, img) {
        if (!srcset) return null;
        
        const sources = srcset.split(',').map(s => s.trim());
        const optimizedSources = [];
        
        for (const source of sources) {
            const [url, descriptor] = source.split(' ');
            const optimizedUrl = await this.getOptimizedImageSrc(url, img);
            optimizedSources.push(`${optimizedUrl} ${descriptor || ''}`);
        }
        
        return optimizedSources.join(', ');
    }
    
    convertToWebP(src) {
        return src.replace(/\.(jpg|jpeg|png)(\?.*)?$/i, '.webp$2');
    }
    
    getResponsiveImageSrc(src, img) {
        const containerWidth = img.parentElement?.offsetWidth || window.innerWidth;
        const devicePixelRatio = window.devicePixelRatio || 1;
        const targetWidth = Math.min(containerWidth * devicePixelRatio, this.config.maxWidth);
        
        // Generate responsive image URL (this would typically be handled by your backend)
        const baseSrc = src.replace(/\.(jpg|jpeg|png|webp)(\?.*)?$/i, '');
        const extension = src.match(/\.(jpg|jpeg|png|webp)(\?.*)?$/i)?.[1] || 'jpg';
        const params = src.match(/\?(.*)$/)?.[1] || '';
        
        return `${baseSrc}_w${Math.round(targetWidth)}.${extension}${params ? '?' + params : ''}`;
    }
    
    preloadImage(src) {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = () => resolve(img);
            img.onerror = reject;
            img.src = src;
        });
    }
    
    async imageExists(src) {
        try {
            await this.preloadImage(src);
            return true;
        } catch {
            return false;
        }
    }
    
    /**
     * Optimize Existing Images
     */
    optimizeExistingImages() {
        document.querySelectorAll('img:not([data-src]):not([data-srcset])').forEach(img => {
            this.optimizeLoadedImage(img);
        });
    }
    
    optimizeLoadedImage(img) {
        // Add loading attribute for native lazy loading support
        if ('loading' in HTMLImageElement.prototype) {
            if (!this.isElementInViewport(img, 200)) {
                img.loading = 'lazy';
            }
        }
        
        // Add responsive attributes if missing
        if (this.config.enableResponsiveImages && !img.srcset) {
            this.addResponsiveAttributes(img);
        }
        
        // Optimize image dimensions
        this.optimizeImageDimensions(img);
    }
    
    addResponsiveAttributes(img) {
        const src = img.src;
        if (!src || src.startsWith('data:')) return;
        
        const baseSrc = src.replace(/\.(jpg|jpeg|png|webp)(\?.*)?$/i, '');
        const extension = src.match(/\.(jpg|jpeg|png|webp)(\?.*)?$/i)?.[1] || 'jpg';
        const params = src.match(/\?(.*)$/)?.[1] || '';
        
        // Generate srcset for different screen densities
        const srcset = [
            `${baseSrc}.${extension}${params ? '?' + params : ''} 1x`,
            `${baseSrc}@2x.${extension}${params ? '?' + params : ''} 2x`,
            `${baseSrc}@3x.${extension}${params ? '?' + params : ''} 3x`
        ].join(', ');
        
        img.srcset = srcset;
    }
    
    optimizeImageDimensions(img) {
        // Set explicit width and height to prevent layout shift
        if (!img.width && !img.height && img.complete) {
            const aspectRatio = img.naturalWidth / img.naturalHeight;
            const containerWidth = img.parentElement?.offsetWidth || 300;
            
            img.width = containerWidth;
            img.height = containerWidth / aspectRatio;
        }
    }
    
    /**
     * Image Upload Optimization
     */
    setupImageUploadOptimization() {
        document.addEventListener('change', (event) => {
            if (event.target.type === 'file' && event.target.accept?.includes('image')) {
                this.handleImageUpload(event.target);
            }
        });
    }
    
    async handleImageUpload(input) {
        const files = Array.from(input.files);
        const optimizedFiles = [];
        
        for (const file of files) {
            if (file.type.startsWith('image/')) {
                try {
                    const optimizedFile = await this.optimizeImageFile(file);
                    optimizedFiles.push(optimizedFile);
                } catch (error) {
                    console.error('Error optimizing image:', error);
                    optimizedFiles.push(file); // Use original file if optimization fails
                }
            } else {
                optimizedFiles.push(file);
            }
        }
        
        // Replace the files in the input
        const dataTransfer = new DataTransfer();
        optimizedFiles.forEach(file => dataTransfer.items.add(file));
        input.files = dataTransfer.files;
    }
    
    async optimizeImageFile(file) {
        return new Promise((resolve, reject) => {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            const img = new Image();
            
            img.onload = () => {
                // Calculate optimized dimensions
                const { width, height } = this.calculateOptimizedDimensions(
                    img.width, 
                    img.height
                );
                
                canvas.width = width;
                canvas.height = height;
                
                // Draw and compress the image
                ctx.drawImage(img, 0, 0, width, height);
                
                canvas.toBlob((blob) => {
                    if (blob) {
                        const optimizedFile = new File([blob], file.name, {
                            type: 'image/jpeg',
                            lastModified: Date.now()
                        });
                        resolve(optimizedFile);
                    } else {
                        reject(new Error('Failed to optimize image'));
                    }
                }, 'image/jpeg', this.config.compressionQuality);
            };
            
            img.onerror = reject;
            img.src = URL.createObjectURL(file);
        });
    }
    
    calculateOptimizedDimensions(originalWidth, originalHeight) {
        const maxWidth = this.config.maxWidth;
        const maxHeight = this.config.maxHeight;
        
        let width = originalWidth;
        let height = originalHeight;
        
        // Scale down if too large
        if (width > maxWidth) {
            height = (height * maxWidth) / width;
            width = maxWidth;
        }
        
        if (height > maxHeight) {
            width = (width * maxHeight) / height;
            height = maxHeight;
        }
        
        return { width: Math.round(width), height: Math.round(height) };
    }
    
    /**
     * Progressive Image Loading
     */
    createProgressiveImage(src, placeholder) {
        const container = document.createElement('div');
        container.className = 'progressive-image-container';
        container.style.cssText = `
            position: relative;
            overflow: hidden;
            background-color: #f0f0f0;
        `;
        
        // Create placeholder (low-quality or blurred version)
        const placeholderImg = document.createElement('img');
        placeholderImg.src = placeholder;
        placeholderImg.className = 'progressive-image-placeholder';
        placeholderImg.style.cssText = `
            width: 100%;
            height: 100%;
            object-fit: cover;
            filter: blur(5px);
            transition: opacity 0.3s ease;
        `;
        
        // Create main image
        const mainImg = document.createElement('img');
        mainImg.className = 'progressive-image-main';
        mainImg.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;
        
        mainImg.onload = () => {
            mainImg.style.opacity = '1';
            placeholderImg.style.opacity = '0';
        };
        
        mainImg.src = src;
        
        container.appendChild(placeholderImg);
        container.appendChild(mainImg);
        
        return container;
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
    
    /**
     * Performance Monitoring
     */
    measureImagePerformance() {
        if ('PerformanceObserver' in window) {
            const observer = new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    if (entry.initiatorType === 'img') {
                        console.log(`Image loaded: ${entry.name} in ${entry.duration}ms`);
                        
                        // Send metrics to analytics
                        this.sendImageMetrics({
                            url: entry.name,
                            loadTime: entry.duration,
                            size: entry.transferSize,
                            timestamp: Date.now()
                        });
                    }
                }
            });
            
            observer.observe({ entryTypes: ['resource'] });
        }
    }
    
    sendImageMetrics(metrics) {
        // Send to analytics service
        if (navigator.sendBeacon) {
            navigator.sendBeacon('/api/image-metrics/', JSON.stringify(metrics));
        }
    }
}

// Initialize Image Optimizer
const imageOptimizer = new ImageOptimizer();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ImageOptimizer;
} else if (typeof window !== 'undefined') {
    window.ImageOptimizer = ImageOptimizer;
}
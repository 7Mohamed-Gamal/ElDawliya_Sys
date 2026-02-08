/**
 * ElDawliya ERP System - Advanced JavaScript Framework
 * Version: 3.0.0
 * Features: AJAX, UI Components, Validation, Charts, Utils
 */

(function() {
    'use strict';

    // ============================================
    // GLOBAL CONFIGURATION
    // ============================================
    
    window.ElDawliya = {
        version: '3.0.0',
        config: {
            apiBaseUrl: '/api/v1/',
            csrfToken: null,
            theme: 'light',
            language: 'ar',
            dateFormat: 'DD/MM/YYYY',
            timeFormat: 'HH:mm',
            currency: 'SAR'
        },
        
        // Initialize Application
        init: function() {
            this.initCSRF();
            this.initTheme();
            this.initComponents();
            this.initEventListeners();
            this.hideLoading();
            console.log('ElDawliya ERP v' + this.version + ' initialized successfully');
        },
        
        // Initialize CSRF Token
        initCSRF: function() {
            const tokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
            if (tokenElement) {
                this.config.csrfToken = tokenElement.value;
            }
            
            // Setup jQuery AJAX if available
            if (typeof $ !== 'undefined') {
                $.ajaxSetup({
                    beforeSend: function(xhr) {
                        if (!this.crossDomain && ElDawliya.config.csrfToken) {
                            xhr.setRequestHeader('X-CSRFToken', ElDawliya.config.csrfToken);
                        }
                    }
                });
            }
        },
        
        // Initialize Theme
        initTheme: function() {
            const savedTheme = localStorage.getItem('eldawliya-theme') || 'light';
            this.setTheme(savedTheme);
        },
        
        // Set Theme
        setTheme: function(theme) {
            this.config.theme = theme;
            document.documentElement.setAttribute('data-theme', theme);
            localStorage.setItem('eldawliya-theme', theme);
            
            const icon = document.getElementById('themeIcon');
            if (icon) {
                icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
            }
        },
        
        // Toggle Theme
        toggleTheme: function() {
            const newTheme = this.config.theme === 'light' ? 'dark' : 'light';
            this.setTheme(newTheme);
        },
        
        // Initialize Components
        initComponents: function() {
            this.initTooltips();
            this.initDropdowns();
            this.initModals();
            this.initTables();
            this.initForms();
            this.initCharts();
        },
        
        // Initialize Event Listeners
        initEventListeners: function() {
            // Auto-hide alerts
            setTimeout(() => {
                document.querySelectorAll('.alert:not(.alert-permanent)').forEach(alert => {
                    this.fadeOut(alert, 300);
                });
            }, 5000);
            
            // Handle AJAX links
            document.querySelectorAll('a[data-ajax="true"]').forEach(link => {
                link.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.loadAjaxContent(link.href, link.dataset.target);
                });
            });
            
            // Handle print buttons
            document.querySelectorAll('[data-print]').forEach(btn => {
                btn.addEventListener('click', () => window.print());
            });
            
            // Handle confirm actions
            document.querySelectorAll('[data-confirm]').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    if (!confirm(btn.dataset.confirm)) {
                        e.preventDefault();
                    }
                });
            });
        }
    };

    // ============================================
    // UI COMPONENTS
    // ============================================
    
    ElDawliya.UI = {
        // Show Loading Overlay
        showLoading: function(message = 'جاري التحميل...') {
            const overlay = document.getElementById('loadingOverlay');
            if (overlay) {
                overlay.classList.add('show');
                const text = overlay.querySelector('.loading-text');
                if (text) text.textContent = message;
            }
        },
        
        // Hide Loading Overlay
        hideLoading: function() {
            const overlay = document.getElementById('loadingOverlay');
            if (overlay) {
                overlay.classList.remove('show');
            }
        },
        
        // Show Toast Notification
        toast: function(message, type = 'info', duration = 5000) {
            const container = document.getElementById('toastContainer') || this.createToastContainer();
            
            const toast = document.createElement('div');
            toast.className = `toast toast-${type}`;
            toast.innerHTML = `
                <i class="fas fa-${this.getToastIcon(type)}"></i>
                <span>${message}</span>
                <button class="toast-close" onclick="this.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            `;
            
            container.appendChild(toast);
            
            // Auto remove
            setTimeout(() => {
                this.fadeOut(toast, 300, () => toast.remove());
            }, duration);
        },
        
        // Create Toast Container
        createToastContainer: function() {
            const container = document.createElement('div');
            container.id = 'toastContainer';
            container.className = 'toast-container';
            document.body.appendChild(container);
            return container;
        },
        
        // Get Toast Icon
        getToastIcon: function(type) {
            const icons = {
                success: 'check-circle',
                error: 'exclamation-circle',
                warning: 'exclamation-triangle',
                info: 'info-circle'
            };
            return icons[type] || icons.info;
        },
        
        // Show Modal
        showModal: function(id, options = {}) {
            const modal = document.getElementById(id);
            if (modal) {
                modal.classList.add('show');
                document.body.style.overflow = 'hidden';
                
                if (options.onShow) options.onShow(modal);
                
                // Handle backdrop click
                modal.addEventListener('click', (e) => {
                    if (e.target === modal && options.backdrop !== false) {
                        this.hideModal(id);
                    }
                });
            }
        },
        
        // Hide Modal
        hideModal: function(id) {
            const modal = document.getElementById(id);
            if (modal) {
                modal.classList.remove('show');
                document.body.style.overflow = '';
            }
        },
        
        // Fade Out Element
        fadeOut: function(element, duration = 300, callback) {
            element.style.transition = `opacity ${duration}ms`;
            element.style.opacity = '0';
            setTimeout(() => {
                if (callback) callback();
                else element.style.display = 'none';
            }, duration);
        },
        
        // Fade In Element
        fadeIn: function(element, duration = 300) {
            element.style.display = '';
            element.style.opacity = '0';
            element.style.transition = `opacity ${duration}ms`;
            setTimeout(() => element.style.opacity = '1', 10);
        },
        
        // Slide Toggle
        slideToggle: function(element, duration = 300) {
            if (window.getComputedStyle(element).display === 'none') {
                this.slideDown(element, duration);
            } else {
                this.slideUp(element, duration);
            }
        },
        
        // Slide Up
        slideUp: function(element, duration = 300) {
            element.style.transition = `height ${duration}ms, opacity ${duration}ms`;
            element.style.height = element.scrollHeight + 'px';
            element.style.opacity = '1';
            
            setTimeout(() => {
                element.style.height = '0';
                element.style.opacity = '0';
            }, 10);
            
            setTimeout(() => {
                element.style.display = 'none';
                element.style.height = '';
            }, duration);
        },
        
        // Slide Down
        slideDown: function(element, duration = 300) {
            element.style.display = '';
            element.style.height = '0';
            element.style.opacity = '0';
            element.style.transition = `height ${duration}ms, opacity ${duration}ms`;
            
            setTimeout(() => {
                element.style.height = element.scrollHeight + 'px';
                element.style.opacity = '1';
            }, 10);
            
            setTimeout(() => {
                element.style.height = '';
            }, duration);
        }
    };

    // ============================================
    // AJAX & API
    // ============================================
    
    ElDawliya.API = {
        // Make AJAX Request
        request: function(options) {
            const defaults = {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'application/json'
                }
            };
            
            const config = { ...defaults, ...options };
            
            // Add CSRF token for non-GET requests
            if (config.method !== 'GET' && ElDawliya.config.csrfToken) {
                config.headers['X-CSRFToken'] = ElDawliya.config.csrfToken;
            }
            
            // Show loading
            if (config.loading !== false) {
                ElDawliya.UI.showLoading(config.loadingMessage);
            }
            
            return fetch(config.url, config)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(response.statusText);
                    }
                    return response.json();
                })
                .finally(() => {
                    if (config.loading !== false) {
                        ElDawliya.UI.hideLoading();
                    }
                });
        },
        
        // GET Request
        get: function(url, options = {}) {
            return this.request({ ...options, url, method: 'GET' });
        },
        
        // POST Request
        post: function(url, data, options = {}) {
            return this.request({
                ...options,
                url,
                method: 'POST',
                headers: {
                    ...options.headers,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
        },
        
        // PUT Request
        put: function(url, data, options = {}) {
            return this.request({
                ...options,
                url,
                method: 'PUT',
                headers: {
                    ...options.headers,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
        },
        
        // DELETE Request
        delete: function(url, options = {}) {
            return this.request({ ...options, url, method: 'DELETE' });
        },
        
        // Load Content via AJAX
        loadContent: function(url, target, options = {}) {
            ElDawliya.UI.showLoading();
            
            return fetch(url, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => response.text())
            .then(html => {
                const element = document.querySelector(target);
                if (element) {
                    element.innerHTML = html;
                    ElDawliya.initComponents();
                }
                if (options.onSuccess) options.onSuccess(html);
            })
            .catch(error => {
                console.error('AJAX Error:', error);
                if (options.onError) options.onError(error);
            })
            .finally(() => {
                ElDawliya.UI.hideLoading();
            });
        }
    };

    // ============================================
    // FORM VALIDATION
    // ============================================
    
    ElDawliya.Validation = {
        // Validate Form
        validate: function(form) {
            const errors = [];
            const fields = form.querySelectorAll('[data-validate]');
            
            fields.forEach(field => {
                const rules = field.dataset.validate.split('|');
                const value = field.value.trim();
                
                rules.forEach(rule => {
                    const [ruleName, ruleValue] = rule.split(':');
                    
                    if (!this.checkRule(ruleName, value, ruleValue)) {
                        errors.push({
                            field: field,
                            message: this.getErrorMessage(ruleName, field, ruleValue)
                        });
                        field.classList.add('is-invalid');
                    } else {
                        field.classList.remove('is-invalid');
                        field.classList.add('is-valid');
                    }
                });
            });
            
            return {
                valid: errors.length === 0,
                errors: errors
            };
        },
        
        // Check Validation Rule
        checkRule: function(rule, value, param) {
            switch(rule) {
                case 'required':
                    return value.length > 0;
                case 'email':
                    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
                case 'min':
                    return value.length >= parseInt(param);
                case 'max':
                    return value.length <= parseInt(param);
                case 'numeric':
                    return !isNaN(value);
                case 'phone':
                    return /^[0-9]{10,15}$/.test(value.replace(/\s/g, ''));
                case 'date':
                    return !isNaN(Date.parse(value));
                default:
                    return true;
            }
        },
        
        // Get Error Message
        getErrorMessage: function(rule, field, param) {
            const messages = {
                required: `حقل ${field.placeholder || field.name} مطلوب`,
                email: 'البريد الإلكتروني غير صحيح',
                min: `الحد الأدنى ${param} أحرف`,
                max: `الحد الأقصى ${param} أحرف`,
                numeric: 'يجب أن يكون رقماً',
                phone: 'رقم الهاتف غير صحيح',
                date: 'التاريخ غير صحيح'
            };
            return messages[rule] || 'قيمة غير صحيحة';
        },
        
        // Clear Validation
        clear: function(form) {
            form.querySelectorAll('.is-invalid, .is-valid').forEach(field => {
                field.classList.remove('is-invalid', 'is-valid');
            });
            form.querySelectorAll('.invalid-feedback').forEach(el => el.remove());
        }
    };

    // ============================================
    // UTILITY FUNCTIONS
    // ============================================
    
    ElDawliya.Utils = {
        // Debounce Function
        debounce: function(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        },
        
        // Throttle Function
        throttle: function(func, limit) {
            let inThrottle;
            return function(...args) {
                if (!inThrottle) {
                    func.apply(this, args);
                    inThrottle = true;
                    setTimeout(() => inThrottle = false, limit);
                }
            };
        },
        
        // Format Date
        formatDate: function(date, format = 'DD/MM/YYYY') {
            const d = new Date(date);
            const day = String(d.getDate()).padStart(2, '0');
            const month = String(d.getMonth() + 1).padStart(2, '0');
            const year = d.getFullYear();
            
            return format
                .replace('DD', day)
                .replace('MM', month)
                .replace('YYYY', year);
        },
        
        // Format Number
        formatNumber: function(num, decimals = 0) {
            return Number(num).toLocaleString('ar-SA', {
                minimumFractionDigits: decimals,
                maximumFractionDigits: decimals
            });
        },
        
        // Format Currency
        formatCurrency: function(amount, currency = 'SAR') {
            return new Intl.NumberFormat('ar-SA', {
                style: 'currency',
                currency: currency
            }).format(amount);
        },
        
        // Format Time Ago
        timeAgo: function(date) {
            const seconds = Math.floor((new Date() - new Date(date)) / 1000);
            
            const intervals = {
                year: 31536000,
                month: 2592000,
                week: 604800,
                day: 86400,
                hour: 3600,
                minute: 60
            };
            
            for (const [unit, secondsInUnit] of Object.entries(intervals)) {
                const interval = Math.floor(seconds / secondsInUnit);
                if (interval >= 1) {
                    return `منذ ${interval} ${this.getArabicUnit(unit, interval)}`;
                }
            }
            
            return 'الآن';
        },
        
        // Get Arabic Time Unit
        getArabicUnit: function(unit, count) {
            const units = {
                year: count === 1 ? 'سنة' : 'سنوات',
                month: count === 1 ? 'شهر' : 'أشهر',
                week: count === 1 ? 'أسبوع' : 'أسابيع',
                day: count === 1 ? 'يوم' : 'أيام',
                hour: count === 1 ? 'ساعة' : 'ساعات',
                minute: count === 1 ? 'دقيقة' : 'دقائق'
            };
            return units[unit] || unit;
        },
        
        // Copy to Clipboard
        copyToClipboard: function(text) {
            if (navigator.clipboard) {
                navigator.clipboard.writeText(text).then(() => {
                    ElDawliya.UI.toast('تم النسخ بنجاح', 'success');
                });
            } else {
                const input = document.createElement('input');
                input.value = text;
                document.body.appendChild(input);
                input.select();
                document.execCommand('copy');
                document.body.removeChild(input);
                ElDawliya.UI.toast('تم النسخ بنجاح', 'success');
            }
        },
        
        // Generate Random ID
        generateId: function(prefix = 'id') {
            return `${prefix}_${Math.random().toString(36).substr(2, 9)}`;
        },
        
        // Deep Clone
        deepClone: function(obj) {
            return JSON.parse(JSON.stringify(obj));
        },
        
        // Serialize Form
        serializeForm: function(form) {
            const formData = new FormData(form);
            const data = {};
            
            for (const [key, value] of formData.entries()) {
                if (data[key]) {
                    if (!Array.isArray(data[key])) {
                        data[key] = [data[key]];
                    }
                    data[key].push(value);
                } else {
                    data[key] = value;
                }
            }
            
            return data;
        }
    };

    // ============================================
    // COMPONENT INITIALIZERS
    // ============================================
    
    ElDawliya.initTooltips = function() {
        document.querySelectorAll('[data-tooltip]').forEach(el => {
            el.classList.add('tooltip');
        });
    };
    
    ElDawliya.initDropdowns = function() {
        document.querySelectorAll('[data-toggle="dropdown"]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const dropdown = btn.closest('.dropdown');
                dropdown.classList.toggle('show');
                
                // Close others
                document.querySelectorAll('.dropdown.show').forEach(d => {
                    if (d !== dropdown) d.classList.remove('show');
                });
            });
        });
        
        // Close on outside click
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.dropdown')) {
                document.querySelectorAll('.dropdown.show').forEach(d => {
                    d.classList.remove('show');
                });
            }
        });
    };
    
    ElDawliya.initModals = function() {
        // Open modal
        document.querySelectorAll('[data-toggle="modal"]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const target = btn.dataset.target;
                ElDawliya.UI.showModal(target);
            });
        });
        
        // Close modal
        document.querySelectorAll('[data-dismiss="modal"]').forEach(btn => {
            btn.addEventListener('click', () => {
                const modal = btn.closest('.modal');
                if (modal) ElDawliya.UI.hideModal(modal.id);
            });
        });
    };
    
    ElDawliya.initTables = function() {
        // Initialize DataTables if available
        if (typeof $.fn.DataTable !== 'undefined') {
            $('.datatable').DataTable({
                responsive: true,
                language: {
                    url: '//cdn.datatables.net/plug-ins/1.13.7/i18n/ar.json'
                },
                pageLength: 25,
                order: [[0, 'desc']]
            });
        }
        
        // Select all checkbox
        document.querySelectorAll('[data-select-all]').forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                const target = checkbox.dataset.selectAll;
                document.querySelectorAll(target).forEach(cb => {
                    cb.checked = checkbox.checked;
                });
            });
        });
    };
    
    ElDawliya.initForms = function() {
        // Auto-validation
        document.querySelectorAll('form[data-validate]').forEach(form => {
            form.addEventListener('submit', (e) => {
                const result = ElDawliya.Validation.validate(form);
                if (!result.valid) {
                    e.preventDefault();
                    result.errors.forEach(error => {
                        ElDawliya.UI.toast(error.message, 'error');
                    });
                }
            });
        });
        
        // Character counter
        document.querySelectorAll('[data-maxlength]').forEach(field => {
            const max = field.dataset.maxlength;
            const counter = document.createElement('small');
            counter.className = 'text-muted d-block mt-1';
            field.parentNode.appendChild(counter);
            
            field.addEventListener('input', () => {
                const remaining = max - field.value.length;
                counter.textContent = `${remaining} حرف متبقي`;
                counter.classList.toggle('text-danger', remaining < 0);
            });
        });
        
        // Auto-save draft
        document.querySelectorAll('form[data-autosave]').forEach(form => {
            const key = form.dataset.autosave;
            
            // Restore draft
            const draft = localStorage.getItem(key);
            if (draft) {
                const data = JSON.parse(draft);
                Object.entries(data).forEach(([name, value]) => {
                    const field = form.querySelector(`[name="${name}"]`);
                    if (field) field.value = value;
                });
            }
            
            // Save draft
            form.addEventListener('input', ElDawliya.Utils.debounce(() => {
                const data = ElDawliya.Utils.serializeForm(form);
                localStorage.setItem(key, JSON.stringify(data));
            }, 1000));
            
            // Clear draft on submit
            form.addEventListener('submit', () => {
                localStorage.removeItem(key);
            });
        });
    };
    
    ElDawliya.initCharts = function() {
        // Initialize Chart.js defaults if available
        if (typeof Chart !== 'undefined') {
            Chart.defaults.font.family = 'Cairo';
            Chart.defaults.color = '#64748b';
            Chart.defaults.scale.grid.color = '#e2e8f0';
            
            // RTL support
            Chart.defaults.plugins.legend.rtl = true;
            Chart.defaults.plugins.tooltip.rtl = true;
        }
    };

    // ============================================
    // INITIALIZE ON DOM READY
    // ============================================
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => ElDawliya.init());
    } else {
        ElDawliya.init();
    }

})();

// ============================================
// GLOBAL HELPER FUNCTIONS
// ============================================

// Quick toast
function toast(message, type = 'info') {
    ElDawliya.UI.toast(message, type);
}

// Quick confirm
toast.confirm = function(message, callback) {
    if (confirm(message)) {
        callback();
    }
};

// Format helpers
function formatDate(date) {
    return ElDawliya.Utils.formatDate(date);
}

function formatNumber(num, decimals) {
    return ElDawliya.Utils.formatNumber(num, decimals);
}

function formatCurrency(amount) {
    return ElDawliya.Utils.formatCurrency(amount);
}

function timeAgo(date) {
    return ElDawliya.Utils.timeAgo(date);
}

// AJAX helpers
function ajaxGet(url, options) {
    return ElDawliya.API.get(url, options);
}

function ajaxPost(url, data, options) {
    return ElDawliya.API.post(url, data, options);
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ElDawliya;
}
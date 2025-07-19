/**
 * HR Components JavaScript
 * مكونات نظام الموارد البشرية التفاعلية
 */

// ========== Global Variables - المتغيرات العامة ==========
const HRSystem = {
    config: {
        apiBaseUrl: '/hr/api/',
        csrfToken: document.querySelector('[name=csrfmiddlewaretoken]')?.value || '',
        language: 'ar',
        dateFormat: 'YYYY-MM-DD',
        timeFormat: 'HH:mm:ss'
    },
    
    // Cache for storing data
    cache: new Map(),
    
    // Event listeners registry
    listeners: new Map(),
    
    // Current user data
    user: null,
    
    // Theme settings
    theme: localStorage.getItem('hr-theme') || 'light'
};

// ========== Utility Functions - الدوال المساعدة ==========

/**
 * Make API request with proper headers
 * إجراء طلب API مع الرؤوس المناسبة
 */
HRSystem.api = {
    async request(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': HRSystem.config.csrfToken,
                'Accept': 'application/json'
            }
        };
        
        const mergedOptions = {
            ...defaultOptions,
            ...options,
            headers: { ...defaultOptions.headers, ...options.headers }
        };
        
        try {
            const response = await fetch(HRSystem.config.apiBaseUrl + url, mergedOptions);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            }
            
            return await response.text();
        } catch (error) {
            console.error('API Request Error:', error);
            throw error;
        }
    },
    
    async get(url) {
        return this.request(url, { method: 'GET' });
    },
    
    async post(url, data) {
        return this.request(url, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    
    async put(url, data) {
        return this.request(url, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },
    
    async delete(url) {
        return this.request(url, { method: 'DELETE' });
    }
};

/**
 * Utility functions
 * الدوال المساعدة
 */
HRSystem.utils = {
    // Format date according to locale
    formatDate(date, format = HRSystem.config.dateFormat) {
        if (!date) return '';
        const d = new Date(date);
        return d.toLocaleDateString('ar-SA');
    },
    
    // Format time
    formatTime(time, format = HRSystem.config.timeFormat) {
        if (!time) return '';
        const t = new Date(`2000-01-01T${time}`);
        return t.toLocaleTimeString('ar-SA', { hour12: false });
    },
    
    // Format currency
    formatCurrency(amount, currency = 'SAR') {
        if (amount === null || amount === undefined) return '';
        return new Intl.NumberFormat('ar-SA', {
            style: 'currency',
            currency: currency
        }).format(amount);
    },
    
    // Format number
    formatNumber(number) {
        if (number === null || number === undefined) return '';
        return new Intl.NumberFormat('ar-SA').format(number);
    },
    
    // Debounce function
    debounce(func, wait) {
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
    
    // Generate UUID
    generateUUID() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    },
    
    // Show notification
    showNotification(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} hr-notification`;
        notification.innerHTML = `
            <div class="d-flex align-items-center">
                <span class="flex-grow-1">${message}</span>
                <button type="button" class="btn-close" onclick="this.parentElement.parentElement.remove()"></button>
            </div>
        `;
        
        // Add to notification container or create one
        let container = document.getElementById('notification-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-container';
            container.className = 'position-fixed top-0 end-0 p-3';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
        }
        
        container.appendChild(notification);
        
        // Auto remove after duration
        if (duration > 0) {
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.remove();
                }
            }, duration);
        }
    },
    
    // Show loading spinner
    showLoading(element) {
        const spinner = document.createElement('div');
        spinner.className = 'hr-loading';
        spinner.innerHTML = '<div class="hr-spinner"></div>';
        element.appendChild(spinner);
        return spinner;
    },
    
    // Hide loading spinner
    hideLoading(spinner) {
        if (spinner && spinner.parentElement) {
            spinner.remove();
        }
    }
};

// ========== Navigation Components - مكونات التنقل ==========

/**
 * Sidebar Navigation
 * التنقل الجانبي
 */
HRSystem.sidebar = {
    init() {
        this.bindEvents();
        this.loadState();
    },
    
    bindEvents() {
        // Toggle sidebar
        document.addEventListener('click', (e) => {
            if (e.target.matches('.hr-sidebar-toggle')) {
                this.toggle();
            }
        });
        
        // Handle nav item clicks
        document.addEventListener('click', (e) => {
            if (e.target.matches('.hr-nav-link')) {
                this.handleNavClick(e);
            }
        });
        
        // Handle submenu toggles
        document.addEventListener('click', (e) => {
            if (e.target.matches('.hr-nav-arrow') || e.target.closest('.hr-nav-arrow')) {
                e.preventDefault();
                this.toggleSubmenu(e.target.closest('.hr-nav-item'));
            }
        });
    },
    
    toggle() {
        const sidebar = document.querySelector('.hr-sidebar');
        if (sidebar) {
            sidebar.classList.toggle('collapsed');
            this.saveState();
        }
    },
    
    handleNavClick(e) {
        // Remove active class from all nav links
        document.querySelectorAll('.hr-nav-link').forEach(link => {
            link.classList.remove('active');
        });
        
        // Add active class to clicked link
        e.target.classList.add('active');
        
        // Update breadcrumb
        this.updateBreadcrumb(e.target);
    },
    
    toggleSubmenu(navItem) {
        navItem.classList.toggle('expanded');
    },
    
    updateBreadcrumb(activeLink) {
        const breadcrumb = document.querySelector('.hr-breadcrumb');
        if (!breadcrumb) return;
        
        const linkText = activeLink.querySelector('.hr-nav-text')?.textContent || '';
        const parentSection = activeLink.closest('.hr-nav-section')?.querySelector('.hr-nav-section-title')?.textContent || '';
        
        breadcrumb.innerHTML = `
            <div class="hr-breadcrumb-item">
                <span>الرئيسية</span>
            </div>
            ${parentSection ? `
                <div class="hr-breadcrumb-item">
                    <span class="hr-breadcrumb-separator">/</span>
                    <span>${parentSection}</span>
                </div>
            ` : ''}
            <div class="hr-breadcrumb-item">
                <span class="hr-breadcrumb-separator">/</span>
                <span>${linkText}</span>
            </div>
        `;
    },
    
    saveState() {
        const sidebar = document.querySelector('.hr-sidebar');
        if (sidebar) {
            localStorage.setItem('hr-sidebar-collapsed', sidebar.classList.contains('collapsed'));
        }
    },
    
    loadState() {
        const isCollapsed = localStorage.getItem('hr-sidebar-collapsed') === 'true';
        const sidebar = document.querySelector('.hr-sidebar');
        if (sidebar && isCollapsed) {
            sidebar.classList.add('collapsed');
        }
    }
};

// ========== Search Component - مكون البحث ==========

HRSystem.search = {
    init() {
        this.bindEvents();
    },
    
    bindEvents() {
        const searchInput = document.querySelector('.hr-search-input');
        if (searchInput) {
            searchInput.addEventListener('input', HRSystem.utils.debounce((e) => {
                this.performSearch(e.target.value);
            }, 300));
        }
    },
    
    async performSearch(query) {
        if (query.length < 2) return;
        
        try {
            const results = await HRSystem.api.get(`search/?q=${encodeURIComponent(query)}`);
            this.displayResults(results);
        } catch (error) {
            console.error('Search error:', error);
        }
    },
    
    displayResults(results) {
        // Implementation for displaying search results
        console.log('Search results:', results);
    }
};

// ========== Data Table Component - مكون جدول البيانات ==========

HRSystem.dataTable = {
    init(tableId, options = {}) {
        const table = document.getElementById(tableId);
        if (!table) return;
        
        const config = {
            apiUrl: '',
            columns: [],
            pageSize: 10,
            sortable: true,
            filterable: true,
            searchable: true,
            ...options
        };
        
        this.setupTable(table, config);
    },
    
    setupTable(table, config) {
        // Add table wrapper classes
        table.classList.add('hr-table');
        
        // Setup pagination
        if (config.pageSize) {
            this.setupPagination(table, config);
        }
        
        // Setup sorting
        if (config.sortable) {
            this.setupSorting(table, config);
        }
        
        // Setup filtering
        if (config.filterable) {
            this.setupFiltering(table, config);
        }
        
        // Load initial data
        if (config.apiUrl) {
            this.loadData(table, config);
        }
    },
    
    async loadData(table, config, params = {}) {
        const loading = HRSystem.utils.showLoading(table.parentElement);
        
        try {
            const queryString = new URLSearchParams(params).toString();
            const url = config.apiUrl + (queryString ? `?${queryString}` : '');
            const data = await HRSystem.api.get(url);
            
            this.renderData(table, data, config);
        } catch (error) {
            console.error('Error loading table data:', error);
            HRSystem.utils.showNotification('حدث خطأ في تحميل البيانات', 'danger');
        } finally {
            HRSystem.utils.hideLoading(loading);
        }
    },
    
    renderData(table, data, config) {
        const tbody = table.querySelector('tbody');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        if (data.results && data.results.length > 0) {
            data.results.forEach(row => {
                const tr = document.createElement('tr');
                
                config.columns.forEach(column => {
                    const td = document.createElement('td');
                    
                    if (column.render) {
                        td.innerHTML = column.render(row[column.field], row);
                    } else {
                        td.textContent = row[column.field] || '';
                    }
                    
                    tr.appendChild(td);
                });
                
                tbody.appendChild(tr);
            });
        } else {
            const tr = document.createElement('tr');
            const td = document.createElement('td');
            td.colSpan = config.columns.length;
            td.textContent = 'لا توجد بيانات';
            td.className = 'text-center text-muted';
            tr.appendChild(td);
            tbody.appendChild(tr);
        }
        
        // Update pagination
        this.updatePagination(table, data, config);
    },
    
    setupPagination(table, config) {
        // Implementation for pagination setup
    },
    
    setupSorting(table, config) {
        // Implementation for sorting setup
    },
    
    setupFiltering(table, config) {
        // Implementation for filtering setup
    },
    
    updatePagination(table, data, config) {
        // Implementation for pagination update
    }
};

// ========== Form Components - مكونات النماذج ==========

HRSystem.forms = {
    init() {
        this.bindEvents();
        this.setupValidation();
    },
    
    bindEvents() {
        // Handle form submissions
        document.addEventListener('submit', (e) => {
            if (e.target.matches('.hr-form')) {
                this.handleSubmit(e);
            }
        });
        
        // Handle file uploads
        document.addEventListener('change', (e) => {
            if (e.target.matches('.hr-file-upload-input')) {
                this.handleFileUpload(e);
            }
        });
        
        // Handle drag and drop
        document.addEventListener('dragover', (e) => {
            if (e.target.closest('.hr-file-upload')) {
                e.preventDefault();
                e.target.closest('.hr-file-upload').classList.add('dragover');
            }
        });
        
        document.addEventListener('dragleave', (e) => {
            if (e.target.closest('.hr-file-upload')) {
                e.target.closest('.hr-file-upload').classList.remove('dragover');
            }
        });
        
        document.addEventListener('drop', (e) => {
            const uploadArea = e.target.closest('.hr-file-upload');
            if (uploadArea) {
                e.preventDefault();
                uploadArea.classList.remove('dragover');
                
                const files = e.dataTransfer.files;
                const input = uploadArea.querySelector('.hr-file-upload-input');
                if (input && files.length > 0) {
                    input.files = files;
                    this.handleFileUpload({ target: input });
                }
            }
        });
    },
    
    async handleSubmit(e) {
        e.preventDefault();
        
        const form = e.target;
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        
        // Show loading state
        const submitBtn = form.querySelector('[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<div class="hr-spinner" style="width: 16px; height: 16px;"></div> جاري الحفظ...';
        
        try {
            const method = form.method.toUpperCase();
            const url = form.action.replace(window.location.origin, '').replace('/hr/', '');
            
            let response;
            if (method === 'POST') {
                response = await HRSystem.api.post(url, data);
            } else if (method === 'PUT') {
                response = await HRSystem.api.put(url, data);
            }
            
            HRSystem.utils.showNotification('تم الحفظ بنجاح', 'success');
            
            // Redirect if specified
            const redirectUrl = form.dataset.redirect;
            if (redirectUrl) {
                window.location.href = redirectUrl;
            }
            
        } catch (error) {
            console.error('Form submission error:', error);
            HRSystem.utils.showNotification('حدث خطأ في الحفظ', 'danger');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    },
    
    handleFileUpload(e) {
        const input = e.target;
        const files = input.files;
        
        if (files.length > 0) {
            const uploadArea = input.closest('.hr-file-upload');
            const textElement = uploadArea.querySelector('.hr-file-upload-text');
            
            if (files.length === 1) {
                textElement.textContent = `تم اختيار: ${files[0].name}`;
            } else {
                textElement.textContent = `تم اختيار ${files.length} ملفات`;
            }
        }
    },
    
    setupValidation() {
        // Add real-time validation
        document.addEventListener('blur', (e) => {
            if (e.target.matches('.hr-form-control[required]')) {
                this.validateField(e.target);
            }
        });
    },
    
    validateField(field) {
        const isValid = field.checkValidity();
        
        field.classList.remove('is-valid', 'is-invalid');
        
        if (isValid) {
            field.classList.add('is-valid');
        } else {
            field.classList.add('is-invalid');
        }
        
        return isValid;
    }
};

// ========== Modal Components - مكونات النوافذ المنبثقة ==========

HRSystem.modal = {
    show(modalId, options = {}) {
        const modal = document.getElementById(modalId);
        if (!modal) return;
        
        const backdrop = modal.querySelector('.hr-modal-backdrop') || this.createBackdrop(modal);
        
        // Show backdrop and modal
        backdrop.classList.add('show');
        modal.classList.add('show');
        
        // Bind close events
        this.bindCloseEvents(modal);
        
        // Focus management
        modal.focus();
        
        // Callback
        if (options.onShow) {
            options.onShow(modal);
        }
    },
    
    hide(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) return;
        
        const backdrop = modal.querySelector('.hr-modal-backdrop');
        
        // Hide modal and backdrop
        modal.classList.remove('show');
        if (backdrop) {
            backdrop.classList.remove('show');
        }
        
        // Remove after animation
        setTimeout(() => {
            if (backdrop && backdrop.parentElement) {
                backdrop.remove();
            }
        }, 300);
    },
    
    createBackdrop(modal) {
        const backdrop = document.createElement('div');
        backdrop.className = 'hr-modal-backdrop';
        document.body.appendChild(backdrop);
        return backdrop;
    },
    
    bindCloseEvents(modal) {
        // Close on backdrop click
        const backdrop = modal.querySelector('.hr-modal-backdrop');
        if (backdrop) {
            backdrop.addEventListener('click', () => {
                this.hide(modal.id);
            });
        }
        
        // Close on close button click
        const closeBtn = modal.querySelector('.hr-modal-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                this.hide(modal.id);
            });
        }
        
        // Close on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modal.classList.contains('show')) {
                this.hide(modal.id);
            }
        });
    }
};

// ========== Theme Management - إدارة الثيمات ==========

HRSystem.theme = {
    init() {
        this.applyTheme(HRSystem.theme);
        this.bindEvents();
    },
    
    bindEvents() {
        document.addEventListener('click', (e) => {
            if (e.target.matches('.theme-toggle')) {
                this.toggle();
            }
        });
    },
    
    toggle() {
        const newTheme = HRSystem.theme === 'light' ? 'dark' : 'light';
        this.setTheme(newTheme);
    },
    
    setTheme(theme) {
        HRSystem.theme = theme;
        this.applyTheme(theme);
        localStorage.setItem('hr-theme', theme);
    },
    
    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
    }
};

// ========== Initialization - التهيئة ==========

document.addEventListener('DOMContentLoaded', () => {
    // Initialize all components
    HRSystem.sidebar.init();
    HRSystem.search.init();
    HRSystem.forms.init();
    HRSystem.theme.init();
    
    // Initialize data tables
    document.querySelectorAll('[data-hr-table]').forEach(table => {
        const config = JSON.parse(table.dataset.hrTable || '{}');
        HRSystem.dataTable.init(table.id, config);
    });
    
    // Initialize modals
    document.addEventListener('click', (e) => {
        if (e.target.matches('[data-hr-modal]')) {
            e.preventDefault();
            const modalId = e.target.dataset.hrModal;
            HRSystem.modal.show(modalId);
        }
    });
    
    console.log('HR System initialized successfully');
});

// Export for global access
window.HRSystem = HRSystem;
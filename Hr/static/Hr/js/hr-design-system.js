/*
=============================================================================
HR Design System JavaScript - جافاسكريبت نظام التصميم للموارد البشرية
=============================================================================
مكتبة JavaScript لإدارة الثيمات والتفاعلات في نظام الموارد البشرية
=============================================================================
*/

class HRDesignSystem {
    constructor() {
        this.currentTheme = localStorage.getItem('hr-theme') || 'light';
        this.init();
    }

    init() {
        this.applyTheme(this.currentTheme);
        this.setupEventListeners();
        this.initializeComponents();
    }

    // =============================================================================
    // THEME MANAGEMENT (إدارة الثيمات)
    // =============================================================================

    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('hr-theme', theme);
        this.currentTheme = theme;
        
        // تحديث أيقونة الثيم
        const themeIcon = document.querySelector('.theme-toggle-icon');
        if (themeIcon) {
            themeIcon.innerHTML = theme === 'dark' ? '☀️' : '🌙';
        }
    }

    toggleTheme() {
        const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.applyTheme(newTheme);
    }

    // =============================================================================
    // EVENT LISTENERS (مستمعي الأحداث)
    // =============================================================================

    setupEventListeners() {
        // تبديل الثيم
        document.addEventListener('click', (e) => {
            if (e.target.matches('.theme-toggle') || e.target.closest('.theme-toggle')) {
                e.preventDefault();
                this.toggleTheme();
            }
        });

        // إغلاق القوائم المنسدلة عند النقر خارجها
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.dropdown')) {
                this.closeAllDropdowns();
            }
        });

        // إدارة القوائم المنسدلة
        document.addEventListener('click', (e) => {
            if (e.target.matches('.dropdown-toggle') || e.target.closest('.dropdown-toggle')) {
                e.preventDefault();
                const dropdown = e.target.closest('.dropdown');
                this.toggleDropdown(dropdown);
            }
        });

        // إدارة علامات التبويب
        document.addEventListener('click', (e) => {
            if (e.target.matches('.tab-button') || e.target.closest('.tab-button')) {
                e.preventDefault();
                const tabButton = e.target.closest('.tab-button');
                this.switchTab(tabButton);
            }
        });

        // إدارة النماذج المتعددة الخطوات
        document.addEventListener('click', (e) => {
            if (e.target.matches('.step-next') || e.target.closest('.step-next')) {
                e.preventDefault();
                this.nextStep(e.target.closest('.multi-step-form'));
            }
            
            if (e.target.matches('.step-prev') || e.target.closest('.step-prev')) {
                e.preventDefault();
                this.prevStep(e.target.closest('.multi-step-form'));
            }
        });

        // إدارة الجداول القابلة للفرز
        document.addEventListener('click', (e) => {
            if (e.target.matches('.sortable-header') || e.target.closest('.sortable-header')) {
                e.preventDefault();
                const header = e.target.closest('.sortable-header');
                this.sortTable(header);
            }
        });

        // إدارة البحث المباشر
        document.addEventListener('input', (e) => {
            if (e.target.matches('.live-search') || e.target.closest('.live-search')) {
                this.handleLiveSearch(e.target);
            }
        });
    }

    // =============================================================================
    // COMPONENT INITIALIZATION (تهيئة المكونات)
    // =============================================================================

    initializeComponents() {
        this.initializeTooltips();
        this.initializeModals();
        this.initializeAlerts();
        this.initializeProgressBars();
        this.initializeDatePickers();
    }

    initializeTooltips() {
        const tooltips = document.querySelectorAll('[data-tooltip]');
        tooltips.forEach(element => {
            element.addEventListener('mouseenter', (e) => {
                this.showTooltip(e.target);
            });
            
            element.addEventListener('mouseleave', (e) => {
                this.hideTooltip(e.target);
            });
        });
    }

    initializeModals() {
        // إغلاق النوافذ المنبثقة بالضغط على ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAllModals();
            }
        });

        // إغلاق النوافذ المنبثقة بالنقر على الخلفية
        document.addEventListener('click', (e) => {
            if (e.target.matches('.modal-backdrop')) {
                this.closeModal(e.target.closest('.modal'));
            }
        });
    }

    initializeAlerts() {
        // إغلاق التنبيهات تلقائياً
        const autoCloseAlerts = document.querySelectorAll('.alert[data-auto-close]');
        autoCloseAlerts.forEach(alert => {
            const delay = parseInt(alert.dataset.autoClose) || 5000;
            setTimeout(() => {
                this.closeAlert(alert);
            }, delay);
        });
    }

    initializeProgressBars() {
        const progressBars = document.querySelectorAll('.progress-bar[data-animate]');
        progressBars.forEach(bar => {
            this.animateProgressBar(bar);
        });
    }

    initializeDatePickers() {
        const datePickers = document.querySelectorAll('.date-picker');
        datePickers.forEach(picker => {
            // تهيئة منتقي التاريخ (يمكن استخدام مكتبة خارجية)
            this.setupDatePicker(picker);
        });
    }

    // =============================================================================
    // DROPDOWN FUNCTIONALITY (وظائف القوائم المنسدلة)
    // =============================================================================

    toggleDropdown(dropdown) {
        const isOpen = dropdown.classList.contains('open');
        
        // إغلاق جميع القوائم المنسدلة الأخرى
        this.closeAllDropdowns();
        
        if (!isOpen) {
            dropdown.classList.add('open');
            const menu = dropdown.querySelector('.dropdown-menu');
            if (menu) {
                menu.classList.add('animate-slideInDown');
            }
        }
    }

    closeAllDropdowns() {
        const openDropdowns = document.querySelectorAll('.dropdown.open');
        openDropdowns.forEach(dropdown => {
            dropdown.classList.remove('open');
            const menu = dropdown.querySelector('.dropdown-menu');
            if (menu) {
                menu.classList.remove('animate-slideInDown');
            }
        });
    }

    // =============================================================================
    // TAB FUNCTIONALITY (وظائف علامات التبويب)
    // =============================================================================

    switchTab(tabButton) {
        const tabContainer = tabButton.closest('.tabs');
        const targetTab = tabButton.dataset.tab;
        
        // إزالة الفئة النشطة من جميع الأزرار والمحتويات
        tabContainer.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.remove('active');
        });
        
        tabContainer.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        
        // إضافة الفئة النشطة للزر والمحتوى المحدد
        tabButton.classList.add('active');
        const targetContent = tabContainer.querySelector(`[data-tab-content="${targetTab}"]`);
        if (targetContent) {
            targetContent.classList.add('active');
            targetContent.classList.add('animate-fadeIn');
        }
    }

    // =============================================================================
    // MULTI-STEP FORM FUNCTIONALITY (وظائف النماذج متعددة الخطوات)
    // =============================================================================

    nextStep(form) {
        const currentStep = form.querySelector('.step.active');
        const nextStep = currentStep.nextElementSibling;
        
        if (nextStep && nextStep.classList.contains('step')) {
            // التحقق من صحة الخطوة الحالية
            if (this.validateStep(currentStep)) {
                currentStep.classList.remove('active');
                nextStep.classList.add('active');
                nextStep.classList.add('animate-slideInRight');
                
                this.updateStepIndicator(form);
            }
        }
    }

    prevStep(form) {
        const currentStep = form.querySelector('.step.active');
        const prevStep = currentStep.previousElementSibling;
        
        if (prevStep && prevStep.classList.contains('step')) {
            currentStep.classList.remove('active');
            prevStep.classList.add('active');
            prevStep.classList.add('animate-slideInLeft');
            
            this.updateStepIndicator(form);
        }
    }

    validateStep(step) {
        const requiredFields = step.querySelectorAll('[required]');
        let isValid = true;
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                this.showFieldError(field, 'هذا الحقل مطلوب');
                isValid = false;
            } else {
                this.clearFieldError(field);
            }
        });
        
        return isValid;
    }

    updateStepIndicator(form) {
        const steps = form.querySelectorAll('.step');
        const indicators = form.querySelectorAll('.step-indicator');
        const currentStepIndex = Array.from(steps).findIndex(step => step.classList.contains('active'));
        
        indicators.forEach((indicator, index) => {
            indicator.classList.toggle('active', index === currentStepIndex);
            indicator.classList.toggle('completed', index < currentStepIndex);
        });
    }

    // =============================================================================
    // TABLE FUNCTIONALITY (وظائف الجداول)
    // =============================================================================

    sortTable(header) {
        const table = header.closest('table');
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        const columnIndex = Array.from(header.parentNode.children).indexOf(header);
        const isAscending = !header.classList.contains('sort-asc');
        
        // إزالة فئات الترتيب من جميع الرؤوس
        table.querySelectorAll('.sortable-header').forEach(h => {
            h.classList.remove('sort-asc', 'sort-desc');
        });
        
        // إضافة فئة الترتيب للرأس الحالي
        header.classList.add(isAscending ? 'sort-asc' : 'sort-desc');
        
        // ترتيب الصفوف
        rows.sort((a, b) => {
            const aValue = a.children[columnIndex].textContent.trim();
            const bValue = b.children[columnIndex].textContent.trim();
            
            // محاولة تحويل إلى رقم
            const aNum = parseFloat(aValue);
            const bNum = parseFloat(bValue);
            
            if (!isNaN(aNum) && !isNaN(bNum)) {
                return isAscending ? aNum - bNum : bNum - aNum;
            } else {
                return isAscending ? 
                    aValue.localeCompare(bValue, 'ar') : 
                    bValue.localeCompare(aValue, 'ar');
            }
        });
        
        // إعادة ترتيب الصفوف في الجدول
        rows.forEach(row => tbody.appendChild(row));
    }

    // =============================================================================
    // SEARCH FUNCTIONALITY (وظائف البحث)
    // =============================================================================

    handleLiveSearch(input) {
        const searchTerm = input.value.toLowerCase();
        const targetSelector = input.dataset.searchTarget;
        const targets = document.querySelectorAll(targetSelector);
        
        targets.forEach(target => {
            const text = target.textContent.toLowerCase();
            const matches = text.includes(searchTerm);
            target.style.display = matches ? '' : 'none';
        });
    }

    // =============================================================================
    // MODAL FUNCTIONALITY (وظائف النوافذ المنبثقة)
    // =============================================================================

    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('active');
            modal.classList.add('animate-fadeIn');
            document.body.style.overflow = 'hidden';
        }
    }

    closeModal(modal) {
        if (modal) {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        }
    }

    closeAllModals() {
        const openModals = document.querySelectorAll('.modal.active');
        openModals.forEach(modal => this.closeModal(modal));
    }

    // =============================================================================
    // TOOLTIP FUNCTIONALITY (وظائف التلميحات)
    // =============================================================================

    showTooltip(element) {
        const tooltipText = element.dataset.tooltip;
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = tooltipText;
        
        document.body.appendChild(tooltip);
        
        const rect = element.getBoundingClientRect();
        tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
        tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px';
        
        tooltip.classList.add('animate-fadeIn');
    }

    hideTooltip(element) {
        const tooltip = document.querySelector('.tooltip');
        if (tooltip) {
            tooltip.remove();
        }
    }

    // =============================================================================
    // ALERT FUNCTIONALITY (وظائف التنبيهات)
    // =============================================================================

    showAlert(message, type = 'info', duration = 5000) {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} animate-slideInDown`;
        alert.innerHTML = `
            <span>${message}</span>
            <button type="button" class="alert-close" onclick="hrDesignSystem.closeAlert(this.parentElement)">
                ×
            </button>
        `;
        
        const container = document.querySelector('.alerts-container') || document.body;
        container.appendChild(alert);
        
        if (duration > 0) {
            setTimeout(() => {
                this.closeAlert(alert);
            }, duration);
        }
    }

    closeAlert(alert) {
        alert.classList.add('animate-slideInUp');
        setTimeout(() => {
            alert.remove();
        }, 300);
    }

    // =============================================================================
    // PROGRESS BAR FUNCTIONALITY (وظائف أشرطة التقدم)
    // =============================================================================

    animateProgressBar(progressBar) {
        const targetWidth = progressBar.dataset.progress || '0';
        progressBar.style.width = '0%';
        
        setTimeout(() => {
            progressBar.style.width = targetWidth + '%';
        }, 100);
    }

    updateProgressBar(progressBar, percentage) {
        progressBar.style.width = percentage + '%';
        progressBar.dataset.progress = percentage;
    }

    // =============================================================================
    // FORM VALIDATION (التحقق من النماذج)
    // =============================================================================

    showFieldError(field, message) {
        this.clearFieldError(field);
        
        field.classList.add('error');
        const errorElement = document.createElement('div');
        errorElement.className = 'field-error';
        errorElement.textContent = message;
        
        field.parentNode.appendChild(errorElement);
    }

    clearFieldError(field) {
        field.classList.remove('error');
        const errorElement = field.parentNode.querySelector('.field-error');
        if (errorElement) {
            errorElement.remove();
        }
    }

    // =============================================================================
    // UTILITY FUNCTIONS (وظائف مساعدة)
    // =============================================================================

    setupDatePicker(picker) {
        // يمكن تخصيص هذه الوظيفة لاستخدام مكتبة منتقي التاريخ المفضلة
        picker.addEventListener('focus', () => {
            // تهيئة منتقي التاريخ
        });
    }

    formatDate(date, format = 'YYYY-MM-DD') {
        const d = new Date(date);
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        
        return format
            .replace('YYYY', year)
            .replace('MM', month)
            .replace('DD', day);
    }

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
    }

    // =============================================================================
    // API HELPERS (مساعدات API)
    // =============================================================================

    async apiRequest(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken(),
            },
        };

        const mergedOptions = { ...defaultOptions, ...options };
        
        try {
            const response = await fetch(url, mergedOptions);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            this.showAlert('حدث خطأ في الاتصال بالخادم', 'danger');
            throw error;
        }
    }

    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }
}

// تهيئة نظام التصميم عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', () => {
    window.hrDesignSystem = new HRDesignSystem();
});

// تصدير الفئة للاستخدام في ملفات أخرى
if (typeof module !== 'undefined' && module.exports) {
    module.exports = HRDesignSystem;
}
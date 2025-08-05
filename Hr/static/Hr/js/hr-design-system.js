/**
 * نظام التصميم التفاعلي لتطبيق الموارد البشرية
 * HR Design System Interactive Components
 */

class HRDesignSystem {
    constructor() {
        this.init();
    }

    init() {
        this.initThemeToggle();
        this.initTooltips();
        this.initModals();
        this.initTabs();
        this.initDropdowns();
        this.initFormValidation();
        this.initDataTables();
        this.initNotifications();
        this.initProgressBars();
    }

    // تبديل الثيم
    initThemeToggle() {
        const themeToggle = document.querySelector('[data-theme-toggle]');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                const currentTheme = document.documentElement.getAttribute('data-theme');
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                document.documentElement.setAttribute('data-theme', newTheme);
                localStorage.setItem('theme', newTheme);
            });
        }

        // تطبيق الثيم المحفوظ
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            document.documentElement.setAttribute('data-theme', savedTheme);
        }
    }

    // تلميحات الأدوات
    initTooltips() {
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

    showTooltip(element) {
        const text = element.getAttribute('data-tooltip');
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = text;
        tooltip.style.cssText = `
            position: absolute;
            background: var(--bg-dark);
            color: var(--text-white);
            padding: var(--spacing-sm) var(--spacing-md);
            border-radius: var(--radius-md);
            font-size: var(--font-size-sm);
            z-index: 1000;
            pointer-events: none;
            opacity: 0;
            transition: opacity var(--transition-fast);
        `;
        
        document.body.appendChild(tooltip);
        
        const rect = element.getBoundingClientRect();
        tooltip.style.top = (rect.top - tooltip.offsetHeight - 5) + 'px';
        tooltip.style.left = (rect.left + rect.width / 2 - tooltip.offsetWidth / 2) + 'px';
        
        setTimeout(() => tooltip.style.opacity = '1', 10);
        element._tooltip = tooltip;
    }

    hideTooltip(element) {
        if (element._tooltip) {
            element._tooltip.remove();
            delete element._tooltip;
        }
    }

    // النوافذ المنبثقة
    initModals() {
        const modalTriggers = document.querySelectorAll('[data-modal-target]');
        const modalCloses = document.querySelectorAll('[data-modal-close]');
        
        modalTriggers.forEach(trigger => {
            trigger.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = trigger.getAttribute('data-modal-target');
                this.openModal(targetId);
            });
        });

        modalCloses.forEach(close => {
            close.addEventListener('click', (e) => {
                e.preventDefault();
                this.closeModal(close.closest('.modal'));
            });
        });

        // إغلاق عند النقر خارج النافذة
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-overlay')) {
                this.closeModal(e.target.querySelector('.modal'));
            }
        });
    }

    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'flex';
            modal.classList.add('animate-fade-in');
            document.body.style.overflow = 'hidden';
        }
    }

    closeModal(modal) {
        if (modal) {
            modal.style.display = 'none';
            modal.classList.remove('animate-fade-in');
            document.body.style.overflow = '';
        }
    }

    // علامات التبويب
    initTabs() {
        const tabButtons = document.querySelectorAll('[data-tab-target]');
        
        tabButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = button.getAttribute('data-tab-target');
                this.switchTab(button, targetId);
            });
        });
    }

    switchTab(activeButton, targetId) {
        const tabContainer = activeButton.closest('[data-tabs]');
        const allButtons = tabContainer.querySelectorAll('[data-tab-target]');
        const allPanes = tabContainer.querySelectorAll('[data-tab-pane]');

        // إزالة الحالة النشطة من جميع الأزرار والألواح
        allButtons.forEach(btn => btn.classList.remove('active'));
        allPanes.forEach(pane => pane.classList.remove('active'));

        // تفعيل الزر والوحة المحددة
        activeButton.classList.add('active');
        const targetPane = document.getElementById(targetId);
        if (targetPane) {
            targetPane.classList.add('active');
            targetPane.classList.add('animate-fade-in');
        }
    }

    // القوائم المنسدلة
    initDropdowns() {
        const dropdownTriggers = document.querySelectorAll('[data-dropdown-toggle]');
        
        dropdownTriggers.forEach(trigger => {
            trigger.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                const targetId = trigger.getAttribute('data-dropdown-toggle');
                this.toggleDropdown(targetId);
            });
        });

        // إغلاق القوائم عند النقر خارجها
        document.addEventListener('click', () => {
            this.closeAllDropdowns();
        });
    }

    toggleDropdown(dropdownId) {
        const dropdown = document.getElementById(dropdownId);
        if (dropdown) {
            const isOpen = dropdown.classList.contains('show');
            this.closeAllDropdowns();
            if (!isOpen) {
                dropdown.classList.add('show');
                dropdown.classList.add('animate-fade-in');
            }
        }
    }

    closeAllDropdowns() {
        const dropdowns = document.querySelectorAll('.dropdown-menu');
        dropdowns.forEach(dropdown => {
            dropdown.classList.remove('show', 'animate-fade-in');
        });
    }

    // التحقق من صحة النماذج
    initFormValidation() {
        const forms = document.querySelectorAll('[data-validate]');
        
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!this.validateForm(form)) {
                    e.preventDefault();
                }
            });

            // التحقق المباشر أثناء الكتابة
            const inputs = form.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                input.addEventListener('blur', () => {
                    this.validateField(input);
                });
            });
        });
    }

    validateForm(form) {
        const inputs = form.querySelectorAll('[required]');
        let isValid = true;

        inputs.forEach(input => {
            if (!this.validateField(input)) {
                isValid = false;
            }
        });

        return isValid;
    }

    validateField(field) {
        const value = field.value.trim();
        const isRequired = field.hasAttribute('required');
        const type = field.getAttribute('type');
        
        let isValid = true;
        let message = '';

        if (isRequired && !value) {
            isValid = false;
            message = 'هذا الحقل مطلوب';
        } else if (value) {
            switch (type) {
                case 'email':
                    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                    if (!emailRegex.test(value)) {
                        isValid = false;
                        message = 'يرجى إدخال بريد إلكتروني صحيح';
                    }
                    break;
                case 'tel':
                    const phoneRegex = /^[\+]?[0-9\s\-\(\)]{10,}$/;
                    if (!phoneRegex.test(value)) {
                        isValid = false;
                        message = 'يرجى إدخال رقم هاتف صحيح';
                    }
                    break;
            }
        }

        this.showFieldValidation(field, isValid, message);
        return isValid;
    }

    showFieldValidation(field, isValid, message) {
        const existingError = field.parentNode.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }

        if (!isValid) {
            field.classList.add('is-invalid');
            const errorDiv = document.createElement('div');
            errorDiv.className = 'field-error text-danger fs-sm mt-1';
            errorDiv.textContent = message;
            field.parentNode.appendChild(errorDiv);
        } else {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
        }
    }

    // جداول البيانات
    initDataTables() {
        const tables = document.querySelectorAll('[data-table]');
        
        tables.forEach(table => {
            this.enhanceTable(table);
        });
    }

    enhanceTable(table) {
        // إضافة البحث
        const searchInput = table.parentNode.querySelector('[data-table-search]');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.filterTable(table, e.target.value);
            });
        }

        // إضافة الترتيب
        const headers = table.querySelectorAll('th[data-sortable]');
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', () => {
                this.sortTable(table, header);
            });
        });
    }

    filterTable(table, searchTerm) {
        const rows = table.querySelectorAll('tbody tr');
        const term = searchTerm.toLowerCase();

        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(term) ? '' : 'none';
        });
    }

    sortTable(table, header) {
        const columnIndex = Array.from(header.parentNode.children).indexOf(header);
        const rows = Array.from(table.querySelectorAll('tbody tr'));
        const isAscending = !header.classList.contains('sort-asc');

        rows.sort((a, b) => {
            const aText = a.children[columnIndex].textContent.trim();
            const bText = b.children[columnIndex].textContent.trim();
            
            const aValue = isNaN(aText) ? aText : parseFloat(aText);
            const bValue = isNaN(bText) ? bText : parseFloat(bText);

            if (aValue < bValue) return isAscending ? -1 : 1;
            if (aValue > bValue) return isAscending ? 1 : -1;
            return 0;
        });

        // إعادة ترتيب الصفوف
        const tbody = table.querySelector('tbody');
        rows.forEach(row => tbody.appendChild(row));

        // تحديث مؤشر الترتيب
        table.querySelectorAll('th').forEach(th => {
            th.classList.remove('sort-asc', 'sort-desc');
        });
        header.classList.add(isAscending ? 'sort-asc' : 'sort-desc');
    }

    // الإشعارات
    initNotifications() {
        this.notificationContainer = this.createNotificationContainer();
    }

    createNotificationContainer() {
        let container = document.getElementById('notification-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-container';
            container.style.cssText = `
                position: fixed;
                top: 20px;
                left: 20px;
                z-index: 9999;
                max-width: 400px;
            `;
            document.body.appendChild(container);
        }
        return container;
    }

    showNotification(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} animate-fade-in`;
        notification.style.cssText = `
            margin-bottom: var(--spacing-sm);
            box-shadow: var(--shadow-lg);
        `;
        notification.textContent = message;

        // زر الإغلاق
        const closeBtn = document.createElement('button');
        closeBtn.innerHTML = '×';
        closeBtn.style.cssText = `
            background: none;
            border: none;
            font-size: 1.5rem;
            float: left;
            margin-right: var(--spacing-sm);
            cursor: pointer;
        `;
        closeBtn.addEventListener('click', () => {
            this.hideNotification(notification);
        });

        notification.appendChild(closeBtn);
        this.notificationContainer.appendChild(notification);

        // إخفاء تلقائي
        if (duration > 0) {
            setTimeout(() => {
                this.hideNotification(notification);
            }, duration);
        }

        return notification;
    }

    hideNotification(notification) {
        notification.style.opacity = '0';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }

    // أشرطة التقدم
    initProgressBars() {
        const progressBars = document.querySelectorAll('.progress-bar');
        
        progressBars.forEach(bar => {
            const fill = bar.querySelector('.progress-fill');
            const value = fill.getAttribute('data-value') || 0;
            
            // تحريك شريط التقدم
            setTimeout(() => {
                fill.style.width = value + '%';
            }, 100);
        });
    }

    // وظائف مساعدة عامة
    static showLoading(element) {
        element.classList.add('animate-pulse');
        element.style.pointerEvents = 'none';
    }

    static hideLoading(element) {
        element.classList.remove('animate-pulse');
        element.style.pointerEvents = '';
    }

    static formatNumber(number, locale = 'ar-SA') {
        return new Intl.NumberFormat(locale).format(number);
    }

    static formatDate(date, locale = 'ar-SA') {
        return new Intl.DateTimeFormat(locale).format(new Date(date));
    }

    static formatCurrency(amount, currency = 'SAR', locale = 'ar-SA') {
        return new Intl.NumberFormat(locale, {
            style: 'currency',
            currency: currency
        }).format(amount);
    }
}

// تهيئة النظام عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', () => {
    window.hrDesignSystem = new HRDesignSystem();
});

// تصدير للاستخدام العام
window.HRDesignSystem = HRDesignSystem;
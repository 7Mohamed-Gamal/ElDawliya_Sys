/*
=============================================================================
نظام التصميم التفاعلي - HR Design System JavaScript
=============================================================================
*/

// إعدادات النظام الأساسية
const HRDesignSystem = {
    // إعدادات الثيم
    theme: {
        current: localStorage.getItem('hr-theme') || 'light',
        toggle: function() {
            this.current = this.current === 'light' ? 'dark' : 'light';
            this.apply();
            localStorage.setItem('hr-theme', this.current);
        },
        apply: function() {
            document.documentElement.setAttribute('data-theme', this.current);
            // تحديث أيقونة الثيم
            const themeIcon = document.querySelector('.theme-toggle i');
            if (themeIcon) {
                themeIcon.className = this.current === 'light' ? 'fas fa-moon' : 'fas fa-sun';
            }
        }
    },

    // إدارة الشريط الجانبي
    sidebar: {
        isCollapsed: localStorage.getItem('hr-sidebar-collapsed') === 'true',
        toggle: function() {
            this.isCollapsed = !this.isCollapsed;
            this.apply();
            localStorage.setItem('hr-sidebar-collapsed', this.isCollapsed);
        },
        apply: function() {
            const sidebar = document.querySelector('.sidebar');
            const mainContent = document.querySelector('.main-content');
            
            if (sidebar) {
                sidebar.classList.toggle('collapsed', this.isCollapsed);
            }
            
            // تحديث عرض المحتوى الرئيسي
            if (mainContent) {
                mainContent.style.marginRight = this.isCollapsed ? '80px' : '280px';
            }
        },
        show: function() {
            const sidebar = document.querySelector('.sidebar');
            if (sidebar) {
                sidebar.classList.add('show');
            }
        },
        hide: function() {
            const sidebar = document.querySelector('.sidebar');
            if (sidebar) {
                sidebar.classList.remove('show');
            }
        }
    },

    // إدارة النماذج
    forms: {
        // التحقق من صحة النماذج
        validate: function(form) {
            let isValid = true;
            const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
            
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    this.showError(input, 'هذا الحقل مطلوب');
                    isValid = false;
                } else {
                    this.clearError(input);
                }
            });
            
            return isValid;
        },
        
        // عرض رسالة خطأ
        showError: function(input, message) {
            input.classList.add('is-invalid');
            
            let errorDiv = input.parentNode.querySelector('.invalid-feedback');
            if (!errorDiv) {
                errorDiv = document.createElement('div');
                errorDiv.className = 'invalid-feedback';
                input.parentNode.appendChild(errorDiv);
            }
            errorDiv.textContent = message;
        },
        
        // إزالة رسالة الخطأ
        clearError: function(input) {
            input.classList.remove('is-invalid');
            const errorDiv = input.parentNode.querySelector('.invalid-feedback');
            if (errorDiv) {
                errorDiv.remove();
            }
        },
        
        // تحسين تجربة المستخدم للنماذج
        enhance: function() {
            // إضافة تأثيرات التركيز
            document.querySelectorAll('.form-control').forEach(input => {
                input.addEventListener('focus', function() {
                    this.parentNode.classList.add('focused');
                });
                
                input.addEventListener('blur', function() {
                    this.parentNode.classList.remove('focused');
                    if (this.value) {
                        this.parentNode.classList.add('filled');
                    } else {
                        this.parentNode.classList.remove('filled');
                    }
                });
            });
        }
    },

    // إدارة الجداول
    tables: {
        // تحسين الجداول المتجاوبة
        enhance: function() {
            document.querySelectorAll('.table-responsive').forEach(wrapper => {
                const table = wrapper.querySelector('table');
                if (table) {
                    // إضافة فئات Bootstrap
                    table.classList.add('table', 'table-hover');
                    
                    // إضافة إمكانية الفرز
                    this.addSorting(table);
                    
                    // إضافة البحث السريع
                    this.addQuickSearch(wrapper);
                }
            });
        },
        
        // إضافة إمكانية الفرز
        addSorting: function(table) {
            const headers = table.querySelectorAll('th[data-sortable]');
            headers.forEach(header => {
                header.style.cursor = 'pointer';
                header.innerHTML += ' <i class=\"fas fa-sort text-muted\"></i>';
                
                header.addEventListener('click', () => {
                    this.sortTable(table, header);
                });
            });
        },
        
        // فرز الجدول
        sortTable: function(table, header) {
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            const columnIndex = Array.from(header.parentNode.children).indexOf(header);
            const isAscending = !header.classList.contains('sort-asc');
            
            // إزالة فئات الفرز من جميع الرؤوس
            table.querySelectorAll('th').forEach(th => {
                th.classList.remove('sort-asc', 'sort-desc');
                const icon = th.querySelector('i');
                if (icon) {
                    icon.className = 'fas fa-sort text-muted';
                }
            });
            
            // إضافة فئة الفرز للرأس الحالي
            header.classList.add(isAscending ? 'sort-asc' : 'sort-desc');
            const icon = header.querySelector('i');
            if (icon) {
                icon.className = isAscending ? 'fas fa-sort-up text-primary' : 'fas fa-sort-down text-primary';
            }
            
            // فرز الصفوف
            rows.sort((a, b) => {
                const aValue = a.children[columnIndex].textContent.trim();
                const bValue = b.children[columnIndex].textContent.trim();
                
                if (isAscending) {
                    return aValue.localeCompare(bValue, 'ar');
                } else {
                    return bValue.localeCompare(aValue, 'ar');
                }
            });
            
            // إعادة ترتيب الصفوف
            rows.forEach(row => tbody.appendChild(row));
        },
        
        // إضافة البحث السريع
        addQuickSearch: function(wrapper) {
            const searchInput = document.createElement('input');
            searchInput.type = 'text';
            searchInput.className = 'form-control mb-3';
            searchInput.placeholder = 'البحث في الجدول...';
            
            wrapper.insertBefore(searchInput, wrapper.firstChild);
            
            searchInput.addEventListener('input', (e) => {
                this.filterTable(wrapper.querySelector('table'), e.target.value);
            });
        },
        
        // فلترة الجدول
        filterTable: function(table, searchTerm) {
            const tbody = table.querySelector('tbody');
            const rows = tbody.querySelectorAll('tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                const shouldShow = text.includes(searchTerm.toLowerCase());
                row.style.display = shouldShow ? '' : 'none';
            });
        }
    },

    // إدارة الإشعارات
    notifications: {
        // عرض إشعار
        show: function(message, type = 'info', duration = 5000) {
            const notification = document.createElement('div');
            notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
            notification.style.cssText = `
                top: 20px;
                left: 20px;
                z-index: 9999;
                min-width: 300px;
                box-shadow: var(--shadow-lg);
            `;
            
            notification.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            
            document.body.appendChild(notification);
            
            // إزالة الإشعار تلقائياً
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, duration);
        },
        
        // إشعار نجاح
        success: function(message, duration) {
            this.show(message, 'success', duration);
        },
        
        // إشعار خطأ
        error: function(message, duration) {
            this.show(message, 'error', duration);
        },
        
        // إشعار تحذير
        warning: function(message, duration) {
            this.show(message, 'warning', duration);
        },
        
        // إشعار معلومات
        info: function(message, duration) {
            this.show(message, 'info', duration);
        }
    },

    // إدارة النوافذ المنبثقة
    modals: {
        // فتح نافذة منبثقة
        open: function(modalId) {
            const modal = document.getElementById(modalId);
            if (modal) {
                modal.classList.add('show');
                modal.style.display = 'block';
                document.body.classList.add('modal-open');
                
                // إضافة backdrop
                const backdrop = document.createElement('div');
                backdrop.className = 'modal-backdrop fade show';
                backdrop.id = modalId + '-backdrop';
                document.body.appendChild(backdrop);
            }
        },
        
        // إغلاق نافذة منبثقة
        close: function(modalId) {
            const modal = document.getElementById(modalId);
            const backdrop = document.getElementById(modalId + '-backdrop');
            
            if (modal) {
                modal.classList.remove('show');
                modal.style.display = 'none';
                document.body.classList.remove('modal-open');
            }
            
            if (backdrop) {
                backdrop.remove();
            }
        }
    },

    // أدوات مساعدة
    utils: {
        // تنسيق التاريخ
        formatDate: function(date, format = 'dd/mm/yyyy') {
            if (!(date instanceof Date)) {
                date = new Date(date);
            }
            
            const day = date.getDate().toString().padStart(2, '0');
            const month = (date.getMonth() + 1).toString().padStart(2, '0');
            const year = date.getFullYear();
            
            return format
                .replace('dd', day)
                .replace('mm', month)
                .replace('yyyy', year);
        },
        
        // تنسيق الأرقام
        formatNumber: function(number, decimals = 0) {
            return new Intl.NumberFormat('ar-SA', {
                minimumFractionDigits: decimals,
                maximumFractionDigits: decimals
            }).format(number);
        },
        
        // تنسيق العملة
        formatCurrency: function(amount, currency = 'SAR') {
            return new Intl.NumberFormat('ar-SA', {
                style: 'currency',
                currency: currency
            }).format(amount);
        },
        
        // تأخير التنفيذ (debounce)
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
        
        // نسخ النص إلى الحافظة
        copyToClipboard: function(text) {
            if (navigator.clipboard) {
                navigator.clipboard.writeText(text).then(() => {
                    HRDesignSystem.notifications.success('تم نسخ النص بنجاح');
                });
            } else {
                // fallback للمتصفحات القديمة
                const textArea = document.createElement('textarea');
                textArea.value = text;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                HRDesignSystem.notifications.success('تم نسخ النص بنجاح');
            }
        }
    },

    // تهيئة النظام
    init: function() {
        // تطبيق الثيم المحفوظ
        this.theme.apply();
        
        // تطبيق حالة الشريط الجانبي
        this.sidebar.apply();
        
        // تحسين النماذج
        this.forms.enhance();
        
        // تحسين الجداول
        this.tables.enhance();
        
        // إضافة مستمعي الأحداث
        this.addEventListeners();
        
        console.log('HR Design System initialized successfully');
    },

    // إضافة مستمعي الأحداث
    addEventListeners: function() {
        // تبديل الثيم
        document.addEventListener('click', (e) => {
            if (e.target.matches('.theme-toggle, .theme-toggle *')) {
                e.preventDefault();
                this.theme.toggle();
            }
        });
        
        // تبديل الشريط الجانبي
        document.addEventListener('click', (e) => {
            if (e.target.matches('.sidebar-toggle, .sidebar-toggle *')) {
                e.preventDefault();
                this.sidebar.toggle();
            }
        });
        
        // إغلاق الشريط الجانبي على الشاشات الصغيرة
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 768 && !e.target.closest('.sidebar') && !e.target.matches('.sidebar-toggle, .sidebar-toggle *')) {
                this.sidebar.hide();
            }
        });
        
        // التحقق من النماذج عند الإرسال
        document.addEventListener('submit', (e) => {
            const form = e.target;
            if (form.hasAttribute('data-validate')) {
                if (!this.forms.validate(form)) {
                    e.preventDefault();
                }
            }
        });
        
        // إغلاق النوافذ المنبثقة
        document.addEventListener('click', (e) => {
            if (e.target.matches('.modal-backdrop, [data-dismiss=\"modal\"]')) {
                const modal = e.target.closest('.modal') || document.querySelector('.modal.show');
                if (modal) {
                    this.modals.close(modal.id);
                }
            }
        });
        
        // تحديث حالة الشريط الجانبي عند تغيير حجم الشاشة
        window.addEventListener('resize', () => {
            if (window.innerWidth <= 768) {
                this.sidebar.hide();
            }
        });
    }
};

// تهيئة النظام عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    HRDesignSystem.init();
});

// تصدير النظام للاستخدام العام
window.HRDesignSystem = HRDesignSystem;
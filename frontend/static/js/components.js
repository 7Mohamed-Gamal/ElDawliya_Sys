/**
 * Component Library JavaScript
 * مكتبة المكونات - JavaScript
 */

/**
 * Enhanced Table Component
 * مكون الجدول المحسن
 */
class EnhancedTable {
    constructor(tableElement, options = {}) {
        this.table = tableElement;
        this.options = {
            sortable: true,
            searchable: true,
            pagination: false,
            pageSize: 10,
            ...options
        };
        
        this.currentSort = { column: null, direction: 'asc' };
        this.currentPage = 1;
        this.filteredData = [];
        this.originalData = [];
        
        this.init();
    }
    
    init() {
        this.setupSorting();
        this.setupSearch();
        this.setupPagination();
        this.storeOriginalData();
    }
    
    storeOriginalData() {
        const rows = Array.from(this.table.querySelectorAll('tbody tr'));
        this.originalData = rows.map(row => ({
            element: row,
            data: Array.from(row.cells).map(cell => cell.textContent.trim())
        }));
        this.filteredData = [...this.originalData];
    }
    
    setupSorting() {
        if (!this.options.sortable) return;
        
        const headers = this.table.querySelectorAll('th.sortable');
        headers.forEach((header, index) => {
            header.addEventListener('click', () => this.sort(index));
            header.style.cursor = 'pointer';
        });
    }
    
    sort(columnIndex) {
        const headers = this.table.querySelectorAll('th.sortable');
        const header = headers[columnIndex];
        
        // Update sort direction
        if (this.currentSort.column === columnIndex) {
            this.currentSort.direction = this.currentSort.direction === 'asc' ? 'desc' : 'asc';
        } else {
            this.currentSort.direction = 'asc';
        }
        this.currentSort.column = columnIndex;
        
        // Update header classes
        headers.forEach(h => h.classList.remove('asc', 'desc'));
        header.classList.add(this.currentSort.direction);
        
        // Sort data
        this.filteredData.sort((a, b) => {
            const aValue = a.data[columnIndex];
            const bValue = b.data[columnIndex];
            
            // Try to parse as numbers
            const aNum = parseFloat(aValue);
            const bNum = parseFloat(bValue);
            
            let comparison = 0;
            if (!isNaN(aNum) && !isNaN(bNum)) {
                comparison = aNum - bNum;
            } else {
                comparison = aValue.localeCompare(bValue, 'ar');
            }
            
            return this.currentSort.direction === 'asc' ? comparison : -comparison;
        });
        
        this.renderTable();
    }
    
    setupSearch() {
        if (!this.options.searchable) return;
        
        // Create search input if it doesn't exist
        let searchInput = document.querySelector(`#search-${this.table.id}`);
        if (!searchInput) {
            searchInput = document.createElement('input');
            searchInput.type = 'text';
            searchInput.id = `search-${this.table.id}`;
            searchInput.className = 'form-control-enhanced';
            searchInput.placeholder = 'البحث في الجدول...';
            
            const searchContainer = document.createElement('div');
            searchContainer.className = 'table-search mb-3';
            searchContainer.appendChild(searchInput);
            
            this.table.parentNode.insertBefore(searchContainer, this.table);
        }
        
        searchInput.addEventListener('input', (e) => this.search(e.target.value));
    }
    
    search(query) {
        if (!query.trim()) {
            this.filteredData = [...this.originalData];
        } else {
            this.filteredData = this.originalData.filter(row => 
                row.data.some(cell => 
                    cell.toLowerCase().includes(query.toLowerCase())
                )
            );
        }
        
        this.currentPage = 1;
        this.renderTable();
        this.updatePagination();
    }
    
    setupPagination() {
        if (!this.options.pagination) return;
        
        const paginationContainer = document.createElement('div');
        paginationContainer.className = 'table-pagination mt-3 d-flex justify-content-between align-items-center';
        paginationContainer.innerHTML = `
            <div class="pagination-info">
                <span id="pagination-info-${this.table.id}"></span>
            </div>
            <nav>
                <ul class="pagination pagination-sm" id="pagination-${this.table.id}">
                </ul>
            </nav>
        `;
        
        this.table.parentNode.appendChild(paginationContainer);
        this.updatePagination();
    }
    
    updatePagination() {
        if (!this.options.pagination) return;
        
        const totalItems = this.filteredData.length;
        const totalPages = Math.ceil(totalItems / this.options.pageSize);
        const startItem = (this.currentPage - 1) * this.options.pageSize + 1;
        const endItem = Math.min(this.currentPage * this.options.pageSize, totalItems);
        
        // Update info
        const infoElement = document.querySelector(`#pagination-info-${this.table.id}`);
        if (infoElement) {
            infoElement.textContent = `عرض ${startItem} إلى ${endItem} من ${totalItems} عنصر`;
        }
        
        // Update pagination buttons
        const paginationElement = document.querySelector(`#pagination-${this.table.id}`);
        if (paginationElement) {
            paginationElement.innerHTML = '';
            
            // Previous button
            const prevLi = document.createElement('li');
            prevLi.className = `page-item ${this.currentPage === 1 ? 'disabled' : ''}`;
            prevLi.innerHTML = `<a class="page-link" href="#" data-page="${this.currentPage - 1}">السابق</a>`;
            paginationElement.appendChild(prevLi);
            
            // Page numbers
            for (let i = 1; i <= totalPages; i++) {
                if (i === 1 || i === totalPages || (i >= this.currentPage - 2 && i <= this.currentPage + 2)) {
                    const li = document.createElement('li');
                    li.className = `page-item ${i === this.currentPage ? 'active' : ''}`;
                    li.innerHTML = `<a class="page-link" href="#" data-page="${i}">${i}</a>`;
                    paginationElement.appendChild(li);
                } else if (i === this.currentPage - 3 || i === this.currentPage + 3) {
                    const li = document.createElement('li');
                    li.className = 'page-item disabled';
                    li.innerHTML = '<span class="page-link">...</span>';
                    paginationElement.appendChild(li);
                }
            }
            
            // Next button
            const nextLi = document.createElement('li');
            nextLi.className = `page-item ${this.currentPage === totalPages ? 'disabled' : ''}`;
            nextLi.innerHTML = `<a class="page-link" href="#" data-page="${this.currentPage + 1}">التالي</a>`;
            paginationElement.appendChild(nextLi);
            
            // Add click events
            paginationElement.addEventListener('click', (e) => {
                e.preventDefault();
                if (e.target.classList.contains('page-link') && !e.target.parentNode.classList.contains('disabled')) {
                    const page = parseInt(e.target.dataset.page);
                    if (page && page !== this.currentPage) {
                        this.currentPage = page;
                        this.renderTable();
                        this.updatePagination();
                    }
                }
            });
        }
    }
    
    renderTable() {
        const tbody = this.table.querySelector('tbody');
        tbody.innerHTML = '';
        
        let dataToShow = this.filteredData;
        
        if (this.options.pagination) {
            const startIndex = (this.currentPage - 1) * this.options.pageSize;
            const endIndex = startIndex + this.options.pageSize;
            dataToShow = this.filteredData.slice(startIndex, endIndex);
        }
        
        dataToShow.forEach(row => {
            tbody.appendChild(row.element);
        });
        
        if (dataToShow.length === 0) {
            const noDataRow = document.createElement('tr');
            const noDataCell = document.createElement('td');
            noDataCell.colSpan = this.table.querySelectorAll('th').length;
            noDataCell.textContent = 'لا توجد بيانات للعرض';
            noDataCell.className = 'text-center text-muted py-4';
            noDataRow.appendChild(noDataCell);
            tbody.appendChild(noDataRow);
        }
    }
}

/**
 * Modal Component
 * مكون النافذة المنبثقة
 */
class Modal {
    constructor(modalElement, options = {}) {
        this.modal = modalElement;
        this.options = {
            backdrop: true,
            keyboard: true,
            focus: true,
            ...options
        };
        
        this.isOpen = false;
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setupKeyboardNavigation();
    }
    
    setupEventListeners() {
        // Close button
        const closeButtons = this.modal.querySelectorAll('[data-dismiss="modal"]');
        closeButtons.forEach(button => {
            button.addEventListener('click', () => this.hide());
        });
        
        // Backdrop click
        if (this.options.backdrop) {
            this.modal.addEventListener('click', (e) => {
                if (e.target === this.modal) {
                    this.hide();
                }
            });
        }
    }
    
    setupKeyboardNavigation() {
        if (this.options.keyboard) {
            document.addEventListener('keydown', (e) => {
                if (this.isOpen && e.key === 'Escape') {
                    this.hide();
                }
            });
        }
    }
    
    show() {
        this.isOpen = true;
        this.modal.style.display = 'block';
        this.modal.classList.add('show');
        document.body.classList.add('modal-open');
        
        if (this.options.focus) {
            this.modal.focus();
        }
        
        // Dispatch event
        this.modal.dispatchEvent(new CustomEvent('modal:show'));
    }
    
    hide() {
        this.isOpen = false;
        this.modal.classList.remove('show');
        
        setTimeout(() => {
            this.modal.style.display = 'none';
            document.body.classList.remove('modal-open');
        }, 300);
        
        // Dispatch event
        this.modal.dispatchEvent(new CustomEvent('modal:hide'));
    }
    
    toggle() {
        if (this.isOpen) {
            this.hide();
        } else {
            this.show();
        }
    }
}

/**
 * Toast Notification Component
 * مكون إشعارات التوست
 */
class Toast {
    constructor(options = {}) {
        this.options = {
            title: '',
            message: '',
            type: 'info', // success, warning, error, info
            duration: 5000,
            position: 'top-left', // top-left, top-right, bottom-left, bottom-right
            closable: true,
            ...options
        };
        
        this.element = null;
        this.init();
    }
    
    init() {
        this.createElement();
        this.setupContainer();
        this.show();
    }
    
    createElement() {
        this.element = document.createElement('div');
        this.element.className = `toast toast-${this.options.type}`;
        
        const iconMap = {
            success: 'fas fa-check-circle',
            warning: 'fas fa-exclamation-triangle',
            error: 'fas fa-times-circle',
            info: 'fas fa-info-circle'
        };
        
        this.element.innerHTML = `
            <div class="toast-content">
                <div class="toast-icon">
                    <i class="${iconMap[this.options.type]}"></i>
                </div>
                <div class="toast-body">
                    ${this.options.title ? `<div class="toast-title">${this.options.title}</div>` : ''}
                    <div class="toast-message">${this.options.message}</div>
                </div>
                ${this.options.closable ? '<button class="toast-close" aria-label="إغلاق"><i class="fas fa-times"></i></button>' : ''}
            </div>
            <div class="toast-progress"></div>
        `;
        
        if (this.options.closable) {
            this.element.querySelector('.toast-close').addEventListener('click', () => this.hide());
        }
    }
    
    setupContainer() {
        let container = document.querySelector(`.toast-container.${this.options.position}`);
        if (!container) {
            container = document.createElement('div');
            container.className = `toast-container ${this.options.position}`;
            document.body.appendChild(container);
        }
        this.container = container;
    }
    
    show() {
        this.container.appendChild(this.element);
        
        // Trigger animation
        setTimeout(() => {
            this.element.classList.add('show');
        }, 10);
        
        // Auto hide
        if (this.options.duration > 0) {
            const progressBar = this.element.querySelector('.toast-progress');
            progressBar.style.animationDuration = `${this.options.duration}ms`;
            
            this.timeout = setTimeout(() => {
                this.hide();
            }, this.options.duration);
        }
    }
    
    hide() {
        if (this.timeout) {
            clearTimeout(this.timeout);
        }
        
        this.element.classList.remove('show');
        this.element.classList.add('hide');
        
        setTimeout(() => {
            if (this.element.parentNode) {
                this.element.parentNode.removeChild(this.element);
            }
        }, 300);
    }
    
    static success(message, options = {}) {
        return new Toast({ ...options, message, type: 'success' });
    }
    
    static warning(message, options = {}) {
        return new Toast({ ...options, message, type: 'warning' });
    }
    
    static error(message, options = {}) {
        return new Toast({ ...options, message, type: 'error' });
    }
    
    static info(message, options = {}) {
        return new Toast({ ...options, message, type: 'info' });
    }
}

/**
 * Loading Component
 * مكون التحميل
 */
class Loading {
    constructor(options = {}) {
        this.options = {
            target: document.body,
            message: 'جاري التحميل...',
            spinner: true,
            overlay: true,
            ...options
        };
        
        this.element = null;
        this.isVisible = false;
    }
    
    show() {
        if (this.isVisible) return;
        
        this.createElement();
        this.options.target.appendChild(this.element);
        
        setTimeout(() => {
            this.element.classList.add('show');
        }, 10);
        
        this.isVisible = true;
    }
    
    hide() {
        if (!this.isVisible || !this.element) return;
        
        this.element.classList.remove('show');
        
        setTimeout(() => {
            if (this.element.parentNode) {
                this.element.parentNode.removeChild(this.element);
            }
            this.element = null;
        }, 300);
        
        this.isVisible = false;
    }
    
    createElement() {
        this.element = document.createElement('div');
        this.element.className = 'loading-overlay-enhanced';
        
        let content = '';
        if (this.options.spinner) {
            content += '<div class="loading-spinner-enhanced"></div>';
        }
        if (this.options.message) {
            content += `<div class="loading-message">${this.options.message}</div>`;
        }
        
        this.element.innerHTML = `<div class="loading-content">${content}</div>`;
    }
    
    static show(options = {}) {
        const loading = new Loading(options);
        loading.show();
        return loading;
    }
}

/**
 * Dropdown Component
 * مكون القائمة المنسدلة
 */
class Dropdown {
    constructor(triggerElement, options = {}) {
        this.trigger = triggerElement;
        this.options = {
            placement: 'bottom-start',
            offset: [0, 8],
            ...options
        };
        
        this.dropdown = null;
        this.isOpen = false;
        this.init();
    }
    
    init() {
        this.findDropdown();
        this.setupEventListeners();
    }
    
    findDropdown() {
        const dropdownId = this.trigger.getAttribute('data-dropdown');
        if (dropdownId) {
            this.dropdown = document.getElementById(dropdownId);
        } else {
            this.dropdown = this.trigger.nextElementSibling;
        }
        
        if (this.dropdown) {
            this.dropdown.classList.add('dropdown-menu');
        }
    }
    
    setupEventListeners() {
        this.trigger.addEventListener('click', (e) => {
            e.preventDefault();
            this.toggle();
        });
        
        document.addEventListener('click', (e) => {
            if (!this.trigger.contains(e.target) && !this.dropdown.contains(e.target)) {
                this.hide();
            }
        });
        
        document.addEventListener('keydown', (e) => {
            if (this.isOpen && e.key === 'Escape') {
                this.hide();
            }
        });
    }
    
    show() {
        if (this.isOpen) return;
        
        this.dropdown.classList.add('show');
        this.trigger.setAttribute('aria-expanded', 'true');
        this.isOpen = true;
        
        // Position dropdown
        this.position();
    }
    
    hide() {
        if (!this.isOpen) return;
        
        this.dropdown.classList.remove('show');
        this.trigger.setAttribute('aria-expanded', 'false');
        this.isOpen = false;
    }
    
    toggle() {
        if (this.isOpen) {
            this.hide();
        } else {
            this.show();
        }
    }
    
    position() {
        const triggerRect = this.trigger.getBoundingClientRect();
        const dropdownRect = this.dropdown.getBoundingClientRect();
        
        let top = triggerRect.bottom + this.options.offset[1];
        let left = triggerRect.left + this.options.offset[0];
        
        // Adjust if dropdown goes off screen
        if (left + dropdownRect.width > window.innerWidth) {
            left = triggerRect.right - dropdownRect.width;
        }
        
        if (top + dropdownRect.height > window.innerHeight) {
            top = triggerRect.top - dropdownRect.height - this.options.offset[1];
        }
        
        this.dropdown.style.position = 'fixed';
        this.dropdown.style.top = `${top}px`;
        this.dropdown.style.left = `${left}px`;
        this.dropdown.style.zIndex = '1050';
    }
}

/**
 * Form Validation Component
 * مكون التحقق من النماذج
 */
class FormValidator {
    constructor(formElement, options = {}) {
        this.form = formElement;
        this.options = {
            validateOnSubmit: true,
            validateOnBlur: true,
            validateOnInput: false,
            showErrors: true,
            ...options
        };
        
        this.rules = {};
        this.errors = {};
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.parseRules();
    }
    
    setupEventListeners() {
        if (this.options.validateOnSubmit) {
            this.form.addEventListener('submit', (e) => {
                if (!this.validate()) {
                    e.preventDefault();
                }
            });
        }
        
        if (this.options.validateOnBlur) {
            this.form.addEventListener('blur', (e) => {
                if (e.target.matches('input, select, textarea')) {
                    this.validateField(e.target);
                }
            }, true);
        }
        
        if (this.options.validateOnInput) {
            this.form.addEventListener('input', (e) => {
                if (e.target.matches('input, select, textarea')) {
                    this.validateField(e.target);
                }
            });
        }
    }
    
    parseRules() {
        const fields = this.form.querySelectorAll('[data-rules]');
        fields.forEach(field => {
            const rulesString = field.getAttribute('data-rules');
            this.rules[field.name] = this.parseRuleString(rulesString);
        });
    }
    
    parseRuleString(rulesString) {
        const rules = {};
        const rulePairs = rulesString.split('|');
        
        rulePairs.forEach(pair => {
            const [rule, value] = pair.split(':');
            rules[rule] = value || true;
        });
        
        return rules;
    }
    
    validate() {
        this.errors = {};
        let isValid = true;
        
        Object.keys(this.rules).forEach(fieldName => {
            const field = this.form.querySelector(`[name="${fieldName}"]`);
            if (field && !this.validateField(field)) {
                isValid = false;
            }
        });
        
        return isValid;
    }
    
    validateField(field) {
        const fieldName = field.name;
        const rules = this.rules[fieldName];
        const value = field.value.trim();
        
        if (!rules) return true;
        
        let isValid = true;
        const errors = [];
        
        // Required validation
        if (rules.required && !value) {
            errors.push('هذا الحقل مطلوب');
            isValid = false;
        }
        
        // Only validate other rules if field has value
        if (value) {
            // Min length validation
            if (rules.min && value.length < parseInt(rules.min)) {
                errors.push(`يجب أن يكون الحد الأدنى ${rules.min} أحرف`);
                isValid = false;
            }
            
            // Max length validation
            if (rules.max && value.length > parseInt(rules.max)) {
                errors.push(`يجب أن يكون الحد الأقصى ${rules.max} أحرف`);
                isValid = false;
            }
            
            // Email validation
            if (rules.email && !this.isValidEmail(value)) {
                errors.push('يرجى إدخال بريد إلكتروني صحيح');
                isValid = false;
            }
            
            // Number validation
            if (rules.numeric && !this.isNumeric(value)) {
                errors.push('يجب أن يكون رقماً');
                isValid = false;
            }
            
            // Pattern validation
            if (rules.pattern && !new RegExp(rules.pattern).test(value)) {
                errors.push('التنسيق غير صحيح');
                isValid = false;
            }
        }
        
        // Update field state
        this.updateFieldState(field, isValid, errors);
        
        if (!isValid) {
            this.errors[fieldName] = errors;
        }
        
        return isValid;
    }
    
    updateFieldState(field, isValid, errors) {
        field.classList.remove('is-valid', 'is-invalid');
        
        if (isValid) {
            field.classList.add('is-valid');
        } else {
            field.classList.add('is-invalid');
        }
        
        if (this.options.showErrors) {
            this.showFieldErrors(field, errors);
        }
    }
    
    showFieldErrors(field, errors) {
        // Remove existing error messages
        const existingError = field.parentNode.querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }
        
        if (errors.length > 0) {
            const errorElement = document.createElement('div');
            errorElement.className = 'invalid-feedback';
            errorElement.textContent = errors[0]; // Show first error
            field.parentNode.appendChild(errorElement);
        }
    }
    
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    
    isNumeric(value) {
        return !isNaN(value) && !isNaN(parseFloat(value));
    }
    
    getErrors() {
        return this.errors;
    }
    
    clearErrors() {
        this.errors = {};
        const fields = this.form.querySelectorAll('.is-invalid');
        fields.forEach(field => {
            field.classList.remove('is-invalid');
            const errorElement = field.parentNode.querySelector('.invalid-feedback');
            if (errorElement) {
                errorElement.remove();
            }
        });
    }
}

/**
 * Initialize components when DOM is ready
 */
document.addEventListener('DOMContentLoaded', () => {
    // Initialize enhanced tables
    document.querySelectorAll('.table-enhanced').forEach(table => {
        new EnhancedTable(table, {
            sortable: true,
            searchable: true,
            pagination: table.dataset.pagination === 'true'
        });
    });
    
    // Initialize modals
    document.querySelectorAll('.modal').forEach(modal => {
        new Modal(modal);
    });
    
    // Initialize dropdowns
    document.querySelectorAll('[data-toggle="dropdown"]').forEach(trigger => {
        new Dropdown(trigger);
    });
    
    // Initialize form validation
    document.querySelectorAll('form[data-validate]').forEach(form => {
        new FormValidator(form);
    });
    
    // Modal triggers
    document.addEventListener('click', (e) => {
        const trigger = e.target.closest('[data-toggle="modal"]');
        if (trigger) {
            e.preventDefault();
            const targetSelector = trigger.getAttribute('data-target');
            const modal = document.querySelector(targetSelector);
            if (modal && modal.modalInstance) {
                modal.modalInstance.show();
            }
        }
    });
});

// Make components globally available
window.EnhancedTable = EnhancedTable;
window.Modal = Modal;
window.Toast = Toast;
window.Loading = Loading;
window.Dropdown = Dropdown;
window.FormValidator = FormValidator;
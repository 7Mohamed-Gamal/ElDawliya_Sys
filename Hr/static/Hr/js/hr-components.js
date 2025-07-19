/**
 * HR Components JavaScript
 * Interactive components for HR management system
 */

(function() {
    'use strict';

    // Utility functions
    const utils = {
        // Get element by selector
        $(selector) {
            return document.querySelector(selector);
        },

        // Get all elements by selector
        $$(selector) {
            return document.querySelectorAll(selector);
        },

        // Add event listener
        on(element, event, handler) {
            if (typeof element === 'string') {
                element = this.$(element);
            }
            if (element) {
                element.addEventListener(event, handler);
            }
        },

        // Remove class from element
        removeClass(element, className) {
            if (typeof element === 'string') {
                element = this.$(element);
            }
            if (element) {
                element.classList.remove(className);
            }
        },

        // Add class to element
        addClass(element, className) {
            if (typeof element === 'string') {
                element = this.$(element);
            }
            if (element) {
                element.classList.add(className);
            }
        },

        // Toggle class on element
        toggleClass(element, className) {
            if (typeof element === 'string') {
                element = this.$(element);
            }
            if (element) {
                element.classList.toggle(className);
            }
        },

        // Check if element has class
        hasClass(element, className) {
            if (typeof element === 'string') {
                element = this.$(element);
            }
            return element ? element.classList.contains(className) : false;
        },

        // Create element
        createElement(tag, attributes = {}, content = '') {
            const element = document.createElement(tag);
            
            Object.keys(attributes).forEach(key => {
                if (key === 'className') {
                    element.className = attributes[key];
                } else {
                    element.setAttribute(key, attributes[key]);
                }
            });
            
            if (content) {
                element.innerHTML = content;
            }
            
            return element;
        },

        // Show element
        show(element) {
            if (typeof element === 'string') {
                element = this.$(element);
            }
            if (element) {
                element.style.display = '';
                this.removeClass(element, 'hidden');
            }
        },

        // Hide element
        hide(element) {
            if (typeof element === 'string') {
                element = this.$(element);
            }
            if (element) {
                this.addClass(element, 'hidden');
            }
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

        // Format date
        formatDate(date, locale = 'ar-EG') {
            return new Intl.DateTimeFormat(locale).format(new Date(date));
        },

        // Format number
        formatNumber(number, locale = 'ar-EG') {
            return new Intl.NumberFormat(locale).format(number);
        }
    };

    // Modal Component
    class Modal {
        constructor(element) {
            this.element = typeof element === 'string' ? utils.$(element) : element;
            this.backdrop = null;
            this.isOpen = false;
            
            this.init();
        }

        init() {
            if (!this.element) return;

            // Find close buttons
            const closeButtons = this.element.querySelectorAll('[data-modal-close]');
            closeButtons.forEach(btn => {
                utils.on(btn, 'click', () => this.close());
            });

            // Close on backdrop click
            utils.on(this.element, 'click', (e) => {
                if (e.target === this.element) {
                    this.close();
                }
            });

            // Close on escape key
            utils.on(document, 'keydown', (e) => {
                if (e.key === 'Escape' && this.isOpen) {
                    this.close();
                }
            });
        }

        open() {
            if (this.isOpen) return;

            this.isOpen = true;
            utils.show(this.element);
            utils.addClass(document.body, 'modal-open');
            
            // Focus first focusable element
            const focusable = this.element.querySelector('input, button, select, textarea, [tabindex]:not([tabindex="-1"])');
            if (focusable) {
                focusable.focus();
            }

            // Trigger event
            this.element.dispatchEvent(new CustomEvent('modal:open'));
        }

        close() {
            if (!this.isOpen) return;

            this.isOpen = false;
            utils.hide(this.element);
            utils.removeClass(document.body, 'modal-open');

            // Trigger event
            this.element.dispatchEvent(new CustomEvent('modal:close'));
        }

        static init() {
            // Initialize all modals
            utils.$$('.modal-backdrop').forEach(modal => {
                new Modal(modal);
            });

            // Handle modal triggers
            utils.$$('[data-modal-target]').forEach(trigger => {
                utils.on(trigger, 'click', (e) => {
                    e.preventDefault();
                    const targetId = trigger.getAttribute('data-modal-target');
                    const modal = utils.$(targetId);
                    if (modal && modal.modalInstance) {
                        modal.modalInstance.open();
                    }
                });
            });
        }
    }

    // Dropdown Component
    class Dropdown {
        constructor(element) {
            this.element = typeof element === 'string' ? utils.$(element) : element;
            this.trigger = this.element.querySelector('[data-dropdown-trigger]');
            this.menu = this.element.querySelector('.dropdown-menu');
            this.isOpen = false;
            
            this.init();
        }

        init() {
            if (!this.element || !this.trigger || !this.menu) return;

            // Toggle on trigger click
            utils.on(this.trigger, 'click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.toggle();
            });

            // Close on outside click
            utils.on(document, 'click', (e) => {
                if (!this.element.contains(e.target) && this.isOpen) {
                    this.close();
                }
            });

            // Close on escape key
            utils.on(document, 'keydown', (e) => {
                if (e.key === 'Escape' && this.isOpen) {
                    this.close();
                }
            });

            // Handle item clicks
            const items = this.menu.querySelectorAll('.dropdown-item');
            items.forEach(item => {
                utils.on(item, 'click', () => {
                    this.close();
                });
            });
        }

        open() {
            if (this.isOpen) return;

            this.isOpen = true;
            utils.addClass(this.element, 'active');
            
            // Position menu
            this.positionMenu();

            // Trigger event
            this.element.dispatchEvent(new CustomEvent('dropdown:open'));
        }

        close() {
            if (!this.isOpen) return;

            this.isOpen = false;
            utils.removeClass(this.element, 'active');

            // Trigger event
            this.element.dispatchEvent(new CustomEvent('dropdown:close'));
        }

        toggle() {
            if (this.isOpen) {
                this.close();
            } else {
                this.open();
            }
        }

        positionMenu() {
            const rect = this.trigger.getBoundingClientRect();
            const menuRect = this.menu.getBoundingClientRect();
            const viewportWidth = window.innerWidth;
            const viewportHeight = window.innerHeight;

            // Reset position
            this.menu.style.left = '';
            this.menu.style.right = '';
            this.menu.style.top = '';
            this.menu.style.bottom = '';

            // Check if menu fits on the right
            if (rect.right + menuRect.width > viewportWidth) {
                this.menu.style.right = '0';
            } else {
                this.menu.style.left = '0';
            }

            // Check if menu fits below
            if (rect.bottom + menuRect.height > viewportHeight) {
                this.menu.style.bottom = '100%';
                this.menu.style.top = 'auto';
            }
        }

        static init() {
            utils.$$('.dropdown').forEach(dropdown => {
                new Dropdown(dropdown);
            });
        }
    }

    // Alert Component
    class Alert {
        constructor(element) {
            this.element = typeof element === 'string' ? utils.$(element) : element;
            this.closeButton = this.element.querySelector('.alert-close');
            
            this.init();
        }

        init() {
            if (!this.element) return;

            if (this.closeButton) {
                utils.on(this.closeButton, 'click', () => this.close());
            }

            // Auto-dismiss after timeout
            const timeout = this.element.getAttribute('data-timeout');
            if (timeout) {
                setTimeout(() => this.close(), parseInt(timeout));
            }
        }

        close() {
            this.element.style.opacity = '0';
            this.element.style.transform = 'translateY(-10px)';
            
            setTimeout(() => {
                this.element.remove();
            }, 300);

            // Trigger event
            this.element.dispatchEvent(new CustomEvent('alert:close'));
        }

        static show(message, type = 'primary', timeout = 5000) {
            const alertContainer = utils.$('#alert-container') || document.body;
            
            const alert = utils.createElement('div', {
                className: `alert alert-${type} alert-dismissible`,
                'data-timeout': timeout
            }, `
                <div class="alert-title">${message}</div>
                <button type="button" class="alert-close">&times;</button>
            `);

            alertContainer.appendChild(alert);
            new Alert(alert);

            return alert;
        }

        static init() {
            utils.$$('.alert-dismissible').forEach(alert => {
                new Alert(alert);
            });
        }
    }

    // Form Validation
    class FormValidator {
        constructor(form) {
            this.form = typeof form === 'string' ? utils.$(form) : form;
            this.rules = {};
            this.errors = {};
            
            this.init();
        }

        init() {
            if (!this.form) return;

            // Parse validation rules from data attributes
            const inputs = this.form.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                const rules = this.parseRules(input);
                if (Object.keys(rules).length > 0) {
                    this.rules[input.name] = rules;
                }

                // Real-time validation
                utils.on(input, 'blur', () => this.validateField(input));
                utils.on(input, 'input', utils.debounce(() => this.validateField(input), 300));
            });

            // Form submission
            utils.on(this.form, 'submit', (e) => {
                if (!this.validate()) {
                    e.preventDefault();
                }
            });
        }

        parseRules(input) {
            const rules = {};
            
            if (input.hasAttribute('required')) {
                rules.required = true;
            }
            
            if (input.hasAttribute('data-min-length')) {
                rules.minLength = parseInt(input.getAttribute('data-min-length'));
            }
            
            if (input.hasAttribute('data-max-length')) {
                rules.maxLength = parseInt(input.getAttribute('data-max-length'));
            }
            
            if (input.type === 'email') {
                rules.email = true;
            }
            
            if (input.hasAttribute('data-pattern')) {
                rules.pattern = new RegExp(input.getAttribute('data-pattern'));
            }

            return rules;
        }

        validateField(input) {
            const rules = this.rules[input.name];
            if (!rules) return true;

            const value = input.value.trim();
            const errors = [];

            // Required validation
            if (rules.required && !value) {
                errors.push('هذا الحقل مطلوب');
            }

            // Min length validation
            if (rules.minLength && value.length < rules.minLength) {
                errors.push(`يجب أن يكون الحد الأدنى ${rules.minLength} أحرف`);
            }

            // Max length validation
            if (rules.maxLength && value.length > rules.maxLength) {
                errors.push(`يجب أن يكون الحد الأقصى ${rules.maxLength} أحرف`);
            }

            // Email validation
            if (rules.email && value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
                errors.push('يرجى إدخال بريد إلكتروني صحيح');
            }

            // Pattern validation
            if (rules.pattern && value && !rules.pattern.test(value)) {
                errors.push('تنسيق غير صحيح');
            }

            // Update UI
            this.updateFieldUI(input, errors);

            // Store errors
            if (errors.length > 0) {
                this.errors[input.name] = errors;
                return false;
            } else {
                delete this.errors[input.name];
                return true;
            }
        }

        updateFieldUI(input, errors) {
            const formGroup = input.closest('.form-group');
            if (!formGroup) return;

            // Remove existing error classes and messages
            utils.removeClass(input, 'error');
            const existingError = formGroup.querySelector('.form-error');
            if (existingError) {
                existingError.remove();
            }

            // Add error state if there are errors
            if (errors.length > 0) {
                utils.addClass(input, 'error');
                
                const errorElement = utils.createElement('div', {
                    className: 'form-error'
                }, errors[0]);
                
                formGroup.appendChild(errorElement);
            }
        }

        validate() {
            const inputs = this.form.querySelectorAll('input, select, textarea');
            let isValid = true;

            inputs.forEach(input => {
                if (!this.validateField(input)) {
                    isValid = false;
                }
            });

            return isValid;
        }

        static init() {
            utils.$$('form[data-validate]').forEach(form => {
                new FormValidator(form);
            });
        }
    }

    // Table Component
    class DataTable {
        constructor(element, options = {}) {
            this.element = typeof element === 'string' ? utils.$(element) : element;
            this.options = {
                sortable: true,
                searchable: true,
                pagination: true,
                pageSize: 10,
                ...options
            };
            
            this.data = [];
            this.filteredData = [];
            this.currentPage = 1;
            this.sortColumn = null;
            this.sortDirection = 'asc';
            
            this.init();
        }

        init() {
            if (!this.element) return;

            this.parseData();
            this.setupSearch();
            this.setupSort();
            this.setupPagination();
            this.render();
        }

        parseData() {
            const rows = this.element.querySelectorAll('tbody tr');
            this.data = Array.from(rows).map(row => {
                const cells = row.querySelectorAll('td');
                return Array.from(cells).map(cell => cell.textContent.trim());
            });
            this.filteredData = [...this.data];
        }

        setupSearch() {
            if (!this.options.searchable) return;

            const searchInput = utils.$(`#${this.element.id}-search`);
            if (searchInput) {
                utils.on(searchInput, 'input', utils.debounce((e) => {
                    this.search(e.target.value);
                }, 300));
            }
        }

        setupSort() {
            if (!this.options.sortable) return;

            const headers = this.element.querySelectorAll('th[data-sortable]');
            headers.forEach((header, index) => {
                utils.addClass(header, 'sortable');
                utils.on(header, 'click', () => this.sort(index));
            });
        }

        setupPagination() {
            if (!this.options.pagination) return;

            const paginationContainer = utils.$(`#${this.element.id}-pagination`);
            if (paginationContainer) {
                this.paginationContainer = paginationContainer;
            }
        }

        search(query) {
            if (!query) {
                this.filteredData = [...this.data];
            } else {
                this.filteredData = this.data.filter(row => 
                    row.some(cell => 
                        cell.toLowerCase().includes(query.toLowerCase())
                    )
                );
            }
            
            this.currentPage = 1;
            this.render();
        }

        sort(columnIndex) {
            if (this.sortColumn === columnIndex) {
                this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
            } else {
                this.sortColumn = columnIndex;
                this.sortDirection = 'asc';
            }

            this.filteredData.sort((a, b) => {
                const aVal = a[columnIndex];
                const bVal = b[columnIndex];
                
                // Try to parse as numbers
                const aNum = parseFloat(aVal);
                const bNum = parseFloat(bVal);
                
                let comparison = 0;
                if (!isNaN(aNum) && !isNaN(bNum)) {
                    comparison = aNum - bNum;
                } else {
                    comparison = aVal.localeCompare(bVal, 'ar');
                }
                
                return this.sortDirection === 'asc' ? comparison : -comparison;
            });

            this.render();
        }

        render() {
            const tbody = this.element.querySelector('tbody');
            if (!tbody) return;

            // Calculate pagination
            const totalPages = Math.ceil(this.filteredData.length / this.options.pageSize);
            const startIndex = (this.currentPage - 1) * this.options.pageSize;
            const endIndex = startIndex + this.options.pageSize;
            const pageData = this.filteredData.slice(startIndex, endIndex);

            // Render rows
            tbody.innerHTML = '';
            pageData.forEach(rowData => {
                const row = utils.createElement('tr');
                rowData.forEach(cellData => {
                    const cell = utils.createElement('td', {}, cellData);
                    row.appendChild(cell);
                });
                tbody.appendChild(row);
            });

            // Update pagination
            if (this.paginationContainer) {
                this.renderPagination(totalPages);
            }

            // Update sort indicators
            this.updateSortIndicators();
        }

        renderPagination(totalPages) {
            if (totalPages <= 1) {
                this.paginationContainer.innerHTML = '';
                return;
            }

            let paginationHTML = '<ul class="pagination">';
            
            // Previous button
            paginationHTML += `
                <li class="pagination-item">
                    <a href="#" class="pagination-link ${this.currentPage === 1 ? 'disabled' : ''}" 
                       data-page="${this.currentPage - 1}">السابق</a>
                </li>
            `;

            // Page numbers
            for (let i = 1; i <= totalPages; i++) {
                if (i === 1 || i === totalPages || (i >= this.currentPage - 2 && i <= this.currentPage + 2)) {
                    paginationHTML += `
                        <li class="pagination-item">
                            <a href="#" class="pagination-link ${i === this.currentPage ? 'active' : ''}" 
                               data-page="${i}">${i}</a>
                        </li>
                    `;
                } else if (i === this.currentPage - 3 || i === this.currentPage + 3) {
                    paginationHTML += '<li class="pagination-item"><span>...</span></li>';
                }
            }

            // Next button
            paginationHTML += `
                <li class="pagination-item">
                    <a href="#" class="pagination-link ${this.currentPage === totalPages ? 'disabled' : ''}" 
                       data-page="${this.currentPage + 1}">التالي</a>
                </li>
            `;

            paginationHTML += '</ul>';
            this.paginationContainer.innerHTML = paginationHTML;

            // Add click handlers
            const links = this.paginationContainer.querySelectorAll('.pagination-link:not(.disabled)');
            links.forEach(link => {
                utils.on(link, 'click', (e) => {
                    e.preventDefault();
                    const page = parseInt(link.getAttribute('data-page'));
                    if (page >= 1 && page <= totalPages) {
                        this.currentPage = page;
                        this.render();
                    }
                });
            });
        }

        updateSortIndicators() {
            const headers = this.element.querySelectorAll('th[data-sortable]');
            headers.forEach((header, index) => {
                header.classList.remove('sort-asc', 'sort-desc');
                if (index === this.sortColumn) {
                    header.classList.add(`sort-${this.sortDirection}`);
                }
            });
        }

        static init() {
            utils.$$('table[data-table]').forEach(table => {
                const options = JSON.parse(table.getAttribute('data-table') || '{}');
                new DataTable(table, options);
            });
        }
    }

    // Toast Notifications
    class Toast {
        static show(message, type = 'success', duration = 5000) {
            const toastContainer = utils.$('#toast-container') || this.createContainer();
            
            const toast = utils.createElement('div', {
                className: `alert alert-${type} toast-notification`,
                style: 'margin-bottom: 10px; opacity: 0; transform: translateX(100%); transition: all 0.3s ease;'
            }, `
                <div>${message}</div>
                <button type="button" class="alert-close">&times;</button>
            `);

            toastContainer.appendChild(toast);

            // Animate in
            setTimeout(() => {
                toast.style.opacity = '1';
                toast.style.transform = 'translateX(0)';
            }, 10);

            // Auto remove
            setTimeout(() => {
                this.remove(toast);
            }, duration);

            // Manual close
            const closeBtn = toast.querySelector('.alert-close');
            utils.on(closeBtn, 'click', () => this.remove(toast));

            return toast;
        }

        static remove(toast) {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }

        static createContainer() {
            const container = utils.createElement('div', {
                id: 'toast-container',
                style: 'position: fixed; top: 20px; left: 20px; z-index: 9999; max-width: 400px;'
            });
            
            document.body.appendChild(container);
            return container;
        }
    }

    // Initialize all components when DOM is ready
    function init() {
        Modal.init();
        Dropdown.init();
        Alert.init();
        FormValidator.init();
        DataTable.init();
    }

    // Auto-initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Expose components globally
    window.HRComponents = {
        Modal,
        Dropdown,
        Alert,
        FormValidator,
        DataTable,
        Toast,
        utils
    };

})();
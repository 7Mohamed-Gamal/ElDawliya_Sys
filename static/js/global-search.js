/**
 * Global Search System for ElDawliya Management System
 * Provides unified search functionality across all modules
 */

class GlobalSearchManager {
    constructor() {
        this.searchInput = null;
        this.searchResults = null;
        this.searchOverlay = null;
        this.searchTimeout = null;
        this.currentModule = null;
        this.isSearchActive = false;
        
        this.init();
    }

    init() {
        this.createSearchInterface();
        this.bindEvents();
        this.detectCurrentModule();
    }

    createSearchInterface() {
        // Create global search overlay
        this.searchOverlay = document.createElement('div');
        this.searchOverlay.className = 'global-search-overlay hidden';
        this.searchOverlay.innerHTML = `
            <div class="global-search-container">
                <div class="global-search-header">
                    <div class="search-input-wrapper">
                        <i class="fas fa-search search-icon"></i>
                        <input type="text" 
                               class="global-search-input" 
                               placeholder="البحث في جميع أنحاء النظام..."
                               autocomplete="off">
                        <button class="search-close-btn" type="button">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="search-filters">
                        <select class="search-module-filter">
                            <option value="">جميع الوحدات</option>
                            <option value="hr">الموارد البشرية</option>
                            <option value="inventory">المخزون</option>
                            <option value="tasks">المهام</option>
                            <option value="meetings">الاجتماعات</option>
                            <option value="purchase_orders">طلبات الشراء</option>
                        </select>
                    </div>
                </div>
                <div class="global-search-results">
                    <div class="search-loading hidden">
                        <div class="loading-spinner"></div>
                        <span>جاري البحث...</span>
                    </div>
                    <div class="search-results-content"></div>
                    <div class="search-no-results hidden">
                        <i class="fas fa-search"></i>
                        <p>لا توجد نتائج مطابقة</p>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(this.searchOverlay);
        
        this.searchInput = this.searchOverlay.querySelector('.global-search-input');
        this.searchResults = this.searchOverlay.querySelector('.search-results-content');
    }

    bindEvents() {
        // Global keyboard shortcut (Ctrl+K or Ctrl+/)
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && (e.key === 'k' || e.key === '/')) {
                e.preventDefault();
                this.openSearch();
            }

            if (e.key === 'Escape' && this.isSearchActive) {
                this.closeSearch();
            }
        });

        // Search trigger button
        const searchTrigger = document.querySelector('.global-search-trigger');
        if (searchTrigger) {
            searchTrigger.addEventListener('click', () => {
                this.openSearch();
            });
        }

        // Search input events
        this.searchInput.addEventListener('input', (e) => {
            this.handleSearchInput(e.target.value);
        });

        // Close button
        this.searchOverlay.querySelector('.search-close-btn').addEventListener('click', () => {
            this.closeSearch();
        });

        // Overlay click to close
        this.searchOverlay.addEventListener('click', (e) => {
            if (e.target === this.searchOverlay) {
                this.closeSearch();
            }
        });

        // Module filter change
        this.searchOverlay.querySelector('.search-module-filter').addEventListener('change', (e) => {
            if (this.searchInput.value.trim()) {
                this.performSearch(this.searchInput.value.trim(), e.target.value);
            }
        });
    }

    detectCurrentModule() {
        const path = window.location.pathname;
        if (path.includes('/hr/')) this.currentModule = 'hr';
        else if (path.includes('/inventory/')) this.currentModule = 'inventory';
        else if (path.includes('/tasks/')) this.currentModule = 'tasks';
        else if (path.includes('/meetings/')) this.currentModule = 'meetings';
        else if (path.includes('/purchase_orders/')) this.currentModule = 'purchase_orders';
    }

    openSearch() {
        this.searchOverlay.classList.remove('hidden');
        this.searchInput.focus();
        this.isSearchActive = true;
        
        // Set default module filter to current module
        if (this.currentModule) {
            this.searchOverlay.querySelector('.search-module-filter').value = this.currentModule;
        }
    }

    closeSearch() {
        this.searchOverlay.classList.add('hidden');
        this.searchInput.value = '';
        this.searchResults.innerHTML = '';
        this.isSearchActive = false;
        this.hideLoading();
        this.hideNoResults();
    }

    handleSearchInput(query) {
        clearTimeout(this.searchTimeout);
        
        if (query.length < 2) {
            this.searchResults.innerHTML = '';
            this.hideLoading();
            this.hideNoResults();
            return;
        }

        this.searchTimeout = setTimeout(() => {
            const moduleFilter = this.searchOverlay.querySelector('.search-module-filter').value;
            this.performSearch(query, moduleFilter);
        }, 300);
    }

    async performSearch(query, module = '') {
        this.showLoading();
        this.hideNoResults();

        try {
            const response = await fetch('/api/global-search/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    query: query,
                    module: module,
                    limit: 20
                })
            });

            if (!response.ok) {
                throw new Error('Search request failed');
            }

            const data = await response.json();
            this.displayResults(data.results);
            
        } catch (error) {
            console.error('Search error:', error);
            this.displayError('حدث خطأ أثناء البحث');
        } finally {
            this.hideLoading();
        }
    }

    displayResults(results) {
        if (!results || results.length === 0) {
            this.showNoResults();
            return;
        }

        const groupedResults = this.groupResultsByModule(results);
        let html = '';

        for (const [module, items] of Object.entries(groupedResults)) {
            html += `
                <div class="search-module-group">
                    <div class="search-module-header">
                        <i class="${this.getModuleIcon(module)}"></i>
                        <span>${this.getModuleName(module)}</span>
                        <span class="result-count">${items.length}</span>
                    </div>
                    <div class="search-module-results">
                        ${items.map(item => this.renderResultItem(item)).join('')}
                    </div>
                </div>
            `;
        }

        this.searchResults.innerHTML = html;
        this.bindResultEvents();
    }

    groupResultsByModule(results) {
        return results.reduce((groups, result) => {
            const module = result.module || 'other';
            if (!groups[module]) groups[module] = [];
            groups[module].push(result);
            return groups;
        }, {});
    }

    renderResultItem(item) {
        return `
            <div class="search-result-item" data-url="${item.url}">
                <div class="result-icon">
                    <i class="${item.icon || 'fas fa-file'}"></i>
                </div>
                <div class="result-content">
                    <div class="result-title">${item.title}</div>
                    <div class="result-description">${item.description || ''}</div>
                    <div class="result-meta">
                        ${item.meta ? item.meta.map(m => `<span class="meta-item">${m}</span>`).join('') : ''}
                    </div>
                </div>
                <div class="result-actions">
                    <i class="fas fa-arrow-left"></i>
                </div>
            </div>
        `;
    }

    bindResultEvents() {
        this.searchResults.querySelectorAll('.search-result-item').forEach(item => {
            item.addEventListener('click', () => {
                const url = item.dataset.url;
                if (url) {
                    window.location.href = url;
                }
            });
        });
    }

    getModuleIcon(module) {
        const icons = {
            hr: 'fas fa-users',
            inventory: 'fas fa-warehouse',
            tasks: 'fas fa-tasks',
            meetings: 'fas fa-calendar-alt',
            purchase_orders: 'fas fa-shopping-cart',
            other: 'fas fa-folder'
        };
        return icons[module] || icons.other;
    }

    getModuleName(module) {
        const names = {
            hr: 'الموارد البشرية',
            inventory: 'المخزون',
            tasks: 'المهام',
            meetings: 'الاجتماعات',
            purchase_orders: 'طلبات الشراء',
            other: 'أخرى'
        };
        return names[module] || names.other;
    }

    showLoading() {
        this.searchOverlay.querySelector('.search-loading').classList.remove('hidden');
    }

    hideLoading() {
        this.searchOverlay.querySelector('.search-loading').classList.add('hidden');
    }

    showNoResults() {
        this.searchOverlay.querySelector('.search-no-results').classList.remove('hidden');
    }

    hideNoResults() {
        this.searchOverlay.querySelector('.search-no-results').classList.add('hidden');
    }

    displayError(message) {
        this.searchResults.innerHTML = `
            <div class="search-error">
                <i class="fas fa-exclamation-triangle"></i>
                <p>${message}</p>
            </div>
        `;
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }
}

// Initialize global search when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.globalSearch = new GlobalSearchManager();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GlobalSearchManager;
}

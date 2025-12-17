/**
 * Enhanced Search Component for Module-Specific Pages
 * Provides advanced search functionality with filters, suggestions, and real-time results
 */

class EnhancedSearchComponent {
    constructor(options = {}) {
        this.container = options.container || document.querySelector('.enhanced-search-container');
        this.searchInput = options.searchInput || this.container?.querySelector('.enhanced-search-input');
        this.resultsContainer = options.resultsContainer || this.container?.querySelector('.search-results-container');
        this.filtersContainer = options.filtersContainer || this.container?.querySelector('.search-filters-container');
        
        // Configuration
        this.config = {
            apiEndpoint: options.apiEndpoint || '/api/search/',
            debounceDelay: options.debounceDelay || 300,
            minSearchLength: options.minSearchLength || 2,
            maxResults: options.maxResults || 20,
            enableFilters: options.enableFilters !== false,
            enableSuggestions: options.enableSuggestions !== false,
            enableHistory: options.enableHistory !== false,
            ...options.config
        };

        // State
        this.searchTimeout = null;
        this.currentQuery = '';
        this.currentFilters = {};
        this.searchHistory = this.loadSearchHistory();
        this.isLoading = false;

        this.init();
    }

    init() {
        if (!this.container || !this.searchInput) {
            console.warn('Enhanced search: Required elements not found');
            return;
        }

        this.createSearchInterface();
        this.bindEvents();
        this.loadSavedFilters();
    }

    createSearchInterface() {
        // Add search suggestions dropdown
        if (this.config.enableSuggestions) {
            const suggestionsDropdown = document.createElement('div');
            suggestionsDropdown.className = 'search-suggestions-dropdown hidden';
            this.searchInput.parentNode.appendChild(suggestionsDropdown);
            this.suggestionsDropdown = suggestionsDropdown;
        }

        // Add loading indicator
        const loadingIndicator = document.createElement('div');
        loadingIndicator.className = 'search-loading-indicator hidden';
        loadingIndicator.innerHTML = `
            <div class="loading-spinner"></div>
            <span>جاري البحث...</span>
        `;
        this.searchInput.parentNode.appendChild(loadingIndicator);
        this.loadingIndicator = loadingIndicator;

        // Add clear button
        const clearButton = document.createElement('button');
        clearButton.className = 'search-clear-btn hidden';
        clearButton.type = 'button';
        clearButton.innerHTML = '<i class="fas fa-times"></i>';
        clearButton.setAttribute('aria-label', 'مسح البحث');
        this.searchInput.parentNode.appendChild(clearButton);
        this.clearButton = clearButton;

        // Add search history dropdown
        if (this.config.enableHistory) {
            const historyDropdown = document.createElement('div');
            historyDropdown.className = 'search-history-dropdown hidden';
            this.searchInput.parentNode.appendChild(historyDropdown);
            this.historyDropdown = historyDropdown;
        }
    }

    bindEvents() {
        // Search input events
        this.searchInput.addEventListener('input', (e) => {
            this.handleSearchInput(e.target.value);
        });

        this.searchInput.addEventListener('focus', () => {
            this.showSearchHistory();
        });

        this.searchInput.addEventListener('blur', (e) => {
            // Delay hiding to allow clicking on suggestions
            setTimeout(() => {
                if (!this.container.contains(document.activeElement)) {
                    this.hideSuggestions();
                    this.hideSearchHistory();
                }
            }, 150);
        });

        // Clear button
        if (this.clearButton) {
            this.clearButton.addEventListener('click', () => {
                this.clearSearch();
            });
        }

        // Keyboard navigation
        this.searchInput.addEventListener('keydown', (e) => {
            this.handleKeyboardNavigation(e);
        });

        // Filter events
        if (this.filtersContainer) {
            this.filtersContainer.addEventListener('change', (e) => {
                if (e.target.matches('select, input[type="checkbox"], input[type="radio"]')) {
                    this.handleFilterChange();
                }
            });
        }
    }

    handleSearchInput(query) {
        clearTimeout(this.searchTimeout);
        this.currentQuery = query.trim();

        // Show/hide clear button
        if (this.clearButton) {
            this.clearButton.classList.toggle('hidden', !this.currentQuery);
        }

        // Hide history when typing
        this.hideSearchHistory();

        if (this.currentQuery.length < this.config.minSearchLength) {
            this.hideSuggestions();
            this.hideLoading();
            if (this.currentQuery.length === 0) {
                this.clearResults();
            }
            return;
        }

        // Show suggestions if enabled
        if (this.config.enableSuggestions) {
            this.showSuggestions();
        }

        // Debounced search
        this.searchTimeout = setTimeout(() => {
            this.performSearch();
        }, this.config.debounceDelay);
    }

    async performSearch() {
        if (this.isLoading) return;

        this.isLoading = true;
        this.showLoading();

        try {
            const searchData = {
                query: this.currentQuery,
                filters: this.currentFilters,
                limit: this.config.maxResults
            };

            const response = await fetch(this.config.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(searchData)
            });

            if (!response.ok) {
                throw new Error(`Search failed: ${response.status}`);
            }

            const data = await response.json();
            this.displayResults(data);
            
            // Save to history
            if (this.config.enableHistory) {
                this.addToSearchHistory(this.currentQuery);
            }

        } catch (error) {
            console.error('Search error:', error);
            this.displayError('حدث خطأ أثناء البحث');
        } finally {
            this.isLoading = false;
            this.hideLoading();
            this.hideSuggestions();
        }
    }

    displayResults(data) {
        if (!this.resultsContainer) return;

        const results = data.results || [];
        
        if (results.length === 0) {
            this.displayNoResults();
            return;
        }

        let html = `
            <div class="search-results-header">
                <div class="results-count">
                    <i class="fas fa-search"></i>
                    <span>تم العثور على ${results.length} نتيجة</span>
                </div>
                <div class="results-actions">
                    <button class="btn btn-sm btn-outline-primary export-results-btn">
                        <i class="fas fa-download"></i>
                        تصدير النتائج
                    </button>
                </div>
            </div>
            <div class="search-results-list">
        `;

        results.forEach(result => {
            html += this.renderResultItem(result);
        });

        html += '</div>';

        // Add pagination if needed
        if (data.pagination) {
            html += this.renderPagination(data.pagination);
        }

        this.resultsContainer.innerHTML = html;
        this.bindResultEvents();
    }

    renderResultItem(result) {
        return `
            <div class="search-result-item" data-id="${result.id}" data-url="${result.url || '#'}">
                <div class="result-checkbox">
                    <input type="checkbox" class="form-check-input" value="${result.id}">
                </div>
                <div class="result-content">
                    <div class="result-header">
                        <div class="result-title">${result.title}</div>
                        <div class="result-meta">
                            ${result.meta ? result.meta.map(m => `<span class="meta-badge">${m}</span>`).join('') : ''}
                        </div>
                    </div>
                    <div class="result-description">${result.description || ''}</div>
                    <div class="result-footer">
                        <div class="result-tags">
                            ${result.tags ? result.tags.map(tag => `<span class="tag">${tag}</span>`).join('') : ''}
                        </div>
                        <div class="result-actions">
                            <button class="btn btn-sm btn-outline-primary view-btn" data-url="${result.url}">
                                <i class="fas fa-eye"></i>
                                عرض
                            </button>
                            ${result.editUrl ? `
                                <button class="btn btn-sm btn-outline-secondary edit-btn" data-url="${result.editUrl}">
                                    <i class="fas fa-edit"></i>
                                    تعديل
                                </button>
                            ` : ''}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    bindResultEvents() {
        // Result item clicks
        this.resultsContainer.querySelectorAll('.search-result-item').forEach(item => {
            item.addEventListener('click', (e) => {
                if (!e.target.matches('input, button, a')) {
                    const url = item.dataset.url;
                    if (url && url !== '#') {
                        window.location.href = url;
                    }
                }
            });
        });

        // Action buttons
        this.resultsContainer.querySelectorAll('.view-btn, .edit-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const url = btn.dataset.url;
                if (url) {
                    window.location.href = url;
                }
            });
        });

        // Export button
        const exportBtn = this.resultsContainer.querySelector('.export-results-btn');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => {
                this.exportResults();
            });
        }
    }

    displayNoResults() {
        if (!this.resultsContainer) return;

        this.resultsContainer.innerHTML = `
            <div class="search-no-results">
                <div class="no-results-icon">
                    <i class="fas fa-search"></i>
                </div>
                <div class="no-results-title">لا توجد نتائج</div>
                <div class="no-results-message">
                    لم يتم العثور على نتائج مطابقة لـ "<strong>${this.currentQuery}</strong>"
                </div>
                <div class="no-results-suggestions">
                    <p>جرب:</p>
                    <ul>
                        <li>التحقق من الإملاء</li>
                        <li>استخدام كلمات مختلفة</li>
                        <li>تقليل عدد الفلاتر</li>
                    </ul>
                </div>
            </div>
        `;
    }

    displayError(message) {
        if (!this.resultsContainer) return;

        this.resultsContainer.innerHTML = `
            <div class="search-error">
                <div class="error-icon">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <div class="error-message">${message}</div>
                <button class="btn btn-primary retry-search-btn">
                    <i class="fas fa-redo"></i>
                    إعادة المحاولة
                </button>
            </div>
        `;

        // Retry button
        const retryBtn = this.resultsContainer.querySelector('.retry-search-btn');
        if (retryBtn) {
            retryBtn.addEventListener('click', () => {
                this.performSearch();
            });
        }
    }

    // Additional methods for search history, suggestions, filters, etc.
    addToSearchHistory(query) {
        if (!query || this.searchHistory.includes(query)) return;
        
        this.searchHistory.unshift(query);
        this.searchHistory = this.searchHistory.slice(0, 10); // Keep last 10 searches
        this.saveSearchHistory();
    }

    loadSearchHistory() {
        try {
            return JSON.parse(localStorage.getItem('eldawliya-search-history') || '[]');
        } catch {
            return [];
        }
    }

    saveSearchHistory() {
        localStorage.setItem('eldawliya-search-history', JSON.stringify(this.searchHistory));
    }

    clearSearch() {
        this.searchInput.value = '';
        this.currentQuery = '';
        this.clearResults();
        this.hideSuggestions();
        this.hideSearchHistory();
        if (this.clearButton) {
            this.clearButton.classList.add('hidden');
        }
    }

    clearResults() {
        if (this.resultsContainer) {
            this.resultsContainer.innerHTML = '';
        }
    }

    showLoading() {
        if (this.loadingIndicator) {
            this.loadingIndicator.classList.remove('hidden');
        }
    }

    hideLoading() {
        if (this.loadingIndicator) {
            this.loadingIndicator.classList.add('hidden');
        }
    }

    showSuggestions() {
        // Implementation for showing search suggestions
    }

    hideSuggestions() {
        if (this.suggestionsDropdown) {
            this.suggestionsDropdown.classList.add('hidden');
        }
    }

    showSearchHistory() {
        // Implementation for showing search history
    }

    hideSearchHistory() {
        if (this.historyDropdown) {
            this.historyDropdown.classList.add('hidden');
        }
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }
}

// Auto-initialize enhanced search components
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.enhanced-search-container').forEach(container => {
        new EnhancedSearchComponent({ container });
    });
});

// Export for manual initialization
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EnhancedSearchComponent;
}

/**
 * نظام البحث المتقدم والذكي - JavaScript
 */

class AdvancedSearchSystem {
    constructor() {
        this.apiEndpoints = {
            search: '/hr/search/api/',
            suggestions: '/hr/search/suggestions/',
            smartSearch: '/hr/search/smart/',
            saveSearch: '/hr/search/save/',
            savedSearches: '/hr/search/saved/',
            executeSaved: '/hr/search/execute/{id}/',
            deleteSaved: '/hr/search/delete/{id}/',
        };
        
        this.settings = {
            suggestionDelay: 300,
            minQueryLength: 2,
            maxSuggestions: 10,
            cacheTimeout: 300000, // 5 دقائق
        };
        
        this.cache = new Map();
        this.suggestionTimer = null;
        this.currentRequest = null;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setupKeyboardShortcuts();
        this.loadSearchHistory();
    }
    
    setupEventListeners() {
        const searchInput = document.getElementById('searchInput');
        const searchForm = document.getElementById('searchForm');
        const suggestionsContainer = document.getElementById('searchSuggestions');
        
        if (searchInput) {
            // البحث التلقائي أثناء الكتابة
            searchInput.addEventListener('input', (e) => {
                this.handleSearchInput(e.target.value);
            });
            
            // إخفاء الاقتراحات عند فقدان التركيز
            searchInput.addEventListener('blur', () => {
                setTimeout(() => {
                    this.hideSuggestions();
                }, 200);
            });
            
            // التنقل بالكيبورد في الاقتراحات
            searchInput.addEventListener('keydown', (e) => {
                this.handleKeyboardNavigation(e);
            });
        }
        
        if (searchForm) {
            searchForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.performSearch();
            });
        }
        
        // معالجة النقر على الاقتراحات
        document.addEventListener('click', (e) => {
            if (e.target.matches('.suggestion-item')) {
                this.selectSuggestion(e.target);
            }
        });
        
        // معالجة تغيير الفلاتر
        document.addEventListener('change', (e) => {
            if (e.target.matches('.filter-control, .content-type-checkbox')) {
                this.handleFilterChange();
            }
        });
    }
    
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + K - التركيز على البحث
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                const searchInput = document.getElementById('searchInput');
                if (searchInput) {
                    searchInput.focus();
                    searchInput.select();
                }
            }
            
            // Escape - إلغاء البحث أو إخفاء الاقتراحات
            if (e.key === 'Escape') {
                this.hideSuggestions();
                if (this.currentRequest) {
                    this.currentRequest.abort();
                    this.currentRequest = null;
                }
            }
        });
    }
    
    handleSearchInput(query) {
        // إلغاء المؤقت السابق
        if (this.suggestionTimer) {
            clearTimeout(this.suggestionTimer);
        }
        
        // إخفاء الاقتراحات للاستعلامات القصيرة
        if (query.length < this.settings.minQueryLength) {
            this.hideSuggestions();
            return;
        }
        
        // تأخير البحث عن الاقتراحات
        this.suggestionTimer = setTimeout(() => {
            this.fetchSuggestions(query);
        }, this.settings.suggestionDelay);
    }
    
    async fetchSuggestions(query) {
        try {
            // التحقق من الكاش
            const cacheKey = `suggestions_${query}`;
            if (this.cache.has(cacheKey)) {
                const cached = this.cache.get(cacheKey);
                if (Date.now() - cached.timestamp < this.settings.cacheTimeout) {
                    this.displaySuggestions(cached.data);
                    return;
                }
            }
            
            const response = await fetch(`${this.apiEndpoints.suggestions}?q=${encodeURIComponent(query)}`, {
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const suggestions = await response.json();
            
            // حفظ في الكاش
            this.cache.set(cacheKey, {
                data: suggestions,
                timestamp: Date.now()
            });
            
            this.displaySuggestions(suggestions);
            
        } catch (error) {
            console.error('Error fetching suggestions:', error);
        }
    }
    
    displaySuggestions(suggestions) {
        const container = document.getElementById('searchSuggestions');
        if (!container || !suggestions.length) {
            this.hideSuggestions();
            return;
        }
        
        container.innerHTML = '';
        
        suggestions.forEach((suggestion, index) => {
            const item = document.createElement('div');
            item.className = 'suggestion-item';
            item.dataset.index = index;
            item.dataset.text = suggestion.text;
            
            item.innerHTML = `
                <div class="suggestion-text">${this.highlightQuery(suggestion.text)}</div>
                <div class="suggestion-type">${this.getSuggestionTypeLabel(suggestion.type)}</div>
            `;
            
            container.appendChild(item);
        });
        
        container.style.display = 'block';
    }
    
    hideSuggestions() {
        const container = document.getElementById('searchSuggestions');
        if (container) {
            container.style.display = 'none';
        }
    }
    
    selectSuggestion(suggestionElement) {
        const text = suggestionElement.dataset.text;
        const searchInput = document.getElementById('searchInput');
        
        if (searchInput && text) {
            searchInput.value = text;
            this.hideSuggestions();
            this.performSearch();
        }
    }
    
    handleKeyboardNavigation(e) {
        const container = document.getElementById('searchSuggestions');
        if (!container || container.style.display === 'none') {
            return;
        }
        
        const items = container.querySelectorAll('.suggestion-item');
        if (!items.length) {
            return;
        }
        
        let currentIndex = -1;
        const activeItem = container.querySelector('.suggestion-item.active');
        if (activeItem) {
            currentIndex = parseInt(activeItem.dataset.index);
        }
        
        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                currentIndex = Math.min(currentIndex + 1, items.length - 1);
                this.highlightSuggestion(items, currentIndex);
                break;
                
            case 'ArrowUp':
                e.preventDefault();
                currentIndex = Math.max(currentIndex - 1, -1);
                this.highlightSuggestion(items, currentIndex);
                break;
                
            case 'Enter':
                e.preventDefault();
                if (currentIndex >= 0 && items[currentIndex]) {
                    this.selectSuggestion(items[currentIndex]);
                } else {
                    this.performSearch();
                }
                break;
                
            case 'Tab':
                if (currentIndex >= 0 && items[currentIndex]) {
                    e.preventDefault();
                    this.selectSuggestion(items[currentIndex]);
                }
                break;
        }
    }
    
    highlightSuggestion(items, index) {
        // إزالة التمييز السابق
        items.forEach(item => item.classList.remove('active'));
        
        // تمييز العنصر الحالي
        if (index >= 0 && items[index]) {
            items[index].classList.add('active');
            items[index].scrollIntoView({ block: 'nearest' });
        }
    }
    
    async performSearch() {
        const formData = new FormData(document.getElementById('searchForm'));
        const query = formData.get('q');
        
        if (!query || !query.trim()) {
            return;
        }
        
        this.showLoading();
        this.hideSuggestions();
        
        try {
            // بناء معاملات البحث
            const params = new URLSearchParams();
            for (const [key, value] of formData.entries()) {
                if (value) {
                    params.append(key, value);
                }
            }
            
            const response = await fetch(`${this.apiEndpoints.search}?${params}`, {
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const results = await response.json();
            this.displayResults(results);
            
            // حفظ في التاريخ
            this.saveToHistory(query, results.total_count);
            
        } catch (error) {
            console.error('Search error:', error);
            this.showError('حدث خطأ أثناء البحث. يرجى المحاولة مرة أخرى.');
        } finally {
            this.hideLoading();
        }
    }
    
    async performSmartSearch(query) {
        this.showLoading();
        
        try {
            const response = await fetch(this.apiEndpoints.smartSearch, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify({
                    query: query,
                    context: this.getSearchContext()
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const results = await response.json();
            this.displayResults(results);
            
            // تحديث حقل البحث إذا تم تحسين الاستعلام
            if (results.enhanced_query && results.enhanced_query !== query) {
                document.getElementById('searchInput').value = results.enhanced_query;
            }
            
        } catch (error) {
            console.error('Smart search error:', error);
            this.showError('حدث خطأ أثناء البحث الذكي. يرجى المحاولة مرة أخرى.');
        } finally {
            this.hideLoading();
        }
    }
    
    displayResults(results) {
        const container = document.getElementById('searchResults');
        const resultsList = document.getElementById('resultsList');
        
        if (!container || !resultsList) {
            return;
        }
        
        // تحديث معلومات النتائج
        this.updateResultsHeader(results);
        
        if (results.results && results.results.length > 0) {
            // عرض النتائج
            resultsList.innerHTML = '';
            
            results.results.forEach(result => {
                const resultElement = this.createResultElement(result);
                resultsList.appendChild(resultElement);
            });
            
            // تحديث التصفح
            this.updatePagination(results);
            
            container.style.display = 'block';
        } else {
            // عرض رسالة عدم وجود نتائج
            this.showNoResults(results);
        }
    }
    
    createResultElement(result) {
        const element = document.createElement('div');
        element.className = 'result-item';
        
        element.innerHTML = `
            <div class="result-header">
                <a href="${result.url}" class="result-title">
                    ${result.title}
                </a>
                <span class="result-type">${result.content_type_name}</span>
            </div>
            
            <div class="result-content">
                ${result.content}...
            </div>
            
            <div class="result-meta">
                <div class="result-date">
                    <i class="fas fa-calendar-alt me-1"></i>
                    ${this.formatDate(result.created_at)}
                </div>
                
                <div class="result-actions">
                    <a href="${result.url}" class="btn btn-sm btn-outline-primary">
                        <i class="fas fa-eye me-1"></i>
                        عرض
                    </a>
                </div>
            </div>
        `;
        
        return element;
    }
    
    updateResultsHeader(results) {
        const countElement = document.querySelector('.results-count');
        const timeElement = document.querySelector('.results-time');
        
        if (countElement) {
            countElement.textContent = `تم العثور على ${results.total_count} نتيجة`;
            if (results.query) {
                countElement.textContent += ` لـ "${results.query}"`;
            }
        }
        
        if (timeElement) {
            timeElement.textContent = `(${results.execution_time.toFixed(3)} ثانية)`;
        }
    }
    
    updatePagination(results) {
        // تحديث التصفح - يمكن تطويره حسب الحاجة
        const paginationContainer = document.querySelector('.pagination-container');
        if (paginationContainer && results.total_pages > 1) {
            // إنشاء روابط التصفح
            this.createPaginationLinks(results, paginationContainer);
        }
    }
    
    showNoResults(results) {
        const container = document.getElementById('searchResults');
        const resultsList = document.getElementById('resultsList');
        
        if (!container || !resultsList) {
            return;
        }
        
        resultsList.innerHTML = `
            <div class="no-results">
                <div class="no-results-icon">
                    <i class="fas fa-search"></i>
                </div>
                <div class="no-results-title">لا توجد نتائج</div>
                <div class="no-results-message">
                    لم يتم العثور على نتائج لـ "${results.query || 'البحث المحدد'}"
                </div>
                ${this.createSuggestionsHTML(results.suggestions)}
            </div>
        `;
        
        container.style.display = 'block';
    }
    
    createSuggestionsHTML(suggestions) {
        if (!suggestions || !suggestions.length) {
            return '';
        }
        
        const suggestionChips = suggestions.map(suggestion => 
            `<a href="?q=${encodeURIComponent(suggestion)}" class="suggestion-chip">${suggestion}</a>`
        ).join('');
        
        return `
            <div class="suggestions-list">
                <strong>جرب البحث عن:</strong>
                ${suggestionChips}
            </div>
        `;
    }
    
    async saveCurrentSearch(formData) {
        try {
            const searchParams = new URLSearchParams(window.location.search);
            const searchData = {
                name: formData.get('name'),
                description: formData.get('description'),
                is_public: formData.get('is_public') === 'on',
                query: searchParams.get('q') || '',
                filters: {},
                content_types: searchParams.getAll('content_types'),
                search_type: 'advanced'
            };
            
            // جمع الفلاتر
            for (const [key, value] of searchParams.entries()) {
                if (key !== 'q' && key !== 'content_types' && value) {
                    searchData.filters[key] = value;
                }
            }
            
            const response = await fetch(this.apiEndpoints.saveSearch, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify(searchData)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (result.success) {
                // إغلاق النافذة المنبثقة
                const modal = bootstrap.Modal.getInstance(document.getElementById('saveSearchModal'));
                modal.hide();
                
                // إظهار رسالة نجاح
                this.showSuccess('تم حفظ البحث بنجاح');
                
                // إعادة تحميل عمليات البحث المحفوظة
                this.loadSavedSearches();
            } else {
                throw new Error(result.error || 'فشل في حفظ البحث');
            }
            
        } catch (error) {
            console.error('Error saving search:', error);
            this.showError('حدث خطأ أثناء حفظ البحث');
        }
    }
    
    async executeSavedSearch(searchId) {
        try {
            const response = await fetch(
                this.apiEndpoints.executeSaved.replace('{id}', searchId),
                {
                    headers: {
                        'X-CSRFToken': this.getCSRFToken(),
                    }
                }
            );
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const results = await response.json();
            this.displayResults(results);
            
            // تحديث النموذج بمعايير البحث
            this.updateFormFromSavedSearch(results.search_criteria);
            
        } catch (error) {
            console.error('Error executing saved search:', error);
            this.showError('حدث خطأ أثناء تنفيذ البحث المحفوظ');
        }
    }
    
    async deleteSavedSearch(searchId) {
        try {
            const response = await fetch(
                this.apiEndpoints.deleteSaved.replace('{id}', searchId),
                {
                    method: 'DELETE',
                    headers: {
                        'X-CSRFToken': this.getCSRFToken(),
                    }
                }
            );
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (result.success) {
                // إزالة العنصر من الواجهة
                const searchElement = document.querySelector(`[data-search-id="${searchId}"]`);
                if (searchElement) {
                    searchElement.remove();
                }
                
                this.showSuccess('تم حذف البحث المحفوظ');
            } else {
                throw new Error(result.error || 'فشل في حذف البحث');
            }
            
        } catch (error) {
            console.error('Error deleting saved search:', error);
            this.showError('حدث خطأ أثناء حذف البحث المحفوظ');
        }
    }
    
    handleFilterChange() {
        // تأخير قصير قبل تطبيق الفلاتر
        setTimeout(() => {
            this.performSearch();
        }, 100);
    }
    
    getSearchContext() {
        return {
            user_department: this.getCurrentUserDepartment(),
            user_company: this.getCurrentUserCompany(),
            current_page: window.location.pathname,
            timestamp: Date.now()
        };
    }
    
    getCurrentUserDepartment() {
        // يمكن الحصول على هذه المعلومات من البيانات المضمنة في الصفحة
        return window.userContext?.department_id || null;
    }
    
    getCurrentUserCompany() {
        // يمكن الحصول على هذه المعلومات من البيانات المضمنة في الصفحة
        return window.userContext?.company_id || null;
    }
    
    saveToHistory(query, resultCount) {
        try {
            const history = JSON.parse(localStorage.getItem('searchHistory') || '[]');
            
            // إضافة البحث الجديد
            history.unshift({
                query: query,
                resultCount: resultCount,
                timestamp: Date.now()
            });
            
            // الاحتفاظ بآخر 50 بحث فقط
            const limitedHistory = history.slice(0, 50);
            
            localStorage.setItem('searchHistory', JSON.stringify(limitedHistory));
        } catch (error) {
            console.error('Error saving search history:', error);
        }
    }
    
    loadSearchHistory() {
        try {
            const history = JSON.parse(localStorage.getItem('searchHistory') || '[]');
            // يمكن استخدام التاريخ لعرض البحثات السابقة
            return history;
        } catch (error) {
            console.error('Error loading search history:', error);
            return [];
        }
    }
    
    async loadSavedSearches() {
        try {
            const response = await fetch(this.apiEndpoints.savedSearches, {
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const savedSearches = await response.json();
            this.displaySavedSearches(savedSearches);
            
        } catch (error) {
            console.error('Error loading saved searches:', error);
        }
    }
    
    displaySavedSearches(savedSearches) {
        const container = document.querySelector('.saved-searches .row');
        if (!container || !savedSearches.length) {
            return;
        }
        
        container.innerHTML = '';
        
        savedSearches.forEach(search => {
            const element = document.createElement('div');
            element.className = 'col-md-6 col-lg-4 mb-2';
            element.innerHTML = `
                <div class="saved-search-item" data-search-id="${search.id}">
                    <div class="saved-search-info">
                        <div class="saved-search-name">${search.name}</div>
                        <div class="saved-search-meta">
                            ${search.usage_count} استخدام • 
                            ${this.formatRelativeTime(search.last_used_at)}
                        </div>
                    </div>
                    <div class="saved-search-actions">
                        <button class="btn btn-sm btn-outline-primary" 
                                onclick="executeSavedSearch('${search.id}')">
                            <i class="fas fa-play"></i>
                        </button>
                        ${search.can_delete ? `
                        <button class="btn btn-sm btn-outline-danger" 
                                onclick="deleteSavedSearch('${search.id}')">
                            <i class="fas fa-trash"></i>
                        </button>
                        ` : ''}
                    </div>
                </div>
            `;
            
            container.appendChild(element);
        });
    }
    
    updateFormFromSavedSearch(criteria) {
        // تحديث حقل البحث
        const searchInput = document.getElementById('searchInput');
        if (searchInput && criteria.query) {
            searchInput.value = criteria.query;
        }
        
        // تحديث الفلاتر
        if (criteria.filters) {
            for (const [key, value] of Object.entries(criteria.filters)) {
                const element = document.querySelector(`[name="${key}"]`);
                if (element) {
                    if (element.type === 'checkbox') {
                        element.checked = value;
                    } else {
                        element.value = value;
                    }
                }
            }
        }
        
        // تحديث أنواع المحتوى
        if (criteria.content_types) {
            const checkboxes = document.querySelectorAll('[name="content_types"]');
            checkboxes.forEach(checkbox => {
                checkbox.checked = criteria.content_types.includes(checkbox.value);
            });
        }
    }
    
    highlightQuery(text) {
        const query = document.getElementById('searchInput').value;
        if (!query || !text) {
            return text;
        }
        
        const words = query.split(/\s+/);
        let highlighted = text;
        
        words.forEach(word => {
            if (word.length > 1) {
                const regex = new RegExp(`(${this.escapeRegex(word)})`, 'gi');
                highlighted = highlighted.replace(regex, '<strong>$1</strong>');
            }
        });
        
        return highlighted;
    }
    
    getSuggestionTypeLabel(type) {
        const labels = {
            'keyword': 'كلمة مفتاحية',
            'phrase': 'عبارة',
            'filter': 'فلتر',
            'correction': 'تصحيح',
            'title': 'عنوان',
            'content': 'محتوى'
        };
        
        return labels[type] || type;
    }
    
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('ar-SA');
    }
    
    formatRelativeTime(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
        
        if (diffDays === 0) {
            return 'اليوم';
        } else if (diffDays === 1) {
            return 'أمس';
        } else if (diffDays < 7) {
            return `${diffDays} أيام مضت`;
        } else if (diffDays < 30) {
            const weeks = Math.floor(diffDays / 7);
            return `${weeks} أسبوع مضى`;
        } else {
            const months = Math.floor(diffDays / 30);
            return `${months} شهر مضى`;
        }
    }
    
    escapeRegex(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }
    
    showLoading() {
        const spinner = document.getElementById('loadingSpinner');
        const results = document.getElementById('searchResults');
        
        if (spinner) {
            spinner.style.display = 'block';
        }
        
        if (results) {
            results.style.display = 'none';
        }
    }
    
    hideLoading() {
        const spinner = document.getElementById('loadingSpinner');
        
        if (spinner) {
            spinner.style.display = 'none';
        }
    }
    
    showSuccess(message) {
        this.showToast(message, 'success');
    }
    
    showError(message) {
        this.showToast(message, 'error');
    }
    
    showToast(message, type = 'info') {
        // إنشاء عنصر التوست
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type === 'success' ? 'success' : 'danger'} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        // إضافة إلى الصفحة
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container position-fixed top-0 start-50 translate-middle-x p-3';
            document.body.appendChild(toastContainer);
        }
        
        toastContainer.appendChild(toast);
        
        // إظهار التوست
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // إزالة التوست بعد الإخفاء
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }
    
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }
}

// تصدير الفئة للاستخدام العام
window.AdvancedSearchSystem = AdvancedSearchSystem;
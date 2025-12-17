/**
 * Direct Filter Enhancer
 * مُحسن الفلترة المباشر
 * 
 * ملف JavaScript مستقل يمكن إضافته مباشرة عبر وسم script في HTML
 * قم بإضافة هذا السطر في نهاية الصفحة قبل الوسم </body> مباشرة:
 * <script src="/static/inventory/js/direct_filter.js"></script>
 */

(function() {
    // تنفيذ عند تحميل الصفحة
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initFilterEnhancements);
    } else {
        initFilterEnhancements();
    }
    
    // تهيئة تحسينات الفلترة
    function initFilterEnhancements() {
        console.log('جاري تهيئة تحسينات الفلترة المباشرة...');
        
        // التحقق من وجود نافذة البحث
        const searchModal = document.getElementById('productSearchModal');
        if (!searchModal) {
            console.log('لا توجد نافذة بحث في هذه الصفحة.');
            return;
        }
        
        // إضافة فلتر وحدة القياس
        addUnitFilter();
        
        // تحسين وظيفة البحث
        enhanceSearchFunction();
        
        // جلب وتحميل وحدات القياس
        loadUnitOptions();
    }
    
    // إضافة فلتر وحدة القياس
    function addUnitFilter() {
        // البحث عن صف الفلاتر
        const filtersRow = document.querySelector('.search-section .row .col-md-12 .row');
        if (!filtersRow) return;
        
        // التحقق من وجود فلتر الوحدة
        if (document.getElementById('modal-unit-filter')) {
            console.log('فلتر الوحدة موجود بالفعل');
            return;
        }
        
        console.log('إضافة فلتر الوحدة...');
        
        // إنشاء فلتر الوحدة
        const unitFilterCol = document.createElement('div');
        unitFilterCol.className = 'col-md-4';
        unitFilterCol.innerHTML = `
            <label for="modal-unit-filter" class="form-label mb-1">الوحدة</label>
            <select id="modal-unit-filter" class="form-select">
                <option value="">كل الوحدات</option>
                <!-- سيتم تحميل الوحدات ديناميكياً -->
            </select>
        `;
        
        // إضافة فلتر الوحدة للصف
        filtersRow.appendChild(unitFilterCol);
        
        // ربط حدث تغيير فلتر الوحدة بوظيفة البحث
        const unitFilter = document.getElementById('modal-unit-filter');
        if (unitFilter) {
            unitFilter.addEventListener('change', function() {
                if (window.searchProducts) window.searchProducts();
            });
            
            console.log('تم إضافة فلتر الوحدة بنجاح');
        }
    }
    
    // تحميل خيارات وحدات القياس
    function loadUnitOptions() {
        console.log('جلب وحدات القياس...');
        
        fetch('/inventory/api/units/')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const unitFilter = document.getElementById('modal-unit-filter');
                    if (!unitFilter) return;
                    
                    // مسح الخيارات الحالية
                    unitFilter.innerHTML = '<option value="">كل الوحدات</option>';
                    
                    // إضافة الوحدات
                    data.units.forEach(unit => {
                        const option = document.createElement('option');
                        option.value = unit.id;
                        option.textContent = unit.name;
                        unitFilter.appendChild(option);
                    });
                    
                    console.log(`تم تحميل ${data.units.length} وحدة قياس`);
                }
            })
            .catch(err => console.error('خطأ في جلب وحدات القياس:', err));
    }
    
    // تحسين وظيفة البحث
    function enhanceSearchFunction() {
        // التأكد من وجود وظيفة البحث الأصلية
        if (!window.searchProducts) {
            console.warn('لم يتم العثور على وظيفة البحث الأصلية.');
            return;
        }
        
        console.log('تحسين وظيفة البحث...');
        
        // حفظ الوظيفة الأصلية
        const originalSearchFunction = window.searchProducts;
        
        // استبدال وظيفة البحث بنسخة محسنة
        window.searchProducts = function() {
            const searchTerm = document.getElementById('modal-search-input').value.trim();
            const categoryId = document.getElementById('modal-category-filter').value;
            const unitId = document.getElementById('modal-unit-filter')?.value || '';
            const stockStatus = document.getElementById('modal-stock-filter').value;
            
            console.log(`البحث: مصطلح="${searchTerm}", تصنيف=${categoryId || 'الكل'}, وحدة=${unitId || 'الكل'}, حالة=${stockStatus || 'الكل'}`);
            
            // إظهار مؤشر التحميل
            document.getElementById('loading-indicator').classList.remove('d-none');
            document.getElementById('no-products-message').classList.add('d-none');
            document.getElementById('modal-products-table').classList.add('d-none');
            
            // جلب البيانات من الخادم
            fetch('/inventory/api/products-search/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({
                    search_term: searchTerm,
                    category_id: categoryId,
                    unit_id: unitId, // إضافة معيار البحث بالوحدة
                    stock_status: stockStatus
                })
            })
            .then(response => response.json())
            .then(data => {
                // إخفاء مؤشر التحميل
                document.getElementById('loading-indicator').classList.add('d-none');
                
                if (data.success && data.products.length > 0) {
                    // تخزين النتائج
                    window.productsCache = data.products;
                    
                    // عرض الجدول
                    document.getElementById('modal-products-table').classList.remove('d-none');
                    
                    // استخدام الدالة الأصلية لملء الجدول
                    if (window.populateProductsTable) {
                        window.populateProductsTable(data.products);
                    }
                    
                    // عرض عدد النتائج
                    showResultsCount(data.products.length);
                } else {
                    // عدم وجود نتائج
                    document.getElementById('no-products-message').classList.remove('d-none');
                    document.getElementById('modal-products-table').classList.add('d-none');
                    
                    // إزالة عداد النتائج
                    removeResultsCount();
                }
            })
            .catch(error => {
                console.error('خطأ في البحث:', error);
                document.getElementById('loading-indicator').classList.add('d-none');
                document.getElementById('no-products-message').classList.remove('d-none');
            });
        };
        
        console.log('تم تحسين وظيفة البحث بنجاح');
    }
    
    // إظهار عدد النتائج
    function showResultsCount(count) {
        // إزالة عداد النتائج السابق
        removeResultsCount();
        
        // إنشاء عنصر عداد النتائج
        const resultsCount = document.createElement('div');
        resultsCount.id = 'results-count';
        resultsCount.className = 'text-muted mt-2';
        resultsCount.innerHTML = `<small>تم العثور على ${count} صنف</small>`;
        
        // إضافة عداد النتائج
        const tableContainer = document.querySelector('.table-responsive');
        if (tableContainer) {
            tableContainer.after(resultsCount);
        }
    }
    
    // إزالة عداد النتائج
    function removeResultsCount() {
        const oldCount = document.getElementById('results-count');
        if (oldCount) {
            oldCount.remove();
        }
    }
    
    console.log('تم تحميل سكريبت تحسين الفلترة المباشر');
})();

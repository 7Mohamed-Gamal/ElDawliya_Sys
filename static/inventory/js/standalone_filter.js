/**
 * وحدة فلترة المنتجات المستقلة (Standalone)
 * هذا الملف مستقل تماماً ويمكن إضافته مباشرة في الصفحة بدون الحاجة لاستخدام قوالب Django
 */

(function() {
    console.log('تحميل وحدة الفلترة المستقلة...');
    
    // الانتظار لتحميل الصفحة بالكامل
    function whenDocumentReady(callback) {
        if (document.readyState !== 'loading') {
            callback();
        } else {
            document.addEventListener('DOMContentLoaded', callback);
        }
    }

    // التحقق من وجود واجهة الفلترة وإضافة ميزة الفلترة حسب الوحدة
    whenDocumentReady(function() {
        // التحقق من وجود واجهة البحث المتقدمة
        if (!document.getElementById('productSearchModal')) {
            console.log('لا يوجد نافذة بحث متقدمة على هذه الصفحة');
            return;
        }
        
        console.log('تم العثور على واجهة البحث المتقدمة! جاري تحسين الفلترة...');
        
        // إضافة حقل فلترة حسب الوحدة
        addUnitFilterField();
        
        // تحسين وظيفة البحث عن المنتجات
        enhanceProductSearch();
        
        // جلب وحدات القياس لاستخدامها في الفلترة
        fetchUnits();
        
        // إضافة عداد النتائج
        enhanceResultsDisplay();
    });

    // إضافة حقل فلترة حسب الوحدة
    function addUnitFilterField() {
        // البحث عن صف الفلاتر
        const filterRow = document.querySelector('.search-section .row .col-md-12 .row');
        
        if (!filterRow) return;
        
        // البحث عن فلتر الوحدة (قد يكون موجود بالفعل)
        if (document.getElementById('modal-unit-filter')) {
            console.log('فلتر الوحدة موجود بالفعل');
            return;
        }
        
        console.log('إضافة فلتر الوحدة...');
        
        // إنشاء عنصر التصفية حسب الوحدة
        const unitFilterCol = document.createElement('div');
        unitFilterCol.className = 'col-md-4';
        unitFilterCol.innerHTML = `
            <label for="modal-unit-filter" class="form-label mb-1">الوحدة</label>
            <select id="modal-unit-filter" class="form-select">
                <option value="">كل الوحدات</option>
                <!-- سيتم ملؤها ديناميكياً -->
            </select>
        `;
        
        // إضافة الفلتر إلى الصف
        filterRow.appendChild(unitFilterCol);
        
        // إضافة حدث تغيير قيمة الفلتر
        const unitFilter = document.getElementById('modal-unit-filter');
        if (unitFilter) {
            unitFilter.addEventListener('change', function() {
                triggerSearch();
            });
        }
    }
    
    // جلب وحدات القياس
    function fetchUnits() {
        fetch('/inventory/api/units/')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const unitFilter = document.getElementById('modal-unit-filter');
                    if (!unitFilter) return;
                    
                    // مسح الخيارات الحالية
                    unitFilter.innerHTML = '<option value="">كل الوحدات</option>';
                    
                    // إضافة الوحدات المتاحة
                    data.units.forEach(unit => {
                        const option = document.createElement('option');
                        option.value = unit.id;
                        option.textContent = unit.name;
                        unitFilter.appendChild(option);
                    });
                    
                    console.log('تم تحميل وحدات القياس: ' + data.units.length);
                }
            })
            .catch(error => console.error('خطأ في جلب وحدات القياس:', error));
    }
    
    // تحسين وظيفة البحث عن المنتجات
    function enhanceProductSearch() {
        // دالة البحث الأصلية
        const originalSearchFunction = window.searchProducts;
        
        if (!originalSearchFunction) {
            console.warn('تعذر العثور على دالة البحث الأصلية');
            return;
        }
        
        console.log('تحسين دالة البحث...');
        
        // استبدال دالة البحث القديمة
        window.searchProducts = function() {
            const searchTerm = document.getElementById('modal-search-input').value.trim();
            const categoryId = document.getElementById('modal-category-filter').value;
            const unitId = document.getElementById('modal-unit-filter')?.value || '';
            const stockStatus = document.getElementById('modal-stock-filter').value;
            
            console.log('بحث بمعايير محسنة: ' + 
                        'مصطلح البحث = "' + searchTerm + '", ' + 
                        'التصنيف = ' + (categoryId || 'الكل') + ', ' + 
                        'الوحدة = ' + (unitId || 'الكل') + ', ' + 
                        'حالة المخزون = ' + (stockStatus || 'الكل'));
            
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
                    unit_id: unitId,  // إضافة فلترة حسب الوحدة
                    stock_status: stockStatus
                })
            })
            .then(response => response.json())
            .then(data => {
                // إخفاء مؤشر التحميل
                document.getElementById('loading-indicator').classList.add('d-none');
                
                if (data.success && data.products.length > 0) {
                    // تخزين النتائج في الذاكرة المؤقتة
                    window.productsCache = data.products;
                    
                    // عرض الجدول وملئه بالبيانات
                    document.getElementById('modal-products-table').classList.remove('d-none');
                    
                    // استخدام الدالة الموجودة لملء الجدول
                    if (window.populateProductsTable) {
                        window.populateProductsTable(data.products);
                    }
                    
                    // عرض عداد النتائج
                    showResultsCount(data.products.length);
                } else {
                    // عرض رسالة عدم وجود نتائج
                    document.getElementById('no-products-message').classList.remove('d-none');
                    document.getElementById('modal-products-table').classList.add('d-none');
                    
                    // إزالة عداد النتائج إذا كان موجودًا
                    clearResultsCount();
                }
            })
            .catch(error => {
                console.error('خطأ في البحث عن المنتجات:', error);
                document.getElementById('loading-indicator').classList.add('d-none');
                document.getElementById('no-products-message').classList.remove('d-none');
            });
        };
        
        // إضافة حدث لزر إعادة الضبط
        const resetButton = document.getElementById('modal-reset-filters');
        if (resetButton) {
            resetButton.addEventListener('click', function() {
                // إعادة تعيين قيم الفلاتر
                document.getElementById('modal-search-input').value = '';
                document.getElementById('modal-category-filter').selectedIndex = 0;
                
                // إعادة تعيين فلتر الوحدة إذا كان موجودًا
                const unitFilter = document.getElementById('modal-unit-filter');
                if (unitFilter) unitFilter.selectedIndex = 0;
                
                document.getElementById('modal-stock-filter').selectedIndex = 0;
                
                // تنفيذ البحث مع القيم الافتراضية
                triggerSearch();
            });
        }
    }
    
    // تحسين عرض النتائج
    function enhanceResultsDisplay() {
        // التحقق أن الدالة لإظهار عدد النتائج غير موجودة بالفعل
        if (!window.showResultsCount) {
            window.showResultsCount = function(count) {
                const resultsCountElement = document.createElement('div');
                resultsCountElement.id = 'results-count';
                resultsCountElement.className = 'text-muted mt-2 mb-0';
                resultsCountElement.innerHTML = `<small>تم العثور على ${count} صنف</small>`;
                
                // إزالة أي عداد سابق
                clearResultsCount();
                
                // إضافة العداد الجديد
                const tableContainer = document.querySelector('.table-responsive');
                tableContainer.after(resultsCountElement);
            };
            
            window.clearResultsCount = function() {
                const existingCount = document.getElementById('results-count');
                if (existingCount) existingCount.remove();
            };
        }
    }
    
    // تشغيل البحث
    function triggerSearch() {
        // البحث عن زر البحث وتشغيله
        const searchButton = document.getElementById('modal-search-btn');
        if (searchButton && window.searchProducts) {
            window.searchProducts();
        }
    }

    console.log('تم تحميل وحدة الفلترة المستقلة بنجاح.');
})();

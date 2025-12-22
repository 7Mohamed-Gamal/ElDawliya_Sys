/**
 * تحسينات البحث عن المنتجات - Enhanced Product Search
 * يضيف إمكانية البحث المرن بالوحدات والمزيد من الميزات المتقدمة
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('تم تحميل ملف تحسينات البحث عن المنتجات');
    
    // تهيئة النافذة المنبثقة للبحث عن المنتجات
    const productSearchModal = new bootstrap.Modal(document.getElementById('productSearchModal'));
    
    // متغيرات عامة
    let currentRow = null; // لتخزين الصف الحالي الذي يتم البحث له
    let productsCache = []; // تخزين مؤقت للمنتجات للاستخدام المستقبلي
    let unitsCache = []; // تخزين مؤقت للوحدات للفلترة
    
    // 1. تحميل التصنيفات للفلتر
    function loadCategories() {
        fetch('/inventory/api/categories/')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const categoryFilter = document.getElementById('modal-category-filter');
                    if (categoryFilter) {
                        categoryFilter.innerHTML = '<option value="">كل التصنيفات</option>';
                        
                        data.categories.forEach(category => {
                            const option = document.createElement('option');
                            option.value = category.id;
                            option.textContent = category.name;
                            categoryFilter.appendChild(option);
                        });
                    }
                }
            })
            .catch(error => console.error('خطأ في تحميل التصنيفات:', error));
    }

    // 2. تحميل وحدات القياس للفلتر
    function loadUnits() {
        fetch('/inventory/api/get-units/')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const unitFilter = document.getElementById('modal-unit-filter');
                    if (unitFilter) {
                        unitFilter.innerHTML = '<option value="">كل الوحدات</option>';
                        
                        // تخزين الوحدات في الذاكرة المؤقتة
                        unitsCache = data.units;
                        
                        data.units.forEach(unit => {
                            const option = document.createElement('option');
                            option.value = unit.id;
                            option.textContent = unit.name;
                            unitFilter.appendChild(option);
                        });
                    }
                }
            })
            .catch(error => console.error('خطأ في تحميل الوحدات:', error));
    }
    
    // 3. إعادة ضبط الفلاتر
    function resetFilters() {
        document.getElementById('modal-search-input').value = '';
        document.getElementById('modal-category-filter').selectedIndex = 0;
        document.getElementById('modal-unit-filter').selectedIndex = 0;
        document.getElementById('modal-stock-filter').selectedIndex = 0;
        
        // إخفاء الجداول ورسائل التنبيه
        document.getElementById('modal-products-table').classList.add('d-none');
        document.getElementById('no-products-message').classList.add('d-none');
        
        // إزالة عداد النتائج إذا كان موجودًا
        const tableContainer = document.querySelector('.table-responsive');
        if (tableContainer.nextElementSibling && tableContainer.nextElementSibling.classList.contains('text-muted')) {
            tableContainer.nextElementSibling.remove();
        }
        
        // التركيز على حقل البحث
        document.getElementById('modal-search-input').focus();
    }
    
    // 4. البحث عن المنتجات
    function searchProducts() {
        const searchTerm = document.getElementById('modal-search-input').value.trim();
        const categoryId = document.getElementById('modal-category-filter').value;
        const unitId = document.getElementById('modal-unit-filter').value;
        const stockStatus = document.getElementById('modal-stock-filter').value;
        
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
                unit_id: unitId,
                stock_status: stockStatus
            })
        })
        .then(response => response.json())
        .then(data => {
            // إخفاء مؤشر التحميل
            document.getElementById('loading-indicator').classList.add('d-none');
            
            if (data.success && data.products.length > 0) {
                // تخزين النتائج في الذاكرة المؤقتة
                productsCache = data.products;
                
                // عرض الجدول وملئه بالبيانات
                document.getElementById('modal-products-table').classList.remove('d-none');
                populateProductsTable(data.products);

                // تحديث عدد النتائج
                const resultsCount = document.createElement('div');
                resultsCount.className = 'text-muted mt-2 mb-0';
                resultsCount.innerHTML = `<small>تم العثور على ${data.products.length} صنف</small>`;
                
                const tableContainer = document.querySelector('.table-responsive');
                if (tableContainer.nextElementSibling && tableContainer.nextElementSibling.classList.contains('text-muted')) {
                    tableContainer.nextElementSibling.remove();
                }
                tableContainer.after(resultsCount);
            } else {
                // عرض رسالة عدم وجود نتائج
                document.getElementById('no-products-message').classList.remove('d-none');
                document.getElementById('modal-products-table').classList.add('d-none');
                
                // إزالة عداد النتائج إذا كان موجودًا
                const tableContainer = document.querySelector('.table-responsive');
                if (tableContainer.nextElementSibling && tableContainer.nextElementSibling.classList.contains('text-muted')) {
                    tableContainer.nextElementSibling.remove();
                }
            }
        })
        .catch(error => {
            console.error('خطأ في البحث عن المنتجات:', error);
            document.getElementById('loading-indicator').classList.add('d-none');
            document.getElementById('no-products-message').classList.remove('d-none');
        });
    }
    
    // 5. ملء جدول المنتجات
    function populateProductsTable(products) {
        const tableBody = document.querySelector('#modal-products-table tbody');
        tableBody.innerHTML = '';
        
        products.forEach(product => {
            const row = document.createElement('tr');
            
            // تنسيق خلية الحالة
            let stockClass = '';
            if (product.quantity <= 0) {
                stockClass = 'text-danger fw-bold';
            } else if (product.quantity < product.minimum_threshold) {
                stockClass = 'text-warning fw-bold';
            } else {
                stockClass = 'text-success';
            }
            
            row.innerHTML = `
                <td>${product.product_id}</td>
                <td>${product.name}</td>
                <td>${product.category_name || '-'}</td>
                <td class="${stockClass}">${product.quantity}</td>
                <td>${product.unit_name || '-'}</td>
                <td>
                    <button type="button" class="btn btn-sm btn-primary select-product" 
                            data-product-id="${product.product_id}"
                            data-product-name="${product.name}"
                            data-product-quantity="${product.quantity}"
                            data-product-unit="${product.unit_name || ''}">
                        <i class="fas fa-check ms-1"></i> اختيار
                    </button>
                </td>
            `;
            
            tableBody.appendChild(row);
        });
        
        // تفعيل أزرار اختيار المنتج
        document.querySelectorAll('.select-product').forEach(button => {
            button.addEventListener('click', function() {
                const productId = this.getAttribute('data-product-id');
                const productName = this.getAttribute('data-product-name');
                const productQuantity = this.getAttribute('data-product-quantity');
                const productUnit = this.getAttribute('data-product-unit');
                
                // تحديث الصف في نموذج الإذن
                if (currentRow) {
                    const productCodeInput = currentRow.querySelector('.product-code');
                    const productIdInput = currentRow.querySelector('.product-id');
                    const productNameSpan = currentRow.querySelector('.product-name');
                    const currentStockSpan = currentRow.querySelector('.current-stock');
                    const unitNameSpan = currentRow.querySelector('.unit-name');
                    const quantityInput = currentRow.querySelector('.quantity');
                    
                    if (productCodeInput) productCodeInput.value = productId;
                    if (productIdInput) productIdInput.value = productId;
                    if (productNameSpan) productNameSpan.textContent = productName;
                    if (currentStockSpan) currentStockSpan.textContent = productQuantity;
                    if (unitNameSpan) unitNameSpan.textContent = productUnit;
                    
                    // تحديث الحد الأقصى للكمية في حالة إذن الصرف
                    const voucherType = document.getElementById('id_voucher_type').value;
                    if (voucherType !== 'إذن اضافة' && voucherType !== 'اذن مرتجع عميل' && quantityInput) {
                        quantityInput.max = productQuantity;
                        // التأكد من أن القيمة لا تتجاوز الحد الأقصى
                        if (parseFloat(quantityInput.value) > productQuantity) {
                            quantityInput.value = productQuantity;
                        }
                    }
                }
                
                // إغلاق النافذة المنبثقة
                productSearchModal.hide();
            });
        });
    }
    
    // 6. تفعيل معالجات الأحداث
    function initializeEventHandlers() {
        // زر البحث
        const searchBtn = document.getElementById('modal-search-btn');
        if (searchBtn) {
            searchBtn.addEventListener('click', searchProducts);
        }
        
        // حقل البحث - البحث عند الضغط على Enter
        const searchInput = document.getElementById('modal-search-input');
        if (searchInput) {
            searchInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    searchProducts();
                }
            });
        }
        
        // فلتر التصنيف
        const categoryFilter = document.getElementById('modal-category-filter');
        if (categoryFilter) {
            categoryFilter.addEventListener('change', searchProducts);
        }
        
        // فلتر الوحدة
        const unitFilter = document.getElementById('modal-unit-filter');
        if (unitFilter) {
            unitFilter.addEventListener('change', searchProducts);
        }
        
        // فلتر حالة المخزون
        const stockFilter = document.getElementById('modal-stock-filter');
        if (stockFilter) {
            stockFilter.addEventListener('change', searchProducts);
        }
        
        // زر إعادة ضبط الفلاتر
        const resetBtn = document.getElementById('modal-reset-filters');
        if (resetBtn) {
            resetBtn.addEventListener('click', resetFilters);
        }
    }
    
    // 7. عرض نافذة البحث عن المنتجات
    function showProductSearchModal(row) {
        currentRow = row;
        
        // إعادة تعيين حقول البحث
        document.getElementById('modal-search-input').value = '';
        document.getElementById('modal-category-filter').selectedIndex = 0;
        document.getElementById('modal-unit-filter').selectedIndex = 0;
        document.getElementById('modal-stock-filter').selectedIndex = 0;
        
        // تحميل التصنيفات إذا لم تكن محملة
        if (document.getElementById('modal-category-filter').options.length <= 1) {
            loadCategories();
        }
        
        // تحميل الوحدات إذا لم تكن محملة
        if (document.getElementById('modal-unit-filter').options.length <= 1) {
            loadUnits();
        }
        
        // إخفاء الجداول ورسائل التنبيه
        document.getElementById('modal-products-table').classList.add('d-none');
        document.getElementById('no-products-message').classList.add('d-none');
        document.getElementById('loading-indicator').classList.add('d-none');
        
        // إظهار النافذة المنبثقة
        productSearchModal.show();
        
        // التركيز على حقل البحث
        setTimeout(() => {
            document.getElementById('modal-search-input').focus();
        }, 500);
    }
    
    // تهيئة الوظائف عند تحميل الصفحة
    initializeEventHandlers();
    
    // تعريض الدالة للاستخدام الخارجي
    window.showProductSearchModal = showProductSearchModal;
});

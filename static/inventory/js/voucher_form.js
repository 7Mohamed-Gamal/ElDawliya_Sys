/**
 * وظائف نموذج الإذن - Voucher Form Functions
 * This file handles all functionality related to the voucher form including:
 * - Adding/removing items
 * - Product search and selection
 * - Form validation
 * - Voucher number generation
 * - Form submission
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('تم تحميل صفحة نموذج الإذن');

    // تحسينات الفلترة (تم إضافتها)
    enhanceFilteringCapabilities();

    // 1. إضافة صف جديد للأصناف
    const addItemBtn = document.getElementById('add-item-btn');
    if (addItemBtn) {
        addItemBtn.addEventListener('click', addNewItemRow);
    }

    // 2. البحث عن المنتج بالكود
    initProductCodeSearch();

    // 3. حذف صف من الجدول
    initDeleteRowButtons();

    // 4. توليد رقم إذن جديد
    const generateNumberBtn = document.getElementById('generate-number-btn');
    if (generateNumberBtn) {
        generateNumberBtn.addEventListener('click', generateVoucherNumber);
    }

    // 5. تفعيل tooltips
    try {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    } catch (error) {
        console.warn('تعذر تهيئة tooltips:', error);
    }

    // 6. إضافة تعليمات استخدام في أعلى الصفحة
    const formCard = document.querySelector('.card-body form');
    if (formCard) {
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-info mb-4';
        alertDiv.innerHTML = `
            <h5><i class="fas fa-info-circle"></i> تعليمات استخدام</h5>
            <ul class="mb-0">
                <li>يمكنك البحث عن الصنف بإدخال الكود مباشرة في حقل كود الصنف.</li>
                <li>إذا كنت لا تعرف كود الصنف، يمكنك استخدام زر البحث <i class="fas fa-search"></i> للبحث عن الصنف بالاسم أو التصنيف.</li>
                <li>بعد إضافة الصنف، أدخل الكمية المطلوبة.</li>
                <li>يمكنك إضافة المزيد من الأصناف بالضغط على زر "إضافة صنف".</li>
            </ul>
        `;
        formCard.insertBefore(alertDiv, formCard.firstChild);
    }

    // 7. معالجة إرسال النموذج
    const voucherForm = document.getElementById('voucher-form');
    if (voucherForm) {
        voucherForm.addEventListener('submit', function(event) {
            console.log('معالجة إرسال نموذج الإذن...');

            // تحديث حقول إدارة النماذج المتعددة (formset management form)
            updateFormsetTotalForms();

            // التحقق من صحة البيانات
            const isValid = validateVoucherForm();

            if (!isValid) {
                event.preventDefault();
                return false;
            }

            // تحديث حالة الزر لمنع النقر المتكرر
            const submitButton = voucherForm.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> جاري الإرسال...';
            }

            console.log('نموذج صالح، جاري الإرسال...');
            return true;
        });
    }

    // 8. تحميل ميزات الفلترة المحسنة
    loadEnhancedFilterFeatures();
});

// تحميل ميزات الفلترة المحسنة (البحث حسب الوحدة)
function loadEnhancedFilterFeatures() {
    console.log('جاري تحميل ميزات الفلترة المحسنة...');

    // دالة تحميل ملفات JavaScript
    function loadScript(src, callback) {
        // التحقق ما إذا كان السكريبت مُحمّل بالفعل
        const existingScripts = document.querySelectorAll('script');
        for (let i = 0; i < existingScripts.length; i++) {
            if (existingScripts[i].src.includes(src)) {
                if (callback) callback();
                return;
            }
        }

        // إنشاء عنصر السكريبت الجديد
        const script = document.createElement('script');
        script.src = src;
        script.onload = callback || function() {};

        // إضافة السكريبت إلى رأس المستند
        document.head.appendChild(script);
    }

    // تحميل ملفات الفلترة المحسنة بالترتيب
    loadScript('/static/inventory/js/api_patch.js', function() {
        loadScript('/static/inventory/js/product_search_enhanced.js', function() {
            console.log('تم تحميل جميع ملفات الفلترة المحسنة بنجاح');
        });
    });
}

/**
 * التحقق من صحة النموذج قبل الإرسال
 * Validates the voucher form before submission
 * Checks for voucher number, items, and valid quantities
 * @returns {boolean} True if the form is valid, false otherwise
 */
function validateVoucherForm() {
    // التحقق من وجود رقم الإذن
    const voucherNumber = document.getElementById('id_voucher_number');
    if (!voucherNumber || !voucherNumber.value.trim()) {
        alert('يرجى إدخال رقم الإذن');
        if (voucherNumber) voucherNumber.focus();
        return false;
    }

    // التحقق من وجود صفوف للأصناف
    const rows = document.querySelectorAll('tr.item-row');
    if (rows.length === 0) {
        alert('يرجى إضافة صنف واحد على الأقل');
        return false;
    }

    // التحقق من كل صف
    let hasError = false;
    rows.forEach((row, index) => {
        const productCode = row.querySelector('.product-code');
        const productId = row.querySelector('.product-id');
        const quantity = row.querySelector('.quantity');

        // التحقق من وجود منتج
        if (!productId || !productId.value) {
            alert(`الصف ${index + 1}: يرجى اختيار صنف صحيح`);
            if (productCode) productCode.focus();
            hasError = true;
            return;
        }

        // التحقق من وجود كمية صحيحة
        if (!quantity || !quantity.value || parseFloat(quantity.value) <= 0) {
            alert(`الصف ${index + 1}: يرجى إدخال كمية صحيحة (أكبر من صفر)`);
            if (quantity) quantity.focus();
            hasError = true;
            return;
        }

        // التحقق من الكمية المتاحة في حالة إذن الصرف
        const voucherType = document.getElementById('id_voucher_type');
        if (voucherType && voucherType.value !== 'إذن اضافة' && voucherType.value !== 'اذن مرتجع عميل') {
            const currentStock = parseFloat(row.querySelector('.current-stock')?.textContent || '0');
            if (parseFloat(quantity.value) > currentStock) {
                alert(`الصف ${index + 1}: الكمية المطلوبة (${quantity.value}) أكبر من الرصيد المتاح (${currentStock})`);
                quantity.focus();
                hasError = true;
                return;
            }
        }
    });

    return !hasError;
}

/**
 * تحديث عدد النماذج في المجموعة
 * Updates the total forms count in the formset management form
 * This is required for Django formsets to work correctly
 */
function updateFormsetTotalForms() {
    const rows = document.querySelectorAll('tr.item-row');
    const totalFormsInput = document.querySelector('input[name="form-TOTAL_FORMS"]');

    if (totalFormsInput) {
        totalFormsInput.value = rows.length.toString();
        console.log(`تم تحديث عدد النماذج في المجموعة إلى ${rows.length}`);
    } else {
        console.warn('لم يتم العثور على حقل إدارة النماذج المتعددة (form-TOTAL_FORMS)');
    }
}

/**
 * إضافة صف جديد للأصناف
 * Adds a new item row to the voucher items table
 * Creates different row content based on voucher type
 */
function addNewItemRow() {
    console.log('إضافة صف جديد');

    const itemsTable = document.getElementById('items-table');
    if (!itemsTable) {
        console.error('لم يتم العثور على جدول الأصناف');
        return;
    }

    const tbody = itemsTable.querySelector('tbody');
    if (!tbody) {
        console.error('لم يتم العثور على tbody في جدول الأصناف');
        return;
    }

    const rows = tbody.querySelectorAll('tr.item-row');
    const rowCount = rows.length;

    // إنشاء صف جديد
    const newRow = document.createElement('tr');
    newRow.className = 'item-row';

    // الحصول على نوع الإذن
    const voucherType = document.getElementById('id_voucher_type').value;

    // تحديد محتوى الصف بناءً على نوع الإذن
    let rowContent = `
        <td>
            <input type="text" class="form-control product-code" name="form-${rowCount}-product_code" value="" required>
            <input type="hidden" class="product-id" name="form-${rowCount}-product" value="">
        </td>
        <td>
            <span class="product-name"></span>
        </td>
        <td>
            <span class="current-stock">0</span>
        </td>
        <td>
            <span class="unit-name"></span>
        </td>
    `;

    // إضافة حقل الكمية المناسب حسب نوع الإذن
    if (voucherType === 'إذن اضافة' || voucherType === 'اذن مرتجع عميل') {
        rowContent += `
            <td>
                <input type="number" class="form-control quantity" name="form-${rowCount}-quantity" value="1" min="0.01" step="0.01" required>
            </td>
        `;
    } else {
        rowContent += `
            <td>
                <input type="number" class="form-control quantity" name="form-${rowCount}-quantity" value="1" min="0.01" step="0.01" max="0" required>
            </td>
        `;
    }

    // إضافة حقول الماكينة إذا كان نوع الإذن هو إذن صرف
    if (voucherType === 'إذن صرف') {
        rowContent += `
            <td>
                <input type="text" class="form-control machine-name" name="form-${rowCount}-machine_name" value="">
            </td>
            <td>
                <input type="text" class="form-control machine-unit" name="form-${rowCount}-machine_unit" value="">
            </td>
        `;
    }

    // إضافة زر الحذف
    rowContent += `
        <td>
            <button type="button" class="btn btn-sm btn-danger delete-row">
                <i class="fas fa-trash"></i>
            </button>
        </td>
    `;

    // إضافة المحتوى للصف
    newRow.innerHTML = rowContent;

    // إضافة الصف للجدول
    tbody.appendChild(newRow);

    // تحديث عدد النماذج في المجموعة
    updateFormsetTotalForms();

    // تفعيل البحث عن المنتج في الصف الجديد
    initProductCodeSearchForRow(newRow);

    // تفعيل زر الحذف في الصف الجديد
    initDeleteRowButtonForRow(newRow);
}

/**
 * تفعيل البحث عن المنتج بالكود
 * Initializes product code search for all existing rows
 */
function initProductCodeSearch() {
    const rows = document.querySelectorAll('tr.item-row');
    rows.forEach(row => {
        initProductCodeSearchForRow(row);
    });
}

/**
 * تفعيل البحث عن المنتج بالكود لصف محدد
 * Initializes product code search for a specific row
 * Adds blur event to search by code and click event for search button
 * @param {HTMLElement} row - The table row to initialize
 */
function initProductCodeSearchForRow(row) {
    if (!row) return;

    const productCodeInput = row.querySelector('.product-code');
    if (productCodeInput) {
        // إضافة حدث blur للبحث عن المنتج عند مغادرة الحقل
        productCodeInput.addEventListener('blur', function() {
            const productCode = this.value.trim();
            if (productCode) {
                fetchProductDetails(productCode, row);
            }
        });

        // إضافة زر البحث المرن
        const searchBtn = document.createElement('button');
        searchBtn.type = 'button';
        searchBtn.className = 'btn btn-sm btn-primary search-product-btn ms-2';
        searchBtn.innerHTML = '<i class="fas fa-search"></i>';
        searchBtn.title = 'بحث عن صنف';

        // إضافة الزر بعد حقل الكود
        const parentCell = productCodeInput.parentNode;
        parentCell.appendChild(searchBtn);

        // إضافة حدث النقر على زر البحث
        searchBtn.addEventListener('click', function() {
            showProductSearchModal(row);
        });
    }
}

/**
 * جلب بيانات المنتج بالكود
 * Fetches product details by product code from the server
 * @param {string} productCode - The product code to search for
 * @param {HTMLElement} row - The table row to update with product details
 */
function fetchProductDetails(productCode, row) {
    if (!productCode || !row) {
        console.error('معلمات غير صالحة لجلب بيانات المنتج');
        return;
    }

    console.log(`جلب بيانات المنتج: ${productCode}`);

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    if (!csrfToken) {
        console.error('لم يتم العثور على رمز CSRF');
        return;
    }

    fetch('/inventory/api/product-details/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken.value
        },
        body: JSON.stringify({ product_code: productCode })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            updateRowWithProductDetails(row, data.product);
        } else {
            alert(data.message || 'لم يتم العثور على المنتج');
            clearRowProductDetails(row);
        }
    })
    .catch(error => {
        console.error('خطأ في جلب بيانات المنتج:', error);
        alert('حدث خطأ أثناء جلب بيانات المنتج');
    });
}

/**
 * تحسين قدرات الفلترة
 * Enhances filtering capabilities by loading standalone filter script
 */
function enhanceFilteringCapabilities() {
    console.log('تحسين قدرات الفلترة...');

    // إضافة سكريبت مستقل للفلترة المحسنة
    const script = document.createElement('script');
    script.src = '/static/inventory/js/standalone_filter.js';
    document.body.appendChild(script);

    console.log('تم تحميل سكريبت الفلترة المحسنة');
}

/**
 * عرض نافذة البحث عن المنتج
 * Shows a modal dialog for searching products by name, category, etc.
 * @param {HTMLElement} row - The table row to update with selected product
 */
function showProductSearchModal(row) {
    console.log('فتح نافذة البحث عن المنتج');

    // التحقق من وجود نافذة البحث
    let searchModal = document.getElementById('product-search-modal');

    // إنشاء نافذة البحث إذا لم تكن موجودة
    if (!searchModal) {
        searchModal = document.createElement('div');
        searchModal.id = 'product-search-modal';
        searchModal.className = 'modal fade';
        searchModal.tabIndex = '-1';
        searchModal.setAttribute('aria-hidden', 'true');

        // إنشاء محتوى النافذة
        searchModal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">بحث عن صنف</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="إغلاق"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row mb-3">
                            <div class="col-md-8">
                                <input type="text" id="product-search-input" class="form-control" placeholder="اكتب اسم الصنف أو الكود...">
                            </div>
                            <div class="col-md-4">
                                <select id="product-category-filter" class="form-select">
                                    <option value="">جميع التصنيفات</option>
                                </select>
                            </div>
                        </div>
                        <div class="table-responsive">
                            <table class="table table-striped table-hover">
                                <thead>
                                    <tr>
                                        <th>الكود</th>
                                        <th>الاسم</th>
                                        <th>الوحدة</th>
                                        <th>الرصيد</th>
                                        <th>اختيار</th>
                                    </tr>
                                </thead>
                                <tbody id="product-search-results">
                                    <tr>
                                        <td colspan="5" class="text-center">ابدأ البحث...</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إغلاق</button>
                    </div>
                </div>
            </div>
        `;

        // إضافة النافذة للصفحة
        document.body.appendChild(searchModal);

        // تهيئة النافذة باستخدام Bootstrap
        new bootstrap.Modal(searchModal);

        // تحميل التصنيفات
        loadProductCategories();

        // إضافة حدث البحث
        const searchInput = document.getElementById('product-search-input');
        const categoryFilter = document.getElementById('product-category-filter');

        if (searchInput) {
            searchInput.addEventListener('input', function() {
                searchProducts(this.value, categoryFilter ? categoryFilter.value : '');
            });
        }

        if (categoryFilter) {
            categoryFilter.addEventListener('change', function() {
                searchProducts(searchInput ? searchInput.value : '', this.value);
            });
        }
    } else {
        // إعادة تعيين حقل البحث
        const searchInput = document.getElementById('product-search-input');
        if (searchInput) searchInput.value = '';

        // إعادة تعيين نتائج البحث
        const resultsContainer = document.getElementById('product-search-results');
        if (resultsContainer) {
            resultsContainer.innerHTML = '<tr><td colspan="5" class="text-center">ابدأ البحث...</td></tr>';
        }
    }

    // تخزين الصف الحالي في النافذة
    searchModal.dataset.currentRow = row ? row.rowIndex : '';

    // عرض النافذة
    const modalInstance = bootstrap.Modal.getInstance(searchModal) || new bootstrap.Modal(searchModal);
    modalInstance.show();
}

/**
 * تحميل تصنيفات المنتجات
 * Loads product categories for the search modal
 */
function loadProductCategories() {
    console.log('تحميل تصنيفات المنتجات');

    const categoryFilter = document.getElementById('product-category-filter');
    if (!categoryFilter) return;

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch('/inventory/api/categories/', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success && data.categories) {
            // حفظ الخيار المحدد حاليًا
            const currentValue = categoryFilter.value;

            // مسح الخيارات الحالية (باستثناء الخيار الأول)
            while (categoryFilter.options.length > 1) {
                categoryFilter.remove(1);
            }

            // إضافة التصنيفات
            data.categories.forEach(category => {
                const option = document.createElement('option');
                option.value = category.id;
                option.textContent = category.name;
                categoryFilter.appendChild(option);
            });

            // إعادة تحديد الخيار السابق إذا كان موجودًا
            if (currentValue) {
                categoryFilter.value = currentValue;
            }
        }
    })
    .catch(error => {
        console.error('خطأ في تحميل التصنيفات:', error);
    });
}

/**
 * البحث عن المنتجات
 * Searches for products based on search term and category
 * @param {string} searchTerm - The search term
 * @param {string} categoryId - The category ID to filter by
 */
function searchProducts(searchTerm, categoryId) {
    console.log(`البحث عن المنتجات: "${searchTerm}" في التصنيف: ${categoryId || 'الكل'}`);

    const resultsContainer = document.getElementById('product-search-results');
    if (!resultsContainer) return;

    // عرض رسالة التحميل
    resultsContainer.innerHTML = '<tr><td colspan="5" class="text-center"><i class="fas fa-spinner fa-spin"></i> جاري البحث...</td></tr>';

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch('/inventory/api/search-products/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            search_term: searchTerm,
            category_id: categoryId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success && data.products) {
            if (data.products.length === 0) {
                resultsContainer.innerHTML = '<tr><td colspan="5" class="text-center">لم يتم العثور على نتائج</td></tr>';
                return;
            }

            // عرض النتائج
            let html = '';
            data.products.forEach(product => {
                html += `
                    <tr>
                        <td>${product.code}</td>
                        <td>${product.name}</td>
                        <td>${product.unit_name || ''}</td>
                        <td>${product.quantity}</td>
                        <td>
                            <button type="button" class="btn btn-sm btn-success select-product"
                                    data-product-id="${product.id}"
                                    data-product-code="${product.code}"
                                    data-product-name="${product.name}"
                                    data-product-quantity="${product.quantity}"
                                    data-product-unit="${product.unit_name || ''}">
                                <i class="fas fa-check"></i>
                            </button>
                        </td>
                    </tr>
                `;
            });

            resultsContainer.innerHTML = html;

            // إضافة أحداث النقر على أزرار الاختيار
            resultsContainer.querySelectorAll('.select-product').forEach(button => {
                button.addEventListener('click', function() {
                    selectProductFromSearch(this);
                });
            });
        } else {
            resultsContainer.innerHTML = '<tr><td colspan="5" class="text-center">حدث خطأ أثناء البحث</td></tr>';
        }
    })
    .catch(error => {
        console.error('خطأ في البحث عن المنتجات:', error);
        resultsContainer.innerHTML = '<tr><td colspan="5" class="text-center">حدث خطأ أثناء البحث</td></tr>';
    });
}

/**
 * اختيار منتج من نتائج البحث
 * Selects a product from search results and updates the row
 * @param {HTMLElement} button - The select button that was clicked
 */
function selectProductFromSearch(button) {
    console.log('اختيار منتج من نتائج البحث');

    // الحصول على بيانات المنتج من زر الاختيار
    const productId = button.dataset.productId;
    const productCode = button.dataset.productCode;
    const productName = button.dataset.productName;
    const productQuantity = button.dataset.productQuantity;
    const productUnit = button.dataset.productUnit;

    // الحصول على الصف المرتبط
    const searchModal = document.getElementById('product-search-modal');
    if (!searchModal || !searchModal.dataset.currentRow) return;

    // الحصول على الصف من الجدول
    const rows = document.querySelectorAll('tr.item-row');
    const rowIndex = parseInt(searchModal.dataset.currentRow) - 1;
    const row = rows[rowIndex];

    if (row) {
        // تحديث حقول الصف
        const productIdInput = row.querySelector('.product-id');
        const productCodeInput = row.querySelector('.product-code');
        const productNameSpan = row.querySelector('.product-name');
        const currentStockSpan = row.querySelector('.current-stock');
        const unitNameSpan = row.querySelector('.unit-name');

        if (productIdInput) productIdInput.value = productId;
        if (productCodeInput) productCodeInput.value = productCode;
        if (productNameSpan) productNameSpan.textContent = productName;
        if (currentStockSpan) currentStockSpan.textContent = productQuantity;
        if (unitNameSpan) unitNameSpan.textContent = productUnit;

        // تحديث الحد الأقصى للكمية في حالة إذن الصرف
        const voucherType = document.getElementById('id_voucher_type').value;
        const quantityInput = row.querySelector('.quantity');

        if (quantityInput && voucherType !== 'إذن اضافة' && voucherType !== 'اذن مرتجع عميل') {
            quantityInput.max = productQuantity;

            // التأكد من أن القيمة لا تتجاوز الحد الأقصى
            if (parseFloat(quantityInput.value) > productQuantity) {
                quantityInput.value = productQuantity;
            }
        }
    }

    // إغلاق النافذة
    const modalInstance = bootstrap.Modal.getInstance(searchModal);
    if (modalInstance) modalInstance.hide();
}

// تحديث صف بالبيانات
function updateRowWithProductDetails(row, product) {
    console.log('تحديث الصف بالبيانات:', product);

    // تحديث حقل معرف المنتج
    const productIdInput = row.querySelector('.product-id');
    if (productIdInput) productIdInput.value = product.id;

    // اسم المنتج
    const productNameSpan = row.querySelector('.product-name');
    if (productNameSpan) productNameSpan.textContent = product.name;

    // الرصيد الحالي
    const currentStockSpan = row.querySelector('.current-stock');
    if (currentStockSpan) currentStockSpan.textContent = product.quantity;

    // اسم الوحدة
    const unitNameSpan = row.querySelector('.unit-name');
    if (unitNameSpan) unitNameSpan.textContent = product.unit_name || '';

    // تحديث الحد الأقصى للكمية في حالة إذن الصرف
    const voucherType = document.getElementById('id_voucher_type').value;
    const quantityInput = row.querySelector('.quantity');

    if (quantityInput && voucherType !== 'إذن اضافة' && voucherType !== 'اذن مرتجع عميل') {
        quantityInput.max = product.quantity;

        // التأكد من أن القيمة لا تتجاوز الحد الأقصى
        if (parseFloat(quantityInput.value) > product.quantity) {
            quantityInput.value = product.quantity;
        }
    }
}

/**
 * مسح بيانات صف
 * Clears all product details from a row
 * @param {HTMLElement} row - The table row to clear
 */
function clearRowProductDetails(row) {
    if (!row) return;

    const productIdInput = row.querySelector('.product-id');
    const productNameSpan = row.querySelector('.product-name');
    const currentStockSpan = row.querySelector('.current-stock');
    const unitNameSpan = row.querySelector('.unit-name');

    if (productIdInput) productIdInput.value = '';
    if (productNameSpan) productNameSpan.textContent = '';
    if (currentStockSpan) currentStockSpan.textContent = '0';
    if (unitNameSpan) unitNameSpan.textContent = '';

    const quantityInput = row.querySelector('.quantity');
    if (quantityInput) {
        quantityInput.max = '';
        quantityInput.value = '0';
    }
}

/**
 * تفعيل أزرار حذف الصفوف
 * Initializes delete buttons for all existing rows
 */
function initDeleteRowButtons() {
    document.querySelectorAll('.delete-row').forEach(button => {
        const row = button.closest('tr.item-row');
        if (row) {
            initDeleteRowButtonForRow(row);
        }
    });
}

/**
 * تفعيل زر حذف الصف
 * Initializes the delete button for a specific row
 * @param {HTMLElement} row - The table row to initialize
 */
function initDeleteRowButtonForRow(row) {
    if (!row) return;

    const deleteButton = row.querySelector('.delete-row');
    if (deleteButton) {
        // Remove any existing event listeners to prevent duplicates
        const newButton = deleteButton.cloneNode(true);
        deleteButton.parentNode.replaceChild(newButton, deleteButton);

        // Add the click event listener
        newButton.addEventListener('click', function() {
            if (confirm('هل أنت متأكد من حذف هذا الصنف؟')) {
                row.remove();
                updateFormsetTotalForms();
            }
        });
    }
}

/**
 * توليد رقم إذن جديد
 * Generates a new voucher number based on the current date and voucher type
 * Format: [Type Prefix]-[Date YYYYMMDD]-[Random 4 digits]
 */
function generateVoucherNumber() {
    const voucherNumberField = document.getElementById('id_voucher_number');
    const voucherTypeField = document.getElementById('id_voucher_type');

    if (!voucherNumberField || !voucherTypeField) {
        console.error('لم يتم العثور على حقول الإذن المطلوبة');
        return;
    }

    const voucherType = voucherTypeField.value;

    // تحديد بادئة حسب نوع الإذن
    let prefix = '';
    switch (voucherType) {
        case 'إذن اضافة':
            prefix = 'ADD';
            break;
        case 'إذن صرف':
            prefix = 'OUT';
            break;
        case 'اذن مرتجع عميل':
            prefix = 'RET';
            break;
        default:
            prefix = 'VCH';
    }

    // إنشاء تاريخ حالي بتنسيق YYYYMMDD
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    const dateStr = `${year}${month}${day}`;

    // إنشاء رقم عشوائي من 4 أرقام
    const randomNum = Math.floor(1000 + Math.random() * 9000);

    // تجميع رقم الإذن
    const voucherNumber = `${prefix}-${dateStr}-${randomNum}`;

    // تعيين رقم الإذن في الحقل
    voucherNumberField.value = voucherNumber;

    // تنبيه المستخدم
    console.log(`تم إنشاء رقم إذن جديد: ${voucherNumber}`);
}

// تحميل ميزات الفلترة المحسنة (البحث حسب الوحدة)
function loadEnhancedFilterFeatures() {
    console.log('جاري تحميل ميزات الفلترة المحسنة...');

    // دالة تحميل ملفات JavaScript
    function loadScript(src, callback) {
        // التحقق ما إذا كان السكريبت مُحمّل بالفعل
        const existingScripts = document.querySelectorAll('script');
        for (let i = 0; i < existingScripts.length; i++) {
            if (existingScripts[i].src.includes(src)) {
                if (callback) callback();
                return;
            }
        }

        // إنشاء عنصر السكريبت الجديد
        const script = document.createElement('script');
        script.src = src;
        script.onload = callback || function() {};

        // إضافة السكريبت إلى رأس المستند
        document.head.appendChild(script);
    }

    // تحميل ملفات الفلترة المحسنة بالترتيب
    loadScript('/static/inventory/js/api_patch.js', function() {
        loadScript('/static/inventory/js/product_search_enhanced.js', function() {
            console.log('تم تحميل جميع ملفات الفلترة المحسنة بنجاح');
        });
    });
}

// التحقق من صحة النموذج قبل الإرسال
function validateVoucherForm() {
    // التحقق من وجود رقم الإذن
    const voucherNumber = document.getElementById('id_voucher_number');
    if (!voucherNumber || !voucherNumber.value.trim()) {
        alert('يرجى إدخال رقم الإذن');
        if (voucherNumber) voucherNumber.focus();
        return false;
    }

    // التحقق من وجود صفوف للأصناف
    const rows = document.querySelectorAll('tr.item-row');
    if (rows.length === 0) {
        alert('يرجى إضافة صنف واحد على الأقل');
        return false;
    }

    // التحقق من كل صف
    let hasError = false;
    rows.forEach((row, index) => {
        const productCode = row.querySelector('.product-code');
        const productId = row.querySelector('.product-id');
        const quantity = row.querySelector('.quantity');

        // التحقق من وجود منتج
        if (!productId.value) {
            alert(`الصف ${index + 1}: يرجى اختيار صنف صحيح`);
            productCode.focus();
            hasError = true;
            return;
        }

        // التحقق من وجود كمية صحيحة
        if (!quantity.value || parseFloat(quantity.value) <= 0) {
            alert(`الصف ${index + 1}: يرجى إدخال كمية صحيحة (أكبر من صفر)`);
            quantity.focus();
            hasError = true;
            return;
        }
    });

    return !hasError;
}

// تحديث عدد النماذج في المجموعة
function updateFormsetTotalForms() {
    const rows = document.querySelectorAll('tr.item-row');
    const totalFormsInput = document.querySelector('input[name="form-TOTAL_FORMS"]');

    if (totalFormsInput) {
        totalFormsInput.value = rows.length.toString();
        console.log(`تم تحديث عدد النماذج في المجموعة إلى ${rows.length}`);
    } else {
        console.warn('لم يتم العثور على حقل إدارة النماذج المتعددة (form-TOTAL_FORMS)');
    }
}

// إضافة صف جديد للأصناف
function addNewItemRow() {
    console.log('إضافة صف جديد');

    const itemsTable = document.getElementById('items-table');
    const tbody = itemsTable.querySelector('tbody');
    const rows = tbody.querySelectorAll('tr.item-row');
    const rowCount = rows.length;

    // إنشاء صف جديد
    const newRow = document.createElement('tr');
    newRow.className = 'item-row';

    // الحصول على نوع الإذن
    const voucherType = document.getElementById('id_voucher_type').value;

    // تحديد محتوى الصف بناءً على نوع الإذن
    let rowContent = `
        <td>
            <input type="text" class="form-control product-code" name="form-${rowCount}-product_code" value="" required>
            <input type="hidden" class="product-id" name="form-${rowCount}-product" value="">
        </td>
        <td>
            <span class="product-name"></span>
        </td>
        <td>
            <span class="current-stock">0</span>
        </td>
        <td>
            <span class="unit-name"></span>
        </td>
    `;

    // إضافة حقل الكمية المناسب حسب نوع الإذن
    if (voucherType === 'إذن اضافة' || voucherType === 'اذن مرتجع عميل') {
        rowContent += `
            <td>
                <input type="number" class="form-control quantity" name="form-${rowCount}-quantity" value="1" min="0.01" step="0.01" required>
            </td>
        `;
    } else {
        rowContent += `
            <td>
                <input type="number" class="form-control quantity" name="form-${rowCount}-quantity" value="1" min="0.01" step="0.01" max="0" required>
            </td>
        `;
    }

    // إضافة حقول الماكينة إذا كان نوع الإذن هو إذن صرف
    if (voucherType === 'إذن صرف') {
        rowContent += `
            <td>
                <input type="text" class="form-control machine-name" name="form-${rowCount}-machine_name" value="">
            </td>
            <td>
                <input type="text" class="form-control machine-unit" name="form-${rowCount}-machine_unit" value="">
            </td>
        `;
    }

    // إضافة زر الحذف
    rowContent += `
        <td>
            <button type="button" class="btn btn-sm btn-danger delete-row">
                <i class="fas fa-trash"></i>
            </button>
        </td>
    `;

    // إضافة المحتوى للصف
    newRow.innerHTML = rowContent;

    // إضافة الصف للجدول
    tbody.appendChild(newRow);

    // تحديث عدد النماذج في المجموعة
    updateFormsetTotalForms();

    // تفعيل البحث عن المنتج في الصف الجديد
    initProductCodeSearchForRow(newRow);

    // تفعيل زر الحذف في الصف الجديد
    initDeleteRowButtonForRow(newRow);
}

// تفعيل البحث عن المنتج بالكود
function initProductCodeSearch() {
    const rows = document.querySelectorAll('tr.item-row');
    rows.forEach(row => {
        initProductCodeSearchForRow(row);
    });
}

// تفعيل البحث عن المنتج بالكود لصف محدد
function initProductCodeSearchForRow(row) {
    const productCodeInput = row.querySelector('.product-code');
    if (productCodeInput) {
        // إضافة حدث blur للبحث عن المنتج عند مغادرة الحقل
        productCodeInput.addEventListener('blur', function() {
            const productCode = this.value.trim();
            if (productCode) {
                fetchProductDetails(productCode, row);
            }
        });

        // إضافة زر البحث المرن
        const searchBtn = document.createElement('button');
        searchBtn.type = 'button';
        searchBtn.className = 'btn btn-sm btn-primary search-product-btn ms-2';
        searchBtn.innerHTML = '<i class="fas fa-search"></i>';
        searchBtn.title = 'بحث عن صنف';

        // إضافة الزر بعد حقل الكود
        const parentCell = productCodeInput.parentNode;
        parentCell.appendChild(searchBtn);

        // إضافة حدث النقر على زر البحث
        searchBtn.addEventListener('click', function() {
            showProductSearchModal(row);
        });
    }
}

// جلب بيانات المنتج بالكود
function fetchProductDetails(productCode, row) {
    console.log(`جلب بيانات المنتج: ${productCode}`);

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch('/inventory/api/product-details/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ product_code: productCode })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateRowWithProductDetails(row, data.product);
        } else {
            alert(data.message || 'لم يتم العثور على المنتج');
            clearRowProductDetails(row);
        }
    })
    .catch(error => {
        console.error('خطأ في جلب بيانات المنتج:', error);
        alert('حدث خطأ أثناء جلب بيانات المنتج');
    });
}

/**
 * تحديث صف بالبيانات
 * Updates a row with product details after fetching from the server
 * @param {HTMLElement} row - The table row to update
 * @param {Object} product - The product data object
 */
function updateRowWithProductDetails(row, product) {
    console.log('تحديث الصف بالبيانات:', product);

    // تحديث حقل معرف المنتج
    const productIdInput = row.querySelector('.product-id');
    if (productIdInput) productIdInput.value = product.id;

    // اسم المنتج
    const productNameSpan = row.querySelector('.product-name');
    if (productNameSpan) productNameSpan.textContent = product.name;

    // الرصيد الحالي
    const currentStockSpan = row.querySelector('.current-stock');
    if (currentStockSpan) currentStockSpan.textContent = product.quantity;

    // اسم الوحدة
    const unitNameSpan = row.querySelector('.unit-name');
    if (unitNameSpan) unitNameSpan.textContent = product.unit_name || '';

    // تحديث الحد الأقصى للكمية في حالة إذن الصرف
    const voucherTypeField = document.getElementById('id_voucher_type');
    if (voucherTypeField) {
        const voucherType = voucherTypeField.value;
        const quantityInput = row.querySelector('.quantity');

        if (quantityInput && voucherType !== 'إذن اضافة' && voucherType !== 'اذن مرتجع عميل') {
            quantityInput.max = product.quantity;

            // التأكد من أن القيمة لا تتجاوز الحد الأقصى
            if (parseFloat(quantityInput.value) > product.quantity) {
                quantityInput.value = product.quantity;
            }
        }
    }
}
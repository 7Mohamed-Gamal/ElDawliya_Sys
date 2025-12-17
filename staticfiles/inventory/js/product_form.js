/**
 * product_form.js - JavaScript for the product form functionality
 * Handles product code lookup and auto-fill
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('تم تحميل صفحة نموذج المنتج');

    // تهيئة البحث عن المنتج بالكود
    initProductCodeSearch();

    // تهيئة معاينة الصورة
    initImagePreview();

    // تهيئة ربط حقول الكمية
    initQuantityFieldsSync();

    // تهيئة التحقق من النموذج
    initFormValidation();

    // تهيئة إضافة التصنيف ووحدة القياس
    initCategoryAndUnitAddition();
});

// تهيئة البحث عن المنتج بالكود
function initProductCodeSearch() {
    const productIdField = document.getElementById('id_product_id');

    if (productIdField) {
        // إضافة حدث input للبحث عن المنتج عند كتابة الكود
        productIdField.addEventListener('input', function() {
            const productCode = this.value.trim();
            if (productCode) {
                fetchProductDetails(productCode);
            }
        });

        // إضافة حدث blur للبحث عن المنتج عند مغادرة الحقل
        productIdField.addEventListener('blur', function() {
            const productCode = this.value.trim();
            if (productCode) {
                fetchProductDetails(productCode);
            }
        });
    }
}

// التحقق من صحة كود المنتج
function validateProductCode(productCode) {
    // التحقق من أن الكود ليس فارغًا
    if (!productCode || productCode.trim() === '') {
        return {
            isValid: false,
            message: 'كود المنتج لا يمكن أن يكون فارغًا'
        };
    }

    // التحقق من طول الكود (على الأقل 3 أحرف)
    if (productCode.length < 3) {
        return {
            isValid: false,
            message: 'كود المنتج يجب أن يحتوي على 3 أحرف على الأقل'
        };
    }

    // التحقق من عدم وجود أحرف خاصة غير مسموح بها
    const invalidCharsRegex = /[^\w\d\-_]/;
    if (invalidCharsRegex.test(productCode)) {
        return {
            isValid: false,
            message: 'كود المنتج يحتوي على أحرف غير مسموح بها'
        };
    }

    return {
        isValid: true
    };
}

// جلب بيانات المنتج من الخادم
function fetchProductDetails(productCode) {
    console.log(`جلب بيانات المنتج: ${productCode}`);

    // التحقق من صحة كود المنتج
    const validation = validateProductCode(productCode);
    if (!validation.isValid) {
        showErrorMessage(validation.message);
        return;
    }

    // إظهار مؤشر التحميل
    showLoadingIndicator(true);

    // جلب بيانات المنتج من الخادم
    fetch('/inventory/api/product-details/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({
            product_code: productCode
        })
    })
    .then(response => response.json())
    .then(data => {
        // إخفاء مؤشر التحميل
        showLoadingIndicator(false);

        if (data.success) {
            // تحديث بيانات المنتج في النموذج
            updateProductDetailsInForm(data.product);
            // إظهار رسالة نجاح
            showSuccessMessage(`تم العثور على المنتج: ${data.product.name}`);
        } else {
            // إذا لم يتم العثور على المنتج، نعرض رسالة للمستخدم
            showInfoMessage('لم يتم العثور على منتج بهذا الكود. يمكنك إضافته كمنتج جديد أو البحث عن منتج موجود.');
            // إظهار زر البحث عن المنتجات
            showSearchButton();
        }
    })
    .catch(error => {
        // إخفاء مؤشر التحميل
        showLoadingIndicator(false);
        console.error('خطأ في جلب بيانات المنتج:', error);
        // إظهار رسالة خطأ
        showErrorMessage('حدث خطأ أثناء البحث عن المنتج. يرجى المحاولة مرة أخرى.');
    });
}

// تحديث بيانات المنتج في النموذج
function updateProductDetailsInForm(product) {
    // تحديث حقول المنتج
    const nameField = document.getElementById('id_name');
    const categoryField = document.getElementById('id_category');
    const unitField = document.getElementById('id_unit');
    const initialQuantityField = document.getElementById('id_initial_quantity');
    const quantityField = document.getElementById('id_quantity');
    const unitPriceField = document.getElementById('id_unit_price');
    const minimumThresholdField = document.getElementById('id_minimum_threshold');
    const maximumThresholdField = document.getElementById('id_maximum_threshold');
    const locationField = document.getElementById('id_location');
    const descriptionField = document.getElementById('id_description');

    // تحديث اسم المنتج
    if (nameField) nameField.value = product.name;

    // تحديث التصنيف إذا كان موجودًا
    if (categoryField && product.category_id) {
        // البحث عن الخيار المناسب في القائمة المنسدلة
        const options = categoryField.options;
        for (let i = 0; i < options.length; i++) {
            if (options[i].value == product.category_id) {
                categoryField.selectedIndex = i;
                break;
            }
        }
    }

    // تحديث وحدة القياس إذا كانت موجودة
    if (unitField && product.unit_id) {
        // البحث عن الخيار المناسب في القائمة المنسدلة
        const options = unitField.options;
        for (let i = 0; i < options.length; i++) {
            if (options[i].value == product.unit_id) {
                unitField.selectedIndex = i;
                break;
            }
        }
    }

    // تحديث الكميات
    if (initialQuantityField) initialQuantityField.value = product.initial_quantity || 0;
    if (quantityField) quantityField.value = product.quantity || 0;

    // تحديث سعر الوحدة
    if (unitPriceField) unitPriceField.value = product.unit_price || 0;

    // تحديث الحدود
    if (minimumThresholdField) minimumThresholdField.value = product.minimum_threshold || 0;
    if (maximumThresholdField) maximumThresholdField.value = product.maximum_threshold || 0;

    // تحديث الموقع
    if (locationField) locationField.value = product.location || '';

    // تحديث الوصف
    if (descriptionField) descriptionField.value = product.description || '';

    // تحديث حالة النموذج
    const formStatus = document.getElementById('formStatus');
    if (formStatus) {
        formStatus.textContent = `تم تحميل بيانات المنتج: ${product.name}`;
    }
}

// إظهار أو إخفاء مؤشر التحميل
function showLoadingIndicator(show) {
    const productIdField = document.getElementById('id_product_id');

    if (productIdField) {
        if (show) {
            productIdField.classList.add('loading');
        } else {
            productIdField.classList.remove('loading');
        }
    }
}

// إظهار رسالة خطأ
function showErrorMessage(message) {
    // إنشاء عنصر الرسالة إذا لم يكن موجودًا
    let messageContainer = document.getElementById('product-message-container');
    if (!messageContainer) {
        messageContainer = document.createElement('div');
        messageContainer.id = 'product-message-container';
        messageContainer.className = 'mt-2';

        // إضافة العنصر بعد حقل كود المنتج
        const productIdField = document.getElementById('id_product_id');
        if (productIdField && productIdField.parentNode) {
            productIdField.parentNode.appendChild(messageContainer);
        }
    }

    // تعيين محتوى الرسالة
    messageContainer.innerHTML = `
        <div class="alert alert-danger alert-dismissible fade show" role="alert">
            <i class="fas fa-exclamation-circle me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;

    // إخفاء الرسالة بعد 5 ثوانٍ
    setTimeout(() => {
        const alert = messageContainer.querySelector('.alert');
        if (alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }
    }, 5000);
}

// إظهار رسالة نجاح
function showSuccessMessage(message) {
    // إنشاء عنصر الرسالة إذا لم يكن موجودًا
    let messageContainer = document.getElementById('product-message-container');
    if (!messageContainer) {
        messageContainer = document.createElement('div');
        messageContainer.id = 'product-message-container';
        messageContainer.className = 'mt-2';

        // إضافة العنصر بعد حقل كود المنتج
        const productIdField = document.getElementById('id_product_id');
        if (productIdField && productIdField.parentNode) {
            productIdField.parentNode.appendChild(messageContainer);
        }
    }

    // تعيين محتوى الرسالة
    messageContainer.innerHTML = `
        <div class="alert alert-success alert-dismissible fade show" role="alert">
            <i class="fas fa-check-circle me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;

    // إخفاء الرسالة بعد 5 ثوانٍ
    setTimeout(() => {
        const alert = messageContainer.querySelector('.alert');
        if (alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }
    }, 5000);
}

// إظهار رسالة معلومات
function showInfoMessage(message) {
    // إنشاء عنصر الرسالة إذا لم يكن موجودًا
    let messageContainer = document.getElementById('product-message-container');
    if (!messageContainer) {
        messageContainer = document.createElement('div');
        messageContainer.id = 'product-message-container';
        messageContainer.className = 'mt-2';

        // إضافة العنصر بعد حقل كود المنتج
        const productIdField = document.getElementById('id_product_id');
        if (productIdField && productIdField.parentNode) {
            productIdField.parentNode.appendChild(messageContainer);
        }
    }

    // تعيين محتوى الرسالة
    messageContainer.innerHTML = `
        <div class="alert alert-info alert-dismissible fade show" role="alert">
            <i class="fas fa-info-circle me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;

    // إخفاء الرسالة بعد 8 ثوانٍ
    setTimeout(() => {
        const alert = messageContainer.querySelector('.alert');
        if (alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }
    }, 8000);
}

// إظهار زر البحث عن المنتجات
function showSearchButton() {
    // التحقق من وجود زر البحث
    let searchButton = document.getElementById('product-search-btn');
    if (!searchButton) {
        // إنشاء زر البحث
        searchButton = document.createElement('button');
        searchButton.id = 'product-search-btn';
        searchButton.type = 'button';
        searchButton.className = 'btn btn-primary mt-2';
        searchButton.innerHTML = '<i class="fas fa-search me-2"></i>البحث عن منتج موجود';

        // إضافة حدث النقر لفتح نافذة البحث
        searchButton.addEventListener('click', openProductSearchModal);

        // إضافة الزر بعد حقل كود المنتج
        const productIdField = document.getElementById('id_product_id');
        if (productIdField && productIdField.parentNode) {
            productIdField.parentNode.appendChild(searchButton);
        }
    }
}

// فتح نافذة البحث عن المنتجات
function openProductSearchModal() {
    // فتح النافذة المنبثقة للبحث عن المنتجات
    const productSearchModal = document.getElementById('productSearchModal');
    if (productSearchModal) {
        const modal = new bootstrap.Modal(productSearchModal);
        modal.show();
    } else {
        // إذا لم تكن النافذة موجودة، نقوم بإنشائها
        createProductSearchModal();
    }
}

// إنشاء نافذة البحث عن المنتجات
function createProductSearchModal() {
    // إنشاء عنصر النافذة المنبثقة
    const modalHTML = `
        <div class="modal fade" id="productSearchModal" tabindex="-1" aria-labelledby="productSearchModalLabel" aria-hidden="true" dir="rtl">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header bg-primary text-white">
                        <h5 class="modal-title" id="productSearchModalLabel">
                            <i class="fas fa-search me-2"></i>بحث متقدم عن الأصناف
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <!-- قسم البحث والفلترة -->
                        <div class="search-section mb-3 p-3 bg-light rounded">
                            <div class="row g-2">
                                <!-- بحث بالاسم أو الكود -->
                                <div class="col-md-12 mb-2">
                                    <div class="input-group">
                                        <span class="input-group-text bg-white">
                                            <i class="fas fa-search"></i>
                                        </span>
                                        <input type="text" id="modal-search-input" class="form-control" placeholder="البحث بالاسم أو الرقم أو التصنيف..." autocomplete="off">
                                        <button type="button" id="modal-search-btn" class="btn btn-primary">
                                            بحث
                                        </button>
                                        <button type="button" id="modal-barcode-btn" class="btn btn-secondary">
                                            <i class="fas fa-barcode me-1"></i>مسح الباركود
                                        </button>
                                    </div>
                                    <div class="form-text text-muted">
                                        <i class="fas fa-info-circle me-1"></i>
                                        يمكنك البحث عن طريق كود الصنف، اسم الصنف، التصنيف أو الوحدة
                                    </div>
                                </div>

                                <div class="col-md-12">
                                    <div class="row g-2">
                                        <!-- فلتر التصنيف -->
                                        <div class="col-md-4">
                                            <label for="modal-category-filter" class="form-label mb-1">التصنيف</label>
                                            <select id="modal-category-filter" class="form-select">
                                                <option value="">كل التصنيفات</option>
                                                <!-- سيتم ملؤها ديناميكياً -->
                                            </select>
                                        </div>

                                        <!-- فلتر الوحدة -->
                                        <div class="col-md-4">
                                            <label for="modal-unit-filter" class="form-label mb-1">الوحدة</label>
                                            <select id="modal-unit-filter" class="form-select">
                                                <option value="">كل الوحدات</option>
                                                <!-- سيتم ملؤها ديناميكياً -->
                                            </select>
                                        </div>

                                        <!-- فلتر حالة المخزون -->
                                        <div class="col-md-4">
                                            <label for="modal-stock-filter" class="form-label mb-1">حالة المخزون</label>
                                            <select id="modal-stock-filter" class="form-select">
                                                <option value="">كل الحالات</option>
                                                <option value="available">متوفر</option>
                                                <option value="out">نفذ</option>
                                            </select>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- جدول المنتجات -->
                        <div class="table-responsive">
                            <table class="table table-hover table-striped border" id="modal-products-table">
                                <thead class="table-light">
                                    <tr>
                                        <th>رقم الصنف</th>
                                        <th>اسم الصنف</th>
                                        <th>التصنيف</th>
                                        <th>الرصيد الحالي</th>
                                        <th>وحدة القياس</th>
                                        <th>الإجراءات</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <!-- سيتم ملؤها ديناميكياً -->
                                </tbody>
                            </table>
                        </div>

                        <!-- رسالة عند عدم وجود نتائج -->
                        <div id="no-products-message" class="text-center py-5 d-none">
                            <i class="fas fa-search fa-3x text-muted mb-3"></i>
                            <h6 class="mb-2">لم يتم العثور على أصناف مطابقة</h6>
                            <p class="text-muted mb-0">جرب تغيير كلمات البحث أو إزالة الفلاتر</p>
                        </div>

                        <!-- مؤشر التحميل -->
                        <div id="loading-indicator" class="text-center py-5 d-none">
                            <div class="spinner-border text-primary" role="status">
                                <span class="visually-hidden">جاري التحميل...</span>
                            </div>
                            <p class="mt-3 mb-0">جاري تحميل الأصناف...</p>
                        </div>

                        <!-- قسم قارئ الباركود -->
                        <div id="barcode-scanner-container" class="d-none">
                            <div class="text-center py-3">
                                <h6 class="mb-3">مسح الباركود</h6>
                                <div id="barcode-scanner-preview" class="mx-auto mb-3" style="width: 100%; max-width: 400px; height: 300px; border: 1px solid #ddd; background-color: #f8f9fa; position: relative;">
                                    <video id="barcode-scanner-video" style="width: 100%; height: 100%; object-fit: cover;"></video>
                                    <div id="barcode-scanner-loading" class="position-absolute top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center bg-light bg-opacity-75">
                                        <div class="spinner-border text-primary" role="status">
                                            <span class="visually-hidden">جاري التحميل...</span>
                                        </div>
                                    </div>
                                </div>
                                <p class="text-muted mb-2">ضع الباركود في منتصف الكاميرا للمسح التلقائي</p>
                                <button type="button" id="barcode-scanner-close" class="btn btn-secondary">
                                    <i class="fas fa-times me-1"></i>إغلاق الماسح
                                </button>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer justify-content-between">
                        <div>
                            <button type="button" id="modal-reset-filters" class="btn btn-outline-secondary">
                                <i class="fas fa-redo me-1"></i>إعادة ضبط الفلاتر
                            </button>
                        </div>
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إغلاق</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // إضافة النافذة إلى الصفحة
    document.body.insertAdjacentHTML('beforeend', modalHTML);

    // تهيئة النافذة
    initProductSearchModalFunctionality();
}

// تهيئة وظائف نافذة البحث عن المنتجات
function initProductSearchModalFunctionality() {
    // الحصول على عناصر النافذة
    const modal = document.getElementById('productSearchModal');
    const searchInput = document.getElementById('modal-search-input');
    const searchButton = document.getElementById('modal-search-btn');
    const barcodeButton = document.getElementById('modal-barcode-btn');
    const resetFiltersButton = document.getElementById('modal-reset-filters');
    const categoryFilter = document.getElementById('modal-category-filter');
    const unitFilter = document.getElementById('modal-unit-filter');
    const stockFilter = document.getElementById('modal-stock-filter');
    const productsTable = document.getElementById('modal-products-table');
    const productsTableBody = productsTable.querySelector('tbody');
    const noProductsMessage = document.getElementById('no-products-message');
    const loadingIndicator = document.getElementById('loading-indicator');
    const barcodeScannerContainer = document.getElementById('barcode-scanner-container');
    const barcodeScannerVideo = document.getElementById('barcode-scanner-video');
    const barcodeScannerClose = document.getElementById('barcode-scanner-close');

    // تحميل التصنيفات
    loadCategories();

    // تحميل الوحدات
    loadUnits();

    // إضافة حدث البحث عند النقر على زر البحث
    if (searchButton) {
        searchButton.addEventListener('click', function() {
            searchProducts();
        });
    }

    // إضافة حدث البحث عند الضغط على Enter في حقل البحث
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchProducts();
            }
        });
    }

    // إضافة حدث إعادة ضبط الفلاتر
    if (resetFiltersButton) {
        resetFiltersButton.addEventListener('click', function() {
            resetFilters();
        });
    }

    // إضافة حدث تغيير الفلاتر
    if (categoryFilter) {
        categoryFilter.addEventListener('change', function() {
            searchProducts();
        });
    }

    if (unitFilter) {
        unitFilter.addEventListener('change', function() {
            searchProducts();
        });
    }

    if (stockFilter) {
        stockFilter.addEventListener('change', function() {
            searchProducts();
        });
    }

    // إضافة حدث فتح قارئ الباركود
    if (barcodeButton) {
        barcodeButton.addEventListener('click', function() {
            toggleBarcodeScanner(true);
        });
    }

    // إضافة حدث إغلاق قارئ الباركود
    if (barcodeScannerClose) {
        barcodeScannerClose.addEventListener('click', function() {
            toggleBarcodeScanner(false);
        });
    }

    // تحميل المنتجات عند فتح النافذة
    modal.addEventListener('shown.bs.modal', function() {
        searchProducts();
    });

    // إيقاف قارئ الباركود عند إغلاق النافذة
    modal.addEventListener('hidden.bs.modal', function() {
        stopBarcodeScanner();
    });

    // وظيفة البحث عن المنتجات
    function searchProducts() {
        // إظهار مؤشر التحميل
        loadingIndicator.classList.remove('d-none');
        productsTable.classList.add('d-none');
        noProductsMessage.classList.add('d-none');

        // الحصول على قيم البحث والفلاتر
        const searchTerm = searchInput.value.trim();
        const categoryId = categoryFilter.value;
        const unitId = unitFilter.value;
        const stockStatus = stockFilter.value;

        // إرسال طلب البحث إلى الخادم
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
            loadingIndicator.classList.add('d-none');

            if (data.success && data.products && data.products.length > 0) {
                // عرض جدول المنتجات
                productsTable.classList.remove('d-none');

                // مسح الجدول
                productsTableBody.innerHTML = '';

                // إضافة المنتجات إلى الجدول
                data.products.forEach(product => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${product.product_id}</td>
                        <td>${product.name}</td>
                        <td>${product.category_name || ''}</td>
                        <td>${product.quantity}</td>
                        <td>${product.unit_name || ''}</td>
                        <td>
                            <button type="button" class="btn btn-sm btn-primary select-product" data-product-id="${product.product_id}">
                                <i class="fas fa-check me-1"></i>اختيار
                            </button>
                        </td>
                    `;

                    // إضافة حدث اختيار المنتج
                    const selectButton = row.querySelector('.select-product');
                    if (selectButton) {
                        selectButton.addEventListener('click', function() {
                            const productId = this.getAttribute('data-product-id');
                            selectProduct(productId);
                        });
                    }

                    productsTableBody.appendChild(row);
                });
            } else {
                // عرض رسالة عدم وجود نتائج
                noProductsMessage.classList.remove('d-none');
            }
        })
        .catch(error => {
            console.error('خطأ في البحث عن المنتجات:', error);
            loadingIndicator.classList.add('d-none');
            noProductsMessage.classList.remove('d-none');
        });
    }

    // وظيفة اختيار منتج
    function selectProduct(productId) {
        // إغلاق النافذة
        const modalInstance = bootstrap.Modal.getInstance(modal);
        modalInstance.hide();

        // تعيين كود المنتج في حقل كود المنتج
        const productIdField = document.getElementById('id_product_id');
        if (productIdField) {
            productIdField.value = productId;

            // تشغيل حدث blur لجلب بيانات المنتج
            const event = new Event('blur');
            productIdField.dispatchEvent(event);
        }
    }

    // وظيفة إعادة ضبط الفلاتر
    function resetFilters() {
        searchInput.value = '';
        categoryFilter.value = '';
        unitFilter.value = '';
        stockFilter.value = '';

        // إعادة البحث
        searchProducts();
    }

    // وظيفة تحميل التصنيفات
    function loadCategories() {
        fetch('/inventory/api/categories/')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    categoryFilter.innerHTML = '<option value="">كل التصنيفات</option>';

                    data.categories.forEach(category => {
                        const option = document.createElement('option');
                        option.value = category.id;
                        option.textContent = category.name;
                        categoryFilter.appendChild(option);
                    });
                }
            })
            .catch(error => console.error('خطأ في تحميل التصنيفات:', error));
    }

    // وظيفة تحميل الوحدات
    function loadUnits() {
        fetch('/inventory/api/units/')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    unitFilter.innerHTML = '<option value="">كل الوحدات</option>';

                    data.units.forEach(unit => {
                        const option = document.createElement('option');
                        option.value = unit.id;
                        option.textContent = unit.name;
                        unitFilter.appendChild(option);
                    });
                }
            })
            .catch(error => console.error('خطأ في تحميل الوحدات:', error));
    }

    // وظيفة تبديل عرض قارئ الباركود
    function toggleBarcodeScanner(show) {
        if (show) {
            // إخفاء قسم البحث والجدول
            document.querySelector('.search-section').classList.add('d-none');
            productsTable.classList.add('d-none');
            noProductsMessage.classList.add('d-none');
            loadingIndicator.classList.add('d-none');

            // إظهار قارئ الباركود
            barcodeScannerContainer.classList.remove('d-none');

            // بدء تشغيل قارئ الباركود
            startBarcodeScanner();
        } else {
            // إخفاء قارئ الباركود
            barcodeScannerContainer.classList.add('d-none');

            // إظهار قسم البحث
            document.querySelector('.search-section').classList.remove('d-none');

            // إيقاف قارئ الباركود
            stopBarcodeScanner();

            // إعادة البحث
            searchProducts();
        }
    }

    // متغيرات قارئ الباركود
    let barcodeScanner = null;
    let videoStream = null;

    // وظيفة بدء تشغيل قارئ الباركود
    function startBarcodeScanner() {
        // التحقق من دعم المتصفح للكاميرا
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            alert('المتصفح الخاص بك لا يدعم الوصول إلى الكاميرا');
            toggleBarcodeScanner(false);
            return;
        }

        // إظهار مؤشر التحميل
        document.getElementById('barcode-scanner-loading').classList.remove('d-none');

        // طلب الوصول إلى الكاميرا
        navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } })
            .then(stream => {
                videoStream = stream;
                barcodeScannerVideo.srcObject = stream;
                barcodeScannerVideo.play();

                // إخفاء مؤشر التحميل
                document.getElementById('barcode-scanner-loading').classList.add('d-none');

                // تهيئة قارئ الباركود
                import('https://cdn.jsdelivr.net/npm/@zxing/library@0.19.1/umd/index.min.js')
                    .then(() => {
                        const codeReader = new ZXing.BrowserMultiFormatReader();

                        // بدء المسح المستمر
                        codeReader.decodeFromVideoDevice(null, barcodeScannerVideo, (result, err) => {
                            if (result) {
                                // تم العثور على باركود
                                const barcodeValue = result.getText();
                                console.log('تم مسح الباركود:', barcodeValue);

                                // إيقاف قارئ الباركود
                                stopBarcodeScanner();

                                // إغلاق النافذة
                                const modalInstance = bootstrap.Modal.getInstance(modal);
                                modalInstance.hide();

                                // تعيين كود المنتج في حقل كود المنتج
                                const productIdField = document.getElementById('id_product_id');
                                if (productIdField) {
                                    productIdField.value = barcodeValue;

                                    // تشغيل حدث blur لجلب بيانات المنتج
                                    const event = new Event('blur');
                                    productIdField.dispatchEvent(event);
                                }
                            }

                            if (err && !(err instanceof ZXing.NotFoundException)) {
                                console.error('خطأ في قراءة الباركود:', err);
                            }
                        });

                        barcodeScanner = codeReader;
                    })
                    .catch(error => {
                        console.error('خطأ في تحميل مكتبة قارئ الباركود:', error);
                        alert('حدث خطأ أثناء تحميل مكتبة قارئ الباركود');
                        toggleBarcodeScanner(false);
                    });
            })
            .catch(error => {
                console.error('خطأ في الوصول إلى الكاميرا:', error);
                alert('حدث خطأ أثناء محاولة الوصول إلى الكاميرا');
                toggleBarcodeScanner(false);
            });
    }

    // وظيفة إيقاف قارئ الباركود
    function stopBarcodeScanner() {
        if (barcodeScanner) {
            barcodeScanner.reset();
            barcodeScanner = null;
        }

        if (videoStream) {
            videoStream.getTracks().forEach(track => track.stop());
            videoStream = null;
        }

        if (barcodeScannerVideo) {
            barcodeScannerVideo.srcObject = null;
        }
    }
}

// تهيئة معاينة الصورة
function initImagePreview() {
    const imageInput = document.getElementById('id_image');

    if (imageInput) {
        imageInput.addEventListener('change', function(e) {
            if (this.files && this.files[0]) {
                var reader = new FileReader();

                reader.onload = function(e) {
                    var previewIcon = document.getElementById('preview-icon');
                    var previewImg = document.getElementById('preview-img');

                    if (previewIcon) {
                        previewIcon.style.display = 'none';
                    }

                    if (previewImg) {
                        previewImg.src = e.target.result;
                    } else {
                        previewImg = document.createElement('img');
                        previewImg.id = 'preview-img';
                        previewImg.src = e.target.result;
                        previewImg.style.maxWidth = '100%';
                        previewImg.style.maxHeight = '100%';
                        previewImg.style.objectFit = 'contain';

                        document.querySelector('.image-preview').appendChild(previewImg);
                    }
                }

                reader.readAsDataURL(this.files[0]);
            }
        });
    }
}

// تهيئة ربط حقول الكمية
function initQuantityFieldsSync() {
    const initialQuantityField = document.getElementById('id_initial_quantity');
    const currentQuantityField = document.getElementById('id_quantity');

    if (initialQuantityField && currentQuantityField) {
        // عند تغيير الرصيد الافتتاحي، يتم تحديث الرصيد الحالي
        initialQuantityField.addEventListener('input', function() {
            currentQuantityField.value = this.value;
            console.log(`تم تحديث الرصيد الحالي إلى ${this.value}`);
        });

        // عند تغيير الرصيد الحالي، يتم تحديث الرصيد الافتتاحي (فقط عند إضافة منتج جديد)
        if (!currentQuantityField.hasAttribute('readonly')) {
            currentQuantityField.addEventListener('input', function() {
                initialQuantityField.value = this.value;
                console.log(`تم تحديث الرصيد الافتتاحي إلى ${this.value}`);
            });
        }
    }
}

// تهيئة التحقق من النموذج
function initFormValidation() {
    const form = document.querySelector('form.needs-validation');
    const formStatus = document.getElementById('formStatus');

    if (form) {
        form.addEventListener('submit', function(event) {
            if (formStatus) formStatus.textContent = "جاري التحقق من النموذج...";

            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                if (formStatus) formStatus.textContent = "النموذج غير صالح";
                return;
            }

            // التحقق من وجود رقم الصنف واسم الصنف
            const productId = document.getElementById('id_product_id').value;
            const productName = document.getElementById('id_name').value;

            if (!productId || !productName) {
                event.preventDefault();
                event.stopPropagation();
                alert('يرجى ملء جميع الحقول المطلوبة');
                if (formStatus) formStatus.textContent = "حقول مطلوبة مفقودة";
                return;
            }

            if (formStatus) formStatus.textContent = "جاري إرسال النموذج...";
            form.classList.add('was-validated');
        });
    }
}

// تهيئة إضافة التصنيف ووحدة القياس
function initCategoryAndUnitAddition() {
    // تهيئة إضافة التصنيف
    const saveCategoryBtn = document.getElementById('saveCategoryBtn');
    if (saveCategoryBtn) {
        saveCategoryBtn.addEventListener('click', addNewCategory);
    }

    // تهيئة إضافة وحدة القياس
    const saveUnitBtn = document.getElementById('saveUnitBtn');
    if (saveUnitBtn) {
        saveUnitBtn.addEventListener('click', addNewUnit);
    }
}

// إضافة تصنيف جديد
function addNewCategory() {
    // تنفيذ الكود الموجود في النموذج
}

// إضافة وحدة قياس جديدة
function addNewUnit() {
    // تنفيذ الكود الموجود في النموذج
}

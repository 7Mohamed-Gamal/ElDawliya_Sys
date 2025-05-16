/**
 * voucher_form.js - JavaScript for the voucher form functionality
 * Handles product search, adding/removing items, and form validation
 */

document.addEventListener('DOMContentLoaded', function() {
    // تهيئة النافذة المنبثقة للبحث عن المنتجات
    const productSearchModal = new bootstrap.Modal(document.getElementById('productSearchModal'));

    // معالج بحث المنتجات
    let currentRow = null; // لتخزين الصف الحالي الذي يتم البحث له
    let productsCache = []; // تخزين مؤقت للمنتجات للاستخدام المستقبلي
    let unitsCache = []; // تخزين مؤقت للوحدات للفلترة

    // تحميل التصنيفات للفلتر
    function loadCategories() {
        fetch('/inventory/api/categories/')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const categoryFilter = document.getElementById('modal-category-filter');
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

    // تحميل وحدات القياس للفلتر
    function loadUnits() {
        fetch('/inventory/api/units/')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const unitFilter = document.getElementById('modal-unit-filter');
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
            })
            .catch(error => console.error('خطأ في تحميل الوحدات:', error));
    }

    // تحميل البيانات عند تحميل الصفحة
    loadCategories();
    loadUnits();

    // إضافة صف جديد للأصناف
    const addItemBtn = document.getElementById('add-item-btn');
    if (addItemBtn) {
        addItemBtn.addEventListener('click', function() {
            addNewItemRow();
        });
    }

    // تهيئة صفوف الأصناف الموجودة
    initExistingItemRows();

    // تهيئة زر توليد رقم الإذن
    const generateNumberBtn = document.getElementById('generate-number-btn');
    if (generateNumberBtn) {
        generateNumberBtn.addEventListener('click', function() {
            generateVoucherNumber();
        });
    }

    // تهيئة نموذج الإذن للتحقق قبل الإرسال
    const voucherForm = document.getElementById('voucher-form');
    if (voucherForm) {
        voucherForm.addEventListener('submit', function(e) {
            if (!validateVoucherForm()) {
                e.preventDefault();
            }
        });
    }

    // تهيئة البحث المتقدم عن المنتجات
    initProductSearch();

    // تهيئة التنقل بين الصفوف باستخدام لوحة المفاتيح
    initKeyboardNavigation();
});

// تهيئة صفوف الأصناف الموجودة
function initExistingItemRows() {
    console.log('تهيئة صفوف الأصناف الموجودة');
    const rows = document.querySelectorAll('tr.item-row');
    console.log(`عدد الصفوف الموجودة: ${rows.length}`);

    rows.forEach((row, index) => {
        console.log(`تهيئة الصف رقم ${index + 1}`);
        initItemRow(row);

        // ربط حقل كود المنتج بقائمة الاقتراحات
        const productCodeInput = row.querySelector('.product-code');
        if (productCodeInput && document.getElementById('products-datalist')) {
            productCodeInput.setAttribute('list', 'products-datalist');
        }

        // التحقق من وجود كود منتج مسبق وجلب بياناته
        if (productCodeInput && productCodeInput.value.trim()) {
            console.log(`الصف ${index + 1} يحتوي على كود منتج: ${productCodeInput.value.trim()}`);
            // استدعاء دالة جلب بيانات المنتج بعد تأخير قصير للتأكد من تحميل الصفحة بالكامل
            setTimeout(() => {
                fetchProductDetails(productCodeInput.value.trim(), row);
            }, 500);
        }
    });
}

// تهيئة صف الأصناف
function initItemRow(row) {
    // تهيئة زر الحذف
    const deleteBtn = row.querySelector('.delete-row');
    if (deleteBtn) {
        deleteBtn.addEventListener('click', function() {
            deleteItemRow(row);
        });
    }

    // تهيئة البحث عن المنتج بالكود
    initProductCodeSearchForRow(row);
}

// إضافة صف جديد للأصناف
function addNewItemRow() {
    const table = document.getElementById('items-table');
    const tbody = table.querySelector('tbody');
    const rows = tbody.querySelectorAll('tr.item-row');
    const rowCount = rows.length;

    // تحديث عدد النماذج الكلي
    const totalFormsInput = document.querySelector('input[name="form-TOTAL_FORMS"]');
    totalFormsInput.value = rowCount + 1;

    // إنشاء صف جديد
    const newRow = document.createElement('tr');
    newRow.className = 'item-row';

    // تحديد نوع الإذن
    const voucherType = document.getElementById('id_voucher_type').value;
    const isAddition = voucherType === 'إذن اضافة' || voucherType === 'اذن مرتجع عميل';
    const isDisbursement = voucherType === 'إذن صرف' || voucherType === 'إذن مرتجع مورد';

    // إنشاء محتوى الصف
    let rowHtml = `
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

    // إضافة حقول الكمية حسب نوع الإذن
    if (isAddition) {
        rowHtml += `
            <td>
                <input type="number" class="form-control quantity" name="form-${rowCount}-quantity" value="0" min="0.01" step="0.01" required>
            </td>
        `;
    } else {
        rowHtml += `
            <td>
                <input type="number" class="form-control quantity" name="form-${rowCount}-quantity" value="0" min="0.01" step="0.01" max="0" required>
            </td>
        `;
    }

    // إضافة حقول الماكينة لإذن الصرف
    if (voucherType === 'إذن صرف') {
        rowHtml += `
            <td>
                <input type="text" class="form-control machine-name" name="form-${rowCount}-machine_name" value="">
            </td>
            <td>
                <input type="text" class="form-control machine-unit" name="form-${rowCount}-machine_unit" value="">
            </td>
        `;
    }

    // إضافة زر الحذف
    rowHtml += `
        <td>
            <button type="button" class="btn btn-sm btn-danger delete-row">
                <i class="fas fa-trash"></i>
            </button>
        </td>
    `;

    newRow.innerHTML = rowHtml;
    tbody.appendChild(newRow);

    // تهيئة الصف الجديد
    initItemRow(newRow);

    // ربط حقل كود المنتج بقائمة الاقتراحات
    const productCodeInput = newRow.querySelector('.product-code');
    if (productCodeInput && document.getElementById('products-datalist')) {
        productCodeInput.setAttribute('list', 'products-datalist');
    }

    // تركيز على حقل كود المنتج في الصف الجديد
    if (productCodeInput) {
        setTimeout(() => {
            productCodeInput.focus();
        }, 100);
    }
}

// حذف صف من جدول الأصناف
function deleteItemRow(row) {
    const tbody = row.parentNode;
    const rows = tbody.querySelectorAll('tr.item-row');

    // لا تسمح بحذف الصف الأخير
    if (rows.length <= 1) {
        alert('يجب أن يحتوي الإذن على صنف واحد على الأقل');
        return;
    }

    // حذف الصف
    tbody.removeChild(row);

    // تحديث عدد النماذج الكلي
    const totalFormsInput = document.querySelector('input[name="form-TOTAL_FORMS"]');
    totalFormsInput.value = rows.length - 1;

    // تحديث أسماء الحقول للصفوف المتبقية
    updateRowIndices();
}

// تحديث فهارس الصفوف بعد الحذف
function updateRowIndices() {
    const tbody = document.querySelector('#items-table tbody');
    const rows = tbody.querySelectorAll('tr.item-row');

    rows.forEach((row, index) => {
        // تحديث أسماء الحقول
        const inputs = row.querySelectorAll('input[name^="form-"]');
        inputs.forEach(input => {
            const name = input.getAttribute('name');
            const newName = name.replace(/form-\d+/, `form-${index}`);
            input.setAttribute('name', newName);
        });
    });
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

// تفعيل البحث عن المنتج بالكود لصف محدد
function initProductCodeSearchForRow(row) {
    console.log('تهيئة البحث عن المنتج بالكود للصف:', row);

    const productCodeInput = row.querySelector('.product-code');
    if (productCodeInput) {
        console.log('تم العثور على حقل كود المنتج:', productCodeInput);

        // إضافة حدث change للبحث عن المنتج عند تغيير الكود
        productCodeInput.addEventListener('change', function() {
            const productCode = this.value.trim();
            console.log('تغيير كود المنتج:', productCode);
            if (productCode) {
                fetchProductDetails(productCode, row);
            }
        });

        // إضافة حدث input للبحث عن المنتج عند كتابة الكود
        productCodeInput.addEventListener('input', function() {
            const productCode = this.value.trim();
            console.log('إدخال كود المنتج:', productCode);
            if (productCode && productCode.length >= 3) {
                fetchProductDetails(productCode, row);
            }
        });

        // إضافة حدث blur للبحث عن المنتج عند مغادرة الحقل
        productCodeInput.addEventListener('blur', function() {
            const productCode = this.value.trim();
            console.log('مغادرة حقل كود المنتج:', productCode);
            if (productCode) {
                fetchProductDetails(productCode, row);
            }
        });

        // إضافة حدث keydown للبحث عن المنتج عند الضغط على Enter
        productCodeInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault(); // منع إرسال النموذج
                const productCode = this.value.trim();
                console.log('الضغط على Enter في حقل كود المنتج:', productCode);
                if (productCode) {
                    fetchProductDetails(productCode, row);
                }
            }
        });

        // إضافة زر البحث عن المنتجات
        const searchButton = document.createElement('button');
        searchButton.type = 'button';
        searchButton.className = 'btn btn-sm btn-outline-primary search-product-btn';
        searchButton.innerHTML = '<i class="fas fa-search"></i>';
        searchButton.title = 'البحث عن منتج';
        searchButton.style.position = 'absolute';
        searchButton.style.right = '5px';
        searchButton.style.top = '5px';

        // إضافة حدث النقر لفتح نافذة البحث
        searchButton.addEventListener('click', function() {
            console.log('النقر على زر البحث عن المنتجات');
            openProductSearchModal(row);
        });

        // إضافة الزر بعد حقل كود المنتج
        const inputContainer = productCodeInput.parentNode;
        inputContainer.style.position = 'relative';
        inputContainer.appendChild(searchButton);

        // إضافة زر مسح الباركود
        const barcodeButton = document.createElement('button');
        barcodeButton.type = 'button';
        barcodeButton.className = 'btn btn-sm btn-outline-secondary barcode-scan-btn';
        barcodeButton.innerHTML = '<i class="fas fa-barcode"></i>';
        barcodeButton.title = 'مسح الباركود';
        barcodeButton.style.position = 'absolute';
        barcodeButton.style.right = '40px';
        barcodeButton.style.top = '5px';

        // إضافة حدث النقر لفتح قارئ الباركود
        barcodeButton.addEventListener('click', function() {
            console.log('النقر على زر مسح الباركود');
            openBarcodeScanner(row);
        });

        // إضافة الزر بعد حقل كود المنتج
        inputContainer.appendChild(barcodeButton);

        // ربط حقل كود المنتج بقائمة الاقتراحات
        if (document.getElementById('products-datalist')) {
            productCodeInput.setAttribute('list', 'products-datalist');
            console.log('تم ربط حقل كود المنتج بقائمة الاقتراحات');
        }
    } else {
        console.error('لم يتم العثور على حقل كود المنتج في الصف');
    }
}

// جلب بيانات المنتج من الخادم
function fetchProductDetails(productCode, row) {
    // طباعة معلومات تصحيح الأخطاء
    console.log('جاري البحث عن المنتج بالكود:', productCode);
    console.log('الصف المستهدف:', row);

    // التحقق من وجود الصف
    if (!row) {
        console.error('خطأ: الصف غير محدد');
        return;
    }

    // التحقق من صحة كود المنتج
    const validation = validateProductCode(productCode);
    if (!validation.isValid) {
        showRowError(row, validation.message);
        return;
    }

    // إظهار مؤشر التحميل
    row.classList.add('loading');

    // الحصول على CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    if (!csrfToken) {
        console.error('خطأ: لم يتم العثور على CSRF token');
        row.classList.remove('loading');
        showRowError(row, 'خطأ في الاتصال بالخادم: CSRF token غير موجود');
        return;
    }

    // جلب بيانات المنتج من الخادم
    fetch('/inventory/api/product-details/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken.value
        },
        body: JSON.stringify({
            product_code: productCode
        })
    })
    .then(response => {
        console.log('استجابة الخادم:', response.status);
        return response.json();
    })
    .then(data => {
        // إخفاء مؤشر التحميل
        row.classList.remove('loading');
        console.log('بيانات المنتج المستلمة:', data);

        if (data.success) {
            // تحديث بيانات المنتج في الصف
            updateProductDetailsInRow(row, data.product);
            // إزالة أي رسائل خطأ
            clearRowError(row);
        } else {
            // إظهار رسالة الخطأ
            showRowError(row, 'لم يتم العثور على منتج بهذا الكود');
            // إعادة تعيين حقول المنتج
            resetProductDetailsInRow(row);
        }
    })
    .catch(error => {
        // إخفاء مؤشر التحميل
        row.classList.remove('loading');
        console.error('خطأ في جلب بيانات المنتج:', error);
        // إظهار رسالة الخطأ
        showRowError(row, 'حدث خطأ أثناء البحث عن المنتج');
    });
}

// إظهار رسالة خطأ في الصف
function showRowError(row, message) {
    // إزالة أي رسائل خطأ سابقة
    clearRowError(row);

    // إنشاء عنصر الرسالة
    const errorMessage = document.createElement('div');
    errorMessage.className = 'row-error-message text-danger small mt-1';
    errorMessage.textContent = message;

    // إضافة الرسالة بعد حقل كود المنتج
    const productCodeInput = row.querySelector('.product-code');
    if (productCodeInput && productCodeInput.parentNode) {
        productCodeInput.parentNode.appendChild(errorMessage);
    }

    // إضافة فئة الخطأ إلى حقل الإدخال
    if (productCodeInput) {
        productCodeInput.classList.add('is-invalid');
    }
}

// إزالة رسالة الخطأ من الصف
function clearRowError(row) {
    // إزالة عنصر الرسالة
    const errorMessage = row.querySelector('.row-error-message');
    if (errorMessage && errorMessage.parentNode) {
        errorMessage.parentNode.removeChild(errorMessage);
    }

    // إزالة فئة الخطأ من حقل الإدخال
    const productCodeInput = row.querySelector('.product-code');
    if (productCodeInput) {
        productCodeInput.classList.remove('is-invalid');
    }
}

// إعادة تعيين بيانات المنتج في الصف
function resetProductDetailsInRow(row) {
    // إعادة تعيين حقول المنتج
    const productIdInput = row.querySelector('.product-id');
    const productNameSpan = row.querySelector('.product-name');
    const currentStockSpan = row.querySelector('.current-stock');
    const unitNameSpan = row.querySelector('.unit-name');

    if (productIdInput) productIdInput.value = '';
    if (productNameSpan) productNameSpan.textContent = '';
    if (currentStockSpan) currentStockSpan.textContent = '0';
    if (unitNameSpan) unitNameSpan.textContent = '';
}

// تحديث بيانات المنتج في الصف
function updateProductDetailsInRow(row, product) {
    console.log('تحديث بيانات المنتج في الصف:', product);

    // تحديث حقول المنتج
    const productIdInput = row.querySelector('.product-id');
    const productNameSpan = row.querySelector('.product-name');
    const currentStockSpan = row.querySelector('.current-stock');
    const unitNameSpan = row.querySelector('.unit-name');
    const quantityInput = row.querySelector('.quantity');

    // تحديث حقول الماكينة إذا كانت موجودة
    const machineNameInput = row.querySelector('.machine-name');
    const machineUnitInput = row.querySelector('.machine-unit');

    console.log('العناصر التي تم العثور عليها:');
    console.log('productIdInput:', productIdInput);
    console.log('productNameSpan:', productNameSpan);
    console.log('currentStockSpan:', currentStockSpan);
    console.log('unitNameSpan:', unitNameSpan);
    console.log('quantityInput:', quantityInput);

    if (productIdInput) {
        productIdInput.value = product.id;
        console.log('تم تحديث معرف المنتج:', product.id);
    }

    if (productNameSpan) {
        productNameSpan.textContent = product.name;
        console.log('تم تحديث اسم المنتج:', product.name);
    }

    if (currentStockSpan) {
        currentStockSpan.textContent = product.quantity;
        console.log('تم تحديث الرصيد الحالي:', product.quantity);
    }

    if (unitNameSpan) {
        unitNameSpan.textContent = product.unit_name;
        console.log('تم تحديث اسم الوحدة:', product.unit_name);
    }

    // تحديث الحد الأقصى للكمية في حالة إذن الصرف
    const voucherType = document.getElementById('id_voucher_type').value;
    if ((voucherType === 'إذن صرف' || voucherType === 'إذن مرتجع مورد') && quantityInput) {
        quantityInput.max = product.quantity;
        console.log('تم تحديث الحد الأقصى للكمية:', product.quantity);
    }

    // تركيز على حقل الكمية بعد تحديث بيانات المنتج
    if (quantityInput) {
        // تعيين قيمة افتراضية للكمية (1) إذا كانت الكمية الحالية صفر
        if (parseFloat(quantityInput.value) === 0) {
            quantityInput.value = "1";
            console.log('تم تعيين قيمة افتراضية للكمية: 1');
        }
        // تركيز على حقل الكمية
        setTimeout(() => {
            quantityInput.focus();
            quantityInput.select();
            console.log('تم التركيز على حقل الكمية');
        }, 100);
    }
}

// توليد رقم إذن جديد
function generateVoucherNumber() {
    const voucherType = document.getElementById('id_voucher_type').value;

    fetch('/inventory/api/generate-voucher-number/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({
            voucher_type: voucherType
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('id_voucher_number').value = data.voucher_number;
        } else {
            console.error('خطأ في توليد رقم الإذن:', data.message);
        }
    })
    .catch(error => {
        console.error('خطأ في توليد رقم الإذن:', error);
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

    // التحقق من صحة بيانات الأصناف
    let isValid = true;
    rows.forEach((row, index) => {
        const productCode = row.querySelector('.product-code').value.trim();
        const productId = row.querySelector('.product-id').value.trim();
        const quantity = parseFloat(row.querySelector('.quantity').value);

        if (!productCode) {
            alert(`يرجى إدخال كود الصنف للصف ${index + 1}`);
            row.querySelector('.product-code').focus();
            isValid = false;
            return;
        }

        if (!productId) {
            alert(`يرجى التأكد من صحة كود الصنف للصف ${index + 1}`);
            row.querySelector('.product-code').focus();
            isValid = false;
            return;
        }

        if (isNaN(quantity) || quantity <= 0) {
            alert(`يرجى إدخال كمية صحيحة للصف ${index + 1}`);
            row.querySelector('.quantity').focus();
            isValid = false;
            return;
        }
    });

    return isValid;
}

// تهيئة البحث المتقدم عن المنتجات
function initProductSearch() {
    console.log('تهيئة البحث المتقدم عن المنتجات');

    // إنشاء نافذة البحث عن المنتجات إذا لم تكن موجودة
    if (!document.getElementById('productSearchModal')) {
        createProductSearchModal();
    }

    // إنشاء قائمة الاقتراحات للمنتجات
    createProductsDatalist();

    // إضافة مستمع للأحداث للتعامل مع تغييرات قائمة الاقتراحات
    document.addEventListener('input', function(e) {
        if (e.target.classList.contains('product-code')) {
            const row = e.target.closest('tr.item-row');
            const productCode = e.target.value.trim();

            console.log('تم تغيير قيمة حقل كود المنتج:', productCode);

            if (productCode && productCode.length >= 3) {
                // تأخير قصير لتجنب الطلبات المتكررة
                clearTimeout(e.target.searchTimeout);
                e.target.searchTimeout = setTimeout(() => {
                    fetchProductDetails(productCode, row);
                }, 300);
            }
        }
    });
}

// إنشاء قائمة الاقتراحات للمنتجات
function createProductsDatalist() {
    console.log('إنشاء قائمة الاقتراحات للمنتجات');

    // التحقق من عدم وجود قائمة اقتراحات سابقة
    if (!document.getElementById('products-datalist')) {
        // إنشاء عنصر datalist
        const datalist = document.createElement('datalist');
        datalist.id = 'products-datalist';
        document.body.appendChild(datalist);

        // الحصول على CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        if (!csrfToken) {
            console.error('خطأ: لم يتم العثور على CSRF token');
            return;
        }

        console.log('جاري جلب بيانات المنتجات لقائمة الاقتراحات');

        // جلب بيانات المنتجات لملء قائمة الاقتراحات
        fetch('/inventory/api/products-search/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken.value
            },
            body: JSON.stringify({
                search_term: '',
                category_id: '',
                unit_id: '',
                stock_status: ''
            })
        })
        .then(response => {
            console.log('استجابة الخادم لقائمة المنتجات:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('تم استلام بيانات المنتجات:', data.success, data.products ? data.products.length : 0);

            if (data.success && data.products && data.products.length > 0) {
                // تخزين المنتجات في الذاكرة المؤقتة
                productsCache = data.products;

                console.log(`إضافة ${data.products.length} منتج إلى قائمة الاقتراحات`);

                // إضافة المنتجات إلى قائمة الاقتراحات
                data.products.forEach(product => {
                    const option = document.createElement('option');
                    option.value = product.product_id;
                    option.textContent = `${product.name} (${product.product_id})`;
                    datalist.appendChild(option);
                });

                // ربط حقول كود المنتج بقائمة الاقتراحات
                const productCodeInputs = document.querySelectorAll('.product-code');
                console.log(`ربط ${productCodeInputs.length} حقل كود منتج بقائمة الاقتراحات`);

                productCodeInputs.forEach(input => {
                    input.setAttribute('list', 'products-datalist');
                });

                // تحديث الصفوف الموجودة التي تحتوي على كود منتج
                const rows = document.querySelectorAll('tr.item-row');
                rows.forEach(row => {
                    const productCodeInput = row.querySelector('.product-code');
                    if (productCodeInput && productCodeInput.value.trim()) {
                        // البحث عن المنتج في الذاكرة المؤقتة
                        const productCode = productCodeInput.value.trim();
                        const product = productsCache.find(p => p.product_id === productCode);

                        if (product) {
                            console.log(`تحديث بيانات المنتج ${productCode} من الذاكرة المؤقتة`);
                            // تحديث بيانات المنتج في الصف
                            updateProductDetailsInRow(row, product);
                        }
                    }
                });
            }
        })
        .catch(error => {
            console.error('خطأ في جلب بيانات المنتجات:', error);
        });
    }
}

// فتح نافذة البحث عن المنتجات
function openProductSearchModal(row) {
    // تعيين الصف الحالي
    currentRow = row;

    // فتح النافذة المنبثقة للبحث عن المنتجات
    const productSearchModal = document.getElementById('productSearchModal');
    if (productSearchModal) {
        const modal = new bootstrap.Modal(productSearchModal);
        modal.show();
    }
}

// فتح قارئ الباركود
function openBarcodeScanner(row) {
    // تعيين الصف الحالي
    currentRow = row;

    // فتح النافذة المنبثقة لقارئ الباركود
    const barcodeScannerModal = document.getElementById('barcodeScannerModal');
    if (barcodeScannerModal) {
        const modal = new bootstrap.Modal(barcodeScannerModal);
        modal.show();

        // بدء تشغيل قارئ الباركود
        startBarcodeScanner();
    } else {
        // إنشاء نافذة قارئ الباركود
        createBarcodeScannerModal();
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

// إنشاء نافذة قارئ الباركود
function createBarcodeScannerModal() {
    // إنشاء عنصر النافذة المنبثقة
    const modalHTML = `
        <div class="modal fade" id="barcodeScannerModal" tabindex="-1" aria-labelledby="barcodeScannerModalLabel" aria-hidden="true" dir="rtl">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header bg-primary text-white">
                        <h5 class="modal-title" id="barcodeScannerModalLabel">
                            <i class="fas fa-barcode me-2"></i>مسح الباركود
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <!-- قسم قارئ الباركود -->
                        <div id="barcode-scanner-container">
                            <div class="text-center py-3">
                                <div id="barcode-scanner-preview" class="mx-auto mb-3" style="width: 100%; max-width: 400px; height: 300px; border: 1px solid #ddd; background-color: #f8f9fa; position: relative;">
                                    <video id="barcode-scanner-video" style="width: 100%; height: 100%; object-fit: cover;"></video>
                                    <div id="barcode-scanner-loading" class="position-absolute top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center bg-light bg-opacity-75">
                                        <div class="spinner-border text-primary" role="status">
                                            <span class="visually-hidden">جاري التحميل...</span>
                                        </div>
                                    </div>
                                </div>
                                <p class="text-muted mb-2">ضع الباركود في منتصف الكاميرا للمسح التلقائي</p>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إغلاق</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // إضافة النافذة إلى الصفحة
    document.body.insertAdjacentHTML('beforeend', modalHTML);

    // تهيئة النافذة
    initBarcodeScannerModalFunctionality();
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
            // إغلاق نافذة البحث
            const modalInstance = bootstrap.Modal.getInstance(modal);
            modalInstance.hide();

            // فتح قارئ الباركود
            openBarcodeScanner(currentRow);
        });
    }

    // تحميل المنتجات عند فتح النافذة
    modal.addEventListener('shown.bs.modal', function() {
        searchProducts();
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
        if (currentRow) {
            const productCodeInput = currentRow.querySelector('.product-code');
            if (productCodeInput) {
                productCodeInput.value = productId;

                // تشغيل حدث blur لجلب بيانات المنتج
                const event = new Event('blur');
                productCodeInput.dispatchEvent(event);
            }
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
}

// تهيئة وظائف نافذة قارئ الباركود
function initBarcodeScannerModalFunctionality() {
    // الحصول على عناصر النافذة
    const modal = document.getElementById('barcodeScannerModal');

    // إيقاف قارئ الباركود عند إغلاق النافذة
    modal.addEventListener('hidden.bs.modal', function() {
        stopBarcodeScanner();
    });

    // بدء تشغيل قارئ الباركود عند فتح النافذة
    modal.addEventListener('shown.bs.modal', function() {
        startBarcodeScanner();
    });
}

// تهيئة التنقل بين الصفوف باستخدام لوحة المفاتيح
function initKeyboardNavigation() {
    // إضافة مستمع للأحداث على مستوى الصفحة
    document.addEventListener('keydown', function(e) {
        // التحقق من أن المستخدم ليس في حقل نصي أو منطقة نص
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
            // إذا كان المستخدم في حقل كمية وضغط على Enter
            if (e.key === 'Enter' && e.target.classList.contains('quantity')) {
                e.preventDefault();

                // الحصول على الصف الحالي
                const currentRow = e.target.closest('tr.item-row');
                if (!currentRow) return;

                // الحصول على جميع الصفوف
                const rows = Array.from(document.querySelectorAll('tr.item-row'));
                const currentIndex = rows.indexOf(currentRow);

                // إذا كان هذا هو الصف الأخير، أضف صفًا جديدًا وانتقل إليه
                if (currentIndex === rows.length - 1) {
                    addNewItemRow();

                    // الحصول على الصف الجديد (آخر صف)
                    setTimeout(() => {
                        const newRows = document.querySelectorAll('tr.item-row');
                        const newRow = newRows[newRows.length - 1];
                        if (newRow) {
                            const productCodeInput = newRow.querySelector('.product-code');
                            if (productCodeInput) {
                                productCodeInput.focus();
                            }
                        }
                    }, 100);
                } else {
                    // الانتقال إلى الصف التالي
                    const nextRow = rows[currentIndex + 1];
                    if (nextRow) {
                        const productCodeInput = nextRow.querySelector('.product-code');
                        if (productCodeInput) {
                            productCodeInput.focus();
                        }
                    }
                }
            }

            // إذا كان المستخدم في حقل كود المنتج وضغط على السهم لأسفل
            if (e.key === 'ArrowDown' && e.target.classList.contains('product-code')) {
                e.preventDefault();

                // الحصول على الصف الحالي
                const currentRow = e.target.closest('tr.item-row');
                if (!currentRow) return;

                // الحصول على جميع الصفوف
                const rows = Array.from(document.querySelectorAll('tr.item-row'));
                const currentIndex = rows.indexOf(currentRow);

                // الانتقال إلى الصف التالي
                if (currentIndex < rows.length - 1) {
                    const nextRow = rows[currentIndex + 1];
                    if (nextRow) {
                        const productCodeInput = nextRow.querySelector('.product-code');
                        if (productCodeInput) {
                            productCodeInput.focus();
                        }
                    }
                }
            }

            // إذا كان المستخدم في حقل كود المنتج وضغط على السهم لأعلى
            if (e.key === 'ArrowUp' && e.target.classList.contains('product-code')) {
                e.preventDefault();

                // الحصول على الصف الحالي
                const currentRow = e.target.closest('tr.item-row');
                if (!currentRow) return;

                // الحصول على جميع الصفوف
                const rows = Array.from(document.querySelectorAll('tr.item-row'));
                const currentIndex = rows.indexOf(currentRow);

                // الانتقال إلى الصف السابق
                if (currentIndex > 0) {
                    const prevRow = rows[currentIndex - 1];
                    if (prevRow) {
                        const productCodeInput = prevRow.querySelector('.product-code');
                        if (productCodeInput) {
                            productCodeInput.focus();
                        }
                    }
                }
            }

            // إذا كان المستخدم في حقل الكمية وضغط على السهم لأسفل
            if (e.key === 'ArrowDown' && e.target.classList.contains('quantity')) {
                e.preventDefault();

                // الحصول على الصف الحالي
                const currentRow = e.target.closest('tr.item-row');
                if (!currentRow) return;

                // الحصول على جميع الصفوف
                const rows = Array.from(document.querySelectorAll('tr.item-row'));
                const currentIndex = rows.indexOf(currentRow);

                // الانتقال إلى الصف التالي
                if (currentIndex < rows.length - 1) {
                    const nextRow = rows[currentIndex + 1];
                    if (nextRow) {
                        const quantityInput = nextRow.querySelector('.quantity');
                        if (quantityInput) {
                            quantityInput.focus();
                            quantityInput.select();
                        }
                    }
                }
            }

            // إذا كان المستخدم في حقل الكمية وضغط على السهم لأعلى
            if (e.key === 'ArrowUp' && e.target.classList.contains('quantity')) {
                e.preventDefault();

                // الحصول على الصف الحالي
                const currentRow = e.target.closest('tr.item-row');
                if (!currentRow) return;

                // الحصول على جميع الصفوف
                const rows = Array.from(document.querySelectorAll('tr.item-row'));
                const currentIndex = rows.indexOf(currentRow);

                // الانتقال إلى الصف السابق
                if (currentIndex > 0) {
                    const prevRow = rows[currentIndex - 1];
                    if (prevRow) {
                        const quantityInput = prevRow.querySelector('.quantity');
                        if (quantityInput) {
                            quantityInput.focus();
                            quantityInput.select();
                        }
                    }
                }
            }
        }
    });
}

// متغيرات قارئ الباركود
let barcodeScanner = null;
let videoStream = null;

// وظيفة بدء تشغيل قارئ الباركود
function startBarcodeScanner() {
    // التحقق من دعم المتصفح للكاميرا
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert('المتصفح الخاص بك لا يدعم الوصول إلى الكاميرا');
        return;
    }

    // إظهار مؤشر التحميل
    const loadingIndicator = document.getElementById('barcode-scanner-loading');
    if (loadingIndicator) {
        loadingIndicator.classList.remove('d-none');
    }

    // طلب الوصول إلى الكاميرا
    navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } })
        .then(stream => {
            videoStream = stream;
            const barcodeScannerVideo = document.getElementById('barcode-scanner-video');
            if (barcodeScannerVideo) {
                barcodeScannerVideo.srcObject = stream;
                barcodeScannerVideo.play();
            }

            // إخفاء مؤشر التحميل
            if (loadingIndicator) {
                loadingIndicator.classList.add('d-none');
            }

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
                            const barcodeScannerModal = document.getElementById('barcodeScannerModal');
                            if (barcodeScannerModal) {
                                const modalInstance = bootstrap.Modal.getInstance(barcodeScannerModal);
                                modalInstance.hide();
                            }

                            // تعيين كود المنتج في حقل كود المنتج
                            if (currentRow) {
                                const productCodeInput = currentRow.querySelector('.product-code');
                                if (productCodeInput) {
                                    productCodeInput.value = barcodeValue;

                                    // تشغيل حدث blur لجلب بيانات المنتج
                                    const event = new Event('blur');
                                    productCodeInput.dispatchEvent(event);
                                }
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
                });
        })
        .catch(error => {
            console.error('خطأ في الوصول إلى الكاميرا:', error);
            alert('حدث خطأ أثناء محاولة الوصول إلى الكاميرا');

            // إخفاء مؤشر التحميل
            if (loadingIndicator) {
                loadingIndicator.classList.add('d-none');
            }
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

    const barcodeScannerVideo = document.getElementById('barcode-scanner-video');
    if (barcodeScannerVideo) {
        barcodeScannerVideo.srcObject = null;
    }
}

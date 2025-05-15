// وظائف نموذج الإذن - Voucher Form Functions

document.addEventListener('DOMContentLoaded', function() {
    console.log('تم تحميل صفحة نموذج الإذن');

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
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

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
    const voucherType =

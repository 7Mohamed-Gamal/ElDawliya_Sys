/**
 * تحسينات نموذج الإذن - Voucher Form Enhancements
 * يقوم بتحميل ملفات JavaScript المحسنة وحقن الميزات الإضافية إلى الصفحة
 */

(function() {
    // تحميل ملفات JavaScript المحسنة
    function loadScript(src, callback) {
        const script = document.createElement('script');
        script.src = src;
        script.onload = callback || function() {};
        document.head.appendChild(script);
    }

    // حذف سكريبت البحث القديم غير المدعوم للفلترة حسب الوحدة
    function removeOldSearchScript() {
        // تحديد جميع النصوص البرمجية المضمنة
        const scripts = document.querySelectorAll('script:not([src])');
        
        // البحث عن النص البرمجي الذي يحتوي على وظائف البحث القديمة
        scripts.forEach(script => {
            // البحث عن المحتوى الذي يحتوي على وظيفة البحث عن المنتجات
            if (script.textContent.includes('searchProducts') && 
                script.textContent.includes('showProductSearchModal') && 
                !script.textContent.includes('modal-unit-filter')) {
                // إزالة العنصر من DOM
                script.remove();
            }
        });
    }

    // تحميل ملفات JavaScript المحسنة بالترتيب
    document.addEventListener('DOMContentLoaded', function() {
        // حذف سكريبت البحث القديم
        removeOldSearchScript();
        
        console.log('جاري تحميل تحسينات نموذج الإذن...');
        
        // تحميل ملف تعديل الـ API أولاً
        loadScript('/static/inventory/js/api_patch.js', function() {
            // ثم تحميل ملف البحث المحسن
            loadScript('/static/inventory/js/product_search_enhanced.js', function() {
                console.log('تم تحميل جميع تحسينات نموذج الإذن بنجاح');
            });
        });
    });
})();

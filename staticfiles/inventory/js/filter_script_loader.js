/**
 * مُحمِّل سكريبتات الفلترة المحسنة
 * Script Loader for Enhanced Filtering
 */

// تنفيذ الدالة فورًا عند تحميل السكريبت
(function() {
    console.log('تحميل سكريبتات الفلترة المحسنة...');

    // تحميل ملفات السكريبت المطلوبة
    loadRequiredScripts();

    /**
     * تحميل السكريبتات المطلوبة
     */
    function loadRequiredScripts() {
        // التحقق من وجود معايير البحث المتقدم
        if (!document.getElementById('productSearchModal')) {
            console.log('لا يوجد نافذة بحث على هذه الصفحة');
            return;
        }

        // تحميل سكريبت واجهة برمجة التطبيقات (API)
        loadScript('/static/inventory/js/api_patch.js', function() {
            // بعد تحميل سكريبت API، قم بتحميل سكريبت البحث المحسن
            loadScript('/static/inventory/js/product_search_enhanced.js', function() {
                console.log('تم تحميل جميع سكريبتات الفلترة المحسنة بنجاح');

                // تأخير قصير قبل تهيئة واجهة الفلترة
                setTimeout(enhanceFilterUI, 300);
            });
        });
    }

    /**
     * تحميل سكريبت خارجي مع وظيفة استدعاء
     * @param {string} src - مسار السكريبت
     * @param {Function} callback - الدالة المستدعاة عند اكتمال التحميل
     */
    function loadScript(src, callback) {
        // التحقق مما إذا كان السكريبت محملاً بالفعل
        if (isScriptLoaded(src)) {
            if (callback) callback();
            return;
        }

        // إنشاء عنصر السكريبت وتحميله
        const script = document.createElement('script');
        script.src = src;
        script.onload = callback || function() {};
        
        // إضافة السكريبت إلى رأس الصفحة
        document.head.appendChild(script);
    }

    /**
     * التحقق مما إذا كان السكريبت محملاً بالفعل
     * @param {string} src - مسار السكريبت
     * @returns {boolean} - ما إذا كان السكريبت محملاً أم لا
     */
    function isScriptLoaded(src) {
        const scripts = document.getElementsByTagName('script');
        for (let i = 0; i < scripts.length; i++) {
            if (scripts[i].src.includes(src)) {
                return true;
            }
        }
        return false;
    }

    /**
     * تحسين واجهة الفلترة
     */
    function enhanceFilterUI() {
        // التحقق من وجود عناصر واجهة الفلترة
        const unitFilter = document.getElementById('modal-unit-filter');
        const searchButton = document.getElementById('modal-search-btn');
        
        if (!unitFilter || !searchButton) {
            console.warn('لم يتم العثور على عناصر واجهة الفلترة');
            return;
        }

        // البحث عن وإلغاء السكريبتات القديمة التي قد تتعارض مع النسخة المحسنة
        removeConflictingScripts();

        // تأكيد أن عملية التحسين تمت بنجاح
        console.log('تم تحسين واجهة الفلترة بنجاح');
    }

    /**
     * إزالة النصوص البرمجية المتعارضة
     */
    function removeConflictingScripts() {
        // البحث عن النصوص البرمجية المضمنة التي تحتوي على وظائف البحث القديمة
        const scripts = document.querySelectorAll('script:not([src])');
        let oldScriptRemoved = false;
        
        scripts.forEach(script => {
          if (script.textContent.includes('function searchProducts()') && 
            script.textContent.includes('modal-category-filter') && 
            !script.textContent.includes('loadUnits')) {
            
            // إزالة النصوص البرمجية القديمة لتجنب التعارض
            script.remove();
            oldScriptRemoved = true;
            console.log('تم إزالة نص برمجي قديم');
          }
        });
        
        // الإبلاغ عما إذا تم العثور على نصوص برمجية قديمة وإزالتها
        if (!oldScriptRemoved) {
          console.log('لم يتم العثور على نصوص برمجية قديمة للإزالة');
        }
    }
})();

// إعلام عن اكتمال تحميل السكريبت
console.log('تم تحميل محمل سكريبتات الفلترة');

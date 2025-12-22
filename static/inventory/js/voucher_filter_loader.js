/**
 * محمل ميزات الفلترة المحسنة - Enhanced Filter Loader
 * يقوم بتحميل ملفات JavaScript الخاصة بميزات الفلترة المحسنة تلقائيًا
 */

// إضافة سكريبت تحميل تلقائي يتم تنفيذه بمجرد تحميل الصفحة
(function() {
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

    // دالة محاولة تحميل ميزات الفلترة المحسنة
    function tryLoadEnhancedFilters() {
        // تحديد ما إذا كانت الصفحة هي نموذج الإذن
        if (document.querySelector('#productSearchModal')) {
            console.log('تم اكتشاف نموذج الإذن - جاري تحميل ميزات الفلترة المحسنة');
            
            // إزالة تعريف حقل وحدة القياس القديم
            document.addEventListener('DOMContentLoaded', function() {
                // التحقق من وجود زر البحث القديم
                var scriptTags = document.querySelectorAll('script:not([src])');
                for (var i = 0; i < scriptTags.length; i++) {
                    var scriptContent = scriptTags[i].textContent;
                    if (scriptContent && scriptContent.includes('searchProducts') && !scriptContent.includes('modal-unit-filter')) {
                        console.log('تم اكتشاف سكريبت البحث القديم - جاري تحميل الميزات المحسنة');
                        loadEnhancedScripts();
                        break;
                    }
                }
            });
        }
    }

    // تحميل ملفات الفلترة المحسنة
    function loadEnhancedScripts() {
        // تحميل ملف تعديل الـ API أولاً
        loadScript('/static/inventory/js/api_patch.js', function() {
            // ثم تحميل ملف البحث المحسن
            loadScript('/static/inventory/js/product_search_enhanced.js', function() {
                console.log('تم تحميل جميع ملفات الفلترة المحسنة بنجاح');
            });
        });
    }

    // إضافة السكريبت الحالي إلى الصفحة تلقائيًا
    function autoInjectLoader() {
        // إنشاء عنصر السكريبت الجديد
        var script = document.createElement('script');
        script.src = '/static/inventory/js/voucher_filter_loader.js';
        
        // البحث عن العنصر المناسب لإضافة السكريبت بعده
        var targetScript = document.querySelector('script[src*="voucher_form.js"]');
        if (targetScript) {
            // إضافة السكريبت بعد سكريبت نموذج الإذن
            targetScript.parentNode.insertBefore(script, targetScript.nextSibling);
            console.log('تم حقن محمل ميزات الفلترة المحسنة تلقائيًا');
        } else {
            // إضافة السكريبت في نهاية body إذا لم يتم العثور على سكريبت نموذج الإذن
            document.body.appendChild(script);
            console.log('تم إضافة محمل ميزات الفلترة المحسنة إلى نهاية الصفحة');
        }
    }

    // تنفيذ محاولة التحميل
    tryLoadEnhancedFilters();

    // إضافة السكريبت الحالي إلى الصفحة تلقائيًا
    if (document.readyState === 'complete' || document.readyState === 'interactive') {
        setTimeout(autoInjectLoader, 1000); // تأخير التنفيذ قليلاً للتأكد من تحميل العناصر الأخرى
    } else {
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(autoInjectLoader, 1000);
        });
    }
})();

// تنبيه: هذا السكريبت يحقن نفسه تلقائيًا في الصفحة
console.log('تم تحميل ملف محمل ميزات الفلترة المحسنة');

// إذا كانت الصفحة تحتوي على نموذج البحث، تحقق من حالة السكريبت وقم بإعادة التحميل إذا لزم الأمر
if (document.querySelector('#productSearchModal')) {
    // تحميل ملفات الفلترة المحسنة إذا لم تكن محملة بالفعل
    if (!window.enhancedFiltersLoaded) {
        // تحميل ملف تعديل الـ API أولاً
        var apiPatchScript = document.createElement('script');
        apiPatchScript.src = '/static/inventory/js/api_patch.js';
        
        apiPatchScript.onload = function() {
            // ثم تحميل ملف البحث المحسن
            var searchEnhancedScript = document.createElement('script');
            searchEnhancedScript.src = '/static/inventory/js/product_search_enhanced.js';
            
            searchEnhancedScript.onload = function() {
                window.enhancedFiltersLoaded = true;
                console.log('تم تحميل جميع ملفات الفلترة المحسنة بنجاح');
            };
            
            document.head.appendChild(searchEnhancedScript);
        };
        
        document.head.appendChild(apiPatchScript);
    }
}

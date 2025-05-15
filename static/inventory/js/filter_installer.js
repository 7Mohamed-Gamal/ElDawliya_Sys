/**
 * مثبت ميزة الفلترة - Filter Feature Installer
 * يقوم بتحميل ميزات الفلترة المحسنة تلقائيًا
 */

// تنفيذ الدالة فورًا عند تحميل السكريبت
(function() {
    // تحميل ميزات الفلترة المحسنة بعد تحميل الصفحة
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", loadFilterFeatures);
    } else {
        loadFilterFeatures();
    }
    
    // دالة تحميل ميزات الفلترة
    function loadFilterFeatures() {
        // التحقق إذا كان هناك نافذة منبثقة للبحث عن المنتجات
        if (!document.getElementById('productSearchModal')) {
            console.log('لا يوجد نافذة بحث على هذه الصفحة');
            return;
        }
        
        console.log('جاري تحميل ميزات الفلترة المحسنة...');
        
        // دالة لتحميل السكريبتات المطلوبة
        function loadScript(src) {
            return new Promise((resolve, reject) => {
                if (isScriptLoaded(src)) {
                    resolve();
                    return;
                }

                const script = document.createElement('script');
                script.src = src;
                script.onload = resolve;
                script.onerror = reject;
                document.head.appendChild(script);
            });
        }
        
        // التحقق ما إذا كان السكريبت محملًا بالفعل
        function isScriptLoaded(src) {
            const scripts = document.getElementsByTagName('script');
            for (let i = 0; i < scripts.length; i++) {
                if (scripts[i].src.includes(src)) {
                    return true;
                }
            }
            return false;
        }
        
        // تحميل السكريبتات المطلوبة بالترتيب
        loadScript('/static/inventory/js/api_patch.js')
            .then(() => loadScript('/static/inventory/js/product_search_enhanced.js'))
            .then(() => {
                console.log('تم تحميل جميع ميزات الفلترة المحسنة بنجاح');
                // إضافة زر تحديث لتحديث الفلاتر إذا كان البحث لا يعمل بشكل صحيح
                addRefreshButton();
            })
            .catch(error => {
                console.error('خطأ في تحميل ميزات الفلترة المحسنة:', error);
            });
    }

    // إضافة زر تحديث إلى الواجهة
    function addRefreshButton() {
        const filterContainer = document.querySelector('.search-section .row');
        if (!filterContainer || document.getElementById('refresh-filters-btn')) {
            return;
        }
        
        const refreshBtn = document.createElement('button');
        refreshBtn.id = 'refresh-filters-btn';
        refreshBtn.type = 'button';
        refreshBtn.className = 'btn btn-sm btn-info mt-2';
        refreshBtn.innerHTML = '<i class="fas fa-sync-alt me-1"></i> تحديث الفلاتر';
        
        refreshBtn.addEventListener('click', function() {
            // إعادة تحميل الفلاتر
            window.location.reload();
        });
        
        filterContainer.after(refreshBtn);
    }
})();

// إعلام بتحميل السكريبت
console.log('تم تحميل سكريبت مثبت ميزة الفلترة');

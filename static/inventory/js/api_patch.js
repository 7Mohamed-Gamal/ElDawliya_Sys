/**
 * تعديلات API - API Patches 
 * يضيف دعم الفلترة حسب وحدة القياس لنقاط نهاية API الحالية
 * Adds unit filtering support for existing API endpoints
 */

(function() {
    // الفانكشن الأصلية لجلب التفاصيل
    const originalFetch = window.fetch;
    
    // تعديل الفانكشن fetch لاعتراض الطلبات إلى API
    window.fetch = function(url, options) {
        // اعتراض طلبات البحث عن المنتجات فقط
        if (url.includes('/api/products-search/') || url.includes('/api/search-products/')) {
            // إذا كان هناك خيارات وبيانات body
            if (options && options.body) {
                try {
                    // تحليل البيانات
                    const data = JSON.parse(options.body);
                    
                    // استخراج معرف الوحدة من النموذج إذا كان موجوداً
                    const unitFilterElement = document.getElementById('modal-unit-filter');
                    const unitId = unitFilterElement ? unitFilterElement.value : '';
                    
                    // إضافة معرف الوحدة للبيانات إذا كان موجوداً
                    if (unitId) {
                        data.unit_id = unitId;
                        
                        // إعادة تحويل البيانات إلى سلسلة JSON
                        options.body = JSON.stringify(data);
                    }
                } catch (error) {
                    console.error('خطأ في تعديل طلب البحث عن المنتجات:', error);
                }
            }
        }
        
        // تنفيذ الطلب الأصلي مع الخيارات المعدلة
        return originalFetch(url, options);
    };
    
    // معالجة نتائج البحث بناءً على الفلترة حسب الوحدة
    function filterResultsByUnit(results, unitId) {
        if (!unitId || !results || !Array.isArray(results)) return results;
        
        // فلترة النتائج حسب الوحدة
        return results.filter(product => {
            const productUnitId = product.unit_id;
            return productUnitId == unitId; // استخدام == للمقارنة بين القيم النصية والرقمية
        });
    }
    
    // كشف وجود الفانكشن المعدلة
    console.log('تم تحميل تعديلات API بنجاح');
})();

document.addEventListener('DOMContentLoaded', function() {
    console.log('صفحة التحميل جاهزة');

    // مثال: تنبيه عند إدخال كمية أقل من الحد الأدنى
    const stockInputs = document.querySelectorAll('.stock-input');
    stockInputs.forEach(input => {
        input.addEventListener('change', function() {
            const minThreshold = parseFloat(this.getAttribute('data-min'));
            const currentValue = parseFloat(this.value);
            if (currentValue < minThreshold) {
                alert('تحذير: الكمية أقل من الحد الأدنى!');
            }
        });
    });

    // مثال: تأكيد الحذف
    const deleteButtons = document.querySelectorAll('.delete-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            if (!confirm('هل أنت متأكد من الحذف؟')) {
                event.preventDefault();
            }
        });
    });
});
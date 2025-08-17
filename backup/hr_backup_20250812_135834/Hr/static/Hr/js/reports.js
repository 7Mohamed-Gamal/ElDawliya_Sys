/**
 * نظام التقارير الشامل - JavaScript
 */

class ReportSystem {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
        this.initializeComponents();
    }

    bindEvents() {
        // تحديث الفلاتر عند تغيير القسم
        $(document).on('change', '#department_id', (e) => {
            this.updateEmployeeFilter(e.target.value);
        });

        // تحديث التواريخ الافتراضية
        $(document).on('change', '#report_type', (e) => {
            this.setDefaultDates(e.target.value);
        });

        // معاينة التقرير
        $(document).on('click', '.preview-report', (e) => {
            e.preventDefault();
            this.previewReport(e.target.dataset.templateId);
        });

        // تحديث حالة التقرير
        $(document).on('click', '.refresh-status', (e) => {
            e.preventDefault();
            this.refreshReportStatus(e.target.dataset.instanceId);
        });

        // مشاركة التقرير
        $(document).on('click', '.share-report', (e) => {
            e.preventDefault();
            this.showShareModal(e.target.dataset.instanceId);
        });

        // حذف التقرير
        $(document).on('click', '.delete-report', (e) => {
            e.preventDefault();
            this.deleteReport(e.target.dataset.instanceId);
        });

        // البحث في القوالب
        $(document).on('input', '#template-search', (e) => {
            this.searchTemplates(e.target.value);
        });

        // فلترة القوالب
        $(document).on('change', '.template-filter', (e) => {
            this.filterTemplates();
        });
    }

    initializeComponents() {
        // تهيئة التواريخ الافتراضية
        this.setDefaultDates();
        
        // تهيئة الرسوم البيانية
        this.initCharts();
        
        // تهيئة الجداول
        this.initTables();
        
        // تهيئة التحديث التلقائي
        this.initAutoRefresh();
    }

    updateEmployeeFilter(departmentId) {
        const employeeSelect = $('#employee_id');
        if (!employeeSelect.length) return;

        // إظهار مؤشر التحميل
        employeeSelect.prop('disabled', true);
        employeeSelect.html('<option value="">جاري التحميل...</option>');

        // جلب الموظفين
        $.ajax({
            url: '/Hr/api/employees/',
            data: { department: departmentId },
            success: (data) => {
                let options = '<option value="">جميع الموظفين</option>';
                data.results.forEach(employee => {
                    options += `<option value="${employee.id}">${employee.full_name}</option>`;
                });
                employeeSelect.html(options);
            },
            error: () => {
                employeeSelect.html('<option value="">خطأ في التحميل</option>');
            },
            complete: () => {
                employeeSelect.prop('disabled', false);
            }
        });
    }

    setDefaultDates(reportType = null) {
        const dateFrom = $('#date_from');
        const dateTo = $('#date_to');
        
        if (!dateFrom.length || !dateTo.length) return;

        const today = new Date();
        const thirtyDaysAgo = new Date(today.getTime() - (30 * 24 * 60 * 60 * 1000));
        const oneYearAgo = new Date(today.getTime() - (365 * 24 * 60 * 60 * 1000));

        let fromDate = thirtyDaysAgo;
        
        // تحديد التاريخ الافتراضي حسب نوع التقرير
        switch (reportType) {
            case 'attendance':
                fromDate = thirtyDaysAgo;
                break;
            case 'leave':
                fromDate = oneYearAgo;
                break;
            case 'payroll':
                // للرواتب، استخدم بداية الشهر الحالي
                fromDate = new Date(today.getFullYear(), today.getMonth(), 1);
                break;
            default:
                fromDate = thirtyDaysAgo;
        }

        dateFrom.val(this.formatDate(fromDate));
        dateTo.val(this.formatDate(today));
    }

    formatDate(date) {
        return date.toISOString().split('T')[0];
    }

    previewReport(templateId) {
        // جمع بيانات النموذج
        const formData = this.collectFormData();
        
        // إظهار مؤشر التحميل
        this.showLoading('جاري إنشاء معاينة التقرير...');

        $.ajax({
            url: `/Hr/reports/preview/${templateId}/`,
            method: 'POST',
            data: formData,
            success: (data) => {
                this.showPreviewModal(data);
            },
            error: (xhr) => {
                this.showError('فشل في إنشاء معاينة التقرير');
            },
            complete: () => {
                this.hideLoading();
            }
        });
    }

    collectFormData() {
        const form = $('#reportForm');
        const formData = {};
        
        form.find('input, select, textarea').each(function() {
            const $this = $(this);
            const name = $this.attr('name');
            const value = $this.val();
            
            if (name && value) {
                formData[name] = value;
            }
        });
        
        return formData;
    }

    showPreviewModal(data) {
        const modal = $('#previewModal');
        if (!modal.length) {
            // إنشاء المودال إذا لم يكن موجوداً
            this.createPreviewModal();
        }
        
        $('#previewContent').html(data.html);
        modal.modal('show');
    }

    createPreviewModal() {
        const modalHtml = `
            <div class="modal fade" id="previewModal" tabindex="-1">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">معاينة التقرير</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div id="previewContent"></div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إغلاق</button>
                            <button type="button" class="btn btn-primary" onclick="reportSystem.generateReport()">
                                إنتاج التقرير
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        $('body').append(modalHtml);
    }

    generateReport() {
        const form = $('#reportForm');
        
        // إظهار مؤشر التحميل
        this.showLoading('جاري إنتاج التقرير...');
        
        // إرسال النموذج
        form.submit();
    }

    refreshReportStatus(instanceId) {
        const statusElement = $(`.status-${instanceId}`);
        const refreshButton = $(`.refresh-${instanceId}`);
        
        // إظهار مؤشر التحميل
        refreshButton.html('<i class="fas fa-spinner fa-spin"></i>');
        
        $.ajax({
            url: `/Hr/reports/status/${instanceId}/`,
            success: (data) => {
                statusElement.html(this.getStatusBadge(data.status));
                
                if (data.status === 'completed') {
                    // إضافة رابط التحميل
                    const downloadLink = `<a href="/Hr/reports/download/${instanceId}/" class="btn btn-sm btn-success ms-2">
                        <i class="fas fa-download"></i> تحميل
                    </a>`;
                    statusElement.after(downloadLink);
                    refreshButton.hide();
                } else if (data.status === 'failed') {
                    statusElement.after(`<small class="text-danger d-block">${data.error_message}</small>`);
                    refreshButton.hide();
                }
            },
            error: () => {
                this.showError('فشل في تحديث حالة التقرير');
            },
            complete: () => {
                refreshButton.html('<i class="fas fa-sync-alt"></i>');
            }
        });
    }

    getStatusBadge(status) {
        const badges = {
            'pending': '<span class="badge bg-warning">في الانتظار</span>',
            'processing': '<span class="badge bg-info">قيد المعالجة</span>',
            'completed': '<span class="badge bg-success">مكتمل</span>',
            'failed': '<span class="badge bg-danger">فشل</span>',
            'cancelled': '<span class="badge bg-secondary">ملغي</span>'
        };
        
        return badges[status] || '<span class="badge bg-secondary">غير معروف</span>';
    }

    showShareModal(instanceId) {
        // جلب قائمة المستخدمين
        $.ajax({
            url: '/Hr/api/users/',
            success: (data) => {
                this.createShareModal(instanceId, data.results);
            },
            error: () => {
                this.showError('فشل في جلب قائمة المستخدمين');
            }
        });
    }

    createShareModal(instanceId, users) {
        let userOptions = '';
        users.forEach(user => {
            userOptions += `<option value="${user.id}">${user.full_name || user.username}</option>`;
        });

        const modalHtml = `
            <div class="modal fade" id="shareModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">مشاركة التقرير</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <form method="post" action="/Hr/reports/share/${instanceId}/">
                            <div class="modal-body">
                                <div class="mb-3">
                                    <label for="shared_with" class="form-label">مشاركة مع</label>
                                    <select class="form-select" id="shared_with" name="shared_with" multiple required>
                                        ${userOptions}
                                    </select>
                                </div>
                                <div class="mb-3">
                                    <label for="message" class="form-label">رسالة (اختياري)</label>
                                    <textarea class="form-control" id="message" name="message" rows="3"></textarea>
                                </div>
                                <div class="mb-3">
                                    <label for="expires_days" class="form-label">انتهاء الصلاحية (أيام)</label>
                                    <input type="number" class="form-control" id="expires_days" name="expires_days" value="30" min="1" max="365">
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إلغاء</button>
                                <button type="submit" class="btn btn-primary">مشاركة</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        `;
        
        // إزالة المودال السابق إن وجد
        $('#shareModal').remove();
        
        // إضافة المودال الجديد
        $('body').append(modalHtml);
        
        // تهيئة Select2 للمستخدمين
        $('#shared_with').select2({
            placeholder: 'اختر المستخدمين',
            allowClear: true
        });
        
        // إظهار المودال
        $('#shareModal').modal('show');
    }

    deleteReport(instanceId) {
        if (!confirm('هل أنت متأكد من حذف هذا التقرير؟')) {
            return;
        }

        $.ajax({
            url: `/Hr/reports/delete/${instanceId}/`,
            method: 'DELETE',
            success: () => {
                $(`.report-row-${instanceId}`).fadeOut(() => {
                    $(`.report-row-${instanceId}`).remove();
                });
                this.showSuccess('تم حذف التقرير بنجاح');
            },
            error: () => {
                this.showError('فشل في حذف التقرير');
            }
        });
    }

    searchTemplates(query) {
        const templates = $('.template-card');
        
        if (!query) {
            templates.show();
            return;
        }

        templates.each(function() {
            const $this = $(this);
            const title = $this.find('.template-title').text().toLowerCase();
            const description = $this.find('.template-description').text().toLowerCase();
            
            if (title.includes(query.toLowerCase()) || description.includes(query.toLowerCase())) {
                $this.show();
            } else {
                $this.hide();
            }
        });
    }

    filterTemplates() {
        const category = $('#category-filter').val();
        const type = $('#type-filter').val();
        const templates = $('.template-card');

        templates.each(function() {
            const $this = $(this);
            let show = true;

            if (category && $this.data('category') !== category) {
                show = false;
            }

            if (type && $this.data('type') !== type) {
                show = false;
            }

            if (show) {
                $this.show();
            } else {
                $this.hide();
            }
        });
    }

    initCharts() {
        // رسم بياني لإحصائيات التقارير
        const ctx = document.getElementById('reportsChart');
        if (ctx) {
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['مكتملة', 'قيد المعالجة', 'فشلت'],
                    datasets: [{
                        data: [65, 25, 10],
                        backgroundColor: ['#1cc88a', '#36b9cc', '#e74a3b']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        }
    }

    initTables() {
        // تهيئة جداول البيانات
        $('.data-table').DataTable({
            language: {
                url: '/static/js/datatables-arabic.json'
            },
            responsive: true,
            pageLength: 25,
            order: [[0, 'desc']]
        });
    }

    initAutoRefresh() {
        // تحديث تلقائي لحالة التقارير كل 30 ثانية
        setInterval(() => {
            $('.refresh-status').each(function() {
                const instanceId = $(this).data('instanceId');
                const status = $(this).closest('tr').find('.status-badge').data('status');
                
                if (status === 'pending' || status === 'processing') {
                    this.refreshReportStatus(instanceId);
                }
            });
        }, 30000);
    }

    showLoading(message = 'جاري التحميل...') {
        const loadingHtml = `
            <div id="loadingOverlay" class="position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center" 
                 style="background: rgba(0,0,0,0.5); z-index: 9999;">
                <div class="bg-white p-4 rounded shadow text-center">
                    <div class="spinner-border text-primary mb-3" role="status"></div>
                    <div>${message}</div>
                </div>
            </div>
        `;
        
        $('body').append(loadingHtml);
    }

    hideLoading() {
        $('#loadingOverlay').remove();
    }

    showSuccess(message) {
        this.showAlert('success', message);
    }

    showError(message) {
        this.showAlert('danger', message);
    }

    showAlert(type, message) {
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show position-fixed" 
                 style="top: 20px; right: 20px; z-index: 9999; min-width: 300px;">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        $('body').append(alertHtml);
        
        // إزالة التنبيه تلقائياً بعد 5 ثوان
        setTimeout(() => {
            $('.alert').fadeOut();
        }, 5000);
    }

    // دوال مساعدة للتصدير
    exportToExcel(data, filename) {
        const ws = XLSX.utils.json_to_sheet(data);
        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, 'التقرير');
        XLSX.writeFile(wb, `${filename}.xlsx`);
    }

    exportToPDF(elementId, filename) {
        const element = document.getElementById(elementId);
        const opt = {
            margin: 1,
            filename: `${filename}.pdf`,
            image: { type: 'jpeg', quality: 0.98 },
            html2canvas: { scale: 2 },
            jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
        };
        
        html2pdf().set(opt).from(element).save();
    }

    printReport(elementId) {
        const printWindow = window.open('', '_blank');
        const element = document.getElementById(elementId);
        
        printWindow.document.write(`
            <html>
                <head>
                    <title>طباعة التقرير</title>
                    <link href="/static/Hr/css/reports.css" rel="stylesheet">
                    <style>
                        body { font-family: 'Cairo', sans-serif; }
                        @media print {
                            .no-print { display: none !important; }
                        }
                    </style>
                </head>
                <body>
                    ${element.innerHTML}
                </body>
            </html>
        `);
        
        printWindow.document.close();
        printWindow.print();
    }
}

// تهيئة النظام عند تحميل الصفحة
$(document).ready(function() {
    window.reportSystem = new ReportSystem();
});

// دوال عامة للاستخدام في القوالب
function addToFavorites(templateId) {
    window.reportSystem.addToFavorites(templateId);
}

function removeFromFavorites(favoriteId) {
    window.reportSystem.removeFromFavorites(favoriteId);
}

function shareReport(instanceId) {
    window.reportSystem.showShareModal(instanceId);
}

function deleteReport(instanceId) {
    window.reportSystem.deleteReport(instanceId);
}

function refreshStatus(instanceId) {
    window.reportSystem.refreshReportStatus(instanceId);
}

function previewReport(templateId) {
    window.reportSystem.previewReport(templateId);
}
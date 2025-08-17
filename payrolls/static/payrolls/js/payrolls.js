// Payroll Management System JavaScript Functions

// Global variables
let currentModal = null;
let payrollChart = null;
let salaryChart = null;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializePayrollSystem();
});

// Main initialization function
function initializePayrollSystem() {
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize form validation
    initializeFormValidation();
    
    // Initialize salary calculations
    initializeSalaryCalculations();
    
    // Initialize real-time updates
    initializeRealTimeUpdates();
    
    // Initialize keyboard shortcuts
    initializeKeyboardShortcuts();
    
    // Initialize date validations
    initializeDateValidations();
}

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Initialize form validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
}

// Initialize salary calculations
function initializeSalaryCalculations() {
    const salaryInputs = document.querySelectorAll('input[type="number"]');
    
    salaryInputs.forEach(input => {
        if (input.name && input.name.includes('salary') || 
            input.name.includes('allow') || 
            input.name.includes('deduction')) {
            input.addEventListener('input', function() {
                calculateSalaryTotal();
            });
        }
    });
    
    // Currency change handler
    const currencySelects = document.querySelectorAll('select[name="currency"]');
    currencySelects.forEach(select => {
        select.addEventListener('change', function() {
            updateCurrencyDisplay();
            calculateSalaryTotal();
        });
    });
}

// Initialize real-time updates
function initializeRealTimeUpdates() {
    // Update time every minute
    setInterval(updateCurrentTime, 60000);
    
    // Refresh data every 10 minutes
    setInterval(refreshDashboardData, 600000);
}

// Initialize keyboard shortcuts
function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', function(event) {
        // Ctrl + N for new salary
        if (event.ctrlKey && event.key === 'n') {
            event.preventDefault();
            openNewSalaryModal();
        }
        
        // Ctrl + R for new payroll run
        if (event.ctrlKey && event.key === 'r') {
            event.preventDefault();
            openNewPayrollRunModal();
        }
        
        // Escape to close modals
        if (event.key === 'Escape' && currentModal) {
            currentModal.hide();
        }
    });
}

// Initialize date validations
function initializeDateValidations() {
    const effectiveDateInputs = document.querySelectorAll('input[name="effective_date"]');
    const endDateInputs = document.querySelectorAll('input[name="end_date"]');
    
    effectiveDateInputs.forEach(input => {
        input.addEventListener('change', function() {
            validateDateRange(this);
        });
    });
    
    endDateInputs.forEach(input => {
        input.addEventListener('change', function() {
            validateDateRange(this);
        });
    });
}

// Update current time display
function updateCurrentTime() {
    const timeElements = document.querySelectorAll('.current-time');
    const now = new Date();
    const timeString = now.toLocaleTimeString('ar-EG', {
        hour: '2-digit',
        minute: '2-digit'
    });
    
    timeElements.forEach(element => {
        element.textContent = timeString;
    });
}

// Refresh dashboard data
function refreshDashboardData() {
    if (window.location.pathname.includes('dashboard')) {
        fetch(window.location.href, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            updateDashboardStats(data);
        })
        .catch(error => {
            console.error('Error refreshing data:', error);
        });
    }
}

// Update dashboard statistics
function updateDashboardStats(data) {
    if (data.stats) {
        Object.keys(data.stats).forEach(key => {
            const element = document.querySelector(`[data-stat="${key}"]`);
            if (element) {
                element.textContent = data.stats[key];
            }
        });
    }
}

// Calculate salary total
function calculateSalaryTotal() {
    const basicSalary = parseFloat(document.getElementById('modal_basic_salary')?.value) || 0;
    const housingAllow = parseFloat(document.getElementById('modal_housing_allow')?.value) || 0;
    const transport = parseFloat(document.getElementById('modal_transport')?.value) || 0;
    const otherAllow = parseFloat(document.getElementById('modal_other_allow')?.value) || 0;
    const gosiDeduction = parseFloat(document.getElementById('modal_gosi_deduction')?.value) || 0;
    const taxDeduction = parseFloat(document.getElementById('modal_tax_deduction')?.value) || 0;
    
    const totalAllowances = basicSalary + housingAllow + transport + otherAllow;
    const totalDeductions = gosiDeduction + taxDeduction;
    const netSalary = totalAllowances - totalDeductions;
    
    const currency = document.getElementById('modal_currency')?.value || 'SAR';
    
    const calculationElement = document.getElementById('total_calculation');
    if (calculationElement) {
        calculationElement.innerHTML = `
            <div class="row">
                <div class="col-md-4">
                    <strong>إجمالي البدلات:</strong><br>
                    <span class="text-success salary-amount">${formatCurrency(totalAllowances, currency)}</span>
                </div>
                <div class="col-md-4">
                    <strong>إجمالي الخصومات:</strong><br>
                    <span class="text-danger salary-amount">${formatCurrency(totalDeductions, currency)}</span>
                </div>
                <div class="col-md-4">
                    <strong>صافي الراتب:</strong><br>
                    <span class="text-primary net-salary">${formatCurrency(netSalary, currency)}</span>
                </div>
            </div>
        `;
        
        // Add glow effect for high salaries
        if (netSalary > 15000) {
            calculationElement.classList.add('money-glow');
        } else {
            calculationElement.classList.remove('money-glow');
        }
    }
}

// Update currency display
function updateCurrencyDisplay() {
    const currency = document.getElementById('modal_currency')?.value || 'SAR';
    const currencyElements = document.querySelectorAll('.currency-display');
    
    currencyElements.forEach(element => {
        element.textContent = currency;
    });
}

// Validate date range
function validateDateRange(input) {
    const form = input.closest('form');
    if (!form) return;
    
    const effectiveDate = form.querySelector('input[name="effective_date"]')?.value;
    const endDate = form.querySelector('input[name="end_date"]')?.value;
    
    if (effectiveDate && endDate) {
        if (new Date(endDate) <= new Date(effectiveDate)) {
            showNotification('تاريخ الانتهاء يجب أن يكون بعد تاريخ السريان', 'warning');
            input.value = '';
        }
    }
}

// Open new salary modal
function openNewSalaryModal() {
    const modal = document.getElementById('addSalaryModal');
    if (modal) {
        currentModal = new bootstrap.Modal(modal);
        
        // Set today's date as default
        const dateInput = modal.querySelector('input[name="effective_date"]');
        if (dateInput) {
            dateInput.value = new Date().toISOString().split('T')[0];
        }
        
        currentModal.show();
    }
}

// Open new payroll run modal
function openNewPayrollRunModal() {
    const modal = document.getElementById('newPayrollRunModal');
    if (modal) {
        currentModal = new bootstrap.Modal(modal);
        
        // Set current month and today's date as defaults
        const now = new Date();
        const monthInput = modal.querySelector('input[name="month_year"]');
        const dateInput = modal.querySelector('input[name="run_date"]');
        
        if (monthInput) {
            const currentMonth = now.getFullYear() + '-' + String(now.getMonth() + 1).padStart(2, '0');
            monthInput.value = currentMonth;
        }
        
        if (dateInput) {
            dateInput.value = now.toISOString().split('T')[0];
        }
        
        currentModal.show();
    }
}

// Submit salary
function submitSalary() {
    const form = document.getElementById('addSalaryForm');
    if (!form) return;
    
    const formData = new FormData(form);
    
    // Show loading state
    const submitBtn = document.querySelector('#addSalaryModal .btn-info');
    const originalText = submitBtn.textContent;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>جاري الحفظ...';
    submitBtn.disabled = true;
    
    fetch(getSalaryCreateUrl(), {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('تم حفظ الراتب بنجاح', 'success');
            currentModal.hide();
            setTimeout(() => location.reload(), 1000);
        } else {
            showNotification('حدث خطأ: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('حدث خطأ في الاتصال', 'error');
    })
    .finally(() => {
        // Reset button state
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    });
}

// Submit payroll run
function submitPayrollRun() {
    const form = document.getElementById('newPayrollRunForm');
    if (!form) return;
    
    const formData = new FormData(form);
    
    // Show loading state
    const submitBtn = document.querySelector('#newPayrollRunModal .btn-info');
    const originalText = submitBtn.textContent;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>جاري التشغيل...';
    submitBtn.disabled = true;
    
    fetch(getPayrollRunCreateUrl(), {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('تم إنشاء تشغيل الرواتب بنجاح', 'success');
            currentModal.hide();
            setTimeout(() => location.reload(), 1000);
        } else {
            showNotification('حدث خطأ: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('حدث خطأ في الاتصال', 'error');
    })
    .finally(() => {
        // Reset button state
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    });
}

// Confirm payroll run
function confirmPayrollRun(runId) {
    if (confirm('هل أنت متأكد من تأكيد هذا التشغيل؟ لن يمكن التراجع عن هذا الإجراء.')) {
        fetch(getConfirmPayrollRunUrl(runId), {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('تم تأكيد التشغيل بنجاح', 'success');
                setTimeout(() => location.reload(), 1000);
            } else {
                showNotification('حدث خطأ: ' + data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('حدث خطأ في الاتصال', 'error');
        });
    }
}

// Show notification
function showNotification(message, type = 'info') {
    const alertClass = type === 'success' ? 'alert-success' : 
                      type === 'error' ? 'alert-danger' : 
                      type === 'warning' ? 'alert-warning' : 'alert-info';
    
    const alertHtml = `
        <div class="alert ${alertClass} alert-dismissible fade show position-fixed" 
             style="top: 20px; right: 20px; z-index: 9999; min-width: 300px;" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', alertHtml);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const alert = document.querySelector('.alert:last-of-type');
        if (alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }
    }, 5000);
}

// Get CSRF token
function getCSRFToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : '';
}

// Get URLs (these should be set by templates)
function getSalaryCreateUrl() {
    return window.salaryCreateUrl || '/payrolls/salary/add/';
}

function getPayrollRunCreateUrl() {
    return window.payrollRunCreateUrl || '/payrolls/runs/create/';
}

function getConfirmPayrollRunUrl(runId) {
    return window.confirmPayrollRunUrl ? 
           window.confirmPayrollRunUrl.replace('0', runId) : 
           `/payrolls/runs/${runId}/confirm/`;
}

// Format currency
function formatCurrency(amount, currency = 'SAR') {
    const formatted = parseFloat(amount).toFixed(2);
    
    switch (currency) {
        case 'SAR':
            return `${formatted} ر.س`;
        case 'USD':
            return `$${formatted}`;
        case 'EUR':
            return `€${formatted}`;
        default:
            return `${formatted} ${currency}`;
    }
}

// Get salary range class
function getSalaryRangeClass(amount) {
    if (amount < 5000) return 'salary-low';
    if (amount < 10000) return 'salary-medium';
    if (amount < 20000) return 'salary-high';
    return 'salary-very-high';
}

// Export functions
function exportToExcel(url, params = {}) {
    const queryString = new URLSearchParams(params);
    queryString.set('export', 'excel');
    window.location.href = `${url}?${queryString.toString()}`;
}

function exportToPDF(url, params = {}) {
    const queryString = new URLSearchParams(params);
    queryString.set('export', 'pdf');
    window.location.href = `${url}?${queryString.toString()}`;
}

// Chart functions
function initializeCharts() {
    // Initialize salary distribution chart
    const salaryCtx = document.getElementById('salaryDistributionChart');
    if (salaryCtx && window.chartData) {
        salaryChart = new Chart(salaryCtx.getContext('2d'), {
            type: 'doughnut',
            data: window.chartData.salary,
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                    }
                }
            }
        });
    }
    
    // Initialize payroll trend chart
    const payrollCtx = document.getElementById('payrollTrendChart');
    if (payrollCtx && window.chartData) {
        payrollChart = new Chart(payrollCtx.getContext('2d'), {
            type: 'line',
            data: window.chartData.payroll,
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
}

// Utility functions
function calculateNetSalary(basicSalary, allowances, deductions) {
    const totalAllowances = basicSalary + (allowances || 0);
    const totalDeductions = deductions || 0;
    return Math.max(0, totalAllowances - totalDeductions);
}

function calculateTaxDeduction(grossSalary, taxRate = 0.05) {
    return grossSalary * taxRate;
}

function calculateGosiDeduction(basicSalary, gosiRate = 0.10) {
    return basicSalary * gosiRate;
}

// Search and filter functions
function searchTable(inputId, tableId) {
    const input = document.getElementById(inputId);
    const table = document.getElementById(tableId);
    
    if (!input || !table) return;
    
    const filter = input.value.toLowerCase();
    const rows = table.getElementsByTagName('tr');
    
    for (let i = 1; i < rows.length; i++) {
        const row = rows[i];
        const cells = row.getElementsByTagName('td');
        let found = false;
        
        for (let j = 0; j < cells.length; j++) {
            const cell = cells[j];
            if (cell.textContent.toLowerCase().indexOf(filter) > -1) {
                found = true;
                break;
            }
        }
        
        row.style.display = found ? '' : 'none';
    }
}

// Print functions
function printReport() {
    window.print();
}

function printPayslip(payslipId) {
    window.open(`/payrolls/payslips/${payslipId}/print/`, '_blank');
}

function printPayrollRun(runId) {
    window.open(`/payrolls/runs/${runId}/print/`, '_blank');
}

// Payroll calculations
function calculateOvertimePay(regularHours, overtimeHours, hourlyRate, overtimeRate = 1.5) {
    const regularPay = regularHours * hourlyRate;
    const overtimePay = overtimeHours * hourlyRate * overtimeRate;
    return regularPay + overtimePay;
}

function calculateAnnualBonus(basicSalary, performanceRating, bonusPercentage = 0.1) {
    const baseBonus = basicSalary * bonusPercentage;
    const performanceMultiplier = performanceRating / 100;
    return baseBonus * performanceMultiplier;
}

// Payroll validation
function validatePayrollData(payrollData) {
    const errors = [];
    
    if (!payrollData.employee_id) {
        errors.push('معرف الموظف مطلوب');
    }
    
    if (!payrollData.basic_salary || payrollData.basic_salary <= 0) {
        errors.push('الراتب الأساسي يجب أن يكون أكبر من صفر');
    }
    
    if (payrollData.effective_date && payrollData.end_date) {
        if (new Date(payrollData.end_date) <= new Date(payrollData.effective_date)) {
            errors.push('تاريخ الانتهاء يجب أن يكون بعد تاريخ السريان');
        }
    }
    
    return errors;
}

// Salary comparison
function compareSalaries(salary1, salary2) {
    const diff = salary1 - salary2;
    const percentage = ((diff / salary2) * 100).toFixed(1);
    
    if (diff > 0) {
        return `أعلى بـ ${formatCurrency(diff)} (${percentage}%)`;
    } else if (diff < 0) {
        return `أقل بـ ${formatCurrency(Math.abs(diff))} (${Math.abs(percentage)}%)`;
    } else {
        return 'متساوي';
    }
}

// Initialize charts when Chart.js is loaded
if (typeof Chart !== 'undefined') {
    document.addEventListener('DOMContentLoaded', initializeCharts);
}

// Initialize salary calculations on page load
document.addEventListener('DOMContentLoaded', function() {
    calculateSalaryTotal();
    updateCurrencyDisplay();
});
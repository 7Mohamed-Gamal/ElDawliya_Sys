// Leave Management System JavaScript Functions

// Global variables
let currentModal = null;
let leaveChart = null;
let balanceChart = null;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeLeaveSystem();
});

// Main initialization function
function initializeLeaveSystem() {
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize date pickers
    initializeDatePickers();
    
    // Initialize form validation
    initializeFormValidation();
    
    // Initialize real-time updates
    initializeRealTimeUpdates();
    
    // Initialize keyboard shortcuts
    initializeKeyboardShortcuts();
    
    // Initialize date calculations
    initializeDateCalculations();
}

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Initialize date pickers with default values
function initializeDatePickers() {
    const today = new Date().toISOString().split('T')[0];
    
    // Set minimum date to today for new leave requests
    const startDateInputs = document.querySelectorAll('input[name="start_date"]');
    startDateInputs.forEach(input => {
        input.min = today;
    });
    
    const endDateInputs = document.querySelectorAll('input[name="end_date"]');
    endDateInputs.forEach(input => {
        input.min = today;
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
        // Ctrl + N for new leave request
        if (event.ctrlKey && event.key === 'n') {
            event.preventDefault();
            openNewLeaveModal();
        }
        
        // Escape to close modals
        if (event.key === 'Escape' && currentModal) {
            currentModal.hide();
        }
    });
}

// Initialize date calculations
function initializeDateCalculations() {
    // Add event listeners for date calculation
    const startDateInputs = document.querySelectorAll('input[name="start_date"]');
    const endDateInputs = document.querySelectorAll('input[name="end_date"]');
    
    startDateInputs.forEach(input => {
        input.addEventListener('change', calculateLeaveDays);
    });
    
    endDateInputs.forEach(input => {
        input.addEventListener('change', calculateLeaveDays);
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

// Calculate leave days
function calculateLeaveDays() {
    const startDateInput = document.querySelector('input[name="start_date"]');
    const endDateInput = document.querySelector('input[name="end_date"]');
    const daysDisplay = document.getElementById('days_calculation');
    
    if (!startDateInput || !endDateInput || !daysDisplay) return;
    
    const startDate = startDateInput.value;
    const endDate = endDateInput.value;
    
    if (startDate && endDate) {
        const start = new Date(startDate);
        const end = new Date(endDate);
        
        if (end >= start) {
            const diffTime = Math.abs(end - start);
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
            
            // Calculate working days (excluding weekends)
            const workingDays = calculateWorkingDays(start, end);
            
            daysDisplay.innerHTML = `
                <i class="fas fa-calendar-day me-1"></i> 
                عدد الأيام: <strong>${diffDays}</strong> يوم
                <br>
                <small class="text-muted">أيام العمل: ${workingDays} يوم</small>
            `;
            daysDisplay.className = 'alert alert-info';
        } else {
            daysDisplay.innerHTML = '<i class="fas fa-exclamation-triangle me-1"></i> تاريخ النهاية يجب أن يكون بعد تاريخ البداية';
            daysDisplay.className = 'alert alert-warning';
        }
        
        // Update end date minimum
        endDateInput.min = startDate;
    }
}

// Calculate working days (excluding weekends)
function calculateWorkingDays(startDate, endDate) {
    let count = 0;
    const current = new Date(startDate);
    
    while (current <= endDate) {
        const dayOfWeek = current.getDay();
        // Exclude Friday (5) and Saturday (6) for most Arab countries
        if (dayOfWeek !== 5 && dayOfWeek !== 6) {
            count++;
        }
        current.setDate(current.getDate() + 1);
    }
    
    return count;
}

// Open new leave modal
function openNewLeaveModal() {
    const modal = document.getElementById('newLeaveModal');
    if (modal) {
        currentModal = new bootstrap.Modal(modal);
        currentModal.show();
    }
}

// Submit leave request
function submitLeaveRequest() {
    const form = document.getElementById('newLeaveForm');
    if (!form) return;
    
    const formData = new FormData(form);
    
    // Show loading state
    const submitBtn = document.querySelector('#newLeaveModal .btn-success');
    const originalText = submitBtn.textContent;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>جاري التقديم...';
    submitBtn.disabled = true;
    
    fetch(getLeaveRequestUrl(), {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('تم تقديم طلب الإجازة بنجاح', 'success');
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

// Approve leave request
function approveLeave(leaveId) {
    if (confirm('هل أنت متأكد من الموافقة على هذا الطلب؟')) {
        fetch(getApproveLeaveUrl(leaveId), {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('تم الموافقة على الطلب بنجاح', 'success');
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

// Reject leave request
function rejectLeave(leaveId) {
    const reason = prompt('سبب الرفض (اختياري):');
    if (reason !== null) {
        fetch(getRejectLeaveUrl(leaveId), {
            method: 'POST',
            body: JSON.stringify({reason: reason}),
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('تم رفض الطلب', 'warning');
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
function getLeaveRequestUrl() {
    return window.leaveRequestUrl || '/leaves/create/';
}

function getApproveLeaveUrl(leaveId) {
    return window.approveLeaveUrl ? window.approveLeaveUrl.replace('0', leaveId) : `/leaves/approve/${leaveId}/`;
}

function getRejectLeaveUrl(leaveId) {
    return window.rejectLeaveUrl ? window.rejectLeaveUrl.replace('0', leaveId) : `/leaves/reject/${leaveId}/`;
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

// Filter functions
function applyFilters(formId) {
    const form = document.getElementById(formId);
    if (form) {
        form.submit();
    }
}

function clearFilters(baseUrl) {
    window.location.href = baseUrl;
}

// Chart functions
function initializeCharts() {
    // Initialize leave status chart
    const leaveStatusCtx = document.getElementById('leaveStatusChart');
    if (leaveStatusCtx && window.chartData) {
        leaveChart = new Chart(leaveStatusCtx.getContext('2d'), {
            type: 'doughnut',
            data: window.chartData.leaveStatus,
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
    
    // Initialize balance chart
    const balanceCtx = document.getElementById('balanceChart');
    if (balanceCtx && window.chartData) {
        balanceChart = new Chart(balanceCtx.getContext('2d'), {
            type: 'bar',
            data: window.chartData.balance,
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

// Calendar functions
function initializeCalendar() {
    const calendarEl = document.getElementById('leaveCalendar');
    if (!calendarEl) return;
    
    // Simple calendar implementation
    const today = new Date();
    const currentMonth = today.getMonth();
    const currentYear = today.getFullYear();
    
    let calendarHTML = '<div class="text-center mb-2"><strong>' + 
        today.toLocaleDateString('ar-EG', { month: 'long', year: 'numeric' }) + 
        '</strong></div>';
    
    calendarHTML += '<div class="row text-center small">';
    const days = ['ح', 'ن', 'ث', 'ر', 'خ', 'ج', 'س'];
    days.forEach(day => {
        calendarHTML += `<div class="col">${day}</div>`;
    });
    calendarHTML += '</div>';
    
    // Add calendar days
    const firstDay = new Date(currentYear, currentMonth, 1).getDay();
    const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
    
    let dayCount = 1;
    for (let week = 0; week < 6; week++) {
        calendarHTML += '<div class="row text-center">';
        for (let day = 0; day < 7; day++) {
            if (week === 0 && day < firstDay) {
                calendarHTML += '<div class="col p-1"></div>';
            } else if (dayCount <= daysInMonth) {
                const isToday = dayCount === today.getDate();
                const dayClass = isToday ? 'bg-success text-white rounded' : '';
                calendarHTML += `<div class="col p-1"><span class="d-block ${dayClass}">${dayCount}</span></div>`;
                dayCount++;
            } else {
                calendarHTML += '<div class="col p-1"></div>';
            }
        }
        calendarHTML += '</div>';
        if (dayCount > daysInMonth) break;
    }
    
    calendarEl.innerHTML = calendarHTML;
}

// Utility functions
function formatDate(dateString) {
    if (!dateString) return 'غير محدد';
    
    const date = new Date(dateString);
    return date.toLocaleDateString('ar-EG', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function formatDateShort(dateString) {
    if (!dateString) return 'غير محدد';
    
    const date = new Date(dateString);
    return date.toLocaleDateString('ar-EG', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    });
}

function calculateDaysBetween(startDate, endDate) {
    if (!startDate || !endDate) return 0;
    
    const start = new Date(startDate);
    const end = new Date(endDate);
    const diffTime = Math.abs(end - start);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    return diffDays + 1;
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

function printTable(tableId) {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
        <html>
        <head>
            <title>تقرير الإجازات</title>
            <style>
                body { font-family: Arial, sans-serif; direction: rtl; }
                table { width: 100%; border-collapse: collapse; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: right; }
                th { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
            <h2>تقرير الإجازات</h2>
            ${table.outerHTML}
        </body>
        </html>
    `);
    printWindow.document.close();
    printWindow.print();
}

// Leave balance functions
function checkLeaveBalance(employeeId, leaveTypeId) {
    return fetch(`/leaves/balance/${employeeId}/${leaveTypeId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                return data.balance;
            } else {
                throw new Error(data.message);
            }
        });
}

function updateBalanceDisplay(balance) {
    const balanceElement = document.getElementById('leave_balance_display');
    if (balanceElement && balance) {
        balanceElement.innerHTML = `
            <div class="alert alert-info">
                <strong>الرصيد المتاح:</strong> ${balance.available} يوم
                <br>
                <small>المستخدم: ${balance.used} يوم من أصل ${balance.total} يوم</small>
            </div>
        `;
    }
}

// Initialize charts when Chart.js is loaded
if (typeof Chart !== 'undefined') {
    document.addEventListener('DOMContentLoaded', initializeCharts);
}

// Initialize calendar
document.addEventListener('DOMContentLoaded', initializeCalendar);// Adva
nced Leave Management Functions

// Real-time leave balance checker
function checkLeaveBalance(employeeId, leaveTypeId) {
    if (!employeeId || !leaveTypeId) return;
    
    fetch(`/leaves/api/balance/${employeeId}/${leaveTypeId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateBalanceDisplay(data.balance);
                validateLeaveRequest(data.balance);
            }
        })
        .catch(error => console.error('Error checking balance:', error));
}

// Update balance display in UI
function updateBalanceDisplay(balance) {
    const balanceCard = document.getElementById('leaveBalance');
    const availableDays = document.getElementById('availableDays');
    const balanceDetails = document.getElementById('balanceDetails');
    
    if (balanceCard && availableDays && balanceDetails) {
        balanceCard.style.display = 'block';
        availableDays.textContent = balance.available_days;
        balanceDetails.innerHTML = `
            <div class="row">
                <div class="col-6">
                    <small>الرصيد السنوي: ${balance.annual_entitlement || 'غير محدود'}</small>
                </div>
                <div class="col-6">
                    <small>المستخدم: ${balance.used_days} يوم</small>
                </div>
            </div>
        `;
        
        // Update progress bar if exists
        const progressBar = balanceCard.querySelector('.progress-bar');
        if (progressBar && balance.annual_entitlement) {
            const percentage = (balance.used_days / balance.annual_entitlement) * 100;
            progressBar.style.width = `${percentage}%`;
            progressBar.className = `progress-bar ${percentage > 80 ? 'bg-danger' : percentage > 60 ? 'bg-warning' : 'bg-success'}`;
        }
    }
}

// Validate leave request against balance
function validateLeaveRequest(balance) {
    const startDate = document.getElementById('start_date');
    const endDate = document.getElementById('end_date');
    
    if (startDate && endDate && startDate.value && endDate.value) {
        const requestedDays = calculateLeaveDays(startDate.value, endDate.value);
        
        if (balance.available_days < requestedDays) {
            showBalanceWarning(requestedDays, balance.available_days);
        } else {
            hideBalanceWarning();
        }
    }
}

// Show balance warning
function showBalanceWarning(requested, available) {
    let warningDiv = document.getElementById('balanceWarning');
    
    if (!warningDiv) {
        warningDiv = document.createElement('div');
        warningDiv.id = 'balanceWarning';
        warningDiv.className = 'alert alert-warning mt-3';
        
        const balanceCard = document.getElementById('leaveBalance');
        if (balanceCard) {
            balanceCard.appendChild(warningDiv);
        }
    }
    
    warningDiv.innerHTML = `
        <i class="fas fa-exclamation-triangle me-2"></i>
        <strong>تحذير:</strong> الأيام المطلوبة (${requested}) تتجاوز الرصيد المتاح (${available})
    `;
    warningDiv.style.display = 'block';
}

// Hide balance warning
function hideBalanceWarning() {
    const warningDiv = document.getElementById('balanceWarning');
    if (warningDiv) {
        warningDiv.style.display = 'none';
    }
}

// Calculate leave days excluding weekends
function calculateLeaveDays(startDate, endDate) {
    const start = new Date(startDate);
    const end = new Date(endDate);
    let days = 0;
    
    for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
        // Skip Fridays (5) and Saturdays (6) - weekend in many Arab countries
        if (d.getDay() !== 5 && d.getDay() !== 6) {
            days++;
        }
    }
    
    return days;
}

// Advanced date validation
function validateLeaveDates(startDate, endDate) {
    const start = new Date(startDate);
    const end = new Date(endDate);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    const errors = [];
    
    // Check if start date is in the past
    if (start < today) {
        errors.push('لا يمكن أن يكون تاريخ البداية في الماضي');
    }
    
    // Check if end date is before start date
    if (end < start) {
        errors.push('تاريخ النهاية يجب أن يكون بعد تاريخ البداية');
    }
    
    // Check for minimum advance notice (e.g., 3 days)
    const minAdvanceDate = new Date(today);
    minAdvanceDate.setDate(minAdvanceDate.getDate() + 3);
    
    if (start < minAdvanceDate) {
        errors.push('يجب تقديم الطلب قبل 3 أيام على الأقل من تاريخ البداية');
    }
    
    return errors;
}

// Check for overlapping leave requests
function checkOverlappingLeaves(employeeId, startDate, endDate, excludeLeaveId = null) {
    const data = {
        employee_id: employeeId,
        start_date: startDate,
        end_date: endDate
    };
    
    if (excludeLeaveId) {
        data.exclude_leave_id = excludeLeaveId;
    }
    
    return fetch('/leaves/api/check-overlap/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json());
}

// Enhanced form validation
function validateLeaveForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    const employee = form.querySelector('[name="employee"]').value;
    const leaveType = form.querySelector('[name="leave_type"]').value;
    const startDate = form.querySelector('[name="start_date"]').value;
    const endDate = form.querySelector('[name="end_date"]').value;
    const reason = form.querySelector('[name="reason"]').value;
    
    let isValid = true;
    const errors = [];
    
    // Basic validation
    if (!employee) {
        errors.push('يرجى اختيار الموظف');
        isValid = false;
    }
    
    if (!leaveType) {
        errors.push('يرجى اختيار نوع الإجازة');
        isValid = false;
    }
    
    if (!startDate) {
        errors.push('يرجى اختيار تاريخ البداية');
        isValid = false;
    }
    
    if (!endDate) {
        errors.push('يرجى اختيار تاريخ النهاية');
        isValid = false;
    }
    
    if (!reason.trim()) {
        errors.push('يرجى كتابة سبب الإجازة');
        isValid = false;
    }
    
    // Date validation
    if (startDate && endDate) {
        const dateErrors = validateLeaveDates(startDate, endDate);
        errors.push(...dateErrors);
        if (dateErrors.length > 0) {
            isValid = false;
        }
    }
    
    // Display errors
    if (!isValid) {
        showFormErrors(errors);
    } else {
        hideFormErrors();
    }
    
    return isValid;
}

// Show form errors
function showFormErrors(errors) {
    let errorDiv = document.getElementById('formErrors');
    
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.id = 'formErrors';
        errorDiv.className = 'alert alert-danger';
        
        const form = document.querySelector('form');
        if (form) {
            form.insertBefore(errorDiv, form.firstChild);
        }
    }
    
    errorDiv.innerHTML = `
        <h6><i class="fas fa-exclamation-triangle me-2"></i>يرجى تصحيح الأخطاء التالية:</h6>
        <ul class="mb-0">
            ${errors.map(error => `<li>${error}</li>`).join('')}
        </ul>
    `;
    errorDiv.style.display = 'block';
    
    // Scroll to errors
    errorDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

// Hide form errors
function hideFormErrors() {
    const errorDiv = document.getElementById('formErrors');
    if (errorDiv) {
        errorDiv.style.display = 'none';
    }
}

// Auto-save draft functionality
function autoSaveDraft(formId) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    const formData = new FormData(form);
    const draftData = {};
    
    for (let [key, value] of formData.entries()) {
        draftData[key] = value;
    }
    
    localStorage.setItem(`leaveDraft_${formId}`, JSON.stringify(draftData));
}

// Load draft data
function loadDraft(formId) {
    const draftData = localStorage.getItem(`leaveDraft_${formId}`);
    if (!draftData) return;
    
    try {
        const data = JSON.parse(draftData);
        const form = document.getElementById(formId);
        
        if (form) {
            Object.keys(data).forEach(key => {
                const field = form.querySelector(`[name="${key}"]`);
                if (field) {
                    field.value = data[key];
                }
            });
            
            // Show draft notification
            showDraftNotification();
        }
    } catch (error) {
        console.error('Error loading draft:', error);
    }
}

// Show draft notification
function showDraftNotification() {
    const notification = document.createElement('div');
    notification.className = 'alert alert-info alert-dismissible fade show';
    notification.innerHTML = `
        <i class="fas fa-info-circle me-2"></i>
        تم استعادة مسودة محفوظة من جلسة سابقة
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const form = document.querySelector('form');
    if (form) {
        form.insertBefore(notification, form.firstChild);
    }
}

// Clear draft
function clearDraft(formId) {
    localStorage.removeItem(`leaveDraft_${formId}`);
}

// Export functions
function exportLeaveData(format = 'excel', filters = {}) {
    const params = new URLSearchParams(filters);
    params.set('export', format);
    
    const url = `/leaves/export/?${params.toString()}`;
    
    // Create temporary link for download
    const link = document.createElement('a');
    link.href = url;
    link.download = `leave_data_${new Date().toISOString().split('T')[0]}.${format}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Print functionality
function printLeaveReport(reportType = 'list') {
    const printWindow = window.open('', '_blank');
    const currentContent = document.querySelector('.container-fluid').innerHTML;
    
    printWindow.document.write(`
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <title>تقرير الإجازات</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                @media print {
                    .no-print { display: none !important; }
                    .btn { display: none !important; }
                    .modal { display: none !important; }
                }
                body { font-family: 'Cairo', sans-serif; }
            </style>
        </head>
        <body>
            <div class="container-fluid">
                ${currentContent}
            </div>
        </body>
        </html>
    `);
    
    printWindow.document.close();
    printWindow.focus();
    
    setTimeout(() => {
        printWindow.print();
        printWindow.close();
    }, 250);
}

// Initialize leave management features
document.addEventListener('DOMContentLoaded', function() {
    // Auto-save functionality
    const forms = document.querySelectorAll('form[id*="leave"]');
    forms.forEach(form => {
        const formId = form.id;
        
        // Load draft on page load
        loadDraft(formId);
        
        // Auto-save on input change
        form.addEventListener('input', debounce(() => {
            autoSaveDraft(formId);
        }, 1000));
        
        // Clear draft on successful submission
        form.addEventListener('submit', () => {
            clearDraft(formId);
        });
    });
    
    // Enhanced date pickers
    const datePickers = document.querySelectorAll('input[type="date"]');
    datePickers.forEach(picker => {
        // Set minimum date to today
        const today = new Date().toISOString().split('T')[0];
        if (picker.name.includes('start_date') || picker.name.includes('end_date')) {
            picker.min = today;
        }
        
        // Add change listeners for validation
        picker.addEventListener('change', function() {
            const form = this.closest('form');
            if (form) {
                const startDate = form.querySelector('[name*="start_date"]');
                const endDate = form.querySelector('[name*="end_date"]');
                
                if (startDate && endDate && startDate.value && endDate.value) {
                    const errors = validateLeaveDates(startDate.value, endDate.value);
                    if (errors.length > 0) {
                        showFormErrors(errors);
                    } else {
                        hideFormErrors();
                    }
                }
            }
        });
    });
    
    // Employee and leave type change handlers
    const employeeSelects = document.querySelectorAll('select[name="employee"]');
    const leaveTypeSelects = document.querySelectorAll('select[name="leave_type"]');
    
    employeeSelects.forEach(select => {
        select.addEventListener('change', function() {
            const form = this.closest('form');
            const leaveTypeSelect = form.querySelector('select[name="leave_type"]');
            
            if (this.value && leaveTypeSelect && leaveTypeSelect.value) {
                checkLeaveBalance(this.value, leaveTypeSelect.value);
            }
        });
    });
    
    leaveTypeSelects.forEach(select => {
        select.addEventListener('change', function() {
            const form = this.closest('form');
            const employeeSelect = form.querySelector('select[name="employee"]');
            
            if (this.value && employeeSelect && employeeSelect.value) {
                checkLeaveBalance(employeeSelect.value, this.value);
            }
        });
    });
});

// Utility function for debouncing
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Notification system
function showNotification(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after duration
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, duration);
}
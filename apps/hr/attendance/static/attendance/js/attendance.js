// Attendance System JavaScript Functions

// Global variables
let currentModal = null;
let attendanceChart = null;
let statusChart = null;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeAttendanceSystem();
});

// Main initialization function
function initializeAttendanceSystem() {
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
    
    // Set default dates for filters
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        if (!input.value && input.name.includes('date')) {
            input.value = today;
        }
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
    // Update time every second
    setInterval(updateCurrentTime, 1000);
    
    // Refresh data every 5 minutes
    setInterval(refreshDashboardData, 300000);
}

// Initialize keyboard shortcuts
function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', function(event) {
        // Ctrl + I for check in
        if (event.ctrlKey && event.key === 'i') {
            event.preventDefault();
            recordAttendance('in');
        }
        
        // Ctrl + O for check out
        if (event.ctrlKey && event.key === 'o') {
            event.preventDefault();
            recordAttendance('out');
        }
        
        // Escape to close modals
        if (event.key === 'Escape' && currentModal) {
            currentModal.hide();
        }
    });
}

// Update current time display
function updateCurrentTime() {
    const timeElements = document.querySelectorAll('.current-time');
    const now = new Date();
    const timeString = now.toLocaleTimeString('ar-EG', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
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

// Record attendance function
function recordAttendance(type, employeeId = null) {
    const modal = document.getElementById('attendanceModal');
    if (!modal) return;
    
    currentModal = new bootstrap.Modal(modal);
    const title = type === 'in' ? 'تسجيل الحضور' : 'تسجيل الانصراف';
    
    // Update modal title
    const titleElement = modal.querySelector('.modal-title');
    if (titleElement) {
        titleElement.textContent = title;
    }
    
    // Set current time
    const timeInput = modal.querySelector('#attendance_time');
    if (timeInput) {
        const now = new Date();
        const localDateTime = formatDateTimeLocal(now);
        timeInput.value = localDateTime;
    }
    
    // Set employee if provided
    const employeeSelect = modal.querySelector('#employee_select');
    if (employeeSelect && employeeId) {
        employeeSelect.value = employeeId;
    }
    
    // Store attendance type
    modal.setAttribute('data-attendance-type', type);
    
    currentModal.show();
}

// Submit attendance record
function submitAttendance() {
    const modal = document.getElementById('attendanceModal');
    const form = modal.querySelector('#attendanceForm');
    const type = modal.getAttribute('data-attendance-type');
    
    if (!form || !type) return;
    
    const formData = new FormData(form);
    formData.append('type', type);
    
    // Show loading state
    const submitBtn = modal.querySelector('.btn-primary');
    const originalText = submitBtn.textContent;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>جاري التسجيل...';
    submitBtn.disabled = true;
    
    fetch(getAttendanceRecordUrl(), {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('تم تسجيل الحضور بنجاح', 'success');
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

// Format date for datetime-local input
function formatDateTimeLocal(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    
    return `${year}-${month}-${day}T${hours}:${minutes}`;
}

// Get CSRF token
function getCSRFToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : '';
}

// Get attendance record URL
function getAttendanceRecordUrl() {
    // This should be set by the template
    return window.attendanceRecordUrl || '/attendance/record/';
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
    // Initialize attendance trend chart
    const attendanceCtx = document.getElementById('attendanceChart');
    if (attendanceCtx && window.chartData) {
        attendanceChart = new Chart(attendanceCtx.getContext('2d'), {
            type: 'line',
            data: window.chartData.attendance,
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
    
    // Initialize status distribution chart
    const statusCtx = document.getElementById('statusChart');
    if (statusCtx && window.chartData) {
        statusChart = new Chart(statusCtx.getContext('2d'), {
            type: 'doughnut',
            data: window.chartData.status,
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
}

// Utility functions
function formatTime(timeString) {
    if (!timeString) return 'غير محدد';
    
    const time = new Date(`2000-01-01T${timeString}`);
    return time.toLocaleTimeString('ar-EG', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatDate(dateString) {
    if (!dateString) return 'غير محدد';
    
    const date = new Date(dateString);
    return date.toLocaleDateString('ar-EG', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function calculateWorkHours(checkIn, checkOut) {
    if (!checkIn || !checkOut) return 0;
    
    const start = new Date(`2000-01-01T${checkIn}`);
    const end = new Date(`2000-01-01T${checkOut}`);
    
    const diffMs = end - start;
    const diffHours = diffMs / (1000 * 60 * 60);
    
    return Math.max(0, diffHours);
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
            <title>تقرير الحضور</title>
            <style>
                body { font-family: Arial, sans-serif; direction: rtl; }
                table { width: 100%; border-collapse: collapse; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: right; }
                th { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
            <h2>تقرير الحضور والانصراف</h2>
            ${table.outerHTML}
        </body>
        </html>
    `);
    printWindow.document.close();
    printWindow.print();
}

// Initialize charts when Chart.js is loaded
if (typeof Chart !== 'undefined') {
    document.addEventListener('DOMContentLoaded', initializeCharts);
}
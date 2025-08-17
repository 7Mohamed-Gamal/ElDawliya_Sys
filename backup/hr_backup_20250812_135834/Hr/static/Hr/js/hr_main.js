/**
 * HR Main JavaScript File
 * Contains common functionality for HR module
 */

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initializeHRModule();
});

/**
 * Initialize HR Module
 */
function initializeHRModule() {
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize modals
    initializeModals();
    
    // Initialize form validation
    initializeFormValidation();
    
    // Initialize data tables
    initializeDataTables();
    
    // Initialize charts
    initializeCharts();
    
    console.log('HR Module initialized successfully');
}

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize Bootstrap modals
 */
function initializeModals() {
    // Add any modal-specific initialization here
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('hidden.bs.modal', function () {
            // Clear form data when modal is closed
            const forms = modal.querySelectorAll('form');
            forms.forEach(form => form.reset());
        });
    });
}

/**
 * Initialize form validation
 */
function initializeFormValidation() {
    // Add Bootstrap validation classes
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

/**
 * Initialize DataTables
 */
function initializeDataTables() {
    // Check if DataTables is available
    if (typeof $.fn.DataTable !== 'undefined') {
        $('.data-table').DataTable({
            responsive: true,
            language: {
                url: '//cdn.datatables.net/plug-ins/1.13.7/i18n/ar.json'
            },
            pageLength: 25,
            order: [[0, 'desc']]
        });
    }
}

/**
 * Initialize Charts
 */
function initializeCharts() {
    // Chart initialization will be handled by individual dashboard components
    console.log('Charts initialization placeholder');
}

/**
 * Utility Functions
 */

/**
 * Show success message
 */
function showSuccessMessage(message) {
    showAlert(message, 'success');
}

/**
 * Show error message
 */
function showErrorMessage(message) {
    showAlert(message, 'danger');
}

/**
 * Show alert message
 */
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alert-container') || document.body;
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.insertBefore(alertDiv, alertContainer.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

/**
 * Format currency for display
 */
function formatCurrency(amount, currency = 'EGP') {
    return new Intl.NumberFormat('ar-EG', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

/**
 * Format date for display
 */
function formatDate(date, options = {}) {
    const defaultOptions = {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    };
    
    return new Intl.DateTimeFormat('ar-EG', { ...defaultOptions, ...options }).format(new Date(date));
}

/**
 * AJAX helper function
 */
function makeAjaxRequest(url, options = {}) {
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        }
    };
    
    return fetch(url, { ...defaultOptions, ...options })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .catch(error => {
            console.error('AJAX request failed:', error);
            showErrorMessage('حدث خطأ في الاتصال بالخادم');
            throw error;
        });
}

/**
 * Get CSRF token from cookie
 */
function getCsrfToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Export functionality
 */
function exportToExcel(tableId, filename = 'hr_data') {
    // Implementation for Excel export
    console.log(`Exporting table ${tableId} to Excel as ${filename}`);
}

function exportToPDF(elementId, filename = 'hr_report') {
    // Implementation for PDF export
    console.log(`Exporting element ${elementId} to PDF as ${filename}`);
}

/**
 * Print functionality
 */
function printElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        const printWindow = window.open('', '_blank');
        printWindow.document.write(`
            <html>
                <head>
                    <title>طباعة</title>
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
                    <style>
                        @media print {
                            .no-print { display: none !important; }
                            body { font-size: 12px; }
                        }
                    </style>
                </head>
                <body class="p-3">
                    ${element.innerHTML}
                </body>
            </html>
        `);
        printWindow.document.close();
        printWindow.print();
    }
}

// Global functions for backward compatibility
window.showSuccessMessage = showSuccessMessage;
window.showErrorMessage = showErrorMessage;
window.formatCurrency = formatCurrency;
window.formatDate = formatDate;
window.makeAjaxRequest = makeAjaxRequest;
window.exportToExcel = exportToExcel;
window.exportToPDF = exportToPDF;
window.printElement = printElement;

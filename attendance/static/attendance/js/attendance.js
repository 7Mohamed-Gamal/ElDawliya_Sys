// Attendance app custom JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize datetime elements
    const datetimeElements = document.querySelectorAll('.datetime-local');
    datetimeElements.forEach(function(element) {
        if (element.value) {
            const date = new Date(element.value);
            element.value = date.toISOString().slice(0, 16);
        }
    });

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Handle form submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';
            }
        });
    });

    // Handle employee select changes
    const employeeSelect = document.getElementById('employee');
    if (employeeSelect) {
        employeeSelect.addEventListener('change', function() {
            const selectedOption = this.options[this.selectedIndex];
            if (selectedOption.value) {
                // You can add custom logic here when an employee is selected
            }
        });
    }

    // Handle date range validation
    const dateFrom = document.getElementById('date_from');
    const dateTo = document.getElementById('date_to');
    if (dateFrom && dateTo) {
        dateFrom.addEventListener('change', validateDateRange);
        dateTo.addEventListener('change', validateDateRange);
    }

    // Handle print functionality
    const printButtons = document.querySelectorAll('.print-button');
    printButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            window.print();
        });
    });

    // Handle export functionality
    const exportButtons = document.querySelectorAll('.export-button');
    exportButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const url = new URL(window.location.href);
            url.searchParams.set('export', 'excel');
            window.location.href = url.toString();
        });
    });

    // Real-time clock update
    function updateTime() {
        const now = new Date();
        const timeElement = document.getElementById('current-time');
        if (timeElement) {
            const hours = now.getHours() % 12 || 12;
            const minutes = now.getMinutes().toString().padStart(2, '0');
            const seconds = now.getSeconds().toString().padStart(2, '0');
            const ampm = now.getHours() >= 12 ? 'م' : 'ص';
            timeElement.textContent = `${hours}:${minutes}:${seconds} ${ampm}`;
        }
    }

    // Update time immediately and every second if on mark attendance page
    if (document.getElementById('current-time')) {
        updateTime();
        setInterval(updateTime, 1000);
    }
});

// Date range validation function
function validateDateRange() {
    const dateFrom = document.getElementById('date_from');
    const dateTo = document.getElementById('date_to');
    
    if (dateFrom.value && dateTo.value) {
        if (dateFrom.value > dateTo.value) {
            alert('From date cannot be later than To date');
            this.value = '';
        }
    }
}

// Format time for display
function formatTime(date) {
    if (!date) return '-';
    const d = new Date(date);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

// Format duration in minutes to hours and minutes
function formatDuration(minutes) {
    if (!minutes) return '-';
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`;
}

// Update current time display
function updateCurrentTime() {
    const currentTimeElement = document.querySelector('.current-time');
    if (currentTimeElement) {
        const now = new Date();
        currentTimeElement.textContent = now.toLocaleTimeString();
    }
}

// Start current time update if element exists
const currentTimeElement = document.querySelector('.current-time');
if (currentTimeElement) {
    updateCurrentTime();
    setInterval(updateCurrentTime, 1000);
}

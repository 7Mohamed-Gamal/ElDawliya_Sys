// Performance Evaluation System JavaScript Functions

// Global variables
let currentModal = null;
let evaluationChart = null;
let performanceChart = null;
let selectedEmployees = [];

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeEvaluationSystem();
});

// Main initialization function
function initializeEvaluationSystem() {
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize form validation
    initializeFormValidation();
    
    // Initialize score feedback
    initializeScoreFeedback();
    
    // Initialize real-time updates
    initializeRealTimeUpdates();
    
    // Initialize keyboard shortcuts
    initializeKeyboardShortcuts();
    
    // Initialize comparison features
    initializeComparisonFeatures();
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

// Initialize score feedback
function initializeScoreFeedback() {
    const scoreInputs = document.querySelectorAll('input[name="score"]');
    
    scoreInputs.forEach(input => {
        input.addEventListener('input', function() {
            updateScoreFeedback(this);
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
        // Ctrl + N for new evaluation
        if (event.ctrlKey && event.key === 'n') {
            event.preventDefault();
            openNewEvaluationModal();
        }
        
        // Ctrl + P for new period
        if (event.ctrlKey && event.key === 'p') {
            event.preventDefault();
            openNewPeriodModal();
        }
        
        // Escape to close modals
        if (event.key === 'Escape' && currentModal) {
            currentModal.hide();
        }
    });
}

// Initialize comparison features
function initializeComparisonFeatures() {
    // Employee selection for comparison
    const employeeCards = document.querySelectorAll('.employee-card');
    employeeCards.forEach(card => {
        card.addEventListener('click', function() {
            toggleEmployeeSelection(this);
        });
    });
    
    // Search functionality
    const searchInput = document.getElementById('employeeSearch');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            filterEmployees(this.value);
        });
    }
    
    // Department filter
    const deptFilter = document.getElementById('departmentFilter');
    if (deptFilter) {
        deptFilter.addEventListener('change', function() {
            filterEmployeesByDepartment(this.value);
        });
    }
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

// Update score feedback
function updateScoreFeedback(input) {
    const score = parseFloat(input.value);
    const feedbackElement = document.getElementById('score_feedback') || 
                           input.parentNode.querySelector('.score-feedback');
    
    if (!feedbackElement) return;
    
    if (isNaN(score) || score < 0 || score > 100) {
        feedbackElement.innerHTML = '<i class="fas fa-info-circle me-1"></i> أدخل درجة صحيحة من 0 إلى 100';
        feedbackElement.className = 'alert alert-info score-feedback';
        return;
    }
    
    let message, className, icon;
    
    if (score >= 90) {
        message = 'ممتاز - أداء استثنائي يفوق التوقعات';
        className = 'alert alert-success score-feedback';
        icon = 'fas fa-star';
    } else if (score >= 75) {
        message = 'جيد - أداء فوق المتوسط ومرضي';
        className = 'alert alert-info score-feedback';
        icon = 'fas fa-thumbs-up';
    } else if (score >= 60) {
        message = 'متوسط - أداء مقبول يحتاج تطوير';
        className = 'alert alert-warning score-feedback';
        icon = 'fas fa-minus-circle';
    } else {
        message = 'ضعيف - أداء دون المستوى المطلوب';
        className = 'alert alert-danger score-feedback';
        icon = 'fas fa-exclamation-triangle';
    }
    
    feedbackElement.innerHTML = `<i class="${icon} me-1"></i> ${message}`;
    feedbackElement.className = className;
    
    // Add glow effect for high scores
    if (score >= 90) {
        feedbackElement.classList.add('score-glow');
    } else {
        feedbackElement.classList.remove('score-glow');
    }
}

// Open new evaluation modal
function openNewEvaluationModal() {
    const modal = document.getElementById('newEvaluationModal');
    if (modal) {
        currentModal = new bootstrap.Modal(modal);
        
        // Set today's date as default
        const dateInput = modal.querySelector('input[name="eval_date"]');
        if (dateInput) {
            dateInput.value = new Date().toISOString().split('T')[0];
        }
        
        currentModal.show();
    }
}

// Open new period modal
function openNewPeriodModal() {
    const modal = document.getElementById('addPeriodModal');
    if (modal) {
        currentModal = new bootstrap.Modal(modal);
        currentModal.show();
    }
}

// Submit evaluation
function submitEvaluation() {
    const form = document.getElementById('newEvaluationForm');
    if (!form) return;
    
    const formData = new FormData(form);
    
    // Show loading state
    const submitBtn = document.querySelector('#newEvaluationModal .btn-warning');
    const originalText = submitBtn.textContent;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>جاري الحفظ...';
    submitBtn.disabled = true;
    
    fetch(getEvaluationCreateUrl(), {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('تم حفظ التقييم بنجاح', 'success');
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

// Submit period
function submitPeriod() {
    const form = document.getElementById('addPeriodForm');
    if (!form) return;
    
    const formData = new FormData(form);
    
    // Validate date range
    const startDate = new Date(formData.get('start_date'));
    const endDate = new Date(formData.get('end_date'));
    
    if (endDate <= startDate) {
        showNotification('تاريخ النهاية يجب أن يكون بعد تاريخ البداية', 'error');
        return;
    }
    
    fetch(getPeriodCreateUrl(), {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('تم إنشاء فترة التقييم بنجاح', 'success');
            currentModal.hide();
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

// Toggle employee selection for comparison
function toggleEmployeeSelection(card) {
    const employeeId = card.getAttribute('data-employee-id');
    
    if (card.classList.contains('selected')) {
        // Deselect
        card.classList.remove('selected');
        selectedEmployees = selectedEmployees.filter(id => id !== employeeId);
    } else {
        // Select (max 4 employees)
        if (selectedEmployees.length < 4) {
            card.classList.add('selected');
            selectedEmployees.push(employeeId);
        } else {
            showNotification('يمكن مقارنة 4 موظفين كحد أقصى', 'warning');
            return;
        }
    }
    
    updateCompareButton();
}

// Update compare button state
function updateCompareButton() {
    const button = document.querySelector('button[onclick="compareSelected()"]');
    if (button) {
        button.disabled = selectedEmployees.length < 2;
        
        if (selectedEmployees.length < 2) {
            button.innerHTML = '<i class="fas fa-balance-scale me-1"></i> اختر موظفين على الأقل';
        } else {
            button.innerHTML = `<i class="fas fa-balance-scale me-1"></i> مقارنة ${selectedEmployees.length} موظفين`;
        }
    }
}

// Compare selected employees
function compareSelected() {
    if (selectedEmployees.length < 2) {
        showNotification('يجب اختيار موظفين على الأقل للمقارنة', 'warning');
        return;
    }
    
    // Show loading
    const resultsContainer = document.getElementById('comparisonResults');
    if (resultsContainer) {
        resultsContainer.innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-warning" role="status">
                    <span class="visually-hidden">جاري التحميل...</span>
                </div>
                <p class="mt-3">جاري تحضير المقارنة...</p>
            </div>
        `;
    }
    
    // Fetch comparison data
    fetch(getCompareEmployeesUrl(), {
        method: 'POST',
        body: JSON.stringify({employee_ids: selectedEmployees}),
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.text())
    .then(html => {
        if (resultsContainer) {
            resultsContainer.innerHTML = html;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        if (resultsContainer) {
            resultsContainer.innerHTML = `
                <div class="text-center py-5">
                    <i class="fas fa-exclamation-triangle fa-3x text-danger mb-3"></i>
                    <h5 class="text-danger">حدث خطأ في جلب بيانات المقارنة</h5>
                </div>
            `;
        }
    });
}

// Filter employees by search term
function filterEmployees(searchTerm) {
    const employeeCards = document.querySelectorAll('.employee-card');
    const term = searchTerm.toLowerCase();
    
    employeeCards.forEach(card => {
        const employeeName = card.querySelector('.fw-bold').textContent.toLowerCase();
        const isVisible = employeeName.includes(term);
        card.style.display = isVisible ? 'block' : 'none';
    });
}

// Filter employees by department
function filterEmployeesByDepartment(departmentId) {
    const employeeCards = document.querySelectorAll('.employee-card');
    
    employeeCards.forEach(card => {
        const cardDepartment = card.getAttribute('data-department');
        const isVisible = !departmentId || cardDepartment === departmentId;
        card.style.display = isVisible ? 'block' : 'none';
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

// Get CSRF token
function getCSRFToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : '';
}

// Get URLs (these should be set by templates)
function getEvaluationCreateUrl() {
    return window.evaluationCreateUrl || '/evaluations/create/';
}

function getPeriodCreateUrl() {
    return window.periodCreateUrl || '/evaluations/periods/add/';
}

function getCompareEmployeesUrl() {
    return window.compareEmployeesUrl || '/evaluations/compare/';
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
    // Initialize performance distribution chart
    const performanceCtx = document.getElementById('performanceChart');
    if (performanceCtx && window.chartData) {
        performanceChart = new Chart(performanceCtx.getContext('2d'), {
            type: 'doughnut',
            data: window.chartData.performance,
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
    
    // Initialize evaluation trend chart
    const trendCtx = document.getElementById('evaluationTrendChart');
    if (trendCtx && window.chartData) {
        evaluationChart = new Chart(trendCtx.getContext('2d'), {
            type: 'line',
            data: window.chartData.trend,
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }
}

// Utility functions
function formatScore(score) {
    if (score === null || score === undefined) return 'غير مقيم';
    return parseFloat(score).toFixed(1);
}

function getScoreClass(score) {
    if (score >= 90) return 'score-excellent';
    if (score >= 75) return 'score-good';
    if (score >= 60) return 'score-average';
    return 'score-poor';
}

function getScoreLabel(score) {
    if (score >= 90) return 'ممتاز';
    if (score >= 75) return 'جيد';
    if (score >= 60) return 'متوسط';
    return 'ضعيف';
}

function calculateImprovement(currentScore, previousScore) {
    if (!currentScore || !previousScore) return 0;
    return currentScore - previousScore;
}

function formatImprovement(improvement) {
    if (improvement > 0) {
        return `<span class="text-success"><i class="fas fa-arrow-up me-1"></i>+${improvement.toFixed(1)}</span>`;
    } else if (improvement < 0) {
        return `<span class="text-danger"><i class="fas fa-arrow-down me-1"></i>${improvement.toFixed(1)}</span>`;
    } else {
        return `<span class="text-muted"><i class="fas fa-minus me-1"></i>0</span>`;
    }
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

function printEvaluation(evalId) {
    window.open(`/evaluations/print/${evalId}/`, '_blank');
}

// Date validation functions
function validateDateRange(startDateId, endDateId) {
    const startDate = document.getElementById(startDateId);
    const endDate = document.getElementById(endDateId);
    
    if (!startDate || !endDate) return;
    
    startDate.addEventListener('change', function() {
        endDate.min = this.value;
        if (endDate.value && new Date(endDate.value) <= new Date(this.value)) {
            endDate.value = '';
            showNotification('تاريخ النهاية يجب أن يكون بعد تاريخ البداية', 'warning');
        }
    });
    
    endDate.addEventListener('change', function() {
        if (startDate.value && new Date(this.value) <= new Date(startDate.value)) {
            this.value = '';
            showNotification('تاريخ النهاية يجب أن يكون بعد تاريخ البداية', 'warning');
        }
    });
}

// Performance insights
function generatePerformanceInsights(data) {
    const insights = [];
    
    if (data.averageScore > 85) {
        insights.push({
            icon: 'fa-star',
            color: 'success',
            title: 'أداء ممتاز',
            description: 'متوسط الأداء العام مرتفع جداً'
        });
    }
    
    if (data.improvementTrend > 0) {
        insights.push({
            icon: 'fa-arrow-up',
            color: 'success',
            title: 'اتجاه إيجابي',
            description: 'الأداء في تحسن مستمر'
        });
    }
    
    if (data.lowPerformers > 0) {
        insights.push({
            icon: 'fa-exclamation-triangle',
            color: 'warning',
            title: 'يحتاج انتباه',
            description: `${data.lowPerformers} موظف يحتاج تطوير`
        });
    }
    
    return insights;
}

// Initialize charts when Chart.js is loaded
if (typeof Chart !== 'undefined') {
    document.addEventListener('DOMContentLoaded', initializeCharts);
}

// Initialize date validation
document.addEventListener('DOMContentLoaded', function() {
    validateDateRange('start_date', 'end_date');
    validateDateRange('edit_start_date', 'edit_end_date');
});/
/ Advanced Evaluation Management Functions

// Real-time score validation and feedback
function validateScore(scoreInput) {
    const score = parseFloat(scoreInput.value);
    const feedbackElement = document.getElementById('score_feedback');
    
    if (!feedbackElement) return;
    
    if (isNaN(score) || score < 0 || score > 100) {
        feedbackElement.innerHTML = '<i class="fas fa-exclamation-triangle me-1"></i> يرجى إدخال درجة صحيحة بين 0 و 100';
        feedbackElement.className = 'alert alert-danger';
        return false;
    }
    
    let message, className, icon;
    
    if (score >= 90) {
        message = 'ممتاز - أداء استثنائي يستحق التقدير';
        className = 'alert alert-success';
        icon = 'fa-star';
    } else if (score >= 75) {
        message = 'جيد - أداء فوق المتوسط';
        className = 'alert alert-info';
        icon = 'fa-thumbs-up';
    } else if (score >= 60) {
        message = 'متوسط - أداء مقبول مع إمكانية للتحسين';
        className = 'alert alert-warning';
        icon = 'fa-minus-circle';
    } else {
        message = 'ضعيف - يحتاج إلى تحسين كبير';
        className = 'alert alert-danger';
        icon = 'fa-exclamation-triangle';
    }
    
    feedbackElement.innerHTML = `<i class="fas ${icon} me-1"></i> ${message}`;
    feedbackElement.className = className;
    
    return true;
}

// Enhanced evaluation form validation
function validateEvaluationForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    const employee = form.querySelector('[name="employee"]').value;
    const period = form.querySelector('[name="period"]').value;
    const score = form.querySelector('[name="score"]').value;
    const evalDate = form.querySelector('[name="eval_date"]').value;
    
    let isValid = true;
    const errors = [];
    
    // Basic validation
    if (!employee) {
        errors.push('يرجى اختيار الموظف');
        isValid = false;
    }
    
    if (!period) {
        errors.push('يرجى اختيار فترة التقييم');
        isValid = false;
    }
    
    if (!score) {
        errors.push('يرجى إدخال درجة التقييم');
        isValid = false;
    } else {
        const scoreValue = parseFloat(score);
        if (isNaN(scoreValue) || scoreValue < 0 || scoreValue > 100) {
            errors.push('درجة التقييم يجب أن تكون بين 0 و 100');
            isValid = false;
        }
    }
    
    if (!evalDate) {
        errors.push('يرجى اختيار تاريخ التقييم');
        isValid = false;
    } else {
        const selectedDate = new Date(evalDate);
        const today = new Date();
        today.setHours(23, 59, 59, 999); // End of today
        
        if (selectedDate > today) {
            errors.push('تاريخ التقييم لا يمكن أن يكون في المستقبل');
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

// Check for duplicate evaluations
function checkDuplicateEvaluation(employeeId, periodId, excludeEvalId = null) {
    const data = {
        employee_id: employeeId,
        period_id: periodId
    };
    
    if (excludeEvalId) {
        data.exclude_eval_id = excludeEvalId;
    }
    
    return fetch('/evaluations/api/check-duplicate/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json());
}

// Enhanced period management
function validatePeriodDates(startDate, endDate) {
    const start = new Date(startDate);
    const end = new Date(endDate);
    const today = new Date();
    
    const errors = [];
    
    if (end <= start) {
        errors.push('تاريخ النهاية يجب أن يكون بعد تاريخ البداية');
    }
    
    const diffTime = Math.abs(end - start);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays < 7) {
        errors.push('فترة التقييم يجب أن تكون أسبوع على الأقل');
    }
    
    if (diffDays > 365) {
        errors.push('فترة التقييم لا يمكن أن تتجاوز سنة واحدة');
    }
    
    return errors;
}

// Performance analytics
function calculatePerformanceMetrics(evaluations) {
    if (!evaluations || evaluations.length === 0) {
        return {
            average: 0,
            median: 0,
            standardDeviation: 0,
            distribution: { excellent: 0, good: 0, average: 0, poor: 0 }
        };
    }
    
    const scores = evaluations.map(e => parseFloat(e.score)).filter(s => !isNaN(s));
    
    // Average
    const average = scores.reduce((sum, score) => sum + score, 0) / scores.length;
    
    // Median
    const sortedScores = [...scores].sort((a, b) => a - b);
    const median = sortedScores.length % 2 === 0
        ? (sortedScores[sortedScores.length / 2 - 1] + sortedScores[sortedScores.length / 2]) / 2
        : sortedScores[Math.floor(sortedScores.length / 2)];
    
    // Standard Deviation
    const variance = scores.reduce((sum, score) => sum + Math.pow(score - average, 2), 0) / scores.length;
    const standardDeviation = Math.sqrt(variance);
    
    // Distribution
    const distribution = {
        excellent: scores.filter(s => s >= 90).length,
        good: scores.filter(s => s >= 75 && s < 90).length,
        average: scores.filter(s => s >= 60 && s < 75).length,
        poor: scores.filter(s => s < 60).length
    };
    
    return {
        average: Math.round(average * 100) / 100,
        median: Math.round(median * 100) / 100,
        standardDeviation: Math.round(standardDeviation * 100) / 100,
        distribution
    };
}

// Advanced search and filtering
function initializeAdvancedSearch() {
    const searchInput = document.getElementById('employeeSearch');
    const departmentFilter = document.getElementById('departmentFilter');
    const scoreRangeFilter = document.getElementById('scoreRangeFilter');
    
    if (searchInput) {
        searchInput.addEventListener('input', debounce(performAdvancedSearch, 300));
    }
    
    if (departmentFilter) {
        departmentFilter.addEventListener('change', performAdvancedSearch);
    }
    
    if (scoreRangeFilter) {
        scoreRangeFilter.addEventListener('change', performAdvancedSearch);
    }
}

function performAdvancedSearch() {
    const searchTerm = document.getElementById('employeeSearch')?.value.toLowerCase() || '';
    const departmentFilter = document.getElementById('departmentFilter')?.value || '';
    const scoreRangeFilter = document.getElementById('scoreRangeFilter')?.value || '';
    
    const items = document.querySelectorAll('.employee-card, .evaluation-card, .searchable-item');
    
    items.forEach(item => {
        const employeeName = item.querySelector('.fw-bold')?.textContent.toLowerCase() || '';
        const department = item.getAttribute('data-department') || '';
        const score = parseFloat(item.getAttribute('data-score')) || 0;
        
        let matchesSearch = !searchTerm || employeeName.includes(searchTerm);
        let matchesDepartment = !departmentFilter || department === departmentFilter;
        let matchesScore = true;
        
        if (scoreRangeFilter) {
            switch (scoreRangeFilter) {
                case 'excellent':
                    matchesScore = score >= 90;
                    break;
                case 'good':
                    matchesScore = score >= 75 && score < 90;
                    break;
                case 'average':
                    matchesScore = score >= 60 && score < 75;
                    break;
                case 'poor':
                    matchesScore = score < 60;
                    break;
            }
        }
        
        item.style.display = matchesSearch && matchesDepartment && matchesScore ? 'block' : 'none';
    });
    
    updateSearchResults();
}

function updateSearchResults() {
    const visibleItems = document.querySelectorAll('.employee-card:not([style*="display: none"]), .evaluation-card:not([style*="display: none"])');
    const resultCount = document.getElementById('searchResultCount');
    
    if (resultCount) {
        resultCount.textContent = `${visibleItems.length} نتيجة`;
    }
}

// Export functionality
function exportEvaluationData(format = 'excel', filters = {}) {
    const params = new URLSearchParams(filters);
    params.set('export', format);
    
    const url = `/evaluations/export/?${params.toString()}`;
    
    // Show loading indicator
    showLoadingIndicator('جاري تصدير البيانات...');
    
    // Create temporary link for download
    const link = document.createElement('a');
    link.href = url;
    link.download = `evaluations_${new Date().toISOString().split('T')[0]}.${format}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Hide loading indicator after a delay
    setTimeout(() => {
        hideLoadingIndicator();
        showNotification('تم تصدير البيانات بنجاح', 'success');
    }, 2000);
}

// Print functionality
function printEvaluationReport(reportType = 'summary') {
    const printWindow = window.open('', '_blank');
    const currentContent = document.querySelector('.container-fluid').innerHTML;
    
    printWindow.document.write(`
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <title>تقرير التقييمات</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                @media print {
                    .no-print, .btn, .modal, .sidebar { display: none !important; }
                    .main-content { margin: 0 !important; padding: 20px !important; }
                    .chart-container { page-break-inside: avoid; }
                }
                body { font-family: 'Cairo', sans-serif; }
                .print-header {
                    text-align: center;
                    border-bottom: 2px solid #ffc107;
                    padding-bottom: 20px;
                    margin-bottom: 30px;
                }
            </style>
        </head>
        <body>
            <div class="print-header">
                <h1>تقرير التقييمات</h1>
                <p>تاريخ الطباعة: ${new Date().toLocaleDateString('ar-EG')}</p>
            </div>
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

// Auto-save functionality for evaluation forms
function initializeAutoSave(formId) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    const inputs = form.querySelectorAll('input, select, textarea');
    
    inputs.forEach(input => {
        input.addEventListener('input', debounce(() => {
            autoSaveEvaluationDraft(formId);
        }, 1000));
    });
    
    // Load existing draft
    loadEvaluationDraft(formId);
}

function autoSaveEvaluationDraft(formId) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    const formData = new FormData(form);
    const draftData = {};
    
    for (let [key, value] of formData.entries()) {
        draftData[key] = value;
    }
    
    localStorage.setItem(`evaluationDraft_${formId}`, JSON.stringify(draftData));
    
    // Show save indicator
    showSaveIndicator();
}

function loadEvaluationDraft(formId) {
    const draftData = localStorage.getItem(`evaluationDraft_${formId}`);
    if (!draftData) return;
    
    try {
        const data = JSON.parse(draftData);
        const form = document.getElementById(formId);
        
        if (form) {
            Object.keys(data).forEach(key => {
                const field = form.querySelector(`[name="${key}"]`);
                if (field) {
                    field.value = data[key];
                    
                    // Trigger change event for score validation
                    if (field.name === 'score') {
                        validateScore(field);
                    }
                }
            });
            
            showDraftNotification();
        }
    } catch (error) {
        console.error('Error loading draft:', error);
    }
}

function clearEvaluationDraft(formId) {
    localStorage.removeItem(`evaluationDraft_${formId}`);
}

// Utility functions
function showLoadingIndicator(message = 'جاري التحميل...') {
    const indicator = document.createElement('div');
    indicator.id = 'loadingIndicator';
    indicator.className = 'position-fixed top-50 start-50 translate-middle bg-white p-4 rounded shadow';
    indicator.style.zIndex = '9999';
    indicator.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-warning mb-2" role="status"></div>
            <div>${message}</div>
        </div>
    `;
    
    document.body.appendChild(indicator);
}

function hideLoadingIndicator() {
    const indicator = document.getElementById('loadingIndicator');
    if (indicator) {
        indicator.remove();
    }
}

function showSaveIndicator() {
    let indicator = document.getElementById('saveIndicator');
    
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.id = 'saveIndicator';
        indicator.className = 'position-fixed top-0 end-0 m-3 alert alert-success';
        indicator.style.zIndex = '9999';
        document.body.appendChild(indicator);
    }
    
    indicator.innerHTML = '<i class="fas fa-check me-1"></i> تم الحفظ تلقائياً';
    indicator.style.display = 'block';
    
    setTimeout(() => {
        indicator.style.display = 'none';
    }, 2000);
}

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

// Initialize all features when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize advanced search
    initializeAdvancedSearch();
    
    // Initialize auto-save for evaluation forms
    const evaluationForms = document.querySelectorAll('form[id*="evaluation"]');
    evaluationForms.forEach(form => {
        initializeAutoSave(form.id);
    });
    
    // Initialize score validation
    const scoreInputs = document.querySelectorAll('input[name="score"]');
    scoreInputs.forEach(input => {
        input.addEventListener('input', function() {
            validateScore(this);
        });
    });
    
    // Initialize date validation
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        if (input.name.includes('eval_date')) {
            // Set max date to today
            input.max = new Date().toISOString().split('T')[0];
        }
    });
    
    // Initialize period date validation
    const startDateInputs = document.querySelectorAll('input[name="start_date"]');
    const endDateInputs = document.querySelectorAll('input[name="end_date"]');
    
    startDateInputs.forEach(input => {
        input.addEventListener('change', function() {
            const form = this.closest('form');
            const endDateInput = form.querySelector('input[name="end_date"]');
            if (endDateInput) {
                endDateInput.min = this.value;
                
                if (endDateInput.value && this.value) {
                    const errors = validatePeriodDates(this.value, endDateInput.value);
                    if (errors.length > 0) {
                        showFormErrors(errors);
                    } else {
                        hideFormErrors();
                    }
                }
            }
        });
    });
    
    endDateInputs.forEach(input => {
        input.addEventListener('change', function() {
            const form = this.closest('form');
            const startDateInput = form.querySelector('input[name="start_date"]');
            if (startDateInput && startDateInput.value) {
                const errors = validatePeriodDates(startDateInput.value, this.value);
                if (errors.length > 0) {
                    showFormErrors(errors);
                } else {
                    hideFormErrors();
                }
            }
        });
    });
});

// Debounce utility function
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

// Show/hide form errors
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

function hideFormErrors() {
    const errorDiv = document.getElementById('formErrors');
    if (errorDiv) {
        errorDiv.style.display = 'none';
    }
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
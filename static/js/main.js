// ElDawliya System - Enhanced JavaScript Functions

document.addEventListener('DOMContentLoaded', function() {
    // Initialize components
    initRTLSupport();
    initScrollToTop();
    initDropdowns();
    initFormValidation();
    initStatusUpdaters();
    initDeleteConfirmations();
    initTooltips();
});

// RTL Support
function initRTLSupport() {
    // Ensure RTL direction is applied to all elements that need it
    document.querySelectorAll('.dropdown-menu, .popover, .tooltip').forEach(element => {
        element.style.textAlign = 'right';
    });

    // Fix any third-party plugins that might not respect RTL
    if (typeof $.fn.DataTable !== 'undefined') {
        $.extend(true, $.fn.DataTable.defaults, {
            language: {
                url: '//cdn.datatables.net/plug-ins/1.10.24/i18n/Arabic.json'
            }
        });
    }

    // Fix FullCalendar if it's being used
    if (typeof FullCalendar !== 'undefined') {
        document.querySelectorAll('.fc').forEach(calendar => {
            calendar.style.direction = 'rtl';
        });
    }

    // Fix any charts if they're being used
    if (typeof Chart !== 'undefined') {
        Chart.defaults.font.family = "'Cairo', 'Helvetica Neue', 'Helvetica', 'Arial', sans-serif";
        Chart.defaults.font.size = 14;
    }
}

// 1. Scroll to top button functionality
function initScrollToTop() {
    const scrollToTopBtn = document.getElementById('scrollToTop');

    if (scrollToTopBtn) {
        // Show/hide the button based on scroll position
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                scrollToTopBtn.classList.add('visible');
            } else {
                scrollToTopBtn.classList.remove('visible');
            }
        });

        // Smooth scroll to top when clicked
        scrollToTopBtn.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
}

// 2. Dropdown initialization for Bootstrap
function initDropdowns() {
    const dropdownToggleList = document.querySelectorAll('.dropdown-toggle');
    if (dropdownToggleList.length > 0) {
        dropdownToggleList.forEach(dropdownToggle => {
            dropdownToggle.addEventListener('click', function(e) {
                e.preventDefault();
                const dropdown = this.nextElementSibling;
                if (dropdown.classList.contains('show')) {
                    dropdown.classList.remove('show');
                } else {
                    // Close all other dropdowns
                    document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                        menu.classList.remove('show');
                    });
                    dropdown.classList.add('show');
                }
            });
        });

        // Close dropdowns when clicking outside
        document.addEventListener('click', function(e) {
            if (!e.target.matches('.dropdown-toggle') && !e.target.closest('.dropdown-menu')) {
                document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                    menu.classList.remove('show');
                });
            }
        });
    }
}

// 3. Form validation
function initFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');

    if (forms.length > 0) {
        forms.forEach(form => {
            form.addEventListener('submit', function(event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();

                    // Show custom validation messages
                    form.querySelectorAll('input, select, textarea').forEach(input => {
                        if (!input.validity.valid) {
                            const formGroup = input.closest('.mb-3');
                            if (formGroup) {
                                const feedback = formGroup.querySelector('.invalid-feedback');
                                if (!feedback) {
                                    const newFeedback = document.createElement('div');
                                    newFeedback.className = 'invalid-feedback';
                                    newFeedback.textContent = input.validationMessage || 'هذا الحقل مطلوب';
                                    formGroup.appendChild(newFeedback);
                                }
                            }
                        }
                    });

                    // Show toast with error message
                    showToast('يرجى تصحيح الأخطاء في النموذج', '#dc3545');
                }

                form.classList.add('was-validated');
            }, false);
        });
    }
}

// 4. Task Status Update (enhanced existing functionality)
function initStatusUpdaters() {
    const statusButtons = document.querySelectorAll('.change-status');

    if (statusButtons.length > 0) {
        statusButtons.forEach(button => {
            button.addEventListener('click', function() {
                const taskId = this.dataset.taskId;
                const newStatus = this.dataset.newStatus;
                const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') ||
                                 document.querySelector('input[name="csrfmiddlewaretoken"]')?.value;

                if (!csrfToken) {
                    console.error('CSRF token not found');
                    showToast('خطأ في العملية: الرمز المميز غير موجود', '#dc3545');
                    return;
                }

                // Show loading state
                button.disabled = true;
                const originalText = button.innerHTML;
                button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> جاري التحديث...';

                // Send status update request
                fetch(`/tasks/${taskId}/update_status/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({status: newStatus})
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        // Update UI
                        const statusElement = document.getElementById(`task-${taskId}-status`);
                        if (statusElement) {
                            // Update status text based on the status code
                            const statusMap = {
                                'pending': 'قيد الانتظار',
                                'in_progress': 'يجرى العمل عليها',
                                'completed': 'مكتملة',
                                'canceled': 'ملغاة',
                                'deferred': 'مؤجلة',
                                'failed': 'فشلت'
                            };

                            statusElement.textContent = statusMap[newStatus] || newStatus;

                            // Update task card status class if it exists
                            const taskCard = statusElement.closest('.task-card');
                            if (taskCard) {
                                // Remove all status classes
                                taskCard.classList.remove('pending', 'in-progress', 'completed', 'canceled', 'deferred', 'failed');
                                // Add the new status class
                                taskCard.classList.add(newStatus.replace('_', '-'));
                            }
                        }

                        // Show success message
                        showToast('تم تحديث حالة المهمة بنجاح!', '#198754');
                    } else {
                        showToast('حدث خطأ أثناء تحديث الحالة', '#dc3545');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showToast('حدث خطأ أثناء الاتصال بالخادم', '#dc3545');
                })
                .finally(() => {
                    // Restore button state
                    button.disabled = false;
                    button.innerHTML = originalText;
                });
            });
        });
    }
}

// دالة جديدة لجلب الإحصائيات المحدثة
function updateDashboardStats() {
    fetch('/api/dashboard_stats/') // تأكد من إنشاء هذا الرابط في Django
        .then(response => response.json())
        .then(data => {
            document.getElementById('meetingCount').textContent = data.meeting_count;
            document.getElementById('taskCount').textContent = data.task_count;
            document.getElementById('completedTaskCount').textContent = data.completed_task_count;
            document.getElementById('userCount').textContent = data.user_count;
        })
        .catch(error => {
            console.error('Error fetching stats:', error);
            showToast('حدث خطأ أثناء تحديث الإحصائيات', '#dc3545');
        });
}

// 5. Delete confirmations
function initDeleteConfirmations() {
    const deleteButtons = document.querySelectorAll('.confirm-delete');

    if (deleteButtons.length > 0) {
        deleteButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();

                const itemType = this.dataset.type || 'العنصر';
                const itemId = this.dataset.id;
                const deleteUrl = this.href || this.dataset.url;

                if (!deleteUrl) {
                    console.error('Delete URL not specified');
                    return;
                }

                if (confirm(`هل أنت متأكد من حذف هذا ${itemType}؟`)) {
                    window.location.href = deleteUrl;
                }
            });
        });
    }
}

// 6. Initialize tooltips
function initTooltips() {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (tooltipTriggerList.length > 0) {
        tooltipTriggerList.forEach(tooltipTriggerEl => {
            new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

// 7. Enhanced Toast notifications
function showToast(message, bgColor = '#198754', duration = 3000) {
    // Check if Toastify is available
    if (typeof Toastify === 'function') {
        Toastify({
            text: message,
            duration: duration,
            close: true,
            gravity: "top",
            position: "center",
            backgroundColor: bgColor,
            stopOnFocus: true,
            className: 'rounded shadow-sm'
        }).showToast();
    } else {
        // Fallback if Toastify is not available
        const toast = document.createElement('div');
        toast.className = 'toast-notification';
        toast.style.backgroundColor = bgColor;
        toast.textContent = message;

        document.body.appendChild(toast);

        // Animate in
        setTimeout(() => {
            toast.style.opacity = '1';
            toast.style.transform = 'translateY(0)';
        }, 10);

        // Remove after duration
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(-20px)';

            // Remove from DOM after animation
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, duration);
    }
}

// 8. Shorthand function for confirm delete (for backward compatibility)
function confirmDelete(id, type = 'الاجتماع', url = null) {
    if (!url && type === 'الاجتماع') {
        url = `/meetings/delete/${id}/`;
    }

    if (confirm(`هل أنت متأكد من حذف هذا ${type}؟`)) {
        window.location.href = url;
    }
}

// 9. Date and time formatting utility
function formatDate(dateString) {
    const options = {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };

    return new Date(dateString).toLocaleDateString('ar-SA', options);
}

// 10. Add dynamic table sorting
function initTableSorting() {
    const sortableTables = document.querySelectorAll('.table-sortable');

    if (sortableTables.length > 0) {
        sortableTables.forEach(table => {
            const headers = table.querySelectorAll('th[data-sort]');

            headers.forEach(header => {
                header.addEventListener('click', function() {
                    const sortKey = this.dataset.sort;
                    const sortDirection = this.classList.contains('sort-asc') ? 'desc' : 'asc';

                    // Remove sort classes from all headers
                    headers.forEach(h => h.classList.remove('sort-asc', 'sort-desc'));

                    // Add sort class to current header
                    this.classList.add(`sort-${sortDirection}`);

                    // Get all rows except header row
                    const tbody = table.querySelector('tbody');
                    const rows = Array.from(tbody.querySelectorAll('tr'));

                    // Sort rows
                    rows.sort((a, b) => {
                        const aValue = a.querySelector(`td[data-sort="${sortKey}"]`).textContent.trim();
                        const bValue = b.querySelector(`td[data-sort="${sortKey}"]`).textContent.trim();

                        if (sortDirection === 'asc') {
                            return aValue.localeCompare(bValue, 'ar');
                        } else {
                            return bValue.localeCompare(aValue, 'ar');
                        }
                    });

                    // Append sorted rows
                    rows.forEach(row => tbody.appendChild(row));
                });
            });
        });
    }
}

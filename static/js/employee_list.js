document.addEventListener('DOMContentLoaded', function() {
    // Enhanced Variable Initialization
    const toggleCheckbox = document.getElementById('employeeStatusToggle');
    const toggleStatusText = document.getElementById('toggleStatusText');
    const employeeListTitle = document.getElementById('employeeListTitle');
    const urlParams = new URLSearchParams(window.location.search);
    const searchInput = document.querySelector('.search-autocomplete');
    const searchResultsDropdown = document.querySelector('.search-results-dropdown');
    const employeeFilterForm = document.getElementById('employeeFilterForm');
    const employeesTable = document.getElementById('employeesTable');

    // View Toggle Elements
    const tableViewBtn = document.getElementById('tableViewBtn');
    const cardViewBtn = document.getElementById('cardViewBtn');
    const tableView = document.getElementById('tableView');
    const cardView = document.getElementById('cardView');

    // Advanced Search Toggle
    const advancedSearchToggle = document.getElementById('advancedSearchToggle');

    // Initialize View Toggle Functionality
    function initializeViewToggle() {
        if (tableViewBtn && cardViewBtn && tableView && cardView) {
            // Get saved view preference
            const savedView = localStorage.getItem('employeeViewMode') || 'table';

            if (savedView === 'card') {
                showCardView();
            } else {
                showTableView();
            }

            tableViewBtn.addEventListener('click', function() {
                showTableView();
                localStorage.setItem('employeeViewMode', 'table');
            });

            cardViewBtn.addEventListener('click', function() {
                showCardView();
                localStorage.setItem('employeeViewMode', 'card');
            });
        }
    }

    function showTableView() {
        if (tableView && cardView && tableViewBtn && cardViewBtn) {
            tableView.style.display = 'block';
            cardView.style.display = 'none';
            tableViewBtn.classList.add('active');
            cardViewBtn.classList.remove('active');
        }
    }

    function showCardView() {
        if (tableView && cardView && tableViewBtn && cardViewBtn) {
            tableView.style.display = 'none';
            cardView.style.display = 'block';
            cardViewBtn.classList.add('active');
            tableViewBtn.classList.remove('active');
        }
    }

    // Initialize view toggle
    initializeViewToggle();


    // Handle form submission
    if (employeeFilterForm) {
        employeeFilterForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const searchValue = searchInput.value.trim();

            // Update form search field value
            let searchField = employeeFilterForm.querySelector('input[name="search"]');
            if (!searchField) {
                searchField = document.createElement('input');
                searchField.type = 'hidden';
                searchField.name = 'search';
                employeeFilterForm.appendChild(searchField);
            }
            searchField.value = searchValue;

            // Submit the form
            this.submit();
        });
    }

    // ===== Enhanced Search and Filter Functions =====

    // 1. Enhanced Instant Search with Suggestions
    if (searchInput && searchResultsDropdown) {
        let searchTimeout;

        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const searchTerm = this.value.trim().toLowerCase();

            if (searchTerm.length < 2) {
                searchResultsDropdown.classList.add('d-none');
                return;
            }

            // Debounce search for better performance
            searchTimeout = setTimeout(() => {
                performEnhancedSearch(searchTerm);
            }, 300);
        });

        function performEnhancedSearch(searchTerm) {
            // Search in both table and card views
            const employeeElements = document.querySelectorAll('.employee-row, .modern-employee-card');
            const matchingEmployees = [];

            employeeElements.forEach(element => {
                const empId = element.getAttribute('data-emp-id');
                const empName = element.getAttribute('data-emp-name').toLowerCase();
                const dept = element.getAttribute('data-dept').toLowerCase();
                const condition = element.getAttribute('data-condition').toLowerCase();

                // Enhanced search including more fields
                if (empName.includes(searchTerm) ||
                    empId.includes(searchTerm) ||
                    dept.includes(searchTerm) ||
                    condition.includes(searchTerm)) {
                    matchingEmployees.push({
                        id: empId,
                        name: element.getAttribute('data-emp-name'),
                        dept: element.getAttribute('data-dept'),
                        condition: element.getAttribute('data-condition')
                    });
                }
            });

            displaySearchResults(matchingEmployees, searchTerm);
        }

        function displaySearchResults(matchingEmployees, searchTerm) {
            if (matchingEmployees.length > 0) {
                searchResultsDropdown.innerHTML = '';
                searchResultsDropdown.classList.remove('d-none');

                // Create enhanced result items
                matchingEmployees.slice(0, 6).forEach((emp, index) => {
                    const resultItem = document.createElement('div');
                    resultItem.className = 'search-result-item';
                    resultItem.innerHTML = `
                        <div class="d-flex align-items-center p-3">
                            <div class="avatar-sm bg-gradient-primary text-white me-3 flex-shrink-0 rounded-circle d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;">
                                ${emp.name.charAt(0).toUpperCase()}
                            </div>
                            <div class="flex-grow-1">
                                <div class="fw-semibold text-dark mb-1">${highlightSearchTerm(emp.name, searchTerm)}</div>
                                <div class="d-flex align-items-center gap-2">
                                    <span class="badge bg-primary-subtle text-primary">#${emp.id}</span>
                                    ${emp.dept ? `<span class="badge bg-info-subtle text-info">${emp.dept}</span>` : ''}
                                </div>
                            </div>
                            <div class="text-end">
                                <i class="fas fa-arrow-left text-muted"></i>
                            </div>
                        </div>
                    `;

                    resultItem.addEventListener('click', function() {
                        navigateToEmployee(emp.id);
                    });

                    searchResultsDropdown.appendChild(resultItem);
                });

                // Add "View All Results" if more than 6 results
                if (matchingEmployees.length > 6) {
                    const viewAllItem = document.createElement('div');
                    viewAllItem.className = 'p-3 text-center border-top bg-light';
                    viewAllItem.innerHTML = `
                        <button class="btn btn-outline-primary btn-sm">
                            <i class="fas fa-search me-1"></i>
                            عرض كل النتائج (${matchingEmployees.length})
                        </button>
                    `;
                    viewAllItem.addEventListener('click', function(e) {
                        e.preventDefault();
                        if (employeeFilterForm) employeeFilterForm.submit();
                    });
                    searchResultsDropdown.appendChild(viewAllItem);
                }
            } else {
                searchResultsDropdown.innerHTML = `
                    <div class="p-4 text-center text-muted">
                        <i class="fas fa-search-minus fa-2x mb-2 text-muted"></i>
                        <div class="fw-medium">لا توجد نتائج مطابقة</div>
                        <small>جرب البحث بكلمات مختلفة</small>
                    </div>
                `;
                searchResultsDropdown.classList.remove('d-none');
            }
        }

        function highlightSearchTerm(text, term) {
            const regex = new RegExp(`(${term})`, 'gi');
            return text.replace(regex, '<mark class="bg-warning text-dark">$1</mark>');
        }

        function navigateToEmployee(empId) {
            if (typeof employeeDetailUrlTemplate !== 'undefined') {
                window.location.href = employeeDetailUrlTemplate.replace('0', empId);
            } else {
                console.error("Employee detail URL template not found.");
            }
        }

        // إخفاء قائمة النتائج عند النقر خارجها
        document.addEventListener('click', function(e) {
            if (!searchInput.contains(e.target) && !searchResultsDropdown.contains(e.target)) {
                searchResultsDropdown.classList.add('d-none');
            }
        });

        // إظهار القائمة عند التركيز على حقل البحث
        searchInput.addEventListener('focus', function() {
            if (this.value.trim().length >= 2 && searchResultsDropdown.children.length > 0) {
                searchResultsDropdown.classList.remove('d-none');
            }
        });
    }

    // 2. إزالة الفلاتر النشطة
    const removeFilterButtons = document.querySelectorAll('.remove-filter');
    removeFilterButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const fieldName = this.getAttribute('data-field');
            const currentUrl = new URL(window.location.href);
            currentUrl.searchParams.delete(fieldName);
            window.location.href = currentUrl.toString();
        });
    });

    // 3. تبديل البحث المتقدم - REMOVED
    // if (toggleAdvancedSearchBtn && advancedSearchCollapse) {
    //     toggleAdvancedSearchBtn.addEventListener('click', function() {
    //         const bsCollapse = new bootstrap.Collapse(advancedSearchCollapse, {
    //             toggle: false // Prevent auto-toggle, we'll do it manually
    //         });
    //         bsCollapse.toggle();
    //     });
    // }

    // 4. ترتيب جدول الموظفين
    if (employeesTable) {
        const sortOptions = document.querySelectorAll('.sort-option');
        const sortDirections = document.querySelectorAll('.sort-direction');
        let currentSortField = localStorage.getItem('employeesSortField') || 'emp_id';
        let currentSortDirection = localStorage.getItem('employeesSortDirection') || 'asc';

        function sortTable() {
            const tbody = employeesTable.querySelector('tbody');
            if (!tbody) return;
            const rows = Array.from(tbody.querySelectorAll('tr'));

            rows.sort((a, b) => {
                let aValue, bValue;

                switch (currentSortField) {
                    case 'emp_id':
                        aValue = parseInt(a.getAttribute('data-emp-id')) || 0;
                        bValue = parseInt(b.getAttribute('data-emp-id')) || 0;
                        break;
                    case 'emp_full_name':
                        aValue = a.getAttribute('data-emp-name') || "";
                        bValue = b.getAttribute('data-emp-name') || "";
                        break;
                    case 'department':
                        aValue = a.getAttribute('data-dept') || "";
                        bValue = b.getAttribute('data-dept') || "";
                        break;
                    case 'working_condition':
                        aValue = a.getAttribute('data-condition') || "";
                        bValue = b.getAttribute('data-condition') || "";
                        break;
                    default: // emp_date_hiring or other date fields
                        aValue = new Date(a.querySelector(`td[data-sort-value="${currentSortField}"]`)?.textContent || 0);
                        bValue = new Date(b.querySelector(`td[data-sort-value="${currentSortField}"]`)?.textContent || 0);
                        if (isNaN(aValue)) aValue = new Date(0); // Handle invalid dates
                        if (isNaN(bValue)) bValue = new Date(0);
                }

                if (aValue === bValue) return 0;

                if (typeof aValue === 'string' && typeof bValue === 'string') {
                    aValue = aValue.toLowerCase();
                    bValue = bValue.toLowerCase();
                }


                if (currentSortDirection === 'asc') {
                    return aValue > bValue ? 1 : -1;
                } else {
                    return aValue < bValue ? 1 : -1;
                }
            });

            rows.forEach(row => tbody.appendChild(row));
            updateSortIcons();
        }

        function updateSortIcons() {
            const headers = employeesTable.querySelectorAll('th.sortable');
            headers.forEach(header => {
                const sortField = header.getAttribute('data-sort');
                const icon = header.querySelector('i.fa-sort, i.fa-sort-up, i.fa-sort-down');
                if (icon) {
                    if (sortField === currentSortField) {
                        icon.className = currentSortDirection === 'asc'
                            ? 'fas fa-sort-up ms-1 text-primary'
                            : 'fas fa-sort-down ms-1 text-primary';
                    } else {
                        icon.className = 'fas fa-sort ms-1 text-muted small';
                    }
                }
            });
        }

        sortOptions.forEach(option => {
            option.addEventListener('click', function(e) {
                e.preventDefault();
                const sortField = this.getAttribute('data-sort');
                if (sortField === currentSortField) {
                    currentSortDirection = currentSortDirection === 'asc' ? 'desc' : 'asc';
                } else {
                    currentSortField = sortField;
                    currentSortDirection = 'asc';
                }
                localStorage.setItem('employeesSortField', currentSortField);
                localStorage.setItem('employeesSortDirection', currentSortDirection);
                sortTable();
            });
        });

        sortDirections.forEach(direction => {
            direction.addEventListener('click', function(e) {
                e.preventDefault();
                currentSortDirection = this.getAttribute('data-direction');
                localStorage.setItem('employeesSortDirection', currentSortDirection);
                sortTable();
            });
        });

        const sortableHeaders = employeesTable.querySelectorAll('th.sortable');
        sortableHeaders.forEach(header => {
            header.addEventListener('click', function() {
                const sortField = this.getAttribute('data-sort');
                if (sortField === currentSortField) {
                    currentSortDirection = currentSortDirection === 'asc' ? 'desc' : 'asc';
                } else {
                    currentSortField = sortField;
                    currentSortDirection = 'asc';
                }
                localStorage.setItem('employeesSortField', currentSortField);
                localStorage.setItem('employeesSortDirection', currentSortDirection);
                sortTable();
            });
        });
        sortTable();
    }

    // ===== وظائف التبديل بين الموظفين النشطين وغير النشطين =====
    function updateToggleTextAndRedirect() {
        const newStatus = toggleCheckbox.checked ? 'active' : 'inactive';

        // Use AJAX for dynamic filtering instead of page reload
        updateEmployeeListDynamically(newStatus);
    }

    // New function for dynamic AJAX filtering
    function updateEmployeeListDynamically(status) {
        // Show loading state
        showLoadingState();

        // Prepare URL parameters
        const currentParams = new URLSearchParams(window.location.search);
        currentParams.set('status', status);

        // Make AJAX request
        fetch(`${employeeListAjaxUrl}?${currentParams.toString()}`, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update statistics cards
                updateStatisticsCards(data.statistics);

                // Update toggle UI
                updateToggleUI(status, data.statistics);

                // Update employee list
                updateEmployeeListContent(data);

                // Update URL without page reload
                const newUrl = `${window.location.pathname}?${currentParams.toString()}`;
                window.history.pushState({}, '', newUrl);

                // Re-initialize interactions
                setTimeout(() => {
                    addTableInteractions();
                    addCardInteractions();
                    initializeDeleteButtons();
                }, 100);

                // Show success message
                showToast(`تم تحديث قائمة ${status === 'active' ? 'الموظفين النشطين' : 'الموظفين غير النشطين'} بنجاح`, 'success');
            } else {
                showToast('حدث خطأ أثناء تحديث البيانات', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('حدث خطأ في الاتصال بالخادم', 'error');
        })
        .finally(() => {
            hideLoadingState();
        });
    }


    function updateToggleTextWithoutRedirect() {
        if (toggleCheckbox.checked) {
            toggleStatusText.textContent = 'موظفين نشطين';
            toggleStatusText.classList.remove('text-danger');
            toggleStatusText.classList.add('text-success');
            if (employeeListTitle) {
                employeeListTitle.textContent = 'قائمة الموظفين النشطين';
            }
        } else {
            toggleStatusText.textContent = 'موظفين غير نشطين';
            toggleStatusText.classList.remove('text-success');
            toggleStatusText.classList.add('text-danger');
            if (employeeListTitle) {
                employeeListTitle.textContent = 'قائمة الموظفين غير النشطين';
            }
        }
    }

    // Function to update statistics cards dynamically
    function updateStatisticsCards(stats) {
        // Update total employees
        const totalEmployeesCount = document.getElementById('totalEmployeesCount');
        if (totalEmployeesCount) {
            animateCounterUpdate(totalEmployeesCount, stats.total_employees);
        }

        // Update active employees
        const activeEmployeesCount = document.getElementById('activeEmployeesCount');
        const activeEmployeesPercentage = document.getElementById('activeEmployeesPercentage');
        const activeEmployeesProgress = document.getElementById('activeEmployeesProgress');

        if (activeEmployeesCount) {
            animateCounterUpdate(activeEmployeesCount, stats.active_employees);
        }
        if (activeEmployeesPercentage) {
            activeEmployeesPercentage.textContent = `${stats.active_percentage}% من الإجمالي`;
        }
        if (activeEmployeesProgress) {
            activeEmployeesProgress.style.width = `${stats.active_percentage}%`;
        }

        // Update resigned employees
        const resignedEmployeesCount = document.getElementById('resignedEmployeesCount');
        const resignedEmployeesProgress = document.getElementById('resignedEmployeesProgress');

        if (resignedEmployeesCount) {
            animateCounterUpdate(resignedEmployeesCount, stats.resigned_employees);
        }
        if (resignedEmployeesProgress) {
            resignedEmployeesProgress.style.width = `${stats.resigned_percentage}%`;
        }

        // Update on leave employees
        const onLeaveEmployeesCount = document.getElementById('onLeaveEmployeesCount');
        if (onLeaveEmployeesCount) {
            animateCounterUpdate(onLeaveEmployeesCount, stats.on_leave_employees);
        }
    }

    // Function to update toggle UI
    function updateToggleUI(status, stats) {
        const toggleStatusText = document.getElementById('toggleStatusText');
        const toggleStatusIcon = document.getElementById('toggleStatusIcon');
        const toggleStatusLabel = document.getElementById('toggleStatusLabel');
        const toggleActiveCount = document.getElementById('toggleActiveCount');
        const toggleInactiveCount = document.getElementById('toggleInactiveCount');

        if (status === 'active') {
            if (toggleStatusText) {
                toggleStatusText.classList.remove('text-danger');
                toggleStatusText.classList.add('text-success');
            }
            if (toggleStatusIcon) {
                toggleStatusIcon.className = 'fas fa-user-check me-2';
            }
            if (toggleStatusLabel) {
                toggleStatusLabel.textContent = 'موظفين نشطين';
            }
        } else {
            if (toggleStatusText) {
                toggleStatusText.classList.remove('text-success');
                toggleStatusText.classList.add('text-danger');
            }
            if (toggleStatusIcon) {
                toggleStatusIcon.className = 'fas fa-user-times me-2';
            }
            if (toggleStatusLabel) {
                toggleStatusLabel.textContent = 'موظفين غير نشطين';
            }
        }

        // Update mini stats
        if (toggleActiveCount) {
            animateCounterUpdate(toggleActiveCount, stats.active_employees);
        }
        if (toggleInactiveCount) {
            animateCounterUpdate(toggleInactiveCount, stats.resigned_employees);
        }

        // Update list title
        const employeeListIcon = document.getElementById('employeeListIcon');
        const employeeListTitleText = document.getElementById('employeeListTitleText');
        const employeeListCount = document.getElementById('employeeListCount');

        if (status === 'active') {
            if (employeeListIcon) {
                employeeListIcon.className = 'fas fa-users text-success me-2';
            }
            if (employeeListTitleText) {
                employeeListTitleText.textContent = 'قائمة الموظفين النشطين';
            }
        } else {
            if (employeeListIcon) {
                employeeListIcon.className = 'fas fa-user-times text-danger me-2';
            }
            if (employeeListTitleText) {
                employeeListTitleText.textContent = 'قائمة الموظفين غير النشطين';
            }
        }

        if (employeeListCount) {
            animateCounterUpdate(employeeListCount, stats.filtered_count);
        }
    }

    // Function to update employee list content
    function updateEmployeeListContent(data) {
        const employeeListContainer = document.getElementById('employeeListContainer');
        if (!employeeListContainer) return;

        // Add fade out effect
        employeeListContainer.style.transition = 'opacity 0.3s ease';
        employeeListContainer.style.opacity = '0';

        setTimeout(() => {
            // Update table view
            const tableView = document.getElementById('tableView');
            if (tableView && data.table_html) {
                tableView.outerHTML = data.table_html;
            }

            // Update card view
            const cardView = document.getElementById('cardView');
            if (cardView && data.card_html) {
                cardView.outerHTML = data.card_html;
            }

            // Restore view mode
            const savedView = localStorage.getItem('employeeViewMode') || 'table';
            if (savedView === 'card') {
                showCardView();
            } else {
                showTableView();
            }

            // Fade in effect
            employeeListContainer.style.opacity = '1';
        }, 300);
    }

    // Animate counter updates
    function animateCounterUpdate(element, targetValue) {
        const currentValue = parseInt(element.textContent) || 0;
        const increment = (targetValue - currentValue) / 20;
        let current = currentValue;

        const timer = setInterval(() => {
            current += increment;
            if ((increment > 0 && current >= targetValue) || (increment < 0 && current <= targetValue)) {
                element.textContent = targetValue;
                clearInterval(timer);
            } else {
                element.textContent = Math.floor(current);
            }
        }, 50);
    }

    if (toggleCheckbox && toggleStatusText) {
        updateToggleTextWithoutRedirect(); // Set initial text
        toggleCheckbox.addEventListener('change', updateToggleTextAndRedirect);
    }


    // ===== وظائف البحث المتقدم - REMOVED =====
    // function setAdvancedSearchFields() {
    //     const fieldsToKeep = [
    //         'phone', 'national_id', 'car', 'insurance_number',
    //         'hire_date_from', 'hire_date_to', 'birth_date_from', 'birth_date_to',
    //         'age_from', 'age_to', 'marital_status', 'governorate',
    //         'shift_type', 'car_pick_up_point'
    //     ];
    //     let advancedFiltersApplied = false;
    //     fieldsToKeep.forEach(field => {
    //         const value = urlParams.get(field);
    //         if (value) {
    //             const input = document.querySelector(`[name="${field}"]`);
    //             if (input) {
    //                 input.value = value;
    //                 advancedFiltersApplied = true;
    //             }
    //         }
    //     });
    //     // Show advanced search if any advanced filter is active
    //     // const advancedSearchCollapse = document.getElementById('collapseAdvanced'); // Ensure this is defined if used
    //     // if (advancedFiltersApplied && advancedSearchCollapse && !advancedSearchCollapse.classList.contains('show')) {
    //     //      const bsCollapse = new bootstrap.Collapse(advancedSearchCollapse, { show: true });
    //     // }
    // }
    // setAdvancedSearchFields();

    const addSearchTooltips = () => {
        const searchInputs = document.querySelectorAll('input[type="text"][name="phone"], input[type="text"][name="national_id"], input[type="text"][name="insurance_number"]');
        searchInputs.forEach(input => {
            input.title = 'يمكنك البحث بجزء من الرقم أيضاً';
        });
    };
    addSearchTooltips();

    // Enhanced Table and Card Interactions
    function addTableInteractions() {
        const rows = document.querySelectorAll('.employee-row');
        rows.forEach(row => {
            row.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-2px)';
                this.style.boxShadow = '0 4px 15px rgba(0,0,0,.1)';
            });

            row.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
                this.style.boxShadow = 'none';
            });

            row.addEventListener('click', function(e) {
                if (e.target.closest('a, button, .btn-group, .dropdown')) return;
                const empId = this.getAttribute('data-emp-id');
                navigateToEmployee(empId);
            });
        });
    }

    function addCardInteractions() {
        const cards = document.querySelectorAll('.modern-employee-card');
        cards.forEach(card => {
            card.addEventListener('click', function(e) {
                if (e.target.closest('a, button, .btn-group, .dropdown')) return;
                const empId = this.getAttribute('data-emp-id');
                navigateToEmployee(empId);
            });

            // Add hover effects
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-8px)';
            });

            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
            });
        });
    }

    // Initialize interactions
    addTableInteractions();
    addCardInteractions();

    // Advanced Search Toggle
    if (advancedSearchToggle) {
        advancedSearchToggle.addEventListener('click', function() {
            const advancedFilters = document.getElementById('advancedFilters');
            if (advancedFilters) {
                const isExpanded = advancedFilters.classList.contains('show');
                const icon = this.querySelector('i');

                if (isExpanded) {
                    icon.className = 'fas fa-sliders-h me-1';
                    this.innerHTML = '<i class="fas fa-sliders-h me-1"></i>فلاتر متقدمة';
                } else {
                    icon.className = 'fas fa-times me-1';
                    this.innerHTML = '<i class="fas fa-times me-1"></i>إخفاء الفلاتر';
                }
            }
        });
    }

    // Enhanced Delete Employee Functionality
    function initializeDeleteButtons() {
        const deleteButtons = document.querySelectorAll('.delete-employee');
        deleteButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();

                const employeeId = this.getAttribute('data-employee-id');
                const employeeName = this.getAttribute('data-employee-name');

                // Show modern confirmation dialog
                showDeleteConfirmation(employeeId, employeeName);
            });
        });
    }

    function showDeleteConfirmation(employeeId, employeeName) {
        // Create modern modal for confirmation
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content border-0 shadow">
                    <div class="modal-header border-0 pb-0">
                        <h5 class="modal-title text-danger">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            تأكيد الحذف
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body pt-0">
                        <div class="text-center py-3">
                            <div class="mb-3">
                                <i class="fas fa-user-times fa-3x text-danger"></i>
                            </div>
                            <h6 class="mb-3">هل أنت متأكد من حذف الموظف؟</h6>
                            <p class="text-muted mb-0">
                                <strong>${employeeName}</strong><br>
                                <small>رقم الموظف: ${employeeId}</small>
                            </p>
                            <div class="alert alert-warning mt-3">
                                <i class="fas fa-warning me-1"></i>
                                لا يمكن التراجع عن هذا الإجراء
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer border-0 pt-0">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                            <i class="fas fa-times me-1"></i>إلغاء
                        </button>
                        <button type="button" class="btn btn-danger" id="confirmDelete">
                            <i class="fas fa-trash me-1"></i>حذف الموظف
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();

        // Handle confirmation
        modal.querySelector('#confirmDelete').addEventListener('click', function() {
            // Here you would typically make an AJAX request to delete the employee
            console.log('Deleting employee:', employeeId);
            bootstrapModal.hide();

            // Show success message
            showToast('تم حذف الموظف بنجاح', 'success');
        });

        // Clean up modal after hiding
        modal.addEventListener('hidden.bs.modal', function() {
            document.body.removeChild(modal);
        });
    }

    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-check-circle me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        // Add to toast container or create one
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }

        toastContainer.appendChild(toast);
        const bootstrapToast = new bootstrap.Toast(toast);
        bootstrapToast.show();

        // Remove toast after hiding
        toast.addEventListener('hidden.bs.toast', function() {
            toastContainer.removeChild(toast);
        });
    }

    // Initialize delete buttons
    initializeDeleteButtons();

    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-bs-theme', savedTheme);

    function toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-bs-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-bs-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeToggleIcon(newTheme);
    }

    function updateThemeToggleIcon(theme) {
        const themeToggleBtn = document.getElementById('themeToggleBtn');
        if (themeToggleBtn) {
            themeToggleBtn.innerHTML = theme === 'light' ? '<i class="fas fa-moon"></i>' : '<i class="fas fa-sun"></i>';
        }
    }

    // Enhanced Theme Toggle
    const themeToggleBtn = document.createElement('button');
    themeToggleBtn.id = 'themeToggleBtn';
    themeToggleBtn.className = 'btn btn-light position-fixed bottom-0 start-0 m-4 rounded-circle shadow-lg';
    themeToggleBtn.style.width = '50px';
    themeToggleBtn.style.height = '50px';
    themeToggleBtn.style.zIndex = '1050';
    themeToggleBtn.style.transition = 'all 0.3s ease';
    themeToggleBtn.onclick = toggleTheme;
    themeToggleBtn.title = 'تبديل المظهر';

    // Add hover effects
    themeToggleBtn.addEventListener('mouseenter', function() {
        this.style.transform = 'scale(1.1)';
    });

    themeToggleBtn.addEventListener('mouseleave', function() {
        this.style.transform = 'scale(1)';
    });

    document.body.appendChild(themeToggleBtn);
    updateThemeToggleIcon(savedTheme);

    // Enhanced Keyboard Shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl + F for search focus
        if (e.ctrlKey && e.key === 'f') {
            e.preventDefault();
            if (searchInput) {
                searchInput.focus();
                searchInput.select();
            }
        }

        // Ctrl + N for new employee
        if (e.ctrlKey && e.key === 'n') {
            e.preventDefault();
            if (typeof newEmployeeUrl !== 'undefined') {
                window.location.href = newEmployeeUrl;
            }
        }

        // Ctrl + T for table view
        if (e.ctrlKey && e.key === 't') {
            e.preventDefault();
            showTableView();
            localStorage.setItem('employeeViewMode', 'table');
        }

        // Ctrl + G for card view
        if (e.ctrlKey && e.key === 'g') {
            e.preventDefault();
            showCardView();
            localStorage.setItem('employeeViewMode', 'card');
        }

        // Escape to close search results
        if (e.key === 'Escape') {
            if (searchResultsDropdown && !searchResultsDropdown.classList.contains('d-none')) {
                searchResultsDropdown.classList.add('d-none');
            }
        }
    });

    // Enhanced Loading States
    function showLoadingState() {
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (loadingOverlay) {
            loadingOverlay.style.display = 'flex';
        }

        // Add loading class to main content
        const mainContent = document.querySelector('.card-body');
        if (mainContent) {
            mainContent.classList.add('content-loading');
        }

        // Disable toggle during loading
        if (toggleCheckbox) {
            toggleCheckbox.disabled = true;
        }
    }

    function hideLoadingState() {
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (loadingOverlay) {
            loadingOverlay.style.display = 'none';
        }

        // Remove loading class
        const mainContent = document.querySelector('.card-body');
        if (mainContent) {
            mainContent.classList.remove('content-loading');
        }

        // Re-enable toggle
        if (toggleCheckbox) {
            toggleCheckbox.disabled = false;
        }
    }

    // Enhanced Form Submission with Loading
    if (employeeFilterForm) {
        employeeFilterForm.addEventListener('submit', function() {
            showLoadingState();
        });
    }

    // Auto-hide loading on page load
    window.addEventListener('load', function() {
        hideLoadingState();
    });

    // Enhanced Statistics Animation
    function animateStatistics() {
        const statNumbers = document.querySelectorAll('.stats-number');
        statNumbers.forEach(stat => {
            const finalValue = parseInt(stat.textContent);
            let currentValue = 0;
            const increment = finalValue / 50;

            const timer = setInterval(() => {
                currentValue += increment;
                if (currentValue >= finalValue) {
                    stat.textContent = finalValue;
                    clearInterval(timer);
                } else {
                    stat.textContent = Math.floor(currentValue);
                }
            }, 30);
        });
    }

    // Run statistics animation on page load
    setTimeout(animateStatistics, 500);

    // Enhanced Print Functionality
    window.printEmployeeList = function() {
        const printWindow = window.open('', '_blank');
        const currentView = cardView && cardView.style.display !== 'none' ? 'card' : 'table';

        let printContent = '';
        if (currentView === 'card') {
            printContent = cardView.innerHTML;
        } else {
            printContent = tableView.innerHTML;
        }

        printWindow.document.write(`
            <html>
                <head>
                    <title>قائمة الموظفين</title>
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
                    <style>
                        body { font-family: 'Cairo', sans-serif; direction: rtl; }
                        .modern-employee-card { break-inside: avoid; margin-bottom: 1rem; }
                        .table { font-size: 0.9rem; }
                        @media print {
                            .btn, .dropdown { display: none !important; }
                            .card { border: 1px solid #dee2e6 !important; }
                        }
                    </style>
                </head>
                <body>
                    <div class="container-fluid">
                        <h2 class="text-center mb-4">قائمة الموظفين</h2>
                        ${printContent}
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
    };

    // Enhanced Export Functionality
    window.exportToExcel = function() {
        showToast('جاري تحضير ملف Excel...', 'info');

        // Here you would typically make an AJAX request to export data
        setTimeout(() => {
            showToast('تم تصدير البيانات بنجاح', 'success');
        }, 2000);
    };

    console.log('Enhanced Employee List initialized successfully');
});


    if (employeesTable) {
        let isScrolling;
        const tableContainer = employeesTable.closest('.table-responsive') || window; // Use table-responsive or window for scroll events

        tableContainer.addEventListener('scroll', (e) => {
            window.clearTimeout(isScrolling);
            if (employeesTable) employeesTable.classList.add('scrolling');
            isScrolling = setTimeout(() => {
                if (employeesTable) employeesTable.classList.remove('scrolling');
            }, 100);
        });

        const lazyImages = document.querySelectorAll('.employee-table-img[data-src]');
        if (lazyImages.length > 0 && 'IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                        observer.unobserve(img);
                    }
                });
            });
            lazyImages.forEach(img => imageObserver.observe(img));
        } else { // Fallback for browsers without IntersectionObserver or if no lazy images
            lazyImages.forEach(img => {
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
            });
        }
    }


    const searchInputPerf = document.querySelector('.search-autocomplete');
    if (searchInputPerf) {
        let searchTimeout;
        const searchCache = new Map();

        searchInputPerf.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            const query = e.target.value.trim().toLowerCase();
            if (query.length < 2) {
                if (searchResultsDropdown) searchResultsDropdown.classList.add('d-none');
                return;
            }
            if (searchCache.has(query)) {
                showSearchResults(searchCache.get(query));
                return;
            }
            searchTimeout = setTimeout(() => {
                performSearchAndDisplay(query, searchCache);
            }, 300);
        });
    }

    async function performSearchAndDisplay(query, cache) {
        // This function would ideally call an API endpoint for server-side search
        // For now, it simulates the previous client-side search for demonstration
        const employeeRows = document.querySelectorAll('.employee-row');
        const matchingEmployees = [];
        employeeRows.forEach(row => {
            const empId = row.getAttribute('data-emp-id');
            const empName = row.getAttribute('data-emp-name').toLowerCase();
            const dept = row.getAttribute('data-dept').toLowerCase();
            if (empName.includes(query) || empId.includes(query) || dept.includes(query)) {
                matchingEmployees.push({
                    id: empId,
                    name: row.getAttribute('data-emp-name'),
                    dept: row.getAttribute('data-dept')
                });
            }
        });
        cache.set(query, matchingEmployees);
        showSearchResults(matchingEmployees);
    }


    function showSearchResults(results) {
        if (!searchResultsDropdown) return;
        if (!results || results.length === 0) {
            searchResultsDropdown.innerHTML = `<div class="p-3 text-center text-muted"><i class="fas fa-search me-1"></i>لا توجد نتائج مطابقة</div>`;
            searchResultsDropdown.classList.remove('d-none');
            return;
        }
        searchResultsDropdown.innerHTML = results.slice(0,10).map(emp => `
            <div class="p-2 border-bottom search-result-item" data-id="${emp.id}">
                <div class="d-flex align-items-center">
                    <div class="avatar-sm bg-primary text-white me-2 flex-shrink-0">${emp.name.charAt(0)}</div>
                    <div>
                        <div class="fw-medium">${emp.name}</div>
                        <div class="small text-muted">${emp.dept || ''}</div>
                    </div>
                </div>
            </div>
        `).join('');

        searchResultsDropdown.querySelectorAll('.search-result-item').forEach(item => {
            item.addEventListener('click', function() {
                const empId = this.getAttribute('data-id');
                let detailUrl = employeeDetailUrlTemplate;
                if (detailUrl) {
                     window.location.href = detailUrl.replace('0', empId);
                } else {
                    console.error("Employee detail URL template not found for search results.");
                }
            });
        });
        searchResultsDropdown.classList.remove('d-none');
    }


    document.querySelectorAll('.action-btn').forEach(btn => {
        btn.addEventListener('mouseenter', function(e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            this.style.setProperty('--x', `${x}px`);
            this.style.setProperty('--y', `${y}px`);
        });
    });

    document.querySelectorAll('.stats-card').forEach(card => {
        card.addEventListener('mousemove', function(e) {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const angleX = (y - centerY) / 20;
            const angleY = (centerX - x) / 20;
            card.style.transform = `perspective(1000px) rotateX(${angleX}deg) rotateY(${angleY}deg) scale(1.05)`;
        });
        card.addEventListener('mouseleave', function() {
            card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale(1)';
        });
    });

    if (employeeFilterForm) {
        employeeFilterForm.addEventListener('change', function(e) {
            if (e.target.matches('select, input[type="checkbox"], input[type="radio"]')) {
                localStorage.setItem(`filter_${e.target.name}`, e.target.type === 'checkbox' ? e.target.checked : e.target.value);
            }
        });
        document.querySelectorAll('#employeeFilterForm select, #employeeFilterForm input[type="checkbox"], #employeeFilterForm input[type="radio"]').forEach(input => {
            const savedValue = localStorage.getItem(`filter_${input.name}`);
            if (savedValue !== null) {
                if (input.type === 'checkbox') {
                    input.checked = savedValue === 'true';
                } else {
                    input.value = savedValue;
                }
            }
        });
    }

    const paginationLinks = document.querySelectorAll('.pagination .page-link');
    paginationLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (!this.parentElement.classList.contains('active') && !this.parentElement.classList.contains('disabled')) {
                e.preventDefault();
                const targetPage = this.getAttribute('href');
                const contentArea = document.querySelector('.table-responsive') || document.body;
                contentArea.style.transition = 'opacity 0.3s ease-out';
                contentArea.style.opacity = '0';
                setTimeout(() => {
                    window.location.href = targetPage;
                }, 300);
            }
        });
    });
});

function showToast(message, type = 'success') {
    const toastEl = document.getElementById('successToast'); // Assuming this is your primary toast element
    if (!toastEl) return;

    const toastMessageEl = toastEl.querySelector('.toast-message');
    const toastIconEl = toastEl.querySelector('i'); // Assuming there's an icon element

    if (toastMessageEl) toastMessageEl.textContent = message;

    // Customize appearance based on type
    toastEl.classList.remove('bg-success', 'bg-danger', 'bg-warning', 'bg-info'); // Remove previous types
    if (toastIconEl) toastIconEl.classList.remove('fa-check-circle', 'fa-times-circle', 'fa-exclamation-triangle', 'fa-info-circle');

    switch (type) {
        case 'success':
            toastEl.classList.add('bg-success');
            if (toastIconEl) toastIconEl.classList.add('fa-check-circle');
            break;
        case 'error':
        case 'danger':
            toastEl.classList.add('bg-danger');
            if (toastIconEl) toastIconEl.classList.add('fa-times-circle');
            break;
        case 'warning':
            toastEl.classList.add('bg-warning');
            if (toastIconEl) toastIconEl.classList.add('fa-exclamation-triangle');
            break;
        case 'info':
            toastEl.classList.add('bg-info');
            if (toastIconEl) toastIconEl.classList.add('fa-info-circle');
            break;
        default:
            toastEl.classList.add('bg-primary'); // Default to primary or a neutral color
            if (toastIconEl) toastIconEl.classList.add('fa-bell');
            break;
    }

    const bsToast = bootstrap.Toast.getOrCreateInstance(toastEl);
    bsToast.show();
}


function showLoading() {
    const indicator = document.getElementById('loadingIndicator');
    if (indicator) indicator.style.display = 'block';
}

function hideLoading() {
    const indicator = document.getElementById('loadingIndicator');
    if (indicator) indicator.style.display = 'none';
}

const quickActionsBtn = document.getElementById('quickActionsBtn');
const quickActionsMenu = document.querySelector('.quick-actions-menu');

if (quickActionsBtn && quickActionsMenu) {
    quickActionsBtn.addEventListener('click', (e) => {
        e.stopPropagation(); // Prevent click from bubbling to document
        quickActionsMenu.style.display = quickActionsMenu.style.display === 'none' || quickActionsMenu.style.display === '' ? 'block' : 'none';
    });

    document.addEventListener('click', (e) => {
        if (quickActionsMenu.style.display === 'block' && !quickActionsBtn.contains(e.target) && !quickActionsMenu.contains(e.target)) {
            quickActionsMenu.style.display = 'none';
        }
    });
}


document.addEventListener('keydown', (e) => {
    if (e.ctrlKey) {
        switch (e.key.toLowerCase()) {
            case 'f':
                e.preventDefault();
                const searchField = document.querySelector('.search-autocomplete');
                if (searchField) searchField.focus();
                break;
            case 'n':
                e.preventDefault();
                if (typeof newEmployeeUrl !== 'undefined') window.location.href = newEmployeeUrl;
                break;
            case 'p':
                e.preventDefault();
                printEmployeeList();
                break;
            case 'e':
                e.preventDefault();
                exportToExcel();
                break;
            case '/':
                 if (document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {
                    e.preventDefault();
                    const modalElement = document.getElementById('keyboardShortcutsModal');
                    if (modalElement) {
                        const modal = bootstrap.Modal.getOrCreateInstance(modalElement);
                        modal.show();
                    }
                }
                break;
        }
    } else if (e.key === 'Escape') {
        const modalElement = document.getElementById('keyboardShortcutsModal');
        if (modalElement && modalElement.classList.contains('show')) {
             const modal = bootstrap.Modal.getInstance(modalElement);
             if(modal) modal.hide();
        }
        const dropdown = document.querySelector('.search-results-dropdown');
        if (dropdown && !dropdown.classList.contains('d-none')) {
            dropdown.classList.add('d-none');
        }
         if (quickActionsMenu && quickActionsMenu.style.display === 'block') {
            quickActionsMenu.style.display = 'none';
        }
    }
});

function printEmployeeList() {
    showLoading();
    const printContent = document.createElement('div');
    printContent.innerHTML = `
        <div class="text-center mb-4">
            <h3>قائمة الموظفين</h3>
            <p class="text-muted">تاريخ الطباعة: ${new Date().toLocaleDateString('ar-EG', { year: 'numeric', month: 'long', day: 'numeric' })}</p>
        </div>
    `;
    const tableToPrint = document.getElementById('employeesTable');
    if (!tableToPrint) {
        hideLoading();
        showToast('جدول الموظفين غير موجود للطباعة.', 'error');
        return;
    }
    const tableClone = tableToPrint.cloneNode(true);
    // Remove action buttons column for printing
    const actionHeader = Array.from(tableClone.querySelectorAll('thead th')).find(th => th.textContent.trim() === 'العمليات');
    const actionCellsIndex = actionHeader ? Array.from(actionHeader.parentNode.children).indexOf(actionHeader) : -1;

    if (actionCellsIndex !== -1) {
        tableClone.querySelectorAll('tr').forEach(row => {
            if (row.children[actionCellsIndex]) {
                row.removeChild(row.children[actionCellsIndex]);
            }
        });
    }
    // Remove images for printing to save ink and improve layout, or replace with initials
    tableClone.querySelectorAll('.employee-table-img').forEach(img => {
        const altText = img.alt || img.closest('tr')?.querySelector('.employee-name')?.textContent?.charAt(0) || ' ';
        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'avatar-print bg-secondary text-white'; // Add a specific class for print avatar
        avatarDiv.textContent = altText.charAt(0).toUpperCase();
        img.parentNode.replaceChild(avatarDiv, img);
    });


    printContent.appendChild(tableClone);

    const printWindow = window.open('', '_blank', 'height=600,width=800');
    printWindow.document.write(`
        <html dir="rtl">
        <head>
            <title>قائمة الموظفين - طباعة</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body { margin: 20px; font-family: 'Arial', sans-serif; }
                .table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
                .table th, .table td { border: 1px solid #dee2e6 !important; padding: 0.5rem; text-align: right; }
                .table thead th { background-color: #f8f9fa !important; font-weight: bold; }
                .avatar-print { width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: bold; margin: auto; }
                @media print {
                    body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
                    .no-print { display: none !important; }
                }
            </style>
        </head>
        <body>
            ${printContent.innerHTML}
        </body>
        </html>
    `);
    printWindow.document.close();
    printWindow.onload = function() {
        hideLoading();
        printWindow.focus(); // Required for some browsers
        printWindow.print();
        // printWindow.close(); // Closing too soon might cancel print in some browsers
    };
}


async function exportToExcel() {
    showLoading();
    try {
        // Ensure exportUrlTemplate is defined (e.g., in your Django template)
        if (typeof exportUrlTemplate === 'undefined') {
            showToast('رابط التصدير غير معرف.', 'error');
            hideLoading();
            return;
        }

        const currentFilters = new URLSearchParams(window.location.search).toString();
        const exportUrl = exportUrlTemplate; // Use the template directly

        const response = await fetch(exportUrl, { // Use the defined exportUrl
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken // Ensure csrfToken is globally available
            },
            body: JSON.stringify({
                format: 'xlsx',
                filters: currentFilters
            })
        });

        if (response.ok) {
            const blob = await response.blob();
            const contentDisposition = response.headers.get('content-disposition');
            let filename = `employees_${new Date().toISOString().split('T')[0]}.xlsx`; // Default filename
            if (contentDisposition) {
                const filenameMatch = contentDisposition.match(/filename="?(.+)"?/i);
                if (filenameMatch && filenameMatch.length > 1) {
                    filename = filenameMatch[1];
                }
            }

            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            showToast('تم تصدير البيانات بنجاح');
        } else {
            const errorData = await response.json().catch(() => ({ detail: 'فشل التصدير. الحالة: ' + response.status }));
            showToast(errorData.detail || 'فشل التصدير', 'error');
        }
    } catch (error) {
        console.error('Export error:', error);
        showToast('حدث خطأ أثناء التصدير: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}


let searchDebounceTimer;
const searchInputExp = document.querySelector('.search-autocomplete');

if (searchInputExp && typeof employeeSearchUrlTemplate !== 'undefined') {
    searchInputExp.addEventListener('input', (e) => {
        clearTimeout(searchDebounceTimer);
        const query = e.target.value.trim();
        const resultsDropdown = document.querySelector('.search-results-dropdown');

        if (query.length < 2) {
            if(resultsDropdown) resultsDropdown.classList.add('d-none');
            return;
        }

        showLoading();
        searchDebounceTimer = setTimeout(async () => {
            try {
                const searchUrl = employeeSearchUrlTemplate.replace('QUERY_PLACEHOLDER', encodeURIComponent(query));
                const response = await fetch(searchUrl); // Using GET by default for search
                if (!response.ok) {
                    throw new Error(`Search request failed: ${response.status}`);
                }
                const results = await response.json();
                updateSearchResultsForLiveSearch(results);
            } catch (error) {
                console.error('Search error:', error);
                if(resultsDropdown) {
                    resultsDropdown.innerHTML = `<div class="p-3 text-center text-danger">خطأ في البحث.</div>`;
                    resultsDropdown.classList.remove('d-none');
                }
            } finally {
                hideLoading();
            }
        }, 350); // Increased debounce time slightly
    });
}

function updateSearchResultsForLiveSearch(results) {
    const dropdown = document.querySelector('.search-results-dropdown');
    if (!dropdown) return;

    if (!results || !results.employees || results.employees.length === 0) {
        dropdown.innerHTML = `
            <div class="p-3 text-center text-muted">
                <i class="fas fa-search me-1"></i>
                لا توجد نتائج مطابقة
            </div>
        `;
        dropdown.classList.remove('d-none');
        return;
    }

    dropdown.innerHTML = results.employees.map(emp => `
        <div class="p-2 border-bottom search-result-item" data-id="${emp.id}">
            <div class="d-flex align-items-center">
                <div class="avatar-sm ${emp.image_url ? '' : 'bg-primary text-white'} me-2 flex-shrink-0">
                    ${emp.image_url ? `<img src="${emp.image_url}" alt="${emp.name}" class="rounded-circle object-fit-cover" width="32" height="32">` : emp.name.charAt(0).toUpperCase()}
                </div>
                <div>
                    <div class="fw-medium">${emp.name}</div>
                    <small class="text-muted d-block">${emp.job_title || ''}</small>
                    <small class="text-muted">${emp.department || ''}</small>
                </div>
            </div>
        </div>
    `).join('');

    dropdown.querySelectorAll('.search-result-item').forEach(item => {
        item.addEventListener('click', function() {
            const empId = this.getAttribute('data-id');
            if (typeof employeeDetailUrlTemplate !== 'undefined') {
                window.location.href = employeeDetailUrlTemplate.replace('0', empId);
            } else {
                console.error("Employee detail URL template not defined for live search results.");
            }
        });
    });
    dropdown.classList.remove('d-none');
}


const Accessibility = {
    init() {
        this.setupKeyboardNav();
        this.setupAnnouncer();
        this.addARIALabels();
    },

    setupKeyboardNav() {
        document.addEventListener('keydown', (e) => {
            if (e.target.matches('input, textarea, select')) return; // Ignore if in form element

            switch(e.key) {
                case '/':
                    if (e.ctrlKey) { // Keep Ctrl+/ for main search focus
                        e.preventDefault();
                        document.querySelector('.search-autocomplete')?.focus();
                    }
                    break;
                case 'Escape':
                    const activeModal = document.querySelector('.modal.show');
                    if (activeModal) {
                        bootstrap.Modal.getInstance(activeModal)?.hide();
                    } else {
                        document.querySelector('.search-results-dropdown:not(.d-none)')?.classList.add('d-none');
                        document.querySelector('.quick-actions-menu[style*="display: block"]')?.style.setProperty('display', 'none', 'important');
                    }
                    break;
                // Tab navigation is generally handled well by browsers, specific trapping might not be needed unless in modals.
            }
        });
    },

    setupAnnouncer() {
        let announcer = document.getElementById('liveAnnouncer');
        if (!announcer) {
            announcer = document.createElement('div');
            announcer.id = 'liveAnnouncer';
            announcer.setAttribute('aria-live', 'polite');
            announcer.className = 'visually-hidden'; // Bootstrap class for screen-reader only
            document.body.appendChild(announcer);
        }


        // Announce table updates (example, needs specific trigger)
        const tableBody = document.querySelector('#employeesTable tbody');
        if (tableBody) {
            const observer = new MutationObserver(() => {
                const count = tableBody.querySelectorAll('tr').length;
                this.announce(`تم تحديث قائمة الموظفين. يوجد الآن ${count} موظف.`);
            });
            observer.observe(tableBody, { childList: true, subtree: false }); // Observe direct children changes
        }
    },

    announce(message) {
        const announcer = document.getElementById('liveAnnouncer');
        if (announcer) {
            announcer.textContent = ''; // Clear previous message
            setTimeout(() => { // Timeout ensures screen readers pick up the change
                announcer.textContent = message;
            }, 100);
        }
    },

    addARIALabels() {
        document.querySelectorAll('.action-btn, .btn').forEach(btn => {
            if (!btn.hasAttribute('aria-label') && (btn.title || btn.textContent.trim())) {
                btn.setAttribute('aria-label', btn.title || btn.textContent.trim().replace(/\s+/g, ' '));
            }
        });
        const mainTable = document.getElementById('employeesTable');
        if (mainTable && !mainTable.hasAttribute('aria-label')) {
            mainTable.setAttribute('aria-label', 'جدول قائمة الموظفين');
        }
        document.querySelectorAll('input[placeholder]').forEach(input => {
            if (!input.hasAttribute('aria-label') && !document.querySelector(`label[for="${input.id}"]`)) {
                input.setAttribute('aria-label', input.placeholder);
            }
        });
    },
};

document.addEventListener('DOMContentLoaded', () => {
    Accessibility.init();
});


const SmartFilters = {
    init() {
        this.setupFilterMemory();
        this.setupSmartSort();
        // this.setupQuickFilters(); // Quick filters might be redundant with the main toggle
    },

    setupFilterMemory() {
        const form = document.getElementById('employeeFilterForm');
        if (!form) return;

        const loadFilters = () => {
            try {
                const savedFilters = JSON.parse(localStorage.getItem('employeeFilters') || '{}');
                Object.entries(savedFilters).forEach(([name, value]) => {
                    const input = form.querySelector(`[name="${name}"]`);
                    if (input) {
                        if (input.type === 'checkbox') input.checked = value === 'true';
                        else input.value = value;
                    }
                });
            } catch (e) { console.error("Error loading filters from localStorage:", e); }
        };
        loadFilters();

        form.addEventListener('change', e => {
            if (e.target.matches('select, input:not([type="button"]):not([type="submit"])')) {
                try {
                    const filters = JSON.parse(localStorage.getItem('employeeFilters') || '{}');
                    filters[e.target.name] = e.target.type === 'checkbox' ? e.target.checked.toString() : e.target.value;
                    localStorage.setItem('employeeFilters', JSON.stringify(filters));
                } catch (er) { console.error("Error saving filters to localStorage:", er); }
            }
        });
         // Clear filters button
        const clearFiltersButton = document.querySelector('a[href*="Hr:employees:list"].btn-outline-secondary'); // More specific selector
        if (clearFiltersButton && clearFiltersButton.textContent.includes('مسح الكل') || clearFiltersButton.textContent.includes('إعادة تعيين')) {
            clearFiltersButton.addEventListener('click', (e) => {
                // e.preventDefault(); // Prevent default link behavior if we are handling it all in JS
                localStorage.removeItem('employeeFilters');
                // Optionally, reset form fields visually if not redirecting
                // form.reset();
                // window.location.href = clearFiltersButton.href; // Then navigate
            });
        }
    },

    setupSmartSort() {
        const table = document.getElementById('employeesTable');
        if (!table) return;
        const headers = table.querySelectorAll('thead th[data-sort]');
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            // Add visual indicator for sortable columns if not already present by FontAwesome
            if (!header.querySelector('i.fa-sort')) {
                 // const sortIcon = document.createElement('i');
                 // sortIcon.className = 'fas fa-sort ms-1 text-muted small';
                 // header.appendChild(sortIcon);
            }

            header.addEventListener('click', () => {
                const sortKey = header.dataset.sort;
                let direction = 'asc';
                if (header.classList.contains('sort-asc')) {
                    direction = 'desc';
                    header.classList.remove('sort-asc');
                    header.classList.add('sort-desc');
                } else {
                    header.classList.remove('sort-desc');
                    header.classList.add('sort-asc');
                }
                // Reset other headers
                headers.forEach(h => {
                    if (h !== header) {
                        h.classList.remove('sort-asc', 'sort-desc');
                        // h.querySelector('i.fa-sort-up, i.fa-sort-down')?.classList.replace('fa-sort-up', 'fa-sort').replace('fa-sort-down', 'fa-sort');
                    }
                });
                // Update icon (already handled by main sort function's updateSortIcons)
                this.sortTable(table, sortKey, direction);
            });
        });
    },

    sortTable(table, key, direction) {
        const tbody = table.querySelector('tbody');
        if (!tbody) return;
        const rows = Array.from(tbody.querySelectorAll('tr'));
        const sortedRows = this.sortRows(rows, key, direction);

        // Batch DOM updates
        const fragment = document.createDocumentFragment();
        sortedRows.forEach(row => fragment.appendChild(row));
        tbody.innerHTML = ''; // Clear existing rows
        tbody.appendChild(fragment); // Append sorted rows

        // Update ARIA sort attributes
        table.querySelectorAll('thead th[data-sort]').forEach(th => {
            if (th.dataset.sort === key) {
                th.setAttribute('aria-sort', direction === 'asc' ? 'ascending' : 'descending');
            } else {
                th.removeAttribute('aria-sort');
            }
        });
         Accessibility.announce(`تم ترتيب الجدول حسب ${key} ${direction === 'asc' ? 'تصاعدياً' : 'تنازلياً'}`);
    },

    sortRows(rows, key, direction) {
        return rows.sort((a, b) => {
            let aValue = this.getSortValue(a, key);
            let bValue = this.getSortValue(b, key);

            // Type-aware comparison
            if (typeof aValue === 'string' && typeof bValue === 'string') {
                aValue = aValue.toLowerCase();
                bValue = bValue.toLowerCase();
            } else if (typeof aValue === 'number' && typeof bValue === 'number') {
                // standard numeric comparison
            } else { // mixed types or other, convert to string for safety
                aValue = String(aValue).toLowerCase();
                bValue = String(bValue).toLowerCase();
            }


            let comparison = 0;
            if (aValue > bValue) comparison = 1;
            else if (aValue < bValue) comparison = -1;
            return direction === 'asc' ? comparison : comparison * -1;
        });
    },

    getSortValue(row, key) {
        // Prioritize data attributes for sorting values if available
        const dataAttrValue = row.getAttribute(`data-${key}`);
        if (dataAttrValue) {
            // Attempt to parse as number if it looks like one
            const num = parseFloat(dataAttrValue);
            if (!isNaN(num) && dataAttrValue.trim() === num.toString()) return num;
            return dataAttrValue;
        }

        // Fallback to cell content
        const cell = row.querySelector(`td[data-column="${key}"]`) || row.cells[this.getColumnIndex(key)];
        let value = cell ? cell.textContent.trim() : '';

        if (key === 'emp_id' || key.includes('date') || key.includes('number')) { // Heuristic for numeric/date
            const num = parseFloat(value);
            if (!isNaN(num)) return num;
            if (key.includes('date')) return new Date(value).getTime() || 0; // Sort by timestamp
        }
        return value;
    },
    getColumnIndex(key) { // Helper to find column index by key if not using data-column
        const headers = document.querySelectorAll('#employeesTable thead th');
        for(let i=0; i < headers.length; i++) {
            if(headers[i].dataset.sort === key) return i;
        }
        return 0; // Default to first column if not found
    },


    updateResultsCount() {
        const visibleRows = document.querySelectorAll('#employeesTable tbody tr:not(.d-none)').length;
        const counterElement = document.querySelector('#employeeListTitle + small .fw-bold.text-primary'); // More specific
        if (counterElement) {
            counterElement.textContent = visibleRows;
        }
        const noResultsMessage = document.querySelector('.text-center.py-5'); // Assuming this is the "no results" message
        if (noResultsMessage) {
            noResultsMessage.style.display = visibleRows === 0 ? 'block' : 'none';
        }
         Accessibility.announce(`تم تحديث الفلتر. عدد النتائج: ${visibleRows}`);
    }
};

document.addEventListener('DOMContentLoaded', () => {
    SmartFilters.init();

    // Initialize ultra modern features
    initializeCounterAnimations();
    initializeEnhancedInteractions();
});

// Ultra Modern Counter Animation Function
function initializeCounterAnimations() {
    const counters = document.querySelectorAll('.counter-animate');

    const animateCounter = (counter) => {
        const target = parseInt(counter.getAttribute('data-target'));
        const duration = 2000; // 2 seconds
        const increment = target / (duration / 16); // 60fps
        let current = 0;

        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            counter.textContent = Math.floor(current);
        }, 16);
    };

    // Intersection Observer for triggering animations when visible
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !entry.target.classList.contains('animated')) {
                entry.target.classList.add('animated');
                animateCounter(entry.target);
            }
        });
    }, { threshold: 0.5 });

    counters.forEach(counter => observer.observe(counter));
}

// Enhanced Interactions for Ultra Modern UI
function initializeEnhancedInteractions() {
    // Enhanced search input with suggestions
    const searchInput = document.querySelector('.ultra-modern-search-input');
    if (searchInput) {
        let searchTimeout;

        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();

            if (query.length >= 2) {
                searchTimeout = setTimeout(() => {
                    // Show loading state
                    this.style.background = 'linear-gradient(90deg, #f8f9fa 25%, #e9ecef 50%, #f8f9fa 75%)';
                    this.style.backgroundSize = '200% 100%';
                    this.style.animation = 'loading 1.5s infinite';

                    // Simulate search delay
                    setTimeout(() => {
                        this.style.background = '';
                        this.style.animation = '';
                    }, 500);
                }, 300);
            }
        });
    }

    // Enhanced toggle with smooth transitions
    const statusToggle = document.getElementById('employeeStatusToggle');
    if (statusToggle) {
        statusToggle.addEventListener('change', function() {
            const toggleText = document.getElementById('toggleStatusText');

            if (toggleText) {
                // Add transition effect
                toggleText.style.opacity = '0.5';
                toggleText.style.transform = 'scale(0.95)';

                setTimeout(() => {
                    if (this.checked) {
                        toggleText.className = 'mb-1 fw-bold d-flex align-items-center text-success';
                        toggleText.innerHTML = '<i class="fas fa-user-check me-2"></i>موظفين نشطين';
                    } else {
                        toggleText.className = 'mb-1 fw-bold d-flex align-items-center text-danger';
                        toggleText.innerHTML = '<i class="fas fa-user-times me-2"></i>موظفين غير نشطين';
                    }

                    toggleText.style.opacity = '1';
                    toggleText.style.transform = 'scale(1)';
                }, 150);
            }
        });
    }

    // Enhanced card hover effects
    const employeeCards = document.querySelectorAll('.ultra-modern-stats-card');
    employeeCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px) scale(1.02)';

            // Add glow effect
            const glow = this.querySelector('.stats-glow');
            if (glow) {
                glow.style.opacity = '1';
            }
        });

        card.addEventListener('mouseleave', function() {
            this.style.transform = '';

            // Remove glow effect
            const glow = this.querySelector('.stats-glow');
            if (glow) {
                glow.style.opacity = '0';
            }
        });
    });

    // Add loading animation keyframes
    const style = document.createElement('style');
    style.textContent = `
        @keyframes loading {
            0% { background-position: 200% 0; }
            100% { background-position: -200% 0; }
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .fade-in-up {
            animation: fadeInUp 0.6s ease-out;
        }

        .ultra-modern-stats-card {
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .stats-glow {
            transition: opacity 0.3s ease;
        }
    `;
    document.head.appendChild(style);
}

// Reset Filters Function
function resetFilters() {
    const form = document.getElementById('employeeFilterForm');
    if (form) {
        // Clear all form inputs
        const inputs = form.querySelectorAll('input, select');
        inputs.forEach(input => {
            if (input.type === 'text' || input.type === 'search') {
                input.value = '';
            } else if (input.type === 'select-one') {
                input.selectedIndex = 0;
            } else if (input.type === 'checkbox' || input.type === 'radio') {
                input.checked = false;
            }
        });

        // Submit form to refresh results
        form.submit();
    }
}
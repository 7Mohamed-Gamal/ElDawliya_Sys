/**
 * Database Setup JavaScript
 *
 * This script handles the database setup form functionality, including:
 * - Testing the database connection
 * - Toggling Windows authentication fields
 * - Populating the database dropdown
 * - Form validation
 */

document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const useWindowsAuth = document.getElementById('use_windows_auth');
    const usernameField = document.getElementById('username');
    const passwordField = document.getElementById('password');
    const testConnectionBtn = document.getElementById('testConnection');
    const connectionLoader = document.getElementById('connectionLoader');
    const databaseSelect = document.getElementById('database');
    const dbForm = document.getElementById('dbSettingsForm');
    const saveButton = document.getElementById('saveButton');

    // Toggle Windows Authentication
    if (useWindowsAuth) {
        useWindowsAuth.addEventListener('change', function() {
            toggleWindowsAuth();
        });

        // Initial toggle based on checkbox state
        toggleWindowsAuth();
    }

    // Test Connection Button
    if (testConnectionBtn) {
        testConnectionBtn.addEventListener('click', function() {
            testConnection();
        });
    }

    // Form Submission
    if (dbForm) {
        dbForm.addEventListener('submit', function(e) {
            if (!validateForm()) {
                e.preventDefault();
                return false;
            }

            // Show loading state
            saveButton.disabled = true;
            saveButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>جاري الحفظ...';

            return true;
        });
    }

    /**
     * Toggle Windows Authentication fields
     */
    function toggleWindowsAuth() {
        if (useWindowsAuth.checked) {
            // Disable SQL authentication fields
            usernameField.disabled = true;
            passwordField.disabled = true;
            usernameField.parentElement.parentElement.classList.add('opacity-50');
            passwordField.parentElement.parentElement.classList.add('opacity-50');
        } else {
            // Enable SQL authentication fields
            usernameField.disabled = false;
            passwordField.disabled = false;
            usernameField.parentElement.parentElement.classList.remove('opacity-50');
            passwordField.parentElement.parentElement.classList.remove('opacity-50');
        }
    }

    /**
     * Test the database connection
     */
    function testConnection() {
        // Get form values
        const host = document.getElementById('host').value;
        const port = document.getElementById('db_port').value;
        const username = useWindowsAuth.checked ? '' : usernameField.value;
        const password = useWindowsAuth.checked ? '' : passwordField.value;
        const useWinAuth = useWindowsAuth.checked;

        // Validate required fields
        if (!host) {
            showAlert('يرجى إدخال اسم الخادم', 'danger');
            return;
        }

        if (!useWinAuth && (!username || !password)) {
            showAlert('يرجى إدخال اسم المستخدم وكلمة المرور', 'danger');
            return;
        }

        // Show loading state
        testConnectionBtn.disabled = true;
        connectionLoader.style.display = 'inline-block';
        testConnectionBtn.innerHTML = '<span class="loader" style="display:inline-block"></span> جاري الاختبار...';

        // Create form data
        const formData = new FormData();
        formData.append('host', host);
        formData.append('port', port);
        formData.append('username', username);
        formData.append('password', password);
        formData.append('auth_type', useWinAuth ? 'windows' : 'sql');

        // Send AJAX request
        fetch('/administrator/test-connection/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            // Reset button state
            testConnectionBtn.disabled = false;
            connectionLoader.style.display = 'none';
            testConnectionBtn.innerHTML = '<i class="fas fa-plug me-2"></i>اختبار الاتصال';

            if (data.success) {
                // Show success message
                showAlert('تم الاتصال بالخادم بنجاح!', 'success');

                // Populate database dropdown
                populateDatabaseDropdown(data.databases);
            } else {
                // Show error message
                showAlert(`فشل الاتصال: ${data.error}`, 'danger');
            }
        })
        .catch(error => {
            // Reset button state
            testConnectionBtn.disabled = false;
            connectionLoader.style.display = 'none';
            testConnectionBtn.innerHTML = '<i class="fas fa-plug me-2"></i>اختبار الاتصال';

            // Show error message
            showAlert(`حدث خطأ: ${error.message}`, 'danger');
        });
    }

    /**
     * Populate the database dropdown with available databases
     */
    function populateDatabaseDropdown(databases) {
        // Clear existing options
        databaseSelect.innerHTML = '';

        // Add default option
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = 'اختر قاعدة البيانات';
        databaseSelect.appendChild(defaultOption);

        // Add option to create new database
        const newDbOption = document.createElement('option');
        newDbOption.value = 'new';
        newDbOption.textContent = '-- إنشاء قاعدة بيانات جديدة --';
        databaseSelect.appendChild(newDbOption);

        // Add database options
        databases.forEach(db => {
            const option = document.createElement('option');
            option.value = db;
            option.textContent = db;
            databaseSelect.appendChild(option);
        });

        // Enable the dropdown
        databaseSelect.disabled = false;
    }

    /**
     * Validate the form before submission
     */
    function validateForm() {
        // Get form values
        const host = document.getElementById('host').value;
        const dbName = databaseSelect.value;
        const username = useWindowsAuth.checked ? '' : usernameField.value;
        const password = useWindowsAuth.checked ? '' : passwordField.value;

        // Validate required fields
        if (!host) {
            showAlert('يرجى إدخال اسم الخادم', 'danger');
            return false;
        }

        if (!dbName) {
            showAlert('يرجى اختيار قاعدة البيانات', 'danger');
            return false;
        }

        if (!useWindowsAuth.checked && (!username || !password)) {
            showAlert('يرجى إدخال اسم المستخدم وكلمة المرور', 'danger');
            return false;
        }

        return true;
    }

    /**
     * Show an alert message
     */
    function showAlert(message, type) {
        // Create alert element
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;

        // Insert alert before the form
        const form = document.getElementById('dbSettingsForm');
        form.parentNode.insertBefore(alertDiv, form);

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alertDiv.classList.remove('show');
            setTimeout(() => {
                alertDiv.remove();
            }, 150);
        }, 5000);
    }

    /**
     * Get CSRF token from cookies
     */
    function getCookie(name) {
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
});

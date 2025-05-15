document.addEventListener('DOMContentLoaded', function() {
    // Database Connection Elements
    const useWindowsAuthCheckbox = document.getElementById('use_windows_auth');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const hostInput = document.getElementById('host');
    const databaseInput = document.getElementById('database');
    const dbPortInput = document.getElementById('db_port');
    const testConnectionBtn = document.getElementById('testConnection');
    const connectionLoader = document.getElementById('connectionLoader');
    const saveButton = document.getElementById('saveButton');
    const dbSettingsForm = document.getElementById('dbSettingsForm');
    
    // Initialize form state
    initializeForm();
    
    // Handle Windows authentication change
    useWindowsAuthCheckbox.addEventListener('change', function() {
        updateAuthFields();
    });

    // Handle test connection
    testConnectionBtn.addEventListener('click', async function() {
        // Validate required fields
        if (!hostInput.value.trim()) {
            showStatus('error', 'يرجى إدخال اسم الخادم أولاً');
            hostInput.focus();
            return;
        }

        if (!useWindowsAuthCheckbox.checked && (!usernameInput.value.trim() || !passwordInput.value.trim())) {
            showStatus('error', 'يرجى إدخال اسم المستخدم وكلمة المرور');
            usernameInput.focus();
            return;
        }

        // Show loading state
        testConnectionBtn.disabled = true;
        if (connectionLoader) {
            connectionLoader.style.display = 'inline-block';
        }
        showStatus('info', 'جاري اختبار الاتصال...');

        const formData = new FormData();
        formData.append('host', hostInput.value);
        formData.append('auth_type', useWindowsAuthCheckbox.checked ? 'windows' : 'sql');
        formData.append('username', usernameInput.value);
        formData.append('password', passwordInput.value);

        try {
            const response = await fetch('/administrator/test-connection/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            });

            const data = await response.json();

            if (data.success) {
                // Enable database select
                databaseInput.disabled = false;

                // Clear existing options
                databaseInput.innerHTML = '<option value="">-- اختر قاعدة البيانات --</option>';

                if (data.databases && data.databases.length > 0) {
                    // Add new database options
                    data.databases.forEach(db => {
                        const option = document.createElement('option');
                        option.value = db;
                        option.textContent = db;
                        databaseInput.appendChild(option);
                    });

                    // Select current database if it exists
                    const currentDb = databaseInput.getAttribute('data-current');
                    if (currentDb && data.databases.includes(currentDb)) {
                        databaseInput.value = currentDb;
                    } else if (data.databases.length === 1) {
                        // If there's only one database, select it automatically
                        databaseInput.value = data.databases[0];
                    }

                    showStatus('success', `تم الاتصال بالخادم بنجاح! تم العثور على ${data.databases.length} قاعدة بيانات. يرجى اختيار واحدة.`);
                } else {
                    showStatus('warning', 'تم الاتصال بالخادم بنجاح، لكن لم يتم العثور على قواعد بيانات. يمكنك إنشاء قاعدة بيانات جديدة أو إدخال اسم قاعدة البيانات يدوياً.');

                    // Add an input field for manual entry
                    const manualOption = document.createElement('option');
                    manualOption.value = "manual";
                    manualOption.textContent = "إدخال اسم قاعدة البيانات يدوياً";
                    databaseInput.appendChild(manualOption);

                    databaseInput.addEventListener('change', function() {
                        if (this.value === 'manual') {
                            const dbName = prompt('الرجاء إدخال اسم قاعدة البيانات:');
                            if (dbName && dbName.trim()) {
                                // Add the new option
                                const newOption = document.createElement('option');
                                newOption.value = dbName.trim();
                                newOption.textContent = dbName.trim();
                                databaseInput.appendChild(newOption);
                                
                                // Select the new option
                                databaseInput.value = dbName.trim();
                            } else {
                                // If no name provided, revert to first option
                                databaseInput.selectedIndex = 0;
                            }
                        }
                    });
                }
            } else {
                showStatus('error', 'فشل الاتصال: ' + data.error);
                databaseInput.disabled = true;
            }
        } catch (error) {
            showStatus('error', 'خطأ في الاتصال: ' + error.message);
            databaseInput.disabled = true;
        } finally {
            // Reset loading state
            testConnectionBtn.disabled = false;
            if (connectionLoader) {
                connectionLoader.style.display = 'none';
            }
        }
    });

    // Handle form submission
    dbSettingsForm.addEventListener('submit', function(event) {
        // Validate form before submission
        if (!validateForm()) {
            event.preventDefault();
            return false;
        }

        // Show loading state on save button
        saveButton.disabled = true;
        saveButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>جاري الحفظ...';
        
        return true;
    });

    // Helper functions
    function initializeForm() {
        // Set initial state of auth fields
        updateAuthFields();
        
        // Make sure database select is disabled until connection is tested
        databaseInput.disabled = true;
    }

    function updateAuthFields() {
        // Enable/disable username and password fields based on Windows auth
        const useWindowsAuth = useWindowsAuthCheckbox.checked;
        usernameInput.disabled = useWindowsAuth;
        passwordInput.disabled = useWindowsAuth;

        if (useWindowsAuth) {
            usernameInput.value = '';
            passwordInput.value = '';
        }
    }

    function showStatus(type, message) {
        const statusDiv = document.querySelector('.connection-status');
        if (statusDiv) {
            if (!message) {
                statusDiv.style.display = 'none';
                return;
            }

            statusDiv.className = 'connection-status';
            if (type) {
                statusDiv.classList.add(type);
            }

            const messageSpan = statusDiv.querySelector('span');
            if (messageSpan) {
                messageSpan.textContent = message;
            }
            
            statusDiv.style.display = 'block';
        }
    }

    function validateForm() {
        let isValid = true;

        // Check host
        if (!hostInput.value.trim()) {
            showStatus('error', 'يرجى إدخال اسم الخادم');
            hostInput.focus();
            isValid = false;
        }

        // Check SQL auth credentials if not using Windows auth
        else if (!useWindowsAuthCheckbox.checked && (!usernameInput.value.trim() || !passwordInput.value.trim())) {
            showStatus('error', 'يرجى إدخال اسم المستخدم وكلمة المرور');
            usernameInput.focus();
            isValid = false;
        }

        // Check database selection
        else if (!databaseInput.value) {
            showStatus('error', 'يرجى اختيار قاعدة البيانات');
            databaseInput.focus();
            isValid = false;
        }

        // Check port
        else if (!dbPortInput.value.trim() || isNaN(dbPortInput.value)) {
            showStatus('error', 'يرجى إدخال رقم منفذ صحيح');
            dbPortInput.focus();
            isValid = false;
        }

        return isValid;
    }
});

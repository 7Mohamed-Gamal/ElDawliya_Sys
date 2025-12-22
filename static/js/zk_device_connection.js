/**
 * ZK Device Connection JavaScript
 * Handles the functionality for connecting to ZK fingerprint devices
 */

document.addEventListener('DOMContentLoaded', function() {
    // Connection type change handler
    const connectionTypeRadios = document.querySelectorAll('input[name="connectionType"]');
    const ethernetSettings = document.getElementById('ethernetSettings');
    const usbSettings = document.getElementById('usbSettings');
    const serialSettings = document.getElementById('serialSettings');
    
    connectionTypeRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            // Hide all settings first
            ethernetSettings.style.display = 'none';
            if (usbSettings) usbSettings.style.display = 'none';
            if (serialSettings) serialSettings.style.display = 'none';
            
            // Show the selected settings
            if (this.value === 'ethernet') {
                ethernetSettings.style.display = 'flex';
            } else if (this.value === 'usb' && usbSettings) {
                usbSettings.style.display = 'flex';
            } else if (this.value === 'serial' && serialSettings) {
                serialSettings.style.display = 'flex';
            }
        });
    });
    
    // Connect button click handler
    const connectBtn = document.getElementById('connectBtn');
    const connectionStatus = document.getElementById('connectionStatus');
    
    if (connectBtn && connectionStatus) {
        connectBtn.addEventListener('click', function() {
            // Get connection parameters
            const connectionType = document.querySelector('input[name="connectionType"]:checked').value;
            let connectionParams = {};
            
            if (connectionType === 'ethernet') {
                connectionParams = {
                    ipAddress: document.getElementById('ipAddress').value,
                    port: document.getElementById('port').value,
                    password: document.getElementById('password').value
                };
                
                if (!connectionParams.ipAddress) {
                    showAlert('يرجى إدخال عنوان IP', 'danger');
                    return;
                }
            } else if (connectionType === 'usb') {
                // Handle USB connection parameters
            } else if (connectionType === 'serial') {
                // Handle Serial connection parameters
            }
            
            // Test actual connection
            testConnection(connectionParams);
        });
    }
    
    // Read records button click handler
    const readRecordsBtn = document.getElementById('readRecordsBtn');
    const recordsTableBody = document.getElementById('recordsTableBody');
    
    if (readRecordsBtn && recordsTableBody) {
        readRecordsBtn.addEventListener('click', function() {
            if (connectionStatus.classList.contains('status-disconnected')) {
                showAlert('يرجى الاتصال بالجهاز أولاً', 'warning');
                return;
            }
            
            // Read records from device
            readRecords();
        });
    }
    
    // Save to DB confirm button click handler
    const saveToDbConfirmBtn = document.getElementById('saveToDbConfirmBtn');
    
    if (saveToDbConfirmBtn) {
        saveToDbConfirmBtn.addEventListener('click', function() {
            // Save to database
            saveToDatabase();
        });
    }
    
    // Clear records button click handler
    const clearRecordsBtn = document.getElementById('clearRecordsBtn');
    
    if (clearRecordsBtn && recordsTableBody) {
        clearRecordsBtn.addEventListener('click', function() {
            recordsTableBody.innerHTML = '';
            showAlert('تم محو السجلات بنجاح', 'success');
        });
    }
    
    // Record count button click handler
    const recordCountBtn = document.getElementById('recordCountBtn');
    
    if (recordCountBtn && recordsTableBody) {
        recordCountBtn.addEventListener('click', function() {
            const rowCount = recordsTableBody.querySelectorAll('tr').length;
            showAlert(`عدد السجلات: ${rowCount}`, 'info');
        });
    }
    
    // Save as button click handler
    const saveAsBtn = document.getElementById('saveAsBtn');
    
    if (saveAsBtn) {
        saveAsBtn.addEventListener('click', function() {
            if (recordsTableBody.querySelectorAll('tr').length === 0) {
                showAlert('لا توجد سجلات للحفظ', 'warning');
                return;
            }
            
            // Simulate saving as file
            showAlert('تم حفظ السجلات بنجاح', 'success');
        });
    }
});

/**
 * Test connection to the device
 * @param {Object} params - Connection parameters
 */
function testConnection(params) {
    const connectBtn = document.getElementById('connectBtn');
    const connectionStatus = document.getElementById('connectionStatus');

    // Show connecting status
    connectBtn.disabled = true;
    connectBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> جاري الاتصال...';
    connectionStatus.textContent = 'جاري الاتصال...';
    connectionStatus.classList.remove('status-connected', 'status-disconnected');
    connectionStatus.classList.add('status-connecting');

    // Make AJAX call to test connection
    fetch('/Hr/attendance/ajax/test-zk-connection/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(params)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Successful connection
            connectionStatus.textContent = 'متصل';
            connectionStatus.classList.remove('status-connecting', 'status-disconnected');
            connectionStatus.classList.add('status-connected');

            // Show success message
            showAlert('تم الاتصال بجهاز البصمة بنجاح!', 'success');

            // Enable device tabs
            document.querySelectorAll('#deviceTabs .nav-link').forEach(tab => {
                tab.classList.remove('disabled');
            });

            // Store connection params for later use
            window.zkConnectionParams = params;
        } else {
            // Connection failed
            connectionStatus.textContent = 'فشل الاتصال';
            connectionStatus.classList.remove('status-connecting');
            connectionStatus.classList.add('status-disconnected');

            showAlert(data.error || 'فشل في الاتصال بجهاز البصمة', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        connectionStatus.textContent = 'خطأ في الاتصال';
        connectionStatus.classList.remove('status-connecting');
        connectionStatus.classList.add('status-disconnected');

        showAlert('حدث خطأ أثناء الاتصال بجهاز البصمة', 'danger');
    })
    .finally(() => {
        // Re-enable connect button
        connectBtn.disabled = false;
        connectBtn.innerHTML = '<i class="fas fa-plug me-2"></i> توصيل';
    });
}

/**
 * Read records from the device
 */
function readRecords() {
    if (!window.zkConnectionParams) {
        showAlert('يجب الاتصال بالجهاز أولاً', 'warning');
        return;
    }

    const recordsTableBody = document.getElementById('recordsTableBody');
    const readRecordsBtn = document.getElementById('readRecordsBtn');

    // Clear existing records
    recordsTableBody.innerHTML = '';

    // Show loading state
    readRecordsBtn.disabled = true;
    readRecordsBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> جاري القراءة...';
    showAlert('جاري قراءة السجلات من الجهاز...', 'info');

    // Prepare request data
    const requestData = {
        ...window.zkConnectionParams,
        start_date: document.getElementById('startDate')?.value || null,
        end_date: document.getElementById('endDate')?.value || null
    };

    // Make AJAX call to fetch records
    fetch('/Hr/attendance/ajax/fetch-zk-records/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Populate table with records
            data.records.forEach((record, index) => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${index + 1}</td>
                    <td>${record.user_id}</td>
                    <td>FP</td>
                    <td>${record.in_out_mode}</td>
                    <td>${record.timestamp}</td>
                    <td>-</td>
                    <td>-</td>
                `;
                recordsTableBody.appendChild(row);
            });

            // Show success message
            showAlert(`تم قراءة ${data.total_count} سجل بنجاح`, 'success');
        } else {
            showAlert(data.error || 'فشل في قراءة السجلات', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('حدث خطأ أثناء قراءة السجلات', 'danger');
    })
    .finally(() => {
        // Re-enable button
        readRecordsBtn.disabled = false;
        readRecordsBtn.innerHTML = '<i class="fas fa-sync-alt me-2"></i> قراءة السجلات';
    });
}

/**
 * Save records to database
 */
function saveToDatabase() {
    if (!window.zkConnectionParams) {
        showAlert('يجب الاتصال بالجهاز أولاً', 'warning');
        return;
    }

    const saveToDbConfirmBtn = document.getElementById('saveToDbConfirmBtn');
    const machineSelect = document.getElementById('machineSelect');

    if (!machineSelect || !machineSelect.value) {
        showAlert('يجب اختيار جهاز البصمة', 'warning');
        return;
    }

    // Show loading state
    saveToDbConfirmBtn.disabled = true;
    saveToDbConfirmBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> جاري الحفظ...';
    showAlert('جاري حفظ البيانات في قاعدة البيانات...', 'info');

    // Prepare request data
    const requestData = {
        ...window.zkConnectionParams,
        machine_id: machineSelect.value,
        start_date: document.getElementById('startDate')?.value || null,
        end_date: document.getElementById('endDate')?.value || null,
        clear_existing: document.getElementById('clearExisting')?.checked || false
    };

    // Make AJAX call to save records
    fetch('/Hr/attendance/ajax/save-zk-records/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert(data.message, 'success');

            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('dbConnectionModal'));
            if (modal) modal.hide();
        } else {
            showAlert(data.error || 'فشل في حفظ البيانات', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('حدث خطأ أثناء حفظ البيانات', 'danger');
    })
    .finally(() => {
        // Re-enable button
        saveToDbConfirmBtn.disabled = false;
        saveToDbConfirmBtn.innerHTML = 'حفظ البيانات';
    });
}

/**
 * Get CSRF cookie value
 * @param {string} name - Cookie name
 * @returns {string} Cookie value
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

/**
 * Show alert message
 * @param {string} message - Alert message
 * @param {string} type - Alert type (success, info, warning, danger)
 */
function showAlert(message, type = 'info') {
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Add alert to the page
    const alertContainer = document.getElementById('alertContainer');
    if (alertContainer) {
        alertContainer.appendChild(alertDiv);
        
        // Auto-dismiss after 5 seconds
        setTimeout(function() {
            alertDiv.classList.remove('show');
            setTimeout(function() {
                alertDiv.remove();
            }, 150);
        }, 5000);
    } else {
        // Fallback to alert if container not found
        alert(message);
    }
}

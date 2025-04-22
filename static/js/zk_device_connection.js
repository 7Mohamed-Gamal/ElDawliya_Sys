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
            
            // Simulate connection
            simulateConnection(connectionParams);
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
            
            // Simulate reading records
            simulateReadRecords();
        });
    }
    
    // Save to DB confirm button click handler
    const saveToDbConfirmBtn = document.getElementById('saveToDbConfirmBtn');
    
    if (saveToDbConfirmBtn) {
        saveToDbConfirmBtn.addEventListener('click', function() {
            const dbHost = document.getElementById('dbHost').value;
            const dbName = document.getElementById('dbName').value;
            
            if (!dbHost || !dbName) {
                showAlert('يرجى إدخال معلومات قاعدة البيانات المطلوبة', 'warning');
                return;
            }
            
            // Simulate saving to database
            simulateSaveToDatabase(dbHost, dbName);
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
 * Simulate connection to the device
 * @param {Object} params - Connection parameters
 */
function simulateConnection(params) {
    const connectionStatus = document.getElementById('connectionStatus');
    
    // Show loading state
    connectionStatus.textContent = 'جاري الاتصال...';
    connectionStatus.classList.remove('status-connected', 'status-disconnected');
    connectionStatus.classList.add('status-connecting');
    
    // Simulate connection delay
    setTimeout(function() {
        // Simulate successful connection
        connectionStatus.textContent = 'متصل';
        connectionStatus.classList.remove('status-connecting', 'status-disconnected');
        connectionStatus.classList.add('status-connected');
        
        // Show success message
        showAlert('تم الاتصال بجهاز البصمة بنجاح!', 'success');
        
        // Enable device tabs
        document.querySelectorAll('#deviceTabs .nav-link').forEach(tab => {
            tab.classList.remove('disabled');
        });
    }, 1500);
}

/**
 * Simulate reading records from the device
 */
function simulateReadRecords() {
    const recordsTableBody = document.getElementById('recordsTableBody');
    
    // Clear existing records
    recordsTableBody.innerHTML = '';
    
    // Show loading message
    showAlert('جاري قراءة السجلات من الجهاز...', 'info');
    
    // Simulate reading delay
    setTimeout(function() {
        // Generate sample records
        const sampleRecords = [
            { id: 1, empId: '1001', verifyMode: 'FP', inOut: 'حضور', date: '2023-04-18 08:05:22', shift: 'صباحي', result: 'حضور' },
            { id: 2, empId: '1001', verifyMode: 'FP', inOut: 'انصراف', date: '2023-04-18 16:30:45', shift: 'صباحي', result: 'انصراف' },
            { id: 3, empId: '1002', verifyMode: 'FP', inOut: 'حضور', date: '2023-04-18 08:15:10', shift: 'صباحي', result: 'حضور متأخر' },
            { id: 4, empId: '1002', verifyMode: 'FP', inOut: 'انصراف', date: '2023-04-18 16:05:33', shift: 'صباحي', result: 'انصراف مبكر' },
            { id: 5, empId: '1003', verifyMode: 'FP', inOut: 'حضور', date: '2023-04-18 08:02:17', shift: 'صباحي', result: 'حضور' },
            { id: 6, empId: '1003', verifyMode: 'FP', inOut: 'انصراف', date: '2023-04-18 16:45:12', shift: 'صباحي', result: 'انصراف' },
            { id: 7, empId: '1004', verifyMode: 'FP', inOut: 'حضور', date: '2023-04-18 08:10:05', shift: 'صباحي', result: 'حضور' },
            { id: 8, empId: '1004', verifyMode: 'FP', inOut: 'انصراف', date: '2023-04-18 16:15:30', shift: 'صباحي', result: 'انصراف' }
        ];
        
        // Populate table with sample records
        sampleRecords.forEach(record => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${record.id}</td>
                <td>${record.empId}</td>
                <td>${record.verifyMode}</td>
                <td>${record.inOut}</td>
                <td>${record.date}</td>
                <td>${record.shift}</td>
                <td>${record.result}</td>
            `;
            recordsTableBody.appendChild(row);
        });
        
        // Show success message
        showAlert(`تم قراءة ${sampleRecords.length} سجل بنجاح`, 'success');
    }, 2000);
}

/**
 * Simulate saving records to database
 * @param {string} host - Database host
 * @param {string} dbName - Database name
 */
function simulateSaveToDatabase(host, dbName) {
    // Show loading message
    showAlert('جاري حفظ البيانات في قاعدة البيانات...', 'info');
    
    // Simulate saving delay
    setTimeout(function() {
        // Show success message
        showAlert(`تم حفظ البيانات بنجاح في قاعدة البيانات "${dbName}" على المضيف "${host}"`, 'success');
        
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('dbConnectionModal'));
        if (modal) modal.hide();
    }, 1500);
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

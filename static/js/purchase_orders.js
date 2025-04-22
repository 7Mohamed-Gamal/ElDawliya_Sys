/**
 * Purchase Orders JavaScript
 * Contains functionality for the purchase orders application
 */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initTooltips();
    
    // Initialize delete confirmations
    initDeleteConfirmations();
    
    // Initialize product transfer functionality
    initProductTransfer();
    
    // Initialize form validations
    initFormValidations();
    
    // Initialize status filters
    initStatusFilters();
});

/**
 * Initialize Bootstrap tooltips
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize delete confirmation dialogs
 */
function initDeleteConfirmations() {
    const deleteButtons = document.querySelectorAll('.confirm-delete');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const itemType = this.dataset.type || 'العنصر';
            const itemId = this.dataset.id || '';
            const deleteUrl = this.dataset.url || this.getAttribute('href');
            
            if (confirm(`هل أنت متأكد من حذف ${itemType} #${itemId}؟`)) {
                window.location.href = deleteUrl;
            }
        });
    });
}

/**
 * Initialize product transfer functionality
 */
function initProductTransfer() {
    const transferButtons = document.querySelectorAll('.transfer-to-purchase');
    
    transferButtons.forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.dataset.productId;
            const action = this.dataset.action || 'add';
            
            // First check if product is already in a purchase request
            checkProductInPurchaseRequest(productId)
                .then(response => {
                    if (response.in_purchase_request) {
                        // Product is already in a purchase request
                        alert(`هذا المنتج موجود بالفعل في طلب شراء بحالة: ${response.request_status}`);
                        return;
                    }
                    
                    // Transfer product to purchase request
                    transferProductToPurchaseRequest(productId, action)
                        .then(response => {
                            if (response.status === 'success') {
                                alert(response.message);
                                // Update button state
                                updateTransferButtonState(button, true);
                            } else {
                                alert(`خطأ: ${response.message}`);
                            }
                        })
                        .catch(error => {
                            console.error('Error transferring product:', error);
                            alert('حدث خطأ أثناء نقل المنتج إلى طلب الشراء');
                        });
                })
                .catch(error => {
                    console.error('Error checking product:', error);
                    alert('حدث خطأ أثناء التحقق من المنتج');
                });
        });
    });
}

/**
 * Check if product is already in a purchase request
 * @param {string} productId - The product ID to check
 * @returns {Promise} - Promise resolving to response data
 */
async function checkProductInPurchaseRequest(productId) {
    try {
        const response = await fetch(`/purchase/api/check-product/${productId}/`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error checking product:', error);
        throw error;
    }
}

/**
 * Transfer product to purchase request
 * @param {string} productId - The product ID to transfer
 * @param {string} action - The action to perform ('add' or 'remove')
 * @returns {Promise} - Promise resolving to response data
 */
async function transferProductToPurchaseRequest(productId, action) {
    try {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        const response = await fetch('/purchase/api/transfer-product/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                product_id: productId,
                action: action
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error transferring product:', error);
        throw error;
    }
}

/**
 * Update transfer button state
 * @param {HTMLElement} button - The button element to update
 * @param {boolean} inPurchaseRequest - Whether the product is in a purchase request
 */
function updateTransferButtonState(button, inPurchaseRequest) {
    if (inPurchaseRequest) {
        button.classList.remove('btn-primary');
        button.classList.add('btn-success');
        button.innerHTML = '<i class="fas fa-check me-1"></i> تم الإضافة للطلب';
        button.disabled = true;
    } else {
        button.classList.remove('btn-success');
        button.classList.add('btn-primary');
        button.innerHTML = '<i class="fas fa-shopping-cart me-1"></i> إضافة لطلب شراء';
        button.disabled = false;
    }
}

/**
 * Initialize form validations
 */
function initFormValidations() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
}

/**
 * Initialize status filters
 */
function initStatusFilters() {
    const statusFilters = document.querySelectorAll('.status-filter');
    
    statusFilters.forEach(filter => {
        filter.addEventListener('click', function(e) {
            e.preventDefault();
            
            const status = this.dataset.status;
            const tableRows = document.querySelectorAll('tbody tr');
            
            // Remove active class from all filters
            statusFilters.forEach(f => f.classList.remove('active'));
            
            // Add active class to clicked filter
            this.classList.add('active');
            
            // Show/hide rows based on status
            if (status === 'all') {
                tableRows.forEach(row => row.style.display = '');
            } else {
                tableRows.forEach(row => {
                    const rowStatus = row.dataset.status;
                    row.style.display = (rowStatus === status) ? '' : 'none';
                });
            }
        });
    });
}

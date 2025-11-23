/**
 * Permissions Management JavaScript
 * جافا سكريبت إدارة الصلاحيات
 */

class PermissionsManager {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
        this.initializeComponents();
    }

    bindEvents() {
        // Approval workflow actions
        $(document).on('click', '.approve-step-btn', this.handleApprovalAction.bind(this));
        $(document).on('click', '.reject-step-btn', this.handleApprovalAction.bind(this));
        
        // Role assignment
        $(document).on('submit', '#assign-role-form', this.handleRoleAssignment.bind(this));
        
        // Permission filtering
        $(document).on('input', '#permission-search', this.filterPermissions.bind(this));
        $(document).on('change', '#module-filter', this.filterPermissions.bind(this));
        
        // Role management
        $(document).on('click', '.toggle-role-permissions', this.toggleRolePermissions.bind(this));
        
        // User permissions view
        $(document).on('click', '.view-user-permissions', this.viewUserPermissions.bind(this));
        
        // Cache management
        $(document).on('click', '#clear-cache-btn', this.clearPermissionsCache.bind(this));
        
        // Bulk actions
        $(document).on('change', '.select-all-permissions', this.toggleAllPermissions.bind(this));
        $(document).on('change', '.permission-checkbox input', this.updatePermissionCount.bind(this));
    }

    initializeComponents() {
        // Initialize tooltips
        $('[data-bs-toggle="tooltip"]').tooltip();
        
        // Initialize popovers
        $('[data-bs-toggle="popover"]').popover();
        
        // Initialize date pickers
        $('.datepicker').datepicker({
            format: 'yyyy-mm-dd',
            autoclose: true,
            todayHighlight: true,
            language: 'ar'
        });
        
        // Initialize select2 for better dropdowns
        $('.select2').select2({
            theme: 'bootstrap-5',
            language: 'ar'
        });
        
        // Auto-refresh pending approvals count
        this.startApprovalCountRefresh();
    }

    /**
     * Handle approval workflow actions
     */
    async handleApprovalAction(event) {
        event.preventDefault();
        
        const button = $(event.currentTarget);
        const action = button.data('action'); // 'approve' or 'reject'
        const workflowId = button.data('workflow-id');
        const stepId = button.data('step-id');
        
        // Show confirmation modal
        const confirmed = await this.showConfirmationModal(
            action === 'approve' ? 'تأكيد الموافقة' : 'تأكيد الرفض',
            action === 'approve' ? 
                'هل أنت متأكد من الموافقة على هذا الطلب؟' : 
                'هل أنت متأكد من رفض هذا الطلب؟'
        );
        
        if (!confirmed) return;
        
        // Get comments if rejecting
        let comments = '';
        if (action === 'reject') {
            comments = await this.getCommentsModal();
            if (comments === null) return; // User cancelled
        }
        
        // Show loading state
        button.prop('disabled', true).addClass('loading');
        
        try {
            const response = await $.ajax({
                url: `/core/permissions/approvals/${workflowId}/steps/${stepId}/approve/`,
                method: 'POST',
                data: {
                    action: action,
                    comments: comments,
                    csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
                }
            });
            
            if (response.success) {
                this.showNotification('success', response.message);
                
                // Update UI
                this.updateApprovalStepUI(stepId, action, comments);
                
                // Refresh page after short delay
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            } else {
                this.showNotification('error', response.message);
            }
        } catch (error) {
            console.error('Approval action error:', error);
            this.showNotification('error', 'حدث خطأ أثناء معالجة الطلب');
        } finally {
            button.prop('disabled', false).removeClass('loading');
        }
    }

    /**
     * Handle role assignment form submission
     */
    async handleRoleAssignment(event) {
        event.preventDefault();
        
        const form = $(event.currentTarget);
        const formData = new FormData(form[0]);
        
        // Show loading state
        const submitBtn = form.find('button[type="submit"]');
        submitBtn.prop('disabled', true).addClass('loading');
        
        try {
            const response = await $.ajax({
                url: form.attr('action'),
                method: 'POST',
                data: formData,
                processData: false,
                contentType: false
            });
            
            this.showNotification('success', 'تم تعيين الدور بنجاح');
            
            // Reset form
            form[0].reset();
            
            // Refresh role assignments list if exists
            this.refreshRoleAssignments();
            
        } catch (error) {
            console.error('Role assignment error:', error);
            this.showNotification('error', 'حدث خطأ أثناء تعيين الدور');
        } finally {
            submitBtn.prop('disabled', false).removeClass('loading');
        }
    }

    /**
     * Filter permissions based on search and module
     */
    filterPermissions() {
        const searchTerm = $('#permission-search').val().toLowerCase();
        const selectedModule = $('#module-filter').val();
        
        $('.permission-item').each(function() {
            const item = $(this);
            const permissionName = item.find('.permission-name').text().toLowerCase();
            const moduleName = item.data('module');
            
            let showItem = true;
            
            // Filter by search term
            if (searchTerm && !permissionName.includes(searchTerm)) {
                showItem = false;
            }
            
            // Filter by module
            if (selectedModule && moduleName !== selectedModule) {
                showItem = false;
            }
            
            item.toggle(showItem);
        });
        
        // Update visible count
        this.updateVisiblePermissionsCount();
    }

    /**
     * Toggle role permissions visibility
     */
    toggleRolePermissions(event) {
        event.preventDefault();
        
        const button = $(event.currentTarget);
        const roleId = button.data('role-id');
        const permissionsContainer = $(`.role-permissions[data-role-id="${roleId}"]`);
        
        if (permissionsContainer.is(':visible')) {
            permissionsContainer.slideUp();
            button.find('i').removeClass('fa-chevron-up').addClass('fa-chevron-down');
        } else {
            // Load permissions if not already loaded
            if (permissionsContainer.is(':empty')) {
                this.loadRolePermissions(roleId, permissionsContainer);
            }
            
            permissionsContainer.slideDown();
            button.find('i').removeClass('fa-chevron-down').addClass('fa-chevron-up');
        }
    }

    /**
     * Load role permissions via AJAX
     */
    async loadRolePermissions(roleId, container) {
        container.html('<div class="text-center p-3"><i class="fas fa-spinner fa-spin"></i> جاري التحميل...</div>');
        
        try {
            const response = await $.ajax({
                url: '/core/permissions/api/data/',
                method: 'GET',
                data: {
                    type: 'role_permissions',
                    role_id: roleId
                }
            });
            
            if (response.success) {
                this.renderRolePermissions(container, response.permissions);
            } else {
                container.html('<div class="text-danger p-3">خطأ في تحميل الصلاحيات</div>');
            }
        } catch (error) {
            console.error('Load role permissions error:', error);
            container.html('<div class="text-danger p-3">خطأ في تحميل الصلاحيات</div>');
        }
    }

    /**
     * Render role permissions in container
     */
    renderRolePermissions(container, permissions) {
        if (permissions.length === 0) {
            container.html('<div class="text-muted p-3">لا توجد صلاحيات مخصصة لهذا الدور</div>');
            return;
        }
        
        // Group permissions by module
        const groupedPermissions = {};
        permissions.forEach(permission => {
            const moduleName = permission.module__display_name || permission.module__name;
            if (!groupedPermissions[moduleName]) {
                groupedPermissions[moduleName] = [];
            }
            groupedPermissions[moduleName].push(permission);
        });
        
        let html = '<div class="permissions-grid">';
        
        Object.keys(groupedPermissions).forEach(moduleName => {
            html += `<div class="module-permissions">
                        <h6 class="module-name">${moduleName}</h6>
                        <div class="permissions-list">`;
            
            groupedPermissions[moduleName].forEach(permission => {
                html += `<span class="badge bg-primary me-1 mb-1">${permission.name}</span>`;
            });
            
            html += '</div></div>';
        });
        
        html += '</div>';
        container.html(html);
    }

    /**
     * View user permissions in modal
     */
    async viewUserPermissions(event) {
        event.preventDefault();
        
        const button = $(event.currentTarget);
        const userId = button.data('user-id');
        const userName = button.data('user-name');
        
        // Show modal
        const modal = $('#user-permissions-modal');
        modal.find('.modal-title').text(`صلاحيات المستخدم: ${userName}`);
        modal.find('.modal-body').html('<div class="text-center p-4"><i class="fas fa-spinner fa-spin fa-2x"></i><br>جاري التحميل...</div>');
        modal.modal('show');
        
        try {
            const response = await $.ajax({
                url: '/core/permissions/api/data/',
                method: 'GET',
                data: {
                    type: 'user_permissions',
                    user_id: userId
                }
            });
            
            if (response.success) {
                this.renderUserPermissions(modal.find('.modal-body'), response.permissions);
            } else {
                modal.find('.modal-body').html('<div class="text-danger p-3">خطأ في تحميل الصلاحيات</div>');
            }
        } catch (error) {
            console.error('Load user permissions error:', error);
            modal.find('.modal-body').html('<div class="text-danger p-3">خطأ في تحميل الصلاحيات</div>');
        }
    }

    /**
     * Render user permissions in modal
     */
    renderUserPermissions(container, permissions) {
        if (Object.keys(permissions).length === 0) {
            container.html('<div class="text-muted p-3">لا توجد صلاحيات مخصصة لهذا المستخدم</div>');
            return;
        }
        
        let html = '<div class="user-permissions-grid">';
        
        Object.keys(permissions).forEach(moduleName => {
            const modulePermissions = permissions[moduleName];
            const hasAnyPermission = Object.values(modulePermissions).some(hasPerm => hasPerm);
            
            if (hasAnyPermission) {
                html += `<div class="module-permissions mb-3">
                            <h6 class="module-name text-primary">${moduleName}</h6>
                            <div class="permissions-list">`;
                
                Object.keys(modulePermissions).forEach(permName => {
                    const hasPerm = modulePermissions[permName];
                    if (hasPerm) {
                        html += `<span class="badge bg-success me-1 mb-1">${permName}</span>`;
                    }
                });
                
                html += '</div></div>';
            }
        });
        
        html += '</div>';
        container.html(html);
    }

    /**
     * Clear permissions cache
     */
    async clearPermissionsCache(event) {
        event.preventDefault();
        
        const confirmed = await this.showConfirmationModal(
            'مسح ذاكرة التخزين المؤقت',
            'هل أنت متأكد من مسح ذاكرة تخزين الصلاحيات؟ سيؤدي هذا إلى إعادة حساب جميع الصلاحيات.'
        );
        
        if (!confirmed) return;
        
        const button = $(event.currentTarget);
        button.prop('disabled', true).addClass('loading');
        
        try {
            const response = await $.ajax({
                url: '/core/permissions/cache/clear/',
                method: 'POST',
                data: {
                    csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
                }
            });
            
            this.showNotification('success', 'تم مسح ذاكرة التخزين المؤقت بنجاح');
            
        } catch (error) {
            console.error('Clear cache error:', error);
            this.showNotification('error', 'حدث خطأ أثناء مسح ذاكرة التخزين المؤقت');
        } finally {
            button.prop('disabled', false).removeClass('loading');
        }
    }

    /**
     * Toggle all permissions in a group
     */
    toggleAllPermissions(event) {
        const checkbox = $(event.currentTarget);
        const isChecked = checkbox.is(':checked');
        const group = checkbox.closest('.permission-group');
        
        group.find('.permission-checkbox input[type="checkbox"]').prop('checked', isChecked);
        this.updatePermissionCount();
    }

    /**
     * Update permission count display
     */
    updatePermissionCount() {
        const totalPermissions = $('.permission-checkbox input[type="checkbox"]').length;
        const selectedPermissions = $('.permission-checkbox input[type="checkbox"]:checked').length;
        
        $('#selected-permissions-count').text(selectedPermissions);
        $('#total-permissions-count').text(totalPermissions);
    }

    /**
     * Update visible permissions count after filtering
     */
    updateVisiblePermissionsCount() {
        const visiblePermissions = $('.permission-item:visible').length;
        $('#visible-permissions-count').text(visiblePermissions);
    }

    /**
     * Start auto-refresh for approval count
     */
    startApprovalCountRefresh() {
        setInterval(() => {
            this.refreshApprovalCount();
        }, 30000); // Refresh every 30 seconds
    }

    /**
     * Refresh approval count
     */
    async refreshApprovalCount() {
        try {
            const response = await $.ajax({
                url: '/core/permissions/api/data/',
                method: 'GET',
                data: {
                    type: 'approval_count'
                }
            });
            
            if (response.success && response.count !== undefined) {
                const badge = $('.approval-count-badge');
                if (response.count > 0) {
                    badge.text(response.count).show();
                } else {
                    badge.hide();
                }
            }
        } catch (error) {
            console.error('Refresh approval count error:', error);
        }
    }

    /**
     * Refresh role assignments list
     */
    refreshRoleAssignments() {
        const container = $('#role-assignments-list');
        if (container.length) {
            container.load(window.location.href + ' #role-assignments-list > *');
        }
    }

    /**
     * Update approval step UI after action
     */
    updateApprovalStepUI(stepId, action, comments) {
        const stepElement = $(`.approval-step[data-step-id="${stepId}"]`);
        
        if (action === 'approve') {
            stepElement.addClass('approved').removeClass('pending');
            stepElement.find('.step-status').html('<span class="badge bg-success">موافق عليه</span>');
        } else {
            stepElement.addClass('rejected').removeClass('pending');
            stepElement.find('.step-status').html('<span class="badge bg-danger">مرفوض</span>');
        }
        
        // Hide action buttons
        stepElement.find('.step-actions').hide();
        
        // Show comments if any
        if (comments) {
            stepElement.find('.step-comments').text(comments).show();
        }
    }

    /**
     * Show confirmation modal
     */
    showConfirmationModal(title, message) {
        return new Promise((resolve) => {
            const modal = $(`
                <div class="modal fade" tabindex="-1">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">${title}</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <p>${message}</p>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إلغاء</button>
                                <button type="button" class="btn btn-primary confirm-btn">تأكيد</button>
                            </div>
                        </div>
                    </div>
                </div>
            `);
            
            modal.on('click', '.confirm-btn', () => {
                modal.modal('hide');
                resolve(true);
            });
            
            modal.on('hidden.bs.modal', () => {
                modal.remove();
                resolve(false);
            });
            
            modal.modal('show');
        });
    }

    /**
     * Get comments from user via modal
     */
    getCommentsModal() {
        return new Promise((resolve) => {
            const modal = $(`
                <div class="modal fade" tabindex="-1">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">إضافة تعليق</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <div class="mb-3">
                                    <label for="comments" class="form-label">التعليق (اختياري)</label>
                                    <textarea class="form-control" id="comments" rows="3" placeholder="أدخل تعليقك هنا..."></textarea>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إلغاء</button>
                                <button type="button" class="btn btn-primary submit-btn">تأكيد</button>
                            </div>
                        </div>
                    </div>
                </div>
            `);
            
            modal.on('click', '.submit-btn', () => {
                const comments = modal.find('#comments').val();
                modal.modal('hide');
                resolve(comments);
            });
            
            modal.on('hidden.bs.modal', () => {
                modal.remove();
                resolve(null);
            });
            
            modal.modal('show');
        });
    }

    /**
     * Show notification
     */
    showNotification(type, message) {
        const alertClass = type === 'success' ? 'alert-success' : 'alert-danger';
        const icon = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle';
        
        const notification = $(`
            <div class="alert ${alertClass} alert-dismissible fade show position-fixed" 
                 style="top: 20px; left: 20px; z-index: 9999; min-width: 300px;">
                <i class="fas ${icon} me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `);
        
        $('body').append(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            notification.alert('close');
        }, 5000);
    }
}

// Initialize permissions manager when document is ready
$(document).ready(function() {
    window.permissionsManager = new PermissionsManager();
});

// Export for use in other scripts
window.PermissionsManager = PermissionsManager;
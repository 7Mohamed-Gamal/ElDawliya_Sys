/**
 * نظام الإشعارات الذكية - JavaScript
 */

class NotificationSystem {
    constructor() {
        this.apiEndpoints = {
            markRead: '/hr/notifications/{id}/mark-read/',
            markAllRead: '/hr/notifications/mark-all-read/',
            delete: '/hr/notifications/{id}/delete/',
            checkNew: '/hr/notifications/check-new/',
            preferences: '/hr/notifications/preferences/',
            test: '/hr/notifications/test/'
        };
        
        this.settings = {
            autoRefreshInterval: 30000, // 30 ثانية
            toastDuration: 5000, // 5 ثواني
            maxToasts: 3,
            soundEnabled: true,
            animationDuration: 300
        };
        
        this.currentFilter = 'all';
        this.notifications = [];
        this.unreadCount = 0;
        this.refreshTimer = null;
        this.toasts = [];
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.startAutoRefresh();
        this.loadNotificationSound();
        this.setupKeyboardShortcuts();
        this.setupIntersectionObserver();
    }
    
    setupEventListeners() {
        // أزرار الإجراءات
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action="mark-read"]')) {
                e.preventDefault();
                const notificationId = e.target.dataset.notificationId;
                this.markAsRead(notificationId);
            }
            
            if (e.target.matches('[data-action="delete"]')) {
                e.preventDefault();
                const notificationId = e.target.dataset.notificationId;
                this.deleteNotification(notificationId);
            }
            
            if (e.target.matches('[data-action="mark-all-read"]')) {
                e.preventDefault();
                this.markAllAsRead();
            }
        });
        
        // فلاتر الإشعارات
        document.addEventListener('change', (e) => {
            if (e.target.matches('.notification-filter')) {
                this.applyFilters();
            }
        });
        
        // البحث
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('input', this.debounce(() => {
                this.applyFilters();
            }, 300));
        }
        
        // تبديل الفلاتر
        document.addEventListener('click', (e) => {
            if (e.target.matches('.filter-tab')) {
                e.preventDefault();
                this.setActiveTab(e.target);
            }
        });
        
        // إعدادات الإشعارات
        const preferencesForm = document.getElementById('preferencesForm');
        if (preferencesForm) {
            preferencesForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.savePreferences(new FormData(preferencesForm));
            });
        }
        
        // إغلاق التوست
        document.addEventListener('click', (e) => {
            if (e.target.matches('.toast-close')) {
                e.preventDefault();
                this.closeToast(e.target.closest('.notification-toast'));
            }
        });
    }
    
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + Shift + N - فتح مركز الإشعارات
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'N') {
                e.preventDefault();
                window.location.href = '/hr/notifications/';
            }
            
            // Ctrl/Cmd + Shift + M - تحديد الكل كمقروء
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'M') {
                e.preventDefault();
                this.markAllAsRead();
            }
            
            // Escape - إغلاق النوافذ المنبثقة
            if (e.key === 'Escape') {
                this.closeAllToasts();
            }
        });
    }
    
    setupIntersectionObserver() {
        // تحديد الإشعارات كمقروءة عند ظهورها في الشاشة
        if ('IntersectionObserver' in window) {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const notificationElement = entry.target;
                        const notificationId = notificationElement.dataset.id;
                        const isUnread = notificationElement.classList.contains('unread');
                        
                        if (isUnread) {
                            // تأخير قصير قبل تحديد الإشعار كمقروء
                            setTimeout(() => {
                                if (entry.isIntersecting) {
                                    this.markAsRead(notificationId, false); // بدون إشعار
                                }
                            }, 2000);
                        }
                    }
                });
            }, {
                threshold: 0.5,
                rootMargin: '0px 0px -50px 0px'
            });
            
            // مراقبة الإشعارات غير المقروءة
            document.querySelectorAll('.notification-item.unread').forEach(item => {
                observer.observe(item);
            });
        }
    }
    
    async markAsRead(notificationId, showToast = true) {
        try {
            const response = await this.makeRequest('POST', 
                this.apiEndpoints.markRead.replace('{id}', notificationId)
            );
            
            if (response.success) {
                this.updateNotificationUI(notificationId, 'read');
                this.updateUnreadCount(-1);
                
                if (showToast) {
                    this.showToast('تم تحديد الإشعار كمقروء', 'success');
                }
            }
        } catch (error) {
            console.error('Error marking notification as read:', error);
            this.showToast('حدث خطأ أثناء تحديث الإشعار', 'error');
        }
    }
    
    async markAllAsRead() {
        if (!confirm('هل تريد تحديد جميع الإشعارات كمقروءة؟')) {
            return;
        }
        
        try {
            const response = await this.makeRequest('POST', this.apiEndpoints.markAllRead);
            
            if (response.success) {
                // تحديث جميع الإشعارات في الواجهة
                document.querySelectorAll('.notification-item.unread').forEach(item => {
                    item.classList.remove('unread');
                    item.dataset.status = 'read';
                    
                    // إزالة شارة "جديد"
                    const newBadge = item.querySelector('.notification-badge.new');
                    if (newBadge) {
                        newBadge.remove();
                    }
                    
                    // إزالة زر "تحديد كمقروء"
                    const readButton = item.querySelector('[data-action=\"mark-read\"]');
                    if (readButton) {
                        readButton.remove();
                    }
                });
                
                this.updateUnreadCount(0, true);
                this.showToast(`تم تحديد ${response.updated_count} إشعار كمقروء`, 'success');
            }
        } catch (error) {
            console.error('Error marking all notifications as read:', error);
            this.showToast('حدث خطأ أثناء تحديث الإشعارات', 'error');
        }
    }
    
    async deleteNotification(notificationId) {
        if (!confirm('هل تريد حذف هذا الإشعار؟')) {
            return;
        }
        
        try {
            const response = await this.makeRequest('DELETE', 
                this.apiEndpoints.delete.replace('{id}', notificationId)
            );
            
            if (response.success) {
                const notificationElement = document.querySelector(`[data-id=\"${notificationId}\"]`);
                if (notificationElement) {
                    // تأثير الاختفاء
                    notificationElement.style.transition = 'all 0.3s ease';
                    notificationElement.style.transform = 'translateX(-100%)';
                    notificationElement.style.opacity = '0';
                    
                    setTimeout(() => {
                        notificationElement.remove();
                        this.updateCounters();
                    }, 300);
                }
                
                this.showToast('تم حذف الإشعار', 'success');
            }
        } catch (error) {
            console.error('Error deleting notification:', error);
            this.showToast('حدث خطأ أثناء حذف الإشعار', 'error');
        }
    }
    
    async checkNewNotifications() {
        try {
            const response = await this.makeRequest('GET', this.apiEndpoints.checkNew);
            
            if (response.has_new) {
                this.updateUnreadCount(response.unread_count, true);
                
                // إشعار صوتي
                if (this.settings.soundEnabled) {
                    this.playNotificationSound();
                }
                
                // إشعار منبثق
                if (response.new_count > 0) {
                    this.showToast(
                        `لديك ${response.new_count} إشعار جديد`, 
                        'info',
                        {
                            action: {
                                text: 'عرض',
                                callback: () => window.location.href = '/hr/notifications/'
                            }
                        }
                    );
                }
            }
        } catch (error) {
            console.error('Error checking new notifications:', error);
        }
    }
    
    async savePreferences(formData) {
        try {
            const response = await this.makeRequest('POST', this.apiEndpoints.preferences, formData);
            
            if (response.success) {
                this.showToast('تم حفظ الإعدادات بنجاح', 'success');
                
                // إغلاق النافذة المنبثقة
                const modal = document.getElementById('preferencesModal');
                if (modal && bootstrap.Modal.getInstance(modal)) {
                    bootstrap.Modal.getInstance(modal).hide();
                }
            }
        } catch (error) {
            console.error('Error saving preferences:', error);
            this.showToast('حدث خطأ أثناء حفظ الإعدادات', 'error');
        }
    }
    
    async sendTestNotification() {
        try {
            const response = await this.makeRequest('POST', this.apiEndpoints.test);
            
            if (response.success) {
                this.showToast('تم إرسال الإشعار التجريبي', 'success');
            } else {
                this.showToast(response.error || 'فشل في إرسال الإشعار التجريبي', 'error');
            }
        } catch (error) {
            console.error('Error sending test notification:', error);
            this.showToast('حدث خطأ أثناء إرسال الإشعار التجريبي', 'error');
        }
    }
    
    applyFilters() {
        const searchTerm = document.getElementById('searchInput')?.value.toLowerCase() || '';
        const typeFilter = document.getElementById('typeFilter')?.value || '';
        const statusFilter = document.getElementById('statusFilter')?.value || '';
        const dateFilter = document.getElementById('dateFilter')?.value || '';
        
        const notifications = document.querySelectorAll('.notification-item');
        const today = new Date().toISOString().split('T')[0];
        const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
        const monthAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
        
        let visibleCount = 0;
        
        notifications.forEach(notification => {
            const title = notification.dataset.title || '';
            const message = notification.dataset.message || '';
            const type = notification.dataset.type || '';
            const status = notification.dataset.status || '';
            const date = notification.dataset.date || '';
            
            let show = true;
            
            // فلتر البحث
            if (searchTerm && !title.includes(searchTerm) && !message.includes(searchTerm)) {
                show = false;
            }
            
            // فلتر النوع
            if (typeFilter && type !== typeFilter) {
                show = false;
            }
            
            // فلتر الحالة
            if (statusFilter) {
                if (statusFilter === 'unread' && status === 'read') {
                    show = false;
                } else if (statusFilter === 'read' && status !== 'read') {
                    show = false;
                }
            }
            
            // فلتر التاريخ
            if (dateFilter) {
                if (dateFilter === 'today' && date !== today) {
                    show = false;
                } else if (dateFilter === 'week' && date < weekAgo) {
                    show = false;
                } else if (dateFilter === 'month' && date < monthAgo) {
                    show = false;
                }
            }
            
            // فلتر التبويب النشط
            if (this.currentFilter !== 'all') {
                if (this.currentFilter === 'unread' && status === 'read') {
                    show = false;
                } else if (this.currentFilter === 'urgent' && type !== 'urgent') {
                    show = false;
                } else if (this.currentFilter === 'today' && date !== today) {
                    show = false;
                }
            }
            
            notification.style.display = show ? 'block' : 'none';
            if (show) visibleCount++;
        });
        
        // إظهار رسالة عدم وجود نتائج
        this.toggleEmptyState(visibleCount === 0);
    }
    
    setActiveTab(tabElement) {
        // إزالة الفئة النشطة من جميع التبويبات
        document.querySelectorAll('.filter-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        
        // إضافة الفئة النشطة للتبويب المحدد
        tabElement.classList.add('active');
        
        this.currentFilter = tabElement.dataset.filter || 'all';
        this.applyFilters();
    }
    
    clearFilters() {
        document.getElementById('searchInput').value = '';
        document.getElementById('typeFilter').value = '';
        document.getElementById('statusFilter').value = '';
        document.getElementById('dateFilter').value = '';
        
        this.applyFilters();
    }
    
    updateNotificationUI(notificationId, status) {
        const notificationElement = document.querySelector(`[data-id=\"${notificationId}\"]`);
        if (notificationElement) {
            if (status === 'read') {
                notificationElement.classList.remove('unread');
                notificationElement.dataset.status = 'read';
                
                // إزالة شارة "جديد"
                const newBadge = notificationElement.querySelector('.notification-badge.new');
                if (newBadge) {
                    newBadge.remove();
                }
                
                // إزالة زر "تحديد كمقروء"
                const readButton = notificationElement.querySelector('[data-action=\"mark-read\"]');
                if (readButton) {
                    readButton.remove();
                }
            }
        }
    }
    
    updateUnreadCount(count, absolute = false) {
        if (absolute) {
            this.unreadCount = count;
        } else {
            this.unreadCount += count;
        }
        
        // تحديث العدادات في الواجهة
        document.querySelectorAll('.unread-count').forEach(element => {
            element.textContent = this.unreadCount;
            element.style.display = this.unreadCount > 0 ? 'inline' : 'none';
        });
        
        // تحديث عنوان الصفحة
        this.updatePageTitle();
    }
    
    updatePageTitle() {
        const originalTitle = document.title.replace(/^\\(\\d+\\) /, '');
        document.title = this.unreadCount > 0 ? `(${this.unreadCount}) ${originalTitle}` : originalTitle;
    }
    
    updateCounters() {
        // إعادة حساب العدادات
        const totalCount = document.querySelectorAll('.notification-item').length;
        const unreadCount = document.querySelectorAll('.notification-item.unread').length;
        const todayCount = document.querySelectorAll('.notification-item[data-date=\"' + new Date().toISOString().split('T')[0] + '\"]').length;
        const urgentCount = document.querySelectorAll('.notification-item[data-type=\"urgent\"]').length;
        
        // تحديث بطاقات الإحصائيات
        this.updateStatCard('total', totalCount);
        this.updateStatCard('unread', unreadCount);
        this.updateStatCard('today', todayCount);
        this.updateStatCard('urgent', urgentCount);
        
        this.updateUnreadCount(unreadCount, true);
    }
    
    updateStatCard(type, count) {
        const card = document.querySelector(`[data-stat=\"${type}\"] .notification-stat-number`);
        if (card) {
            card.textContent = count;
        }
    }
    
    toggleEmptyState(show) {
        const emptyState = document.getElementById('emptyState');
        const notificationsList = document.getElementById('notificationsList');
        
        if (emptyState && notificationsList) {
            emptyState.style.display = show ? 'block' : 'none';
            notificationsList.style.display = show ? 'none' : 'block';
        }
    }
    
    showToast(message, type = 'info', options = {}) {
        // إزالة التوست القديم إذا تجاوز الحد الأقصى
        if (this.toasts.length >= this.settings.maxToasts) {
            this.closeToast(this.toasts[0]);
        }
        
        const toast = document.createElement('div');
        toast.className = `notification-toast ${type}`;
        toast.innerHTML = `
            <div class=\"d-flex justify-content-between align-items-start\">
                <div class=\"flex-grow-1\">
                    <div class=\"toast-message\">${message}</div>
                </div>
                <div class=\"toast-actions\">
                    ${options.action ? `<button class=\"btn btn-sm btn-link toast-action\">${options.action.text}</button>` : ''}
                    <button class=\"btn btn-sm btn-link toast-close\" aria-label=\"إغلاق\">
                        <i class=\"fas fa-times\"></i>
                    </button>
                </div>
            </div>
        `;
        
        // إضافة معالج الإجراء
        if (options.action) {
            toast.querySelector('.toast-action').addEventListener('click', options.action.callback);
        }
        
        document.body.appendChild(toast);
        this.toasts.push(toast);
        
        // إغلاق تلقائي
        setTimeout(() => {
            this.closeToast(toast);
        }, this.settings.toastDuration);
    }
    
    closeToast(toast) {
        if (toast && toast.parentNode) {
            toast.style.animation = 'slideOut 0.3s ease forwards';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
                this.toasts = this.toasts.filter(t => t !== toast);
            }, 300);
        }
    }
    
    closeAllToasts() {
        this.toasts.forEach(toast => this.closeToast(toast));
    }
    
    startAutoRefresh() {
        this.refreshTimer = setInterval(() => {
            this.checkNewNotifications();
        }, this.settings.autoRefreshInterval);
    }
    
    stopAutoRefresh() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
            this.refreshTimer = null;
        }
    }
    
    loadNotificationSound() {
        this.notificationSound = new Audio('/static/Hr/sounds/notification.mp3');
        this.notificationSound.volume = 0.5;
    }
    
    playNotificationSound() {
        if (this.settings.soundEnabled && this.notificationSound) {
            this.notificationSound.play().catch(error => {
                console.log('Could not play notification sound:', error);
            });
        }
    }
    
    async makeRequest(method, url, data = null) {
        const options = {
            method: method,
            headers: {
                'X-CSRFToken': this.getCSRFToken(),
                'Content-Type': data instanceof FormData ? undefined : 'application/json',
            }
        };
        
        if (data) {
            options.body = data instanceof FormData ? data : JSON.stringify(data);
        }
        
        const response = await fetch(url, options);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
    
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }
    
    debounce(func, wait) {
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
    
    // تنظيف الموارد
    destroy() {
        this.stopAutoRefresh();
        this.closeAllToasts();
        document.removeEventListener('click', this.handleClick);
        document.removeEventListener('keydown', this.handleKeydown);
    }
}

// تهيئة النظام عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', () => {
    window.notificationSystem = new NotificationSystem();
});

// إضافة أنماط CSS للرسوم المتحركة
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
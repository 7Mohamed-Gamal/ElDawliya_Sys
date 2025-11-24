/**
 * نظام المساعدة المدمج - نظام الدولية
 */

class HelpSystem {
    constructor() {
        this.isOpen = false;
        this.currentTourStep = 0;
        this.tourSteps = [];
        this.contextualHelp = {};
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadContextualHelp();
        this.setupKeyboardShortcuts();
        this.checkFirstVisit();
    }

    bindEvents() {
        // زر المساعدة العائم
        document.getElementById('help-toggle').addEventListener('click', () => {
            this.toggleHelpPanel();
        });

        // إغلاق نافذة المساعدة
        document.getElementById('help-close').addEventListener('click', () => {
            this.closeHelpPanel();
        });

        // تبويبات المساعدة
        document.querySelectorAll('.help-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });

        // البحث في المساعدة
        document.getElementById('help-search-btn').addEventListener('click', () => {
            this.searchHelp();
        });

        document.getElementById('help-search-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.searchHelp();
            }
        });

        // نموذج تذكرة الدعم
        document.getElementById('support-ticket-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitSupportTicket();
        });
    }

    toggleHelpPanel() {
        const panel = document.getElementById('help-panel');
        if (this.isOpen) {
            this.closeHelpPanel();
        } else {
            this.openHelpPanel();
        }
    }

    openHelpPanel() {
        const panel = document.getElementById('help-panel');
        panel.classList.add('open');
        this.isOpen = true;
        this.updateContextualHelp();
    }

    closeHelpPanel() {
        const panel = document.getElementById('help-panel');
        panel.classList.remove('open');
        this.isOpen = false;
    }

    switchTab(tabName) {
        // إخفاء جميع التبويبات
        document.querySelectorAll('.help-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelectorAll('.help-tab-content').forEach(content => {
            content.classList.remove('active');
        });

        // إظهار التبويب المحدد
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        document.getElementById(tabName).classList.add('active');
    }
}    loa
dContextualHelp() {
        // تحديد المساعدة السياقية حسب الصفحة الحالية
        const currentPage = window.location.pathname;
        
        this.contextualHelp = {
            '/hr/employees/': {
                title: 'إدارة الموظفين',
                content: `
                    <p>هذه الصفحة تتيح لك إدارة جميع بيانات الموظفين:</p>
                    <ul>
                        <li><strong>إضافة موظف:</strong> اضغط على زر "إضافة موظف جديد"</li>
                        <li><strong>البحث:</strong> استخدم مربع البحث للعثور على موظف محدد</li>
                        <li><strong>الفلترة:</strong> استخدم الفلاتر لتضييق النتائج</li>
                        <li><strong>التصدير:</strong> يمكنك تصدير قائمة الموظفين بصيغ مختلفة</li>
                    </ul>
                `,
                tips: [
                    'يمكنك النقر على اسم الموظف لعرض تفاصيله الكاملة',
                    'استخدم Ctrl+F للبحث السريع في الصفحة',
                    'يمكنك تحديد عدة موظفين لتطبيق إجراء جماعي'
                ]
            },
            '/inventory/products/': {
                title: 'إدارة المنتجات',
                content: `
                    <p>صفحة إدارة المنتجات والمخزون:</p>
                    <ul>
                        <li><strong>إضافة منتج:</strong> اضغط على "منتج جديد"</li>
                        <li><strong>تتبع المخزون:</strong> راقب الكميات المتاحة</li>
                        <li><strong>التنبيهات:</strong> ستظهر تنبيهات للمنتجات منخفضة المخزون</li>
                        <li><strong>الحركات:</strong> تتبع جميع حركات الوارد والصادر</li>
                    </ul>
                `,
                tips: [
                    'المنتجات ذات اللون الأحمر تحتاج إعادة طلب',
                    'يمكنك مسح الباركود لإضافة منتج سريعاً',
                    'استخدم الفئات لتنظيم المنتجات بشكل أفضل'
                ]
            },
            '/projects/': {
                title: 'إدارة المشاريع',
                content: `
                    <p>مركز إدارة المشاريع والمهام:</p>
                    <ul>
                        <li><strong>إنشاء مشروع:</strong> ابدأ مشروع جديد بخطوات بسيطة</li>
                        <li><strong>تعيين المهام:</strong> وزع المهام على أعضاء الفريق</li>
                        <li><strong>تتبع التقدم:</strong> راقب تقدم المشروع في الوقت الفعلي</li>
                        <li><strong>التقويم:</strong> عرض المهام والمواعيد النهائية</li>
                    </ul>
                `,
                tips: [
                    'استخدم عرض كانبان لإدارة المهام بصرياً',
                    'يمكنك سحب وإفلات المهام لتغيير حالتها',
                    'اربط المهام ببعضها لإنشاء تسلسل عمل'
                ]
            }
        };
    }

    updateContextualHelp() {
        const currentPage = window.location.pathname;
        const helpContent = document.getElementById('contextual-help');
        
        if (this.contextualHelp[currentPage]) {
            const help = this.contextualHelp[currentPage];
            helpContent.innerHTML = `
                <h5>${help.title}</h5>
                ${help.content}
                <div class="help-tips">
                    <h6>💡 نصائح مفيدة:</h6>
                    <ul>
                        ${help.tips.map(tip => `<li>${tip}</li>`).join('')}
                    </ul>
                </div>
            `;
        } else {
            helpContent.innerHTML = `
                <p>مرحباً بك في نظام الدولية!</p>
                <p>استخدم البحث أعلاه للعثور على المساعدة التي تحتاجها، أو تصفح الفئات المختلفة.</p>
            `;
        }
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // F1 - فتح المساعدة
            if (e.key === 'F1') {
                e.preventDefault();
                this.toggleHelpPanel();
            }
            
            // Ctrl + / - البحث السريع
            if (e.ctrlKey && e.key === '/') {
                e.preventDefault();
                document.getElementById('help-search-input').focus();
            }
            
            // Escape - إغلاق المساعدة
            if (e.key === 'Escape' && this.isOpen) {
                this.closeHelpPanel();
            }
        });
    }

    checkFirstVisit() {
        // فحص إذا كانت هذه أول زيارة للمستخدم
        if (!localStorage.getItem('eldawliya_visited')) {
            setTimeout(() => {
                this.showWelcomeTour();
            }, 2000);
        }
    }

    showWelcomeTour() {
        this.tourSteps = [
            {
                target: '#sidebar',
                title: 'القائمة الجانبية',
                description: 'هنا تجد جميع وحدات النظام. اضغط على أي وحدة للوصول إليها.',
                position: 'right'
            },
            {
                target: '#search-bar',
                title: 'البحث السريع',
                description: 'استخدم البحث السريع للعثور على أي بيانات في النظام بسرعة.',
                position: 'bottom'
            },
            {
                target: '#notifications',
                title: 'الإشعارات',
                description: 'ستظهر هنا جميع الإشعارات والتنبيهات المهمة.',
                position: 'bottom'
            },
            {
                target: '#user-menu',
                title: 'قائمة المستخدم',
                description: 'من هنا يمكنك الوصول لإعداداتك الشخصية وتسجيل الخروج.',
                position: 'bottom'
            },
            {
                target: '#help-toggle',
                title: 'المساعدة',
                description: 'اضغط هنا في أي وقت للحصول على المساعدة والدعم.',
                position: 'left'
            }
        ];
        
        this.startTour();
    }

    startTour() {
        this.currentTourStep = 0;
        this.showTourStep();
        document.getElementById('tour-overlay').style.display = 'flex';
        
        // ربط أحداث الجولة الإرشادية
        document.getElementById('tour-next').onclick = () => this.nextTourStep();
        document.getElementById('tour-prev').onclick = () => this.prevTourStep();
        document.getElementById('tour-skip').onclick = () => this.endTour();
        document.getElementById('tour-close').onclick = () => this.endTour();
    }

    showTourStep() {
        if (this.currentTourStep >= this.tourSteps.length) {
            this.endTour();
            return;
        }
        
        const step = this.tourSteps[this.currentTourStep];
        const target = document.querySelector(step.target);
        
        if (target) {
            // تمييز العنصر المستهدف
            this.highlightElement(target);
            
            // تحديث محتوى النافذة
            document.getElementById('tour-title').textContent = step.title;
            document.getElementById('tour-description').textContent = step.description;
            document.getElementById('tour-progress').textContent = 
                `${this.currentTourStep + 1} من ${this.tourSteps.length}`;
            
            // تحديث أزرار التنقل
            document.getElementById('tour-prev').style.display = 
                this.currentTourStep > 0 ? 'inline-block' : 'none';
            document.getElementById('tour-next').textContent = 
                this.currentTourStep === this.tourSteps.length - 1 ? 'إنهاء' : 'التالي';
        }
    }

    nextTourStep() {
        this.currentTourStep++;
        this.showTourStep();
    }

    prevTourStep() {
        if (this.currentTourStep > 0) {
            this.currentTourStep--;
            this.showTourStep();
        }
    }

    endTour() {
        document.getElementById('tour-overlay').style.display = 'none';
        this.removeHighlight();
        localStorage.setItem('eldawliya_visited', 'true');
    }

    highlightElement(element) {
        this.removeHighlight();
        element.classList.add('tour-highlight');
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    removeHighlight() {
        document.querySelectorAll('.tour-highlight').forEach(el => {
            el.classList.remove('tour-highlight');
        });
    }

    searchHelp() {
        const query = document.getElementById('help-search-input').value.trim();
        const resultsContainer = document.getElementById('help-search-results');
        
        if (!query) {
            resultsContainer.innerHTML = '<p>أدخل كلمة للبحث</p>';
            return;
        }
        
        // محاكاة البحث (في التطبيق الحقيقي، سيكون هذا استدعاء API)
        const mockResults = this.getMockSearchResults(query);
        
        if (mockResults.length === 0) {
            resultsContainer.innerHTML = '<p>لم يتم العثور على نتائج</p>';
        } else {
            resultsContainer.innerHTML = mockResults.map(result => `
                <div class="search-result">
                    <h5><a href="#" onclick="showHelp('${result.id}')">${result.title}</a></h5>
                    <p>${result.excerpt}</p>
                    <small>الفئة: ${result.category}</small>
                </div>
            `).join('');
        }
    }

    getMockSearchResults(query) {
        const allHelp = [
            {
                id: 'login',
                title: 'كيفية تسجيل الدخول',
                excerpt: 'خطوات تسجيل الدخول إلى النظام وحل مشاكل كلمة المرور',
                category: 'الأساسيات'
            },
            {
                id: 'add-employee',
                title: 'إضافة موظف جديد',
                excerpt: 'شرح مفصل لإضافة موظف جديد وإدخال جميع بياناته',
                category: 'الموارد البشرية'
            },
            {
                id: 'inventory-management',
                title: 'إدارة المخزون',
                excerpt: 'كيفية إضافة منتجات وتتبع المخزون وإدارة الحركات',
                category: 'المخزون'
            }
        ];
        
        return allHelp.filter(item => 
            item.title.includes(query) || 
            item.excerpt.includes(query) ||
            item.category.includes(query)
        );
    }

    browseCategory(category) {
        // تحديث نتائج البحث لإظهار مواضيع الفئة
        const resultsContainer = document.getElementById('help-search-results');
        const categoryTopics = this.getCategoryTopics(category);
        
        resultsContainer.innerHTML = categoryTopics.map(topic => `
            <div class="search-result">
                <h5><a href="#" onclick="showHelp('${topic.id}')">${topic.title}</a></h5>
                <p>${topic.description}</p>
            </div>
        `).join('');
    }

    getCategoryTopics(category) {
        const topics = {
            'hr': [
                { id: 'hr-overview', title: 'نظرة عامة على الموارد البشرية', description: 'مقدمة شاملة عن وحدة الموارد البشرية' },
                { id: 'employee-management', title: 'إدارة الموظفين', description: 'كيفية إضافة وتعديل وإدارة بيانات الموظفين' },
                { id: 'attendance-system', title: 'نظام الحضور والانصراف', description: 'تسجيل ومتابعة حضور الموظفين' },
                { id: 'payroll-system', title: 'نظام الرواتب', description: 'حساب وإدارة رواتب الموظفين' }
            ],
            'inventory': [
                { id: 'inventory-overview', title: 'نظرة عامة على المخزون', description: 'مقدمة عن وحدة إدارة المخزون' },
                { id: 'product-management', title: 'إدارة المنتجات', description: 'إضافة وتصنيف المنتجات' },
                { id: 'stock-movements', title: 'حركات المخزون', description: 'تسجيل حركات الوارد والصادر' },
                { id: 'suppliers', title: 'إدارة الموردين', description: 'إدارة بيانات الموردين وتقييمهم' }
            ],
            'projects': [
                { id: 'projects-overview', title: 'نظرة عامة على المشاريع', description: 'مقدمة عن وحدة إدارة المشاريع' },
                { id: 'project-creation', title: 'إنشاء مشروع جديد', description: 'خطوات إنشاء وإعداد مشروع جديد' },
                { id: 'task-management', title: 'إدارة المهام', description: 'إنشاء وتعيين ومتابعة المهام' },
                { id: 'team-collaboration', title: 'التعاون الجماعي', description: 'أدوات التعاون والتواصل بين أعضاء الفريق' }
            ],
            'reports': [
                { id: 'reports-overview', title: 'نظرة عامة على التقارير', description: 'مقدمة عن نظام التقارير والتحليلات' },
                { id: 'custom-reports', title: 'التقارير المخصصة', description: 'إنشاء تقارير مخصصة حسب احتياجاتك' },
                { id: 'dashboard', title: 'لوحة المعلومات', description: 'فهم واستخدام لوحة المعلومات التفاعلية' },
                { id: 'data-export', title: 'تصدير البيانات', description: 'تصدير البيانات والتقارير بصيغ مختلفة' }
            ]
        };
        
        return topics[category] || [];
    }

    createSupportTicket() {
        document.getElementById('support-ticket-modal').style.display = 'flex';
    }

    closeSupportTicket() {
        document.getElementById('support-ticket-modal').style.display = 'none';
    }

    submitSupportTicket() {
        const form = document.getElementById('support-ticket-form');
        const formData = new FormData(form);
        
        // في التطبيق الحقيقي، سيتم إرسال البيانات للخادم
        console.log('إرسال تذكرة دعم:', Object.fromEntries(formData));
        
        // إظهار رسالة نجاح
        alert('تم إرسال تذكرة الدعم بنجاح! سنتواصل معك قريباً.');
        
        // إغلاق النافذة وإعادة تعيين النموذج
        this.closeSupportTicket();
        form.reset();
    }

    showShortcuts() {
        document.getElementById('shortcuts-modal').style.display = 'flex';
    }

    closeShortcuts() {
        document.getElementById('shortcuts-modal').style.display = 'none';
    }

    startLiveChat() {
        // في التطبيق الحقيقي، سيتم فتح نافذة الدردشة المباشرة
        alert('ميزة الدردشة المباشرة ستكون متاحة قريباً!');
    }

    reportIssue() {
        // فتح نموذج الإبلاغ عن مشكلة
        this.createSupportTicket();
        document.getElementById('ticket-category').value = 'technical';
    }

    showHelp(topicId) {
        // عرض موضوع مساعدة محدد
        console.log('عرض موضوع المساعدة:', topicId);
        // في التطبيق الحقيقي، سيتم جلب المحتوى من الخادم
    }

    showTooltip(element, title, text) {
        const tooltip = document.getElementById('contextual-tooltip');
        const rect = element.getBoundingClientRect();
        
        document.getElementById('tooltip-title').textContent = title;
        document.getElementById('tooltip-text').textContent = text;
        
        tooltip.style.display = 'block';
        tooltip.style.left = rect.right + 10 + 'px';
        tooltip.style.top = rect.top + 'px';
    }

    hideTooltip() {
        document.getElementById('contextual-tooltip').style.display = 'none';
    }

    showMoreHelp() {
        this.hideTooltip();
        this.openHelpPanel();
    }
}

// تهيئة نظام المساعدة عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', () => {
    window.helpSystem = new HelpSystem();
});

// دوال عامة للاستخدام في الصفحات الأخرى
function startTour() {
    window.helpSystem.showWelcomeTour();
}

function showShortcuts() {
    window.helpSystem.showShortcuts();
}

function closeShortcuts() {
    window.helpSystem.closeShortcuts();
}

function reportIssue() {
    window.helpSystem.reportIssue();
}

function createSupportTicket() {
    window.helpSystem.createSupportTicket();
}

function closeSupportTicket() {
    window.helpSystem.closeSupportTicket();
}

function startLiveChat() {
    window.helpSystem.startLiveChat();
}

function showHelp(topicId) {
    window.helpSystem.showHelp(topicId);
}

function browseCategory(category) {
    window.helpSystem.browseCategory(category);
}

function hideTooltip() {
    window.helpSystem.hideTooltip();
}

function showMoreHelp() {
    window.helpSystem.showMoreHelp();
}
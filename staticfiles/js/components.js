/**
 * ElDawliya Component Library JavaScript
 * Enhanced interactions for UI components
 */

class ComponentManager {
    constructor() {
        this.init();
    }

    init() {
        this.setupModals();
        this.setupTooltips();
        this.setupButtonLoading();
        this.setupFormValidation();
        this.setupTableActions();
        this.setupProgressBars();
        this.setupCardAnimations();
    }

    /**
     * Modal Management
     */
    setupModals() {
        const modalTriggers = document.querySelectorAll('[data-bs-toggle="modal"]');
        const modals = document.querySelectorAll('.modal');

        modalTriggers.forEach(trigger => {
            trigger.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = trigger.getAttribute('data-bs-target');
                const modal = document.querySelector(targetId);
                if (modal) {
                    this.showModal(modal);
                }
            });
        });

        modals.forEach(modal => {
            // Close on backdrop click
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.hideModal(modal);
                }
            });

            // Close on escape key
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && modal.classList.contains('show')) {
                    this.hideModal(modal);
                }
            });

            // Close button
            const closeButtons = modal.querySelectorAll('.btn-close, [data-bs-dismiss="modal"]');
            closeButtons.forEach(btn => {
                btn.addEventListener('click', () => this.hideModal(modal));
            });
        });
    }

    showModal(modal) {
        // Create backdrop
        const backdrop = document.createElement('div');
        backdrop.className = 'modal-backdrop';
        backdrop.setAttribute('data-modal-id', modal.id);
        document.body.appendChild(backdrop);

        // Show modal
        modal.classList.add('show');
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';

        // Focus management
        const firstFocusable = modal.querySelector('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
        if (firstFocusable) {
            setTimeout(() => firstFocusable.focus(), 100);
        }

        // Animate backdrop
        setTimeout(() => backdrop.classList.add('show'), 10);
    }

    hideModal(modal) {
        const backdrop = document.querySelector(`[data-modal-id="${modal.id}"]`);
        
        modal.classList.remove('show');
        if (backdrop) {
            backdrop.remove();
        }
        
        setTimeout(() => {
            modal.style.display = 'none';
            document.body.style.overflow = '';
        }, 150);
    }

    /**
     * Tooltip Management
     */
    setupTooltips() {
        const tooltipElements = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        
        tooltipElements.forEach(element => {
            const tooltipText = element.getAttribute('title') || element.getAttribute('data-bs-title');
            if (!tooltipText) return;

            let tooltip = null;

            element.addEventListener('mouseenter', () => {
                tooltip = this.createTooltip(element, tooltipText);
                document.body.appendChild(tooltip);
                this.positionTooltip(element, tooltip);
                setTimeout(() => tooltip.classList.add('show'), 10);
            });

            element.addEventListener('mouseleave', () => {
                if (tooltip) {
                    tooltip.classList.remove('show');
                    setTimeout(() => {
                        if (tooltip && tooltip.parentNode) {
                            tooltip.parentNode.removeChild(tooltip);
                        }
                    }, 150);
                }
            });

            // Remove title to prevent default tooltip
            element.removeAttribute('title');
        });
    }

    createTooltip(element, text) {
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.innerHTML = `
            <div class="tooltip-arrow"></div>
            <div class="tooltip-inner">${text}</div>
        `;
        return tooltip;
    }

    positionTooltip(element, tooltip) {
        const rect = element.getBoundingClientRect();
        const tooltipRect = tooltip.getBoundingClientRect();
        
        // Position above element by default
        tooltip.style.left = `${rect.left + (rect.width / 2) - (tooltipRect.width / 2)}px`;
        tooltip.style.top = `${rect.top - tooltipRect.height - 8}px`;
    }

    /**
     * Button Loading States
     */
    setupButtonLoading() {
        const loadingButtons = document.querySelectorAll('.btn[data-loading]');
        
        loadingButtons.forEach(button => {
            button.addEventListener('click', () => {
                this.setButtonLoading(button, true);
                
                // Auto-remove loading state after specified time or 3 seconds
                const duration = parseInt(button.getAttribute('data-loading')) || 3000;
                setTimeout(() => {
                    this.setButtonLoading(button, false);
                }, duration);
            });
        });
    }

    setButtonLoading(button, loading) {
        if (loading) {
            button.classList.add('btn-loading');
            button.disabled = true;
            button.setAttribute('data-original-text', button.textContent);
        } else {
            button.classList.remove('btn-loading');
            button.disabled = false;
            const originalText = button.getAttribute('data-original-text');
            if (originalText) {
                button.textContent = originalText;
            }
        }
    }

    /**
     * Form Validation Enhancement
     */
    setupFormValidation() {
        const forms = document.querySelectorAll('.needs-validation');
        
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!form.checkValidity()) {
                    e.preventDefault();
                    e.stopPropagation();
                }
                form.classList.add('was-validated');
            });

            // Real-time validation
            const inputs = form.querySelectorAll('.form-control');
            inputs.forEach(input => {
                input.addEventListener('blur', () => {
                    this.validateField(input);
                });

                input.addEventListener('input', () => {
                    if (input.classList.contains('is-invalid')) {
                        this.validateField(input);
                    }
                });
            });
        });
    }

    validateField(field) {
        const isValid = field.checkValidity();
        field.classList.remove('is-valid', 'is-invalid');
        field.classList.add(isValid ? 'is-valid' : 'is-invalid');
    }

    /**
     * Table Actions
     */
    setupTableActions() {
        const tables = document.querySelectorAll('.table');
        
        tables.forEach(table => {
            // Row selection
            const checkboxes = table.querySelectorAll('input[type="checkbox"]');
            const selectAllCheckbox = table.querySelector('thead input[type="checkbox"]');
            
            if (selectAllCheckbox) {
                selectAllCheckbox.addEventListener('change', () => {
                    checkboxes.forEach(checkbox => {
                        if (checkbox !== selectAllCheckbox) {
                            checkbox.checked = selectAllCheckbox.checked;
                            this.updateRowSelection(checkbox.closest('tr'), checkbox.checked);
                        }
                    });
                });
            }

            checkboxes.forEach(checkbox => {
                if (checkbox !== selectAllCheckbox) {
                    checkbox.addEventListener('change', () => {
                        this.updateRowSelection(checkbox.closest('tr'), checkbox.checked);
                    });
                }
            });

            // Row hover effects
            const rows = table.querySelectorAll('tbody tr');
            rows.forEach(row => {
                row.addEventListener('mouseenter', () => {
                    row.style.transform = 'scale(1.01)';
                });

                row.addEventListener('mouseleave', () => {
                    row.style.transform = 'scale(1)';
                });
            });
        });
    }

    updateRowSelection(row, selected) {
        if (selected) {
            row.classList.add('table-row-selected');
        } else {
            row.classList.remove('table-row-selected');
        }
    }

    /**
     * Progress Bar Animations
     */
    setupProgressBars() {
        const progressBars = document.querySelectorAll('.progress-bar[data-animate]');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const progressBar = entry.target;
                    const targetWidth = progressBar.getAttribute('data-width') || progressBar.style.width;
                    
                    progressBar.style.width = '0%';
                    setTimeout(() => {
                        progressBar.style.width = targetWidth;
                    }, 100);
                    
                    observer.unobserve(progressBar);
                }
            });
        });

        progressBars.forEach(bar => observer.observe(bar));
    }

    /**
     * Card Animations
     */
    setupCardAnimations() {
        const cards = document.querySelectorAll('.card, .feature-card, .stats-card');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, { threshold: 0.1 });

        cards.forEach(card => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            observer.observe(card);
        });
    }

    /**
     * Utility Methods
     */
    static showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        toast.innerHTML = `
            <div class="alert-content">
                <div class="alert-message">${message}</div>
            </div>
            <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 5000);
    }

    static confirmAction(message, callback) {
        const confirmed = confirm(message);
        if (confirmed && typeof callback === 'function') {
            callback();
        }
        return confirmed;
    }
}

// Initialize component manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ComponentManager();
});

// Export for use in other scripts
window.ComponentManager = ComponentManager;

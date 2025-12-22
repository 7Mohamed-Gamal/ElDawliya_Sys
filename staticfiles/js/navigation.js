/**
 * Modern Navigation System
 * Enhanced navigation with accessibility, mobile support, and smooth animations
 */

class NavigationManager {
    constructor() {
        this.init();
    }

    init() {
        this.setupMobileNavigation();
        this.setupDropdowns();
        this.setupAccessibility();
        this.setupScrollBehavior();
        this.setupActiveStates();
    }

    /**
     * Mobile Navigation Setup
     */
    setupMobileNavigation() {
        const navbarToggler = document.querySelector('.navbar-toggler');
        const navbarNav = document.querySelector('.navbar-nav');
        const navbarOverlay = document.querySelector('.navbar-overlay') || this.createOverlay();

        if (navbarToggler && navbarNav) {
            navbarToggler.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleMobileNav(navbarNav, navbarOverlay, navbarToggler);
            });

            // Close on overlay click
            navbarOverlay.addEventListener('click', () => {
                this.closeMobileNav(navbarNav, navbarOverlay, navbarToggler);
            });

            // Close on escape key
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && navbarNav.classList.contains('show')) {
                    this.closeMobileNav(navbarNav, navbarOverlay, navbarToggler);
                }
            });

            // Close on window resize
            window.addEventListener('resize', () => {
                if (window.innerWidth > 991) {
                    this.closeMobileNav(navbarNav, navbarOverlay, navbarToggler);
                }
            });
        }
    }

    /**
     * Create overlay element if it doesn't exist
     */
    createOverlay() {
        const overlay = document.createElement('div');
        overlay.className = 'navbar-overlay';
        document.body.appendChild(overlay);
        return overlay;
    }

    /**
     * Toggle mobile navigation
     */
    toggleMobileNav(navbarNav, overlay, toggler) {
        const isOpen = navbarNav.classList.contains('show');
        
        if (isOpen) {
            this.closeMobileNav(navbarNav, overlay, toggler);
        } else {
            this.openMobileNav(navbarNav, overlay, toggler);
        }
    }

    /**
     * Open mobile navigation
     */
    openMobileNav(navbarNav, overlay, toggler) {
        navbarNav.classList.add('show');
        overlay.classList.add('show');
        toggler.classList.add('collapsed');
        toggler.setAttribute('aria-expanded', 'true');
        document.body.style.overflow = 'hidden';
        
        // Focus first nav link for accessibility
        const firstNavLink = navbarNav.querySelector('.nav-link');
        if (firstNavLink) {
            setTimeout(() => firstNavLink.focus(), 300);
        }
    }

    /**
     * Close mobile navigation
     */
    closeMobileNav(navbarNav, overlay, toggler) {
        navbarNav.classList.remove('show');
        overlay.classList.remove('show');
        toggler.classList.remove('collapsed');
        toggler.setAttribute('aria-expanded', 'false');
        document.body.style.overflow = '';
        
        // Return focus to toggle button
        toggler.focus();
    }

    /**
     * Setup dropdown functionality
     */
    setupDropdowns() {
        const dropdowns = document.querySelectorAll('.dropdown');
        
        dropdowns.forEach(dropdown => {
            const toggle = dropdown.querySelector('.dropdown-toggle');
            const menu = dropdown.querySelector('.dropdown-menu');
            
            if (toggle && menu) {
                // Click to toggle
                toggle.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.toggleDropdown(dropdown, toggle, menu);
                });

                // Keyboard navigation
                toggle.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        this.toggleDropdown(dropdown, toggle, menu);
                    } else if (e.key === 'ArrowDown') {
                        e.preventDefault();
                        this.openDropdown(dropdown, toggle, menu);
                        const firstItem = menu.querySelector('.dropdown-item');
                        if (firstItem) firstItem.focus();
                    }
                });

                // Close on outside click
                document.addEventListener('click', (e) => {
                    if (!dropdown.contains(e.target)) {
                        this.closeDropdown(dropdown, toggle, menu);
                    }
                });
            }
        });
    }

    /**
     * Toggle dropdown
     */
    toggleDropdown(dropdown, toggle, menu) {
        const isOpen = dropdown.classList.contains('show');
        
        if (isOpen) {
            this.closeDropdown(dropdown, toggle, menu);
        } else {
            this.openDropdown(dropdown, toggle, menu);
        }
    }

    /**
     * Open dropdown
     */
    openDropdown(dropdown, toggle, menu) {
        // Close other dropdowns
        document.querySelectorAll('.dropdown.show').forEach(otherDropdown => {
            if (otherDropdown !== dropdown) {
                this.closeDropdown(
                    otherDropdown,
                    otherDropdown.querySelector('.dropdown-toggle'),
                    otherDropdown.querySelector('.dropdown-menu')
                );
            }
        });

        dropdown.classList.add('show');
        toggle.setAttribute('aria-expanded', 'true');
        menu.setAttribute('aria-hidden', 'false');
    }

    /**
     * Close dropdown
     */
    closeDropdown(dropdown, toggle, menu) {
        dropdown.classList.remove('show');
        toggle.setAttribute('aria-expanded', 'false');
        menu.setAttribute('aria-hidden', 'true');
    }

    /**
     * Setup accessibility features
     */
    setupAccessibility() {
        // Add ARIA labels and roles
        const navbar = document.querySelector('.navbar');
        if (navbar) {
            navbar.setAttribute('role', 'navigation');
            navbar.setAttribute('aria-label', 'Main navigation');
        }

        const navbarNav = document.querySelector('.navbar-nav');
        if (navbarNav) {
            navbarNav.setAttribute('role', 'menubar');
        }

        // Setup nav links
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.setAttribute('role', 'menuitem');
            
            // Add keyboard navigation
            link.addEventListener('keydown', (e) => {
                if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {
                    e.preventDefault();
                    this.navigateNavLinks(link, e.key === 'ArrowRight');
                }
            });
        });

        // Setup dropdown items
        const dropdownItems = document.querySelectorAll('.dropdown-item');
        dropdownItems.forEach((item, index, items) => {
            item.setAttribute('role', 'menuitem');
            
            item.addEventListener('keydown', (e) => {
                if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
                    e.preventDefault();
                    this.navigateDropdownItems(items, index, e.key === 'ArrowDown');
                } else if (e.key === 'Escape') {
                    const dropdown = item.closest('.dropdown');
                    const toggle = dropdown.querySelector('.dropdown-toggle');
                    this.closeDropdown(dropdown, toggle, item.closest('.dropdown-menu'));
                    toggle.focus();
                }
            });
        });
    }

    /**
     * Navigate between nav links with keyboard
     */
    navigateNavLinks(currentLink, forward) {
        const navLinks = Array.from(document.querySelectorAll('.nav-link'));
        const currentIndex = navLinks.indexOf(currentLink);
        let nextIndex;

        if (forward) {
            nextIndex = currentIndex + 1 >= navLinks.length ? 0 : currentIndex + 1;
        } else {
            nextIndex = currentIndex - 1 < 0 ? navLinks.length - 1 : currentIndex - 1;
        }

        navLinks[nextIndex].focus();
    }

    /**
     * Navigate between dropdown items with keyboard
     */
    navigateDropdownItems(items, currentIndex, forward) {
        let nextIndex;

        if (forward) {
            nextIndex = currentIndex + 1 >= items.length ? 0 : currentIndex + 1;
        } else {
            nextIndex = currentIndex - 1 < 0 ? items.length - 1 : currentIndex - 1;
        }

        items[nextIndex].focus();
    }

    /**
     * Setup scroll behavior for navbar
     */
    setupScrollBehavior() {
        const navbar = document.querySelector('.navbar');
        if (!navbar) return;

        let lastScrollY = window.scrollY;
        let ticking = false;

        const updateNavbar = () => {
            const currentScrollY = window.scrollY;
            
            if (currentScrollY > 100) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }

            lastScrollY = currentScrollY;
            ticking = false;
        };

        window.addEventListener('scroll', () => {
            if (!ticking) {
                requestAnimationFrame(updateNavbar);
                ticking = true;
            }
        });
    }

    /**
     * Setup active states for navigation
     */
    setupActiveStates() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.nav-link');

        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href && currentPath.includes(href) && href !== '/') {
                link.classList.add('active');
            }
        });
    }
}

// Initialize navigation when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new NavigationManager();
});

// Add scrolled class styles
const style = document.createElement('style');
style.textContent = `
    .navbar.scrolled {
        background: rgba(var(--bg-primary-rgb), 0.95);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        box-shadow: var(--shadow-lg);
    }
`;
document.head.appendChild(style);

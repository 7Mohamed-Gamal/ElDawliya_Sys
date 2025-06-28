/**
 * ElDawliya HR - Advanced Theme Manager
 * Handles light/dark mode switching with smooth transitions and user preferences
 */

class ThemeManager {
    constructor() {
        this.themes = {
            light: 'light',
            dark: 'dark',
            auto: 'auto'
        };
        
        this.currentTheme = this.getStoredTheme() || this.themes.auto;
        this.mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        
        this.init();
    }
    
    init() {
        // Apply initial theme
        this.applyTheme(this.currentTheme);
        
        // Listen for system theme changes
        this.mediaQuery.addEventListener('change', (e) => {
            if (this.currentTheme === this.themes.auto) {
                this.updateThemeDisplay();
            }
        });
        
        // Setup theme toggle buttons
        this.setupThemeToggles();
        
        // Add smooth transition class after initial load
        setTimeout(() => {
            document.documentElement.classList.add('theme-transition');
        }, 100);
    }
    
    getStoredTheme() {
        try {
            return localStorage.getItem('hr-theme');
        } catch (e) {
            console.warn('localStorage not available for theme storage');
            return null;
        }
    }
    
    setStoredTheme(theme) {
        try {
            localStorage.setItem('hr-theme', theme);
        } catch (e) {
            console.warn('localStorage not available for theme storage');
        }
    }
    
    getSystemTheme() {
        return this.mediaQuery.matches ? this.themes.dark : this.themes.light;
    }
    
    getEffectiveTheme() {
        if (this.currentTheme === this.themes.auto) {
            return this.getSystemTheme();
        }
        return this.currentTheme;
    }
    
    applyTheme(theme) {
        this.currentTheme = theme;
        this.setStoredTheme(theme);
        this.updateThemeDisplay();
        this.updateThemeToggles();
        
        // Dispatch theme change event
        window.dispatchEvent(new CustomEvent('themeChanged', {
            detail: {
                theme: theme,
                effectiveTheme: this.getEffectiveTheme()
            }
        }));
    }
    
    updateThemeDisplay() {
        const effectiveTheme = this.getEffectiveTheme();
        document.documentElement.setAttribute('data-theme', effectiveTheme);
        
        // Update meta theme-color for mobile browsers
        this.updateMetaThemeColor(effectiveTheme);
    }
    
    updateMetaThemeColor(theme) {
        let themeColor = '#ffffff'; // Light theme default
        
        if (theme === this.themes.dark) {
            themeColor = '#1f2937'; // Dark theme color
        }
        
        let metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (!metaThemeColor) {
            metaThemeColor = document.createElement('meta');
            metaThemeColor.name = 'theme-color';
            document.head.appendChild(metaThemeColor);
        }
        metaThemeColor.content = themeColor;
    }
    
    setupThemeToggles() {
        // Main theme toggle button
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                this.toggleTheme();
            });
        }
        
        // Theme selector dropdown (if exists)
        const themeSelector = document.getElementById('themeSelector');
        if (themeSelector) {
            themeSelector.addEventListener('change', (e) => {
                this.applyTheme(e.target.value);
            });
        }
        
        // Keyboard shortcut (Ctrl/Cmd + Shift + T)
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'T') {
                e.preventDefault();
                this.toggleTheme();
            }
        });
    }
    
    toggleTheme() {
        const effectiveTheme = this.getEffectiveTheme();
        const newTheme = effectiveTheme === this.themes.dark ? this.themes.light : this.themes.dark;
        this.applyTheme(newTheme);
    }
    
    updateThemeToggles() {
        const effectiveTheme = this.getEffectiveTheme();
        
        // Update main toggle button icon
        const themeIcon = document.getElementById('themeIcon');
        if (themeIcon) {
            themeIcon.className = effectiveTheme === this.themes.dark ? 'fas fa-sun' : 'fas fa-moon';
        }
        
        // Update toggle button title
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            const title = effectiveTheme === this.themes.dark 
                ? 'تبديل إلى الوضع النهاري' 
                : 'تبديل إلى الوضع الليلي';
            themeToggle.title = title;
            themeToggle.setAttribute('aria-label', title);
        }
        
        // Update theme selector
        const themeSelector = document.getElementById('themeSelector');
        if (themeSelector) {
            themeSelector.value = this.currentTheme;
        }
        
        // Update any theme status indicators
        const themeStatus = document.querySelectorAll('[data-theme-status]');
        themeStatus.forEach(element => {
            element.textContent = this.getThemeDisplayName(effectiveTheme);
        });
    }
    
    getThemeDisplayName(theme) {
        const names = {
            light: 'الوضع النهاري',
            dark: 'الوضع الليلي',
            auto: 'تلقائي'
        };
        return names[theme] || theme;
    }
    
    // Public API methods
    setTheme(theme) {
        if (Object.values(this.themes).includes(theme)) {
            this.applyTheme(theme);
        } else {
            console.warn(`Invalid theme: ${theme}`);
        }
    }
    
    getTheme() {
        return this.currentTheme;
    }
    
    getActiveTheme() {
        return this.getEffectiveTheme();
    }
    
    isSystemDarkMode() {
        return this.mediaQuery.matches;
    }
    
    // Animation helpers
    enableTransitions() {
        document.documentElement.classList.add('theme-transition');
    }
    
    disableTransitions() {
        document.documentElement.classList.remove('theme-transition');
    }
    
    // Accessibility helpers
    announceThemeChange() {
        const effectiveTheme = this.getEffectiveTheme();
        const message = `تم تغيير المظهر إلى ${this.getThemeDisplayName(effectiveTheme)}`;
        
        // Create or update live region for screen readers
        let liveRegion = document.getElementById('theme-live-region');
        if (!liveRegion) {
            liveRegion = document.createElement('div');
            liveRegion.id = 'theme-live-region';
            liveRegion.setAttribute('aria-live', 'polite');
            liveRegion.setAttribute('aria-atomic', 'true');
            liveRegion.style.position = 'absolute';
            liveRegion.style.left = '-10000px';
            liveRegion.style.width = '1px';
            liveRegion.style.height = '1px';
            liveRegion.style.overflow = 'hidden';
            document.body.appendChild(liveRegion);
        }
        
        liveRegion.textContent = message;
    }
}

// CSS for smooth theme transitions
const themeTransitionCSS = `
.theme-transition,
.theme-transition *,
.theme-transition *:before,
.theme-transition *:after {
    transition: background-color 300ms cubic-bezier(0.4, 0, 0.2, 1),
                color 300ms cubic-bezier(0.4, 0, 0.2, 1),
                border-color 300ms cubic-bezier(0.4, 0, 0.2, 1),
                box-shadow 300ms cubic-bezier(0.4, 0, 0.2, 1) !important;
}
`;

// Inject transition CSS
const style = document.createElement('style');
style.textContent = themeTransitionCSS;
document.head.appendChild(style);

// Initialize theme manager when DOM is ready
let themeManager;

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        themeManager = new ThemeManager();
        window.themeManager = themeManager; // Make globally accessible
    });
} else {
    themeManager = new ThemeManager();
    window.themeManager = themeManager;
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ThemeManager;
}

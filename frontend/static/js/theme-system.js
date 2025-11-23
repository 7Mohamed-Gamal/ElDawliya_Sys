/**
 * Theme System - Light/Dark Mode Toggle
 * نظام الثيمات - تبديل الوضع الفاتح/الداكن
 */

class ThemeSystem {
    constructor() {
        this.currentTheme = this.getStoredTheme() || this.getPreferredTheme();
        this.init();
    }

    /**
     * Initialize the theme system
     */
    init() {
        // Apply the current theme
        this.applyTheme(this.currentTheme);
        
        // Create theme toggle button
        this.createThemeToggle();
        
        // Listen for system theme changes
        this.listenForSystemThemeChanges();
        
        // Listen for storage changes (for multi-tab sync)
        this.listenForStorageChanges();
    }

    /**
     * Get the stored theme from localStorage
     */
    getStoredTheme() {
        return localStorage.getItem('eldawliya-theme');
    }

    /**
     * Get the preferred theme based on system preference
     */
    getPreferredTheme() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        }
        return 'light';
    }

    /**
     * Store the theme in localStorage
     */
    storeTheme(theme) {
        localStorage.setItem('eldawliya-theme', theme);
    }

    /**
     * Apply the theme to the document
     */
    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        this.currentTheme = theme;
        this.storeTheme(theme);
        
        // Update meta theme-color for mobile browsers
        this.updateMetaThemeColor(theme);
        
        // Dispatch custom event
        this.dispatchThemeChangeEvent(theme);
    }

    /**
     * Toggle between light and dark themes
     */
    toggleTheme() {
        const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        
        // Add transition class to prevent flash
        document.body.classList.add('theme-switching');
        
        // Apply new theme
        this.applyTheme(newTheme);
        
        // Remove transition class after animation
        setTimeout(() => {
            document.body.classList.remove('theme-switching');
        }, 300);
        
        // Update toggle button
        this.updateToggleButton();
        
        // Animate the toggle button
        this.animateToggleButton();
    }

    /**
     * Create the theme toggle button
     */
    createThemeToggle() {
        // Check if toggle already exists
        if (document.querySelector('.theme-toggle')) {
            return;
        }

        const toggle = document.createElement('button');
        toggle.className = 'theme-toggle';
        toggle.setAttribute('aria-label', 'تبديل الثيم');
        toggle.setAttribute('title', 'تبديل بين الوضع الفاتح والداكن');
        
        // Create icons
        const sunIcon = document.createElement('i');
        sunIcon.className = 'fas fa-sun icon sun-icon';
        
        const moonIcon = document.createElement('i');
        moonIcon.className = 'fas fa-moon icon moon-icon';
        
        toggle.appendChild(sunIcon);
        toggle.appendChild(moonIcon);
        
        // Add click event
        toggle.addEventListener('click', () => this.toggleTheme());
        
        // Add keyboard support
        toggle.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.toggleTheme();
            }
        });
        
        // Append to body
        document.body.appendChild(toggle);
        
        // Update button state
        this.updateToggleButton();
    }

    /**
     * Update the toggle button appearance
     */
    updateToggleButton() {
        const toggle = document.querySelector('.theme-toggle');
        if (!toggle) return;
        
        const sunIcon = toggle.querySelector('.sun-icon');
        const moonIcon = toggle.querySelector('.moon-icon');
        
        if (this.currentTheme === 'dark') {
            toggle.setAttribute('aria-label', 'تبديل إلى الوضع الفاتح');
            toggle.setAttribute('title', 'تبديل إلى الوضع الفاتح');
        } else {
            toggle.setAttribute('aria-label', 'تبديل إلى الوضع الداكن');
            toggle.setAttribute('title', 'تبديل إلى الوضع الداكن');
        }
    }

    /**
     * Animate the toggle button
     */
    animateToggleButton() {
        const toggle = document.querySelector('.theme-toggle');
        if (!toggle) return;
        
        // Add pulse animation
        toggle.style.transform = 'scale(1.1)';
        setTimeout(() => {
            toggle.style.transform = '';
        }, 150);
    }

    /**
     * Update meta theme-color for mobile browsers
     */
    updateMetaThemeColor(theme) {
        let metaThemeColor = document.querySelector('meta[name="theme-color"]');
        
        if (!metaThemeColor) {
            metaThemeColor = document.createElement('meta');
            metaThemeColor.name = 'theme-color';
            document.head.appendChild(metaThemeColor);
        }
        
        const colors = {
            light: '#f8fafc',
            dark: '#1e293b'
        };
        
        metaThemeColor.content = colors[theme];
    }

    /**
     * Listen for system theme changes
     */
    listenForSystemThemeChanges() {
        if (window.matchMedia) {
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            
            mediaQuery.addEventListener('change', (e) => {
                // Only auto-switch if user hasn't manually set a preference
                if (!this.getStoredTheme()) {
                    const newTheme = e.matches ? 'dark' : 'light';
                    this.applyTheme(newTheme);
                    this.updateToggleButton();
                }
            });
        }
    }

    /**
     * Listen for storage changes (multi-tab sync)
     */
    listenForStorageChanges() {
        window.addEventListener('storage', (e) => {
            if (e.key === 'eldawliya-theme' && e.newValue !== this.currentTheme) {
                this.applyTheme(e.newValue);
                this.updateToggleButton();
            }
        });
    }

    /**
     * Dispatch custom theme change event
     */
    dispatchThemeChangeEvent(theme) {
        const event = new CustomEvent('themechange', {
            detail: { theme }
        });
        document.dispatchEvent(event);
    }

    /**
     * Get current theme
     */
    getCurrentTheme() {
        return this.currentTheme;
    }

    /**
     * Set theme programmatically
     */
    setTheme(theme) {
        if (theme !== 'light' && theme !== 'dark') {
            console.warn('Invalid theme. Use "light" or "dark".');
            return;
        }
        
        this.applyTheme(theme);
        this.updateToggleButton();
    }

    /**
     * Reset to system preference
     */
    resetToSystemPreference() {
        localStorage.removeItem('eldawliya-theme');
        const systemTheme = this.getPreferredTheme();
        this.applyTheme(systemTheme);
        this.updateToggleButton();
    }
}

/**
 * Theme-aware component utilities
 */
class ThemeUtils {
    /**
     * Get theme-appropriate color
     */
    static getThemeColor(lightColor, darkColor) {
        const theme = document.documentElement.getAttribute('data-theme');
        return theme === 'dark' ? darkColor : lightColor;
    }

    /**
     * Check if current theme is dark
     */
    static isDarkTheme() {
        return document.documentElement.getAttribute('data-theme') === 'dark';
    }

    /**
     * Check if current theme is light
     */
    static isLightTheme() {
        return document.documentElement.getAttribute('data-theme') === 'light';
    }

    /**
     * Get CSS custom property value
     */
    static getCSSVariable(property) {
        return getComputedStyle(document.documentElement).getPropertyValue(property).trim();
    }

    /**
     * Set CSS custom property value
     */
    static setCSSVariable(property, value) {
        document.documentElement.style.setProperty(property, value);
    }

    /**
     * Apply theme to specific element
     */
    static applyThemeToElement(element, lightClass, darkClass) {
        const isDark = this.isDarkTheme();
        element.classList.remove(lightClass, darkClass);
        element.classList.add(isDark ? darkClass : lightClass);
    }
}

/**
 * Chart.js theme integration
 */
class ChartThemeIntegration {
    static getChartOptions() {
        const isDark = ThemeUtils.isDarkTheme();
        
        return {
            plugins: {
                legend: {
                    labels: {
                        color: isDark ? '#f1f5f9' : '#334155'
                    }
                }
            },
            scales: {
                x: {
                    ticks: {
                        color: isDark ? '#cbd5e1' : '#64748b'
                    },
                    grid: {
                        color: isDark ? '#475569' : '#e2e8f0'
                    }
                },
                y: {
                    ticks: {
                        color: isDark ? '#cbd5e1' : '#64748b'
                    },
                    grid: {
                        color: isDark ? '#475569' : '#e2e8f0'
                    }
                }
            }
        };
    }

    static updateChart(chart) {
        const options = this.getChartOptions();
        chart.options = { ...chart.options, ...options };
        chart.update();
    }
}

/**
 * Initialize theme system when DOM is ready
 */
document.addEventListener('DOMContentLoaded', () => {
    // Initialize theme system
    window.themeSystem = new ThemeSystem();
    
    // Make utilities globally available
    window.ThemeUtils = ThemeUtils;
    window.ChartThemeIntegration = ChartThemeIntegration;
    
    // Listen for theme changes to update charts
    document.addEventListener('themechange', (e) => {
        // Update any existing charts
        if (window.Chart && window.Chart.instances) {
            Object.values(window.Chart.instances).forEach(chart => {
                ChartThemeIntegration.updateChart(chart);
            });
        }
        
        // Dispatch event for custom components
        console.log(`Theme changed to: ${e.detail.theme}`);
    });
});

/**
 * Export for module systems
 */
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ThemeSystem, ThemeUtils, ChartThemeIntegration };
}
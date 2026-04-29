/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './apps/**/templates/**/*.html',
    './apps/**/*.py',
    './accounts/templates/**/*.html',
    './administrator/templates/**/*.html',
    './api/templates/**/*.html',
    './core/templates/**/*.html',
    './frontend/templates/**/*.html',
    './notifications/templates/**/*.html',
    './companies/templates/**/*.html',
    './org/templates/**/*.html',
    './audit/templates/**/*.html',
    './static/js/**/*.js',
  ],
  darkMode: 'class', // Enable class-based dark mode
  theme: {
    extend: {
      // =====================
      // COLOR PALETTE
      // =====================
      colors: {
        // Primary Colors - Professional Blue
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',  // Main primary
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
          950: '#172554',
        },
        // Secondary Colors - Indigo
        secondary: {
          50: '#eef2ff',
          100: '#e0e7ff',
          200: '#c7d2fe',
          300: '#a5b4fc',
          400: '#818cf8',
          500: '#6366f1',  // Main secondary
          600: '#4f46e5',
          700: '#4338ca',
          800: '#3730a3',
          900: '#312e81',
          950: '#1e1b4b',
        },
        // Accent Colors - Amber
        accent: {
          50: '#fffbeb',
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',
          500: '#f59e0b',  // Main accent
          600: '#d97706',
          700: '#b45309',
          800: '#92400e',
          900: '#78350f',
          950: '#451a03',
        },
        // Semantic Colors
        success: {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d',
        },
        warning: {
          50: '#fffbeb',
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',
          500: '#f59e0b',
          600: '#d97706',
          700: '#b45309',
          800: '#92400e',
          900: '#78350f',
        },
        error: {
          50: '#fef2f2',
          100: '#fee2e2',
          200: '#fecaca',
          300: '#fca5a5',
          400: '#f87171',
          500: '#ef4444',
          600: '#dc2626',
          700: '#b91c1c',
          800: '#991b1b',
          900: '#7f1d1d',
        },
        info: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
        },
        // Neutral Colors
        neutral: {
          50: '#fafafa',
          100: '#f5f5f5',
          200: '#e5e5e5',
          300: '#d4d4d4',
          400: '#a3a3a3',
          500: '#737373',
          600: '#525252',
          700: '#404040',
          800: '#262626',
          900: '#171717',
          950: '#0a0a0a',
        },
      },

      // =====================
      // TYPOGRAPHY SCALE
      // =====================
      fontFamily: {
        // Arabic Fonts
        sans: ['Cairo', 'system-ui', '-apple-system', 'sans-serif'],
        display: ['Cairo', 'system-ui', 'sans-serif'],
        body: ['Cairo', 'system-ui', 'sans-serif'],
        // Alternative Arabic Fonts
        tajawal: ['Tajawal', 'system-ui', 'sans-serif'],
        almarai: ['Almarai', 'system-ui', 'sans-serif'],
        'ibm-plex': ['IBM Plex Sans Arabic', 'system-ui', 'sans-serif'],
        'noto-sans': ['Noto Sans Arabic', 'system-ui', 'sans-serif'],
      },
      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1rem', letterSpacing: '-0.01em' }],
        'sm': ['0.875rem', { lineHeight: '1.25rem', letterSpacing: '-0.01em' }],
        'base': ['1rem', { lineHeight: '1.5rem', letterSpacing: '0' }],
        'lg': ['1.125rem', { lineHeight: '1.75rem', letterSpacing: '0' }],
        'xl': ['1.25rem', { lineHeight: '1.75rem', letterSpacing: '0' }],
        '2xl': ['1.5rem', { lineHeight: '2rem', letterSpacing: '0' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem', letterSpacing: '0.01em' }],
        '4xl': ['2.25rem', { lineHeight: '2.5rem', letterSpacing: '0.02em' }],
        '5xl': ['3rem', { lineHeight: '1', letterSpacing: '0.02em' }],
        '6xl': ['3.75rem', { lineHeight: '1', letterSpacing: '0.03em' }],
        '7xl': ['4.5rem', { lineHeight: '1', letterSpacing: '0.04em' }],
        '8xl': ['6rem', { lineHeight: '1', letterSpacing: '0.04em' }],
        '9xl': ['8rem', { lineHeight: '1', letterSpacing: '0.05em' }],
      },
      fontWeight: {
        thin: '100',
        extralight: '200',
        light: '300',
        normal: '400',
        medium: '500',
        semibold: '600',
        bold: '700',
        extrabold: '800',
        black: '900',
      },

      // =====================
      // SPACING SYSTEM
      // =====================
      spacing: {
        'px': '1px',
        '0': '0px',
        '0.5': '0.125rem',   // 2px
        '1': '0.25rem',      // 4px
        '1.5': '0.375rem',   // 6px
        '2': '0.5rem',       // 8px
        '2.5': '0.625rem',   // 10px
        '3': '0.75rem',      // 12px
        '3.5': '0.875rem',   // 14px
        '4': '1rem',         // 16px
        '5': '1.25rem',      // 20px
        '6': '1.5rem',       // 24px
        '7': '1.75rem',      // 28px
        '8': '2rem',         // 32px
        '9': '2.25rem',      // 36px
        '10': '2.5rem',      // 40px
        '11': '2.75rem',     // 44px
        '12': '3rem',        // 48px
        '14': '3.5rem',      // 56px
        '16': '4rem',        // 64px
        '20': '5rem',        // 80px
        '24': '6rem',        // 96px
        '28': '7rem',        // 112px
        '32': '8rem',        // 128px
        '36': '9rem',        // 144px
        '40': '10rem',       // 160px
        '44': '11rem',       // 176px
        '48': '12rem',       // 192px
        '52': '13rem',       // 208px
        '56': '14rem',       // 224px
        '60': '15rem',       // 240px
        '64': '16rem',       // 256px
        '72': '18rem',       // 288px
        '80': '20rem',       // 320px
        '96': '24rem',       // 384px
      },

      // =====================
      // CONTAINER SETTINGS
      // =====================
      container: {
        center: true,
        padding: {
          DEFAULT: '1rem',
          sm: '2rem',
          lg: '4rem',
          xl: '5rem',
          '2xl': '6rem',
        },
        screens: {
          sm: '640px',
          md: '768px',
          lg: '1024px',
          xl: '1280px',
          '2xl': '1536px',
        },
      },

      // =====================
      // BORDER RADIUS
      // =====================
      borderRadius: {
        none: '0',
        sm: '0.125rem',
        DEFAULT: '0.25rem',
        md: '0.375rem',
        lg: '0.5rem',
        xl: '0.75rem',
        '2xl': '1rem',
        '3xl': '1.5rem',
        full: '9999px',
      },

      // =====================
      // BOX SHADOWS
      // =====================
      boxShadow: {
        sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
        DEFAULT: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
        md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
        lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
        xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
        '2xl': '0 25px 50px -12px rgb(0 0 0 / 0.25)',
        inner: 'inset 0 2px 4px 0 rgb(0 0 0 / 0.05)',
        // Component-specific shadows
        card: '0 2px 8px 0 rgb(0 0 0 / 0.08)',
        dropdown: '0 4px 12px 0 rgb(0 0 0 / 0.15)',
        modal: '0 20px 60px 0 rgb(0 0 0 / 0.3)',
        tooltip: '0 2px 8px 0 rgb(0 0 0 / 0.15)',
        navbar: '0 2px 4px 0 rgb(0 0 0 / 0.06)',
      },

      // =====================
      // BREAKPOINTS (Mobile-First)
      // =====================
      screens: {
        sm: '640px',
        md: '768px',
        lg: '1024px',
        xl: '1280px',
        '2xl': '1536px',
      },

      // =====================
      // Z-INDEX SCALE
      // =====================
      zIndex: {
        auto: 'auto',
        '0': '0',
        '10': '10',
        '20': '20',
        '30': '30',
        '40': '40',
        '50': '50',
        '75': '75',
        '100': '100',
        dropdown: '1000',
        sticky: '1020',
        fixed: '1030',
        modalBackdrop: '1040',
        modal: '1050',
        popover: '1060',
        tooltip: '1070',
        toast: '1080',
      },

      // =====================
      // ANIMATION
      // =====================
      extend: {
        animation: {
          'fade-in': 'fadeIn 0.3s ease-in-out',
          'fade-out': 'fadeOut 0.3s ease-in-out',
          'slide-in': 'slideIn 0.3s ease-out',
          'slide-out': 'slideOut 0.3s ease-in',
          'scale-in': 'scaleIn 0.2s ease-out',
          'spin-slow': 'spin 2s linear infinite',
          'bounce-slow': 'bounce 1.5s infinite',
          'pulse-slow': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        },
        keyframes: {
          fadeIn: {
            '0%': { opacity: '0' },
            '100%': { opacity: '1' },
          },
          fadeOut: {
            '0%': { opacity: '1' },
            '100%': { opacity: '0' },
          },
          slideIn: {
            '0%': { transform: 'translateY(-10px)', opacity: '0' },
            '100%': { transform: 'translateY(0)', opacity: '1' },
          },
          slideOut: {
            '0%': { transform: 'translateY(0)', opacity: '1' },
            '100%': { transform: 'translateY(-10px)', opacity: '0' },
          },
          scaleIn: {
            '0%': { transform: 'scale(0.95)', opacity: '0' },
            '100%': { transform: 'scale(1)', opacity: '1' },
          },
        },
      },

      // =====================
      // RTL SUPPORT
      // =====================
      extend: {
        // RTL-aware spacing will be handled by logical properties
        // margin-inline-start, margin-inline-end, etc.
      },
    },
  },
  plugins: [
    // Add any Tailwind plugins here
    // require('@tailwindcss/forms'),
    // require('@tailwindcss/typography'),
    // require('@tailwindcss/aspect-ratio'),
  ],
}

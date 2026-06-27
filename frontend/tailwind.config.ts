import type { Config } from 'tailwindcss';

const config: Config = {
  darkMode: ['class', '[data-theme="dark"]'],
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}', './features/**/*.{ts,tsx}', './lib/**/*.{ts,tsx}', './styles/**/*.{ts,tsx}'],
  theme: {
    container: {
      center: true,
      padding: '1.5rem',
      screens: {
        '2xl': '1440px',
      },
    },
    extend: {
      colors: {
        background: 'var(--color-background)',
        sidebar: 'var(--color-sidebar)',
        card: 'var(--color-card)',
        panel: 'var(--color-panel)',
        border: 'var(--color-border)',
        'text-primary': 'var(--color-text-primary)',
        'text-secondary': 'var(--color-text-secondary)',
        'brand-primary': 'var(--color-brand-primary)',
        'brand-primary-hover': 'var(--color-brand-primary-hover)',
        success: 'var(--color-status-success)',
        warning: 'var(--color-status-warning)',
        danger: 'var(--color-status-danger)',
        info: 'var(--color-status-info)',
        neutral: 'var(--color-neutral)',
      },
      borderRadius: {
        button: 'var(--radius-button)',
        card: 'var(--radius-card)',
        dialog: 'var(--radius-dialog)',
        panel: 'var(--radius-panel)',
        input: 'var(--radius-input)',
      },
      boxShadow: {
        sm: 'var(--shadow-sm)',
        md: 'var(--shadow-md)',
        lg: 'var(--shadow-lg)',
        focus: 'var(--shadow-focus)',
      },
      spacing: {
        4: 'var(--space-4)',
        8: 'var(--space-8)',
        12: 'var(--space-12)',
        16: 'var(--space-16)',
        24: 'var(--space-24)',
        32: 'var(--space-32)',
        48: 'var(--space-48)',
        64: 'var(--space-64)',
      },
      transitionDuration: {
        200: '200ms',
      },
      keyframes: {
        fadeIn: {
          from: { opacity: '0' },
          to: { opacity: '1' },
        },
        expand: {
          from: { opacity: '0', transform: 'scale(0.98)' },
          to: { opacity: '1', transform: 'scale(1)' },
        },
      },
      animation: {
        fadeIn: 'fadeIn 200ms ease-out',
        expand: 'expand 200ms ease-out',
      },
    },
  },
  plugins: [],
};

export default config;

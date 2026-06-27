export const typography = {
  fontFamily: {
    sans: 'Inter, system-ui, sans-serif',
    mono: 'JetBrains Mono, ui-monospace, SFMono-Regular, monospace',
  },
  fontSize: {
    h1: ['2.5rem', { lineHeight: '3rem', fontWeight: '600' }],
    h2: ['2rem', { lineHeight: '2.5rem', fontWeight: '600' }],
    h3: ['1.5rem', { lineHeight: '2rem', fontWeight: '600' }],
    h4: ['1.25rem', { lineHeight: '1.75rem', fontWeight: '600' }],
    bodyLarge: ['1rem', { lineHeight: '1.5rem' }],
    body: ['0.875rem', { lineHeight: '1.375rem' }],
    caption: ['0.75rem', { lineHeight: '1rem' }],
    button: ['0.875rem', { lineHeight: '1.25rem', fontWeight: '500' }],
    code: ['0.8125rem', { lineHeight: '1.25rem' }],
  },
} as const;

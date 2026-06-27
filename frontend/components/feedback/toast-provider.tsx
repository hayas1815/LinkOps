'use client';

import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from 'react';

import type { ToastItem, ToastVariant } from '@/components/feedback/toast';
import { ToastMessage } from '@/components/feedback/toast';

type ToastInput = {
  title: string;
  description?: string;
  variant: ToastVariant;
};

type ToastContextValue = {
  notify: (input: ToastInput) => void;
};

const ToastContext = createContext<ToastContextValue | null>(null);

export function ToastProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<ToastItem[]>([]);

  const notify = useCallback((input: ToastInput) => {
    const id = `toast-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    const next: ToastItem = { id, ...input };
    setItems((previous) => [...previous, next]);

    window.setTimeout(() => {
      setItems((previous) => previous.filter((item) => item.id !== id));
    }, 2600);
  }, []);

  const value = useMemo(() => ({ notify }), [notify]);

  return (
    <ToastContext.Provider value={value}>
      {children}
      <section className="pointer-events-none fixed bottom-5 right-5 z-[60] flex w-[22rem] flex-col gap-3">
        {items.map((item) => (
          <ToastMessage key={item.id} item={item} />
        ))}
      </section>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within ToastProvider');
  }
  return context;
}

'use client';

import type { ErrorInfo, ReactNode } from 'react';
import { Component } from 'react';

import { ErrorState } from '@/components/feedback/error-state';

type Props = {
  children: ReactNode;
};

type State = {
  hasError: boolean;
};

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
  };

  public static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary captured an error', error, errorInfo);
  }

  private handleReset = () => {
    this.setState({ hasError: false });
  };

  public render() {
    if (this.state.hasError) {
      return (
        <ErrorState
          title="Unexpected UI error"
          description="A rendering issue occurred in this view."
          actionLabel="Reset view"
          onAction={this.handleReset}
        />
      );
    }

    return this.props.children;
  }
}

// This file provides TypeScript type definitions for our test environment

// Tell TypeScript about the global Jest functions
declare var describe: jest.Describe;
declare var it: jest.It;
declare var expect: jest.Expect;
declare var beforeAll: jest.Lifecycle;
declare var afterAll: jest.Lifecycle;
declare var beforeEach: jest.Lifecycle;
declare var afterEach: jest.Lifecycle;
declare var jest: any; // Use 'any' as a fallback for jest global

// Augment the global namespace to include our custom test utilities
declare namespace NodeJS {
  interface Global {
    __NEXT_DATA__: any;
  }
}

// Mock module declarations
declare module 'next/router' {
  const useRouter: () => any;
  export { useRouter };
}

declare module '@/components/DAGRunStatus' {
  const DAGRunStatus: React.ComponentType<{ dagRun: any }>;
  export default DAGRunStatus;
}

declare module '@/components/ErrorBoundary' {
  const ErrorBoundary: React.ComponentType<{ children: React.ReactNode }>;
  export default ErrorBoundary;
}

declare module '@/lib/types' {
  export function generateMockDAGRun(): Promise<any>;
}

declare module '@/pages/dag/[runId]' {
  const DAGRunPage: React.ComponentType;
  export default DAGRunPage;
}

// Add type definitions for testing-library/jest-dom
import '@testing-library/jest-dom';

// Add type definitions for Jest DOM matchers
declare global {
  namespace jest {
    interface Matchers<R> {
      toBeInTheDocument(): R;
      toBeVisible(): R;
      toHaveClass(...classNames: string[]): R;
      // Add other matchers as needed
    }
  }
}

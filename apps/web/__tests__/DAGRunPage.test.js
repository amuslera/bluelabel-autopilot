// Simple test file for DAGRunPage component
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';

// Mock the DAGRunStatus component
jest.mock('@/components/DAGRunStatus', () => {
  return function MockDAGRunStatus({ dagRun }) {
    return <div data-testid="mock-dag-run-status">{dagRun.dagId} - {dagRun.runId}</div>;
  };
});

// Mock the ErrorBoundary component
jest.mock('@/components/ErrorBoundary', () => {
  return function MockErrorBoundary({ children }) {
    return <div data-testid="mock-error-boundary">{children}</div>;
  };
});

// Mock the generateMockDAGRun function
const mockGenerateDAGRun = jest.fn();
jest.mock('@/lib/types', () => ({
  generateMockDAGRun: mockGenerateDAGRun,
}));

// Mock next/router
const mockPush = jest.fn();
const mockRouter = {
  push: mockPush,
  query: { runId: 'test-run-123' },
  pathname: '/dag/test-run-123',
};
jest.mock('next/router', () => ({
  useRouter: () => mockRouter,
}));

// Import the component after setting up mocks
import DAGRunPage from '@/pages/dag/[runId]';

describe('DAGRunPage', () => {
  const mockDAGRun = {
    id: 'test-run-123',
    dagId: 'example_dag',
    runId: 'test-run-123',
    status: 'running',
    startDate: new Date().toISOString(),
    endDate: null,
    executionDate: new Date().toISOString(),
    steps: [
      { id: 'step1', name: 'Step 1', status: 'success' },
      { id: 'step2', name: 'Step 2', status: 'running' },
      { id: 'step3', name: 'Step 3', status: 'pending' },
    ],
  };

  beforeEach(() => {
    // Reset all mocks before each test
    jest.clearAllMocks();
    
    // Mock the generate function to return our test data
    mockGenerateDAGRun.mockResolvedValue(mockDAGRun);
  });

  it('renders loading state initially', async () => {
    // Render the component
    render(<DAGRunPage />);
    
    // Check for loading state
    const loadingSpinner = document.querySelector('.animate-spin');
    expect(loadingSpinner).toBeInTheDocument();
    
    // Wait for the component to finish loading
    await waitFor(() => {
      expect(mockGenerateDAGRun).toHaveBeenCalled();
    });
  });

  it('displays DAG run details after loading', async () => {
    // Render the component
    render(<DAGRunPage />);
    
    // Wait for the component to finish loading and check for content
    await waitFor(() => {
      expect(screen.getByText(mockDAGRun.runId)).toBeInTheDocument();
      expect(screen.getByText(new RegExp(mockDAGRun.status, 'i'))).toBeInTheDocument();
    });
  });

  it('handles missing runId', async () => {
    // Mock useRouter to return empty query
    jest.spyOn(require('next/router'), 'useRouter').mockImplementationOnce(() => ({
      ...mockRouter,
      query: {},
    }));

    render(<DAGRunPage />);
    
    // The component should not try to fetch data when runId is missing
    await waitFor(() => {
      expect(mockGenerateDAGRun).not.toHaveBeenCalled();
    });
  });
});

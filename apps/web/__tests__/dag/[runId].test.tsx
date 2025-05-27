import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import { useRouter } from 'next/router';
import DAGRunPage from '@/pages/dag/[runId]';
import { DAGRun } from '@/lib/types';

// Mock the console.error to avoid polluting test output
const originalError = console.error;
beforeAll(() => {
  console.error = jest.fn();
});

afterAll(() => {
  console.error = originalError;
});

// Mock the useRouter hook
jest.mock('next/router', () => ({
  useRouter: jest.fn(),
}));

// Mock the DAGRunStatus component
jest.mock('@/components/DAGRunStatus', () => ({
  __esModule: true,
  default: ({ dagRun }: { dagRun: DAGRun }) => (
    <div data-testid="dag-run-status">
      {dagRun.dagId} - {dagRun.runId}
    </div>
  ),
}));

describe('DAGRunPage', () => {
  const mockPush = jest.fn();
  const mockBack = jest.fn();

  beforeEach(() => {
    // Reset all mocks before each test
    jest.clearAllMocks();
    
    // Setup the router mock
    (useRouter as jest.Mock).mockImplementation(() => ({
      query: { runId: 'test-run-123' },
      push: mockPush,
      back: mockBack,
    }));
  });

  it('renders loading state initially', () => {
    render(<DAGRunPage />);
    expect(screen.getByText('Loading DAG run details...')).toBeInTheDocument();
  });

  it('displays DAG run data after loading', async () => {
    render(<DAGRunPage />);
    
    // Wait for the loading to complete
    await waitFor(() => {
      expect(screen.getByTestId('dag-run-status')).toBeInTheDocument();
    });
    
    expect(screen.getByText('example_dag - test-run-123')).toBeInTheDocument();
  });

  it('handles missing runId', () => {
    (useRouter as jest.Mock).mockImplementationOnce(() => ({
      query: {},
      push: mockPush,
      back: mockBack,
    }));
    
    render(<DAGRunPage />);
    expect(screen.getByText('No runId, skipping fetch')).toBeInTheDocument();
  });
});

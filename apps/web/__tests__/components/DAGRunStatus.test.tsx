import React from 'react';
import { render, screen } from '@testing-library/react';
import DAGRunStatus from '../../components/DAGRunStatus';
import { useDAGRun, useDAGRunSteps, useDAGRunUpdates } from '../../lib/api/hooks';

// Mock the hooks
jest.mock('../../lib/api/hooks', () => ({
  useDAGRun: jest.fn(),
  useDAGRunSteps: jest.fn(),
  useDAGRunUpdates: jest.fn()
}));

describe('DAGRunStatus', () => {
  const mockDagRun = {
    dag_id: 'test',
    run_id: 'test-run',
    status: 'running',
    start_date: new Date().toISOString(),
    end_date: null,
    execution_date: new Date().toISOString()
  };

  const mockSteps = [
    {
      step_id: 'step1',
      task_id: 'task1',
      status: 'running',
      start_time: new Date().toISOString(),
      end_time: null,
      retry_count: 0
    }
  ];

  beforeEach(() => {
    (useDAGRun as jest.Mock).mockReturnValue({
      data: mockDagRun,
      error: null,
      isLoading: false
    });
    (useDAGRunSteps as jest.Mock).mockReturnValue({
      data: mockSteps,
      error: null
    });
    (useDAGRunUpdates as jest.Mock).mockReturnValue({
      status: null,
      steps: null,
      error: null
    });
  });

  it('renders the component with real data', () => {
    render(<DAGRunStatus dagId="test" runId="test-run" />);
    expect(screen.getByText('DAG Run Status')).toBeInTheDocument();
    expect(screen.getByText('Run ID: test-run')).toBeInTheDocument();
  });

  it('displays step information correctly', () => {
    render(<DAGRunStatus dagId="test" runId="test-run" />);
    expect(screen.getByText('step1')).toBeInTheDocument();
    expect(screen.getByText('task1')).toBeInTheDocument();
    expect(screen.getByText('running')).toBeInTheDocument();
  });

  it('shows loading state', () => {
    (useDAGRun as jest.Mock).mockReturnValue({
      data: null,
      error: null,
      isLoading: true
    });
    render(<DAGRunStatus dagId="test" runId="test-run" />);
    expect(screen.getByText('Loading DAG run...')).toBeInTheDocument();
  });

  it('shows error state', () => {
    (useDAGRun as jest.Mock).mockReturnValue({
      data: null,
      error: new Error('Failed to load DAG run'),
      isLoading: false
    });
    render(<DAGRunStatus dagId="test" runId="test-run" />);
    expect(screen.getByText('Error: Failed to load DAG run')).toBeInTheDocument();
  });

  it('updates with real-time data', () => {
    render(<DAGRunStatus dagId="test" runId="test-run" />);
    
    // Simulate real-time update
    (useDAGRunUpdates as jest.Mock).mockReturnValue({
      status: 'completed',
      steps: [{
        ...mockSteps[0],
        status: 'completed',
        end_time: new Date().toISOString()
      }],
      error: null
    });

    // Re-render to apply updates
    render(<DAGRunStatus dagId="test" runId="test-run" />);
    expect(screen.getByText('completed')).toBeInTheDocument();
  });
});

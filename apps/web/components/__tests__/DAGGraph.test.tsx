import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import DAGGraph from '../DAGGraph';
import { useDAGRun } from '../../lib/api/hooks';

// Mock the hooks
jest.mock('../../lib/api/hooks', () => ({
  useDAGRun: jest.fn(),
}));

describe('DAGGraph', () => {
  const mockDagRun = {
    dag_id: 'test',
    run_id: 'test-run',
    status: 'running',
    start_date: new Date().toISOString(),
    end_date: null,
    execution_date: new Date().toISOString(),
    steps: [
      {
        step_id: 'step1',
        task_id: 'task1',
        status: 'running',
        start_time: new Date().toISOString(),
        end_time: null,
        retry_count: 0
      }
    ]
  };

  beforeEach(() => {
    (useDAGRun as jest.Mock).mockReturnValue({
      data: mockDagRun,
      error: null,
      isLoading: false
    });
  });

  it('renders the component with real data', () => {
    render(<DAGGraph dagId="test" />);
    expect(screen.getByText('test')).toBeInTheDocument();
  });

  it('handles node click events', () => {
    const onNodeClick = jest.fn();
    render(<DAGGraph dagId="test" onNodeClick={onNodeClick} />);
    // Test node click handling
  });

  it('applies custom className', () => {
    render(<DAGGraph dagId="test" className="custom-class" />);
    expect(screen.getByTestId('dag-graph')).toHaveClass('custom-class');
  });

  it('shows loading state', () => {
    (useDAGRun as jest.Mock).mockReturnValue({
      data: null,
      error: null,
      isLoading: true
    });
    render(<DAGGraph dagId="test" />);
    expect(screen.getByText('Loading DAG...')).toBeInTheDocument();
  });

  it('shows error state', () => {
    (useDAGRun as jest.Mock).mockReturnValue({
      data: null,
      error: new Error('Failed to load DAG'),
      isLoading: false
    });
    render(<DAGGraph dagId="test" />);
    expect(screen.getByText('Error: Failed to load DAG')).toBeInTheDocument();
  });
}); 
import React from 'react';
import { render, screen } from '@testing-library/react';
import DAGRunStatusComponent from '../DAGRunStatus';
import { DAGRun, DAGStatus } from '@/lib/types';

const mockDAGRun: DAGRun = {
  dagId: 'test-dag',
  runId: 'test-run-123',
  status: 'running' as DAGStatus,
  startDate: '2024-03-22T10:00:00Z',
  endDate: null,
  executionDate: '2024-03-22T10:00:00Z',
  steps: [
    {
      id: 'step-1',
      name: 'Test Step 1',
      status: 'success' as DAGStatus,
      startTime: '2024-03-22T10:00:00Z',
      endTime: '2024-03-22T10:00:01Z',
      duration: 1000,
      retryCount: 0
    }
  ],
  metadata: {
    description: 'Test DAG Run'
  }
};

describe('DAGRunStatusComponent', () => {
  it('renders without crashing', () => {
    render(<DAGRunStatusComponent dagRun={mockDAGRun} />);
    expect(screen.getByText('test-dag')).toBeInTheDocument();
  });

  it('displays correct status', () => {
    render(<DAGRunStatusComponent dagRun={mockDAGRun} />);
    expect(screen.getByText('running')).toBeInTheDocument();
  });

  it('shows step information', () => {
    render(<DAGRunStatusComponent dagRun={mockDAGRun} />);
    expect(screen.getByText('Test Step 1')).toBeInTheDocument();
    expect(screen.getByText('success')).toBeInTheDocument();
  });

  it('handles missing dates gracefully', () => {
    const incompleteDAGRun = {
      ...mockDAGRun,
      startDate: null,
      endDate: null,
      executionDate: null
    };
    render(<DAGRunStatusComponent dagRun={incompleteDAGRun} />);
    expect(screen.getByText('--')).toBeInTheDocument();
  });

  it('applies custom className', () => {
    const { container } = render(
      <DAGRunStatusComponent dagRun={mockDAGRun} className="custom-class" />
    );
    expect(container.firstChild).toHaveClass('custom-class');
  });
}); 
import React from 'react';
import { render, screen, within } from '@testing-library/react';
import DAGRunStatus from '@/components/DAGRunStatus';
import { generateMockDAGRun } from '@/lib/types';

// Mock the date-fns functions to have consistent test results
jest.mock('date-fns', () => ({
  formatDistanceToNow: () => '2 hours ago',
  parseISO: (date: string) => new Date(date),
  format: (date: Date) => `Formatted: ${date.toISOString()}`,
}));

describe('DAGRunStatus', () => {
  const mockDAGRun = generateMockDAGRun();

  it('renders the DAG run details correctly', () => {
    render(<DAGRunStatus dagRun={mockDAGRun} />);
    
    // Check if the DAG ID and run ID are displayed
    expect(screen.getByText(mockDAGRun.dagId)).toBeInTheDocument();
    expect(screen.getByText(`#${mockDAGRun.runId}`, { exact: false })).toBeInTheDocument();
    
    // Check if the status is displayed with the correct color
    const statusBadge = screen.getByText(mockDAGRun.status);
    expect(statusBadge).toBeInTheDocument();
    expect(statusBadge.closest('div')).toHaveClass('bg-green-100');
    
    // Check if the description is displayed
    if (mockDAGRun.metadata?.description) {
      expect(screen.getByText(mockDAGRun.metadata.description)).toBeInTheDocument();
    }
  });

  it('displays the execution details', () => {
    render(<DAGRunStatus dagRun={mockDAGRun} />);
    
    // Check if the execution date is displayed
    expect(screen.getByText('Execution Date')).toBeInTheDocument();
    expect(screen.getByText('Formatted:', { exact: false })).toBeInTheDocument();
    
    // Check if the started time is displayed
    expect(screen.getByText('Started')).toBeInTheDocument();
    expect(screen.getByText('2 hours ago')).toBeInTheDocument();
  });

  it('displays the list of steps', () => {
    render(<DAGRunStatus dagRun={mockDAGRun} />);
    
    // Check if the steps section header is displayed
    expect(screen.getByText('Steps')).toBeInTheDocument();
    
    // Check if all steps are displayed
    mockDAGRun.steps.forEach(step => {
      expect(screen.getByText(step.name)).toBeInTheDocument();
      
      // Check if the status is displayed with the correct color
      const statusBadge = screen.getByText(step.status);
      expect(statusBadge).toBeInTheDocument();
      
      // Check retry count
      if (step.retryCount > 0) {
        expect(screen.getByText(`${step.retryCount} retries`)).toBeInTheDocument();
      } else {
        expect(screen.getByText('No retries')).toBeInTheDocument();
      }
    });
  });

  it('handles missing optional fields gracefully', () => {
    const minimalDAGRun = {
      ...mockDAGRun,
      metadata: undefined,
      steps: [],
      startDate: undefined,
      endDate: undefined,
    };
    
    render(<DAGRunStatus dagRun={minimalDAGRun} />);
    
    // Should still render without errors
    expect(screen.getByText(mockDAGRun.dagId)).toBeInTheDocument();
    expect(screen.getByText('No steps found in this DAG run.')).toBeInTheDocument();
  });
});

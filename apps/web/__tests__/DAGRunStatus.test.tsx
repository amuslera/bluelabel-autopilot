import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import DAGRunStatus from '../components/DAGRunStatus';
import { generateMockDAGRun } from '@/lib/types';

describe('DAGRunStatus', () => {
  const mockDagRun = generateMockDAGRun();

  it('renders the DAG run status with steps', () => {
    render(<DAGRunStatus dagRun={mockDagRun} />);
    
    // Check if the main title is rendered
    expect(screen.getByText(mockDagRun.dagId)).toBeInTheDocument();
    
    // Check if the run ID is rendered
    expect(screen.getByText(`#${mockDagRun.runId}`)).toBeInTheDocument();
    
    // Check if all steps are rendered
    mockDagRun.steps.forEach(step => {
      expect(screen.getByText(step.name)).toBeInTheDocument();
    });
  });

  it('expands step details when a step with output is clicked', () => {
    render(<DAGRunStatus dagRun={mockDagRun} />);
    
    // Find a step with output and click it
    const stepWithOutput = mockDagRun.steps.find(step => step.output);
    if (stepWithOutput) {
      const stepElement = screen.getByText(stepWithOutput.name).closest('div[class*="border-b"]');
      if (stepElement) {
        fireEvent.click(stepElement);
        
        // Check if the output content is visible
        if (stepWithOutput.output) {
          expect(screen.getByText(stepWithOutput.output.content.substring(0, 20))).toBeInTheDocument();
        }
      }
    }
  });

  it('displays the correct status for each step', () => {
    render(<DAGRunStatus dagRun={mockDagRun} />);
    
    mockDagRun.steps.forEach(step => {
      const statusElement = screen.getByText(step.status);
      expect(statusElement).toBeInTheDocument();
      expect(statusElement).toHaveClass('capitalize');
    });
  });
});

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import DAGStepOutput from '@/components/DAGStepOutput';
import { DAGStep } from '@/lib/types';

describe('DAGStepOutput', () => {
  const mockStep: DAGStep = {
    id: 'test-step',
    name: 'Test Step',
    status: 'success',
    startTime: new Date().toISOString(),
    endTime: new Date(Date.now() + 1000).toISOString(),
    duration: 1000,
    retryCount: 0,
    output: {
      type: 'text',
      content: 'Test output content',
      timestamp: new Date().toISOString(),
    },
  };

  it('renders step output when expanded', () => {
    render(<DAGStepOutput step={mockStep} />);
    
    // Click to expand
    fireEvent.click(screen.getByText('Step Output'));
    
    expect(screen.getByText('Test output content')).toBeInTheDocument();
    expect(screen.getByTitle('Copy to clipboard')).toBeInTheDocument();
  });

  it('shows error output when step has error', () => {
    const errorStep: DAGStep = {
      ...mockStep,
      status: 'failed',
      error: 'Test error message',
      output: {
        type: 'error',
        content: 'Test error message',
        timestamp: new Date().toISOString(),
      },
    };

    render(<DAGStepOutput step={errorStep} />);
    
    // Click to expand
    fireEvent.click(screen.getByText('Error Details'));
    
    expect(screen.getByText('Test error message')).toBeInTheDocument();
    expect(screen.getByTitle('Copy to clipboard')).toBeInTheDocument();
  });

  it('shows file information for file type output', () => {
    const fileStep: DAGStep = {
      ...mockStep,
      output: {
        type: 'file',
        content: 'test-file.csv',
        size: '1.2 MB',
        timestamp: new Date().toISOString(),
      },
    };

    render(<DAGStepOutput step={fileStep} />);
    
    // Click to expand
    fireEvent.click(screen.getByText('Step Output'));
    
    expect(screen.getByText('test-file.csv')).toBeInTheDocument();
    expect(screen.getByText('(1.2 MB)')).toBeInTheDocument();
    expect(screen.getByTitle('Download file')).toBeInTheDocument();
  });

  it('copies content to clipboard when copy button is clicked', () => {
    const writeTextMock = jest.fn();
    Object.assign(navigator, {
      clipboard: {
        writeText: writeTextMock,
      },
    });

    render(<DAGStepOutput step={mockStep} />);
    
    // Click to expand and then click copy
    fireEvent.click(screen.getByText('Step Output'));
    fireEvent.click(screen.getByTitle('Copy to clipboard'));
    
    expect(writeTextMock).toHaveBeenCalledWith('Test output content');
  });
});

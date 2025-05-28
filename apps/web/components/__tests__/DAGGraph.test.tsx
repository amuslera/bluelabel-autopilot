import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import DAGGraph from '../DAGGraph';
import { mockDagRun } from '../../__mocks__/mockDagRun';

// Mock reactflow to avoid canvas issues in tests
jest.mock('reactflow', () => ({
  __esModule: true,
  default: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="react-flow">{children}</div>
  ),
  Background: () => <div data-testid="background" />,
  Controls: () => <div data-testid="controls" />,
  MiniMap: () => <div data-testid="minimap" />,
  useNodesState: () => [[], jest.fn(), jest.fn()],
  useEdgesState: () => [[], jest.fn(), jest.fn()],
}));

describe('DAGGraph', () => {
  it('renders the component with mock data', () => {
    render(<DAGGraph dagRun={mockDagRun} />);
    expect(screen.getByTestId('react-flow')).toBeInTheDocument();
    expect(screen.getByTestId('background')).toBeInTheDocument();
    expect(screen.getByTestId('controls')).toBeInTheDocument();
    expect(screen.getByTestId('minimap')).toBeInTheDocument();
  });

  it('handles node click events', () => {
    const onNodeClick = jest.fn();
    render(<DAGGraph dagRun={mockDagRun} onNodeClick={onNodeClick} />);
    
    // Simulate node click
    fireEvent.click(screen.getByTestId('react-flow'));
    expect(onNodeClick).toHaveBeenCalled();
  });

  it('applies custom className', () => {
    const { container } = render(
      <DAGGraph dagRun={mockDagRun} className="custom-class" />
    );
    expect(container.firstChild).toHaveClass('custom-class');
  });

  it('renders with error state', () => {
    const errorDagRun = {
      ...mockDagRun,
      steps: [
        {
          id: 'error-step',
          status: 'FAILED',
          error: 'Test error',
          dependencies: [],
        },
      ],
    };
    render(<DAGGraph dagRun={errorDagRun} />);
    expect(screen.getByTestId('react-flow')).toBeInTheDocument();
  });
}); 
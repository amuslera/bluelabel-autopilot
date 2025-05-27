import { render, screen, waitFor } from '@testing-library/react';
import { useRouter } from 'next/router';
import DAGRunPage from '@/pages/dag/[runId]';
import { generateMockDAGRun } from '@/lib/types';

// Mock the DAGRunStatus component
jest.mock('@/components/DAGRunStatus', () => {
  return function MockDAGRunStatus({ dagRun }: { dagRun: any }) {
    return (
      <div data-testid="mock-dag-run-status">
        {dagRun.dagId} - {dagRun.status}
      </div>
    );
  };
});

// Mock next/head
jest.mock('next/head', () => {
  return {
    __esModule: true,
    default: function Head({ children }: { children: React.ReactNode }) {
      return <>{children}</>;
    },
  };
});

describe('DAGRunPage', () => {
  const mockPush = jest.fn();
  const mockBack = jest.fn();
  
  beforeEach(() => {
    // Reset all mocks before each test
    jest.clearAllMocks();
    
    // Setup the mock router
    (useRouter as jest.Mock).mockReturnValue({
      query: { runId: 'test-run-123' },
      push: mockPush,
      back: mockBack,
    });
    
    // Mock the global fetch
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(generateMockDAGRun({ id: 'test-run-123' })),
      })
    ) as jest.Mock;
  });
  
  it('displays loading state initially', async () => {
    render(<DAGRunPage />);
    
    // Should show loading indicator
    expect(screen.getByText('Loading DAG run details...')).toBeInTheDocument();
    
    // Should eventually load the DAG run
    await waitFor(() => {
      expect(screen.getByTestId('mock-dag-run-status')).toBeInTheDocument();
    });
  });
  
  it('displays error message when fetch fails', async () => {
    // Mock a failed fetch
    (global.fetch as jest.Mock).mockImplementationOnce(() =>
      Promise.reject(new Error('Failed to fetch'))
    );
    
    render(<DAGRunPage />);
    
    // Should show error message
    await waitFor(() => {
      expect(screen.getByText('Failed to load DAG run. Please try again later.')).toBeInTheDocument();
    });
    
    // Should not show DAG run status
    expect(screen.queryByTestId('mock-dag-run-status')).not.toBeInTheDocument();
  });
  
  it('navigates back when back button is clicked', async () => {
    render(<DAGRunPage />);
    
    // Wait for the component to load
    await waitFor(() => {
      expect(screen.getByTestId('mock-dag-run-status')).toBeInTheDocument();
    });
    
    // Click the back button
    const backButton = screen.getByRole('button', { name: /back to dag runs/i });
    backButton.click();
    
    // Should call router.back()
    expect(mockBack).toHaveBeenCalled();
  });
  
  it('displays not found message when DAG run is not found', async () => {
    // Mock a 404 response
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 404,
      json: () => Promise.resolve(null),
    });
    
    render(<DAGRunPage />);
    
    // Wait for loading to complete and not found message to appear
    const notFoundMessage = await screen.findByText(/no dag run found with id/i);
    expect(notFoundMessage).toBeInTheDocument();
    
    // Should not show DAG run status
    expect(screen.queryByTestId('mock-dag-run-status')).not.toBeInTheDocument();
  });
});

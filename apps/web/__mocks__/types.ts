import { DAGRun } from '@/lib/types';

export function generateMockDAGRun(): Promise<DAGRun> {
  return Promise.resolve({
    id: 'mock-run-123',
    dagId: 'mock_dag',
    runId: 'mock-run-123',
    status: 'running',
    startDate: new Date().toISOString(),
    endDate: undefined, // Changed from null to undefined to match DAGRun type
    executionDate: new Date().toISOString(),
    steps: [
      { id: 'step1', name: 'Mock Step 1', status: 'success' },
      { id: 'step2', name: 'Mock Step 2', status: 'running' },
      { id: 'step3', name: 'Mock Step 3', status: 'pending' },
    ],
  } as DAGRun); // Type assertion to ensure compatibility
}

export * from '@/lib/types';

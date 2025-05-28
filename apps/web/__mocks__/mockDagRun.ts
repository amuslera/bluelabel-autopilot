import { DAGRun } from '../types/dag';

export const mockDagRun: DAGRun = {
  id: 'dag-run-123',
  status: 'RUNNING',
  startedAt: '2025-05-27T12:00:00Z',
  steps: [
    {
      id: 'fetch-data',
      status: 'SUCCESS',
      duration: 1200,
      dependencies: [],
    },
    {
      id: 'process-data',
      status: 'RUNNING',
      duration: 800,
      dependencies: ['fetch-data'],
    },
    {
      id: 'validate',
      status: 'PENDING',
      dependencies: ['process-data'],
    },
    {
      id: 'save-results',
      status: 'PENDING',
      dependencies: ['validate'],
    },
    {
      id: 'notify',
      status: 'PENDING',
      dependencies: ['save-results'],
    },
  ],
  metadata: {
    workflow: 'sample-workflow',
    version: '1.0.0',
  },
}; 
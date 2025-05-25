/**
 * Types for DAG (Directed Acyclic Graph) Run Status Viewer
 */

export type DAGStatus = 
  | 'pending'
  | 'running'
  | 'success'
  | 'failed'
  | 'skipped';

export interface DAGStep {
  id: string;
  name: string;
  status: DAGStatus;
  startTime?: string; // ISO string
  endTime?: string;   // ISO string
  duration?: number;  // in milliseconds
  retryCount: number;
  error?: string;
  metadata?: Record<string, unknown>;
}

export interface DAGRun {
  id: string;
  dagId: string;
  runId: string;
  executionDate: string; // ISO string
  startDate?: string;    // ISO string
  endDate?: string;      // ISO string
  status: DAGStatus;
  conf?: Record<string, unknown>;
  steps: DAGStep[];
  metadata?: {
    owner?: string;
    description?: string;
    tags?: string[];
  };
}

// Mock data generator for development
export function generateMockDAGRun(overrides: Partial<DAGRun> = {}): DAGRun {
  const now = new Date();
  const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000);
  const thirtyMinutesAgo = new Date(now.getTime() - 30 * 60 * 1000);

  const defaultRun: DAGRun = {
    id: 'run-12345',
    dagId: 'example_dag',
    runId: 'manual__2023-01-01T00:00:00+00:00',
    executionDate: oneHourAgo.toISOString(),
    startDate: oneHourAgo.toISOString(),
    endDate: now.toISOString(),
    status: 'success',
    conf: {
      param1: 'value1',
      param2: 'value2',
    },
    steps: [
      {
        id: 'extract_data',
        name: 'Extract Data',
        status: 'success',
        startTime: oneHourAgo.toISOString(),
        endTime: new Date(oneHourAgo.getTime() + 5 * 60 * 1000).toISOString(),
        duration: 5 * 60 * 1000,
        retryCount: 0,
      },
      {
        id: 'transform_data',
        name: 'Transform Data',
        status: 'success',
        startTime: new Date(oneHourAgo.getTime() + 5 * 60 * 1000).toISOString(),
        endTime: new Date(oneHourAgo.getTime() + 15 * 60 * 1000).toISOString(),
        duration: 10 * 60 * 1000,
        retryCount: 1,
      },
      {
        id: 'load_data',
        name: 'Load Data',
        status: 'running',
        startTime: new Date(oneHourAgo.getTime() + 15 * 60 * 1000).toISOString(),
        endTime: undefined,
        duration: undefined,
        retryCount: 0,
      },
      {
        id: 'send_notifications',
        name: 'Send Notifications',
        status: 'pending',
        startTime: undefined,
        endTime: undefined,
        duration: undefined,
        retryCount: 0,
      },
    ],
    metadata: {
      owner: 'data_team',
      description: 'Example DAG for data pipeline',
      tags: ['example', 'data-pipeline'],
    },
  };

  return { ...defaultRun, ...overrides };
}

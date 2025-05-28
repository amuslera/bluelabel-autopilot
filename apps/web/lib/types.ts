/**
 * Types for DAG (Directed Acyclic Graph) Run Status Viewer
 */

export type DAGStatus = 
  | 'pending'
  | 'running'
  | 'success'
  | 'failed'
  | 'skipped';

export interface DAGStepOutput {
  type: 'text' | 'file' | 'error' | 'json';
  content: string;
  timestamp: string; // ISO string
  size?: string;
  downloadUrl?: string;
}

export interface DAGStep {
  id: string;
  name: string;
  status: DAGStatus;
  startTime?: string; // ISO string
  endTime?: string;   // ISO string
  duration?: number;  // in milliseconds
  retryCount: number;
  error?: string;
  output?: DAGStepOutput;
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
        output: {
          type: 'file',
          content: 'data/extracted_data_20230101.csv',
          timestamp: new Date(oneHourAgo.getTime() + 5 * 60 * 1000).toISOString(),
          size: '2.5 MB',
          downloadUrl: 'https://example.com/data/extracted_data_20230101.csv'
        }
      },
      {
        id: 'transform_data',
        name: 'Transform Data',
        status: 'success',
        startTime: new Date(oneHourAgo.getTime() + 5 * 60 * 1000).toISOString(),
        endTime: new Date(oneHourAgo.getTime() + 15 * 60 * 1000).toISOString(),
        duration: 10 * 60 * 1000,
        retryCount: 1,
        output: {
          type: 'json',
          content: JSON.stringify({
            recordsProcessed: 1250,
            transformationsApplied: 5,
            dataQualityChecks: {
              passed: 1245,
              failed: 5,
              successRate: 0.996
            }
          }, null, 2),
          timestamp: new Date(oneHourAgo.getTime() + 15 * 60 * 1000).toISOString()
        }
      },
      {
        id: 'load_data',
        name: 'Load Data',
        status: 'running',
        startTime: new Date(oneHourAgo.getTime() + 15 * 60 * 1000).toISOString(),
        endTime: undefined,
        duration: undefined,
        retryCount: 0,
        output: {
          type: 'text',
          content: 'Loading data into the target database...\nProcessed 45% (625/1250 records)',
          timestamp: new Date().toISOString()
        }
      },
      {
        id: 'send_notifications',
        name: 'Send Notifications',
        status: 'pending',
        startTime: undefined,
        endTime: undefined,
        duration: undefined,
        retryCount: 0,
        error: 'Dependencies not met - waiting for previous steps to complete',
        output: {
          type: 'error',
          content: 'Dependencies not met - waiting for previous steps to complete',
          timestamp: new Date().toISOString()
        }
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

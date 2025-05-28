export type DAGStepState = 
  | 'PENDING'
  | 'RUNNING'
  | 'SUCCESS'
  | 'FAILED'
  | 'RETRY'
  | 'SKIPPED'
  | 'CANCELLED';

export interface DAGStep {
  id: string;
  status: DAGStepState;
  duration?: number;
  error?: string;
  dependencies?: string[];
  metadata?: Record<string, any>;
}

export interface DAGRun {
  id: string;
  status: DAGStepState;
  steps: DAGStep[];
  startedAt: string;
  completedAt?: string;
  metadata?: Record<string, any>;
} 
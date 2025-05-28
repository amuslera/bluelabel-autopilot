export interface DAGRunStep {
  id: string;
  name: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  duration_ms?: number;
  error?: string;
  timestamp: string;
  start_time?: string;
  end_time?: string;
  retry_count?: number;
}

export interface DAGRun {
  id: string;
  workflow_name: string;
  workflow_version: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  started_at: string;
  completed_at?: string;
  duration_ms?: number;
  step_count: number;
  steps: DAGRunStep[];
  failed_step?: string;
  errors: string[];
  execution_order?: string[];
  metadata?: Record<string, any>;
}

export interface DAG {
  id: string;
  name: string;
  version: string;
  description?: string;
  steps: string[];
  created_at: string;
  updated_at: string;
}

export interface DAGStep {
  id: string;
  name: string;
  agent: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  input?: any;
  output?: any;
  error?: string;
  start_time?: string;
  end_time?: string;
  duration?: number;
  retry_count?: number;
}

export interface APIError {
  message: string;
  status?: number;
  code?: string;
  data?: any;
}
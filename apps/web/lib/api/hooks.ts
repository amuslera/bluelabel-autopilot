import { useState, useEffect, useCallback } from 'react';
import { apiClient } from './client';
import { DAGRun, DAGStep } from '../types';

export interface UseDAGRunResult {
  data: DAGRun | null;
  error: Error | null;
  isLoading: boolean;
  refetch: () => void;
}

export function useDAGRun(dagId: string, runId: string): UseDAGRunResult {
  const [data, setData] = useState<DAGRun | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchData = useCallback(async () => {
    if (!runId) return;

    setIsLoading(true);
    setError(null);

    try {
      const result = await apiClient.getDAGRun(dagId, runId);
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch DAG run'));
    } finally {
      setIsLoading(false);
    }
  }, [dagId, runId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return {
    data,
    error,
    isLoading,
    refetch: fetchData,
  };
}

export interface UseDAGRunsResult {
  data: DAGRun[];
  error: Error | null;
  isLoading: boolean;
  refetch: () => void;
}

export function useDAGRuns(dagId: string, limit: number = 20): UseDAGRunsResult {
  const [data, setData] = useState<DAGRun[]>([]);
  const [error, setError] = useState<Error | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchData = useCallback(async () => {
    if (!dagId) return;

    setIsLoading(true);
    setError(null);

    try {
      const result = await apiClient.listDAGRuns(dagId, limit);
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch DAG runs'));
    } finally {
      setIsLoading(false);
    }
  }, [dagId, limit]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return {
    data,
    error,
    isLoading,
    refetch: fetchData,
  };
}

export interface UseDAGRunStepsResult {
  data: DAGStep[];
  error: Error | null;
  isLoading: boolean;
  refetch: () => void;
}

export function useDAGRunSteps(dagId: string, runId: string): UseDAGRunStepsResult {
  const [data, setData] = useState<DAGStep[]>([]);
  const [error, setError] = useState<Error | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchData = useCallback(async () => {
    if (!runId) return;

    setIsLoading(true);
    setError(null);

    try {
      const result = await apiClient.getDAGRunSteps(dagId, runId);
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch DAG run steps'));
    } finally {
      setIsLoading(false);
    }
  }, [dagId, runId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return {
    data,
    error,
    isLoading,
    refetch: fetchData,
  };
}

export interface UseDAGRunUpdatesResult {
  status: string | null;
  steps: DAGStep[];
  progress: any | null;
  error: Error | null;
  isConnected: boolean;
}

export function useDAGRunUpdates(dagId: string, runId: string): UseDAGRunUpdatesResult {
  const [status, setStatus] = useState<string | null>(null);
  const [steps, setSteps] = useState<DAGStep[]>([]);
  const [progress, setProgress] = useState<any | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    if (!dagId || !runId) return;

    let ws: WebSocket;

    const connectWebSocket = () => {
      ws = apiClient.connectWebSocket(
        (data) => {
          // Handle different event types
          switch (data.event) {
            case 'connected':
              setIsConnected(true);
              setError(null);
              // Subscribe to specific DAG run
              apiClient.subscribeToDAGRun(runId);
              break;

            case 'dag_run_status':
            case 'dag.run.status.updated':
              if (data.run_id === runId) {
                setStatus(data.data?.status);
                if (data.data?.steps) {
                  setSteps(Object.values(data.data.steps));
                }
              }
              break;

            case 'step_status':
            case 'dag.step.status.updated':
              if (data.run_id === runId) {
                setSteps(prevSteps => {
                  const updatedSteps = [...prevSteps];
                  const stepIndex = updatedSteps.findIndex(s => s.id === data.data?.step_id);
                  if (stepIndex !== -1) {
                    updatedSteps[stepIndex] = { ...updatedSteps[stepIndex], ...data.data };
                  }
                  return updatedSteps;
                });
              }
              break;

            case 'dag_run_progress':
            case 'dag.run.completed':
              if (data.run_id === runId) {
                setProgress(data.data);
              }
              break;

            case 'error':
              setError(new Error(data.message || 'WebSocket error'));
              break;

            case 'ping':
              // Keep-alive, no action needed
              break;

            default:
              console.log('Unknown WebSocket event:', data.event);
          }
        },
        (error) => {
          setError(new Error('WebSocket connection error'));
          setIsConnected(false);
        }
      );
    };

    connectWebSocket();

    return () => {
      setIsConnected(false);
      apiClient.disconnectWebSocket();
    };
  }, [dagId, runId]);

  return {
    status,
    steps,
    progress,
    error,
    isConnected,
  };
}

// Workflow execution hooks
export interface UseRunWorkflowResult {
  runWorkflow: (workflowPath: string, inputs?: Record<string, any>) => Promise<{ run_id: string; status: string }>;
  isLoading: boolean;
  error: Error | null;
}

export function useRunWorkflow(): UseRunWorkflowResult {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const runWorkflow = useCallback(async (workflowPath: string, inputs: Record<string, any> = {}) => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await apiClient.runWorkflow(workflowPath, inputs);
      return result;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to run workflow');
      setError(error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    runWorkflow,
    isLoading,
    error,
  };
} 
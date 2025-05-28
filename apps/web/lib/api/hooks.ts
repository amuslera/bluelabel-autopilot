import { useState, useEffect, useCallback } from 'react';
import { apiClient, wsClient, APIError } from './client';
import { DAGRun, DAGStep } from '../types';

// Hook for fetching DAGs with pagination
export function useDAGs(page: number = 1, limit: number = 20) {
  const [data, setData] = useState<{
    items: any[];
    total: number;
    page: number;
    limit: number;
  } | null>(null);
  const [error, setError] = useState<APIError | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchDAGs = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await apiClient.listDAGs(page, limit);
      setData(result);
    } catch (err) {
      setError(err instanceof APIError ? err : new APIError('Failed to fetch DAGs'));
    } finally {
      setLoading(false);
    }
  }, [page, limit]);

  useEffect(() => {
    fetchDAGs();
  }, [fetchDAGs]);

  return { data, error, loading, refetch: fetchDAGs };
}

// Hook for fetching a single DAG run
export function useDAGRun(runId: string) {
  const [data, setData] = useState<DAGRun | null>(null);
  const [error, setError] = useState<APIError | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchDAGRun = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await apiClient.getDAGRun(runId);
      setData(result);
    } catch (err) {
      setError(err instanceof APIError ? err : new APIError('Failed to fetch DAG run'));
    } finally {
      setLoading(false);
    }
  }, [runId]);

  useEffect(() => {
    fetchDAGRun();
  }, [fetchDAGRun]);

  return { data, error, loading, refetch: fetchDAGRun };
}

// Hook for fetching DAG runs with pagination
export function useDAGRuns(dagId: string, page: number = 1, limit: number = 20) {
  const [data, setData] = useState<{
    items: DAGRun[];
    total: number;
    page: number;
    limit: number;
  } | null>(null);
  const [error, setError] = useState<APIError | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchDAGRuns = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await apiClient.listDAGRuns(dagId, page, limit);
      setData(result);
    } catch (err) {
      setError(err instanceof APIError ? err : new APIError('Failed to fetch DAG runs'));
    } finally {
      setLoading(false);
    }
  }, [dagId, page, limit]);

  useEffect(() => {
    fetchDAGRuns();
  }, [fetchDAGRuns]);

  return { data, error, loading, refetch: fetchDAGRuns };
}

// Hook for fetching DAG run steps
export function useDAGRunSteps(dagId: string, runId: string) {
  const [data, setData] = useState<DAGStep[] | null>(null);
  const [error, setError] = useState<APIError | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchSteps = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await apiClient.getDAGRunSteps(dagId, runId);
      setData(result);
    } catch (err) {
      setError(err instanceof APIError ? err : new APIError('Failed to fetch DAG run steps'));
    } finally {
      setLoading(false);
    }
  }, [dagId, runId]);

  useEffect(() => {
    fetchSteps();
  }, [fetchSteps]);

  return { data, error, loading, refetch: fetchSteps };
}

// Hook for real-time DAG run updates
export function useDAGRunUpdates(runId: string) {
  const [status, setStatus] = useState<DAGRun['status'] | null>(null);
  const [steps, setSteps] = useState<Record<string, DAGStep>>({});
  const [progress, setProgress] = useState<{
    totalSteps: number;
    completedSteps: number;
    runningSteps: number;
    failedSteps: number;
    pendingSteps: number;
    completionPercentage: number;
  } | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Connect to WebSocket
    wsClient.connect();

    // Subscribe to DAG updates
    wsClient.subscribe([runId]);

    // Handle DAG run status updates
    const handleStatusUpdate = (data: { status: DAGRun['status'] }) => {
      setStatus(data.status);
    };

    // Handle step status updates
    const handleStepUpdate = (data: DAGStep) => {
      setSteps((prev) => ({
        ...prev,
        [data.id]: data,
      }));
    };

    // Handle progress updates
    const handleProgressUpdate = (data: {
      totalSteps: number;
      completedSteps: number;
      runningSteps: number;
      failedSteps: number;
      pendingSteps: number;
      completionPercentage: number;
    }) => {
      setProgress(data);
    };

    // Handle errors
    const handleError = (data: { error: string }) => {
      setError(data.error);
    };

    // Register event handlers
    wsClient.on('dag.run.status.updated', handleStatusUpdate);
    wsClient.on('dag.step.status.updated', handleStepUpdate);
    wsClient.on('dag.run.completed', handleProgressUpdate);
    wsClient.on('error', handleError);

    // Cleanup
    return () => {
      wsClient.off('dag.run.status.updated', handleStatusUpdate);
      wsClient.off('dag.step.status.updated', handleStepUpdate);
      wsClient.off('dag.run.completed', handleProgressUpdate);
      wsClient.off('error', handleError);
      wsClient.unsubscribe([runId]);
    };
  }, [runId]);

  return { status, steps, progress, error };
} 
import axios, { AxiosInstance, AxiosError } from 'axios';
import { DAG, DAGRun, DAGStep } from '../types';

export class APIError extends Error {
  constructor(message: string, public status?: number) {
    super(message);
    this.name = 'APIError';
  }
}

export class APIClient {
  private client: AxiosInstance;
  private wsClient: WebSocket | null = null;

  constructor(baseURL: string = 'http://localhost:8000/api') {
    this.client = axios.create({
      baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        const message = error.response?.data?.detail || error.message;
        const status = error.response?.status;
        throw new APIError(message, status);
      }
    );
  }

  // DAG operations
  async listDAGs(): Promise<DAG[]> {
    const response = await this.client.get('/workflows/dag-runs');
    return response.data.items || [];
  }

  async getDAGRun(dagId: string, runId: string): Promise<DAGRun | null> {
    try {
      const response = await this.client.get(`/workflows/dag-runs/${runId}`);
      return response.data;
    } catch (error) {
      if (error instanceof APIError && error.status === 404) {
        return null;
      }
      throw error;
    }
  }

  async listDAGRuns(dagId: string, limit: number = 20, offset: number = 0): Promise<DAGRun[]> {
    const response = await this.client.get(`/workflows/dag-runs?limit=${limit}&offset=${offset}`);
    return response.data.items || [];
  }

  async getDAGRunSteps(dagId: string, runId: string): Promise<DAGStep[]> {
    const dagRun = await this.getDAGRun(dagId, runId);
    if (!dagRun || !dagRun.steps) {
      return [];
    }
    
    // Convert steps object to array
    return Object.values(dagRun.steps);
  }

  // Workflow execution
  async runWorkflow(workflowPath: string, inputs: Record<string, any> = {}): Promise<{ run_id: string; status: string }> {
    const response = await this.client.post('/workflows/run', {
      workflow_path: workflowPath,
      inputs
    });
    return response.data;
  }

  async uploadPDF(file: File): Promise<{ run_id: string; status: string }> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.client.post('/workflows/upload-pdf', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  // WebSocket operations
  connectWebSocket(onMessage: (data: any) => void, onError?: (error: Event) => void): WebSocket {
    if (this.wsClient) {
      this.wsClient.close();
    }

    this.wsClient = new WebSocket('ws://localhost:8000/ws');
    
    this.wsClient.onopen = () => {
      console.log('WebSocket connected');
    };

    this.wsClient.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    this.wsClient.onerror = (error) => {
      console.error('WebSocket error:', error);
      if (onError) {
        onError(error);
      }
    };

    this.wsClient.onclose = () => {
      console.log('WebSocket disconnected');
      this.wsClient = null;
    };

    return this.wsClient;
  }

  subscribeToDAGRun(runId: string): void {
    if (this.wsClient && this.wsClient.readyState === WebSocket.OPEN) {
      this.wsClient.send(JSON.stringify({
        action: 'subscribe',
        run_id: runId
      }));
    }
  }

  disconnectWebSocket(): void {
    if (this.wsClient) {
      this.wsClient.close();
      this.wsClient = null;
    }
  }
}

// Global client instance
export const apiClient = new APIClient(); 
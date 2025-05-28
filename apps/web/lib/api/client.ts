import axios, { AxiosInstance, AxiosError } from 'axios';
import { DAG, DAGRun, DAGStep } from '../types';

export class APIError extends Error {
  constructor(
    message: string,
    public status?: number,
    public code?: string,
    public data?: any
  ) {
    super(message);
    this.name = 'APIError';
  }
}

export class APIClient {
  private client: AxiosInstance;

  constructor(baseURL: string = '/api/v1') {
    this.client = axios.create({
      baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response) {
          throw new APIError(
            error.response.data?.message || 'API request failed',
            error.response.status,
            error.response.data?.code,
            error.response.data
          );
        }
        throw new APIError('Network error', undefined, 'NETWORK_ERROR');
      }
    );
  }

  // DAG Operations
  async listDAGs(page: number = 1, limit: number = 20): Promise<{
    items: DAG[];
    total: number;
    page: number;
    limit: number;
  }> {
    const response = await this.client.get('/dags', {
      params: { page, limit },
    });
    return response.data;
  }

  async getDAGRun(dagId: string, runId: string): Promise<DAGRun> {
    const response = await this.client.get(`/dags/${dagId}/runs/${runId}`);
    return response.data;
  }

  async listDAGRuns(
    dagId: string,
    page: number = 1,
    limit: number = 20
  ): Promise<{
    items: DAGRun[];
    total: number;
    page: number;
    limit: number;
  }> {
    const response = await this.client.get(`/dags/${dagId}/runs`, {
      params: { page, limit },
    });
    return response.data;
  }

  async getDAGRunSteps(dagId: string, runId: string): Promise<DAGStep[]> {
    const response = await this.client.get(`/dags/${dagId}/runs/${runId}/steps`);
    return response.data;
  }
}

// WebSocket Client
export class WebSocketClient {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectTimeout: NodeJS.Timeout | null = null;
  private messageHandlers: Map<string, ((data: any) => void)[]> = new Map();
  private subscribedDAGs: Set<string> = new Set();

  constructor(
    private url: string = 'ws://localhost:3000/api/v1/ws',
    private token?: string
  ) {}

  connect() {
    if (this.ws?.readyState === WebSocket.OPEN) return;

    this.ws = new WebSocket(this.url);
    this.setupEventHandlers();
  }

  private setupEventHandlers() {
    if (!this.ws) return;

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
      if (this.token) {
        this.send({ type: 'auth', token: this.token });
      }
      // Resubscribe to DAGs
      if (this.subscribedDAGs.size > 0) {
        this.send({
          type: 'subscribe',
          dagIds: Array.from(this.subscribedDAGs),
        });
      }
    };

    this.ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        const handlers = this.messageHandlers.get(message.type) || [];
        handlers.forEach((handler) => handler(message.data));
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
      this.attemptReconnect();
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  private attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      return;
    }

    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
    this.reconnectTimeout = setTimeout(() => {
      this.reconnectAttempts++;
      this.connect();
    }, delay);
  }

  subscribe(dagIds: string[]) {
    dagIds.forEach((id) => this.subscribedDAGs.add(id));
    this.send({
      type: 'subscribe',
      dagIds,
    });
  }

  unsubscribe(dagIds: string[]) {
    dagIds.forEach((id) => this.subscribedDAGs.delete(id));
    this.send({
      type: 'unsubscribe',
      dagIds,
    });
  }

  on(event: string, handler: (data: any) => void) {
    const handlers = this.messageHandlers.get(event) || [];
    handlers.push(handler);
    this.messageHandlers.set(event, handlers);
  }

  off(event: string, handler: (data: any) => void) {
    const handlers = this.messageHandlers.get(event) || [];
    const index = handlers.indexOf(handler);
    if (index !== -1) {
      handlers.splice(index, 1);
      this.messageHandlers.set(event, handlers);
    }
  }

  private send(data: any) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      console.warn('WebSocket not connected, message not sent:', data);
    }
  }

  disconnect() {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
    }
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

// Create singleton instances
export const apiClient = new APIClient();
export const wsClient = new WebSocketClient(); 
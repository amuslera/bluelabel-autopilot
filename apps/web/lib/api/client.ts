import axios, { AxiosInstance, AxiosError } from 'axios';
import { DAGRun, DAGStep } from '../types';

export class APIError extends Error {
  constructor(message: string, public status?: number) {
    super(message);
    this.name = 'APIError';
  }
}

// AIOS v2 Types
export interface ProcessingJob {
  id: string;
  type: 'pdf' | 'url' | 'audio' | 'email';
  status: 'pending' | 'processing' | 'completed' | 'failed';
  filename?: string;
  url?: string;
  progress: number;
  startedAt: string;
  completedAt?: string;
  result?: any;
  error?: string;
}

export interface Agent {
  id: string;
  name: string;
  type: string;
  status: 'idle' | 'working' | 'error' | 'offline';
  currentTask?: string;
  performance: {
    tasksCompleted: number;
    averageProcessingTime: number;
    successRate: number;
  };
}

export interface KnowledgeItem {
  id: string;
  title: string;
  type: 'document' | 'analysis' | 'summary';
  content: string;
  metadata: Record<string, any>;
  createdAt: string;
  updatedAt: string;
  tags: string[];
}

export interface Insight {
  id: string;
  title: string;
  description: string;
  type: 'trend' | 'pattern' | 'anomaly' | 'recommendation';
  confidence: number;
  createdAt: string;
  metadata: Record<string, any>;
}

export class AIOSAPIClient {
  private client: AxiosInstance;
  private wsClient: WebSocket | null = null;

  constructor(baseURL: string = 'http://localhost:8000') {
    this.client = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        const message = (error.response?.data as any)?.detail || error.message;
        const status = error.response?.status;
        throw new APIError(message, status);
      }
    );
  }

  // File Upload Operations
  async uploadPDF(file: File, options?: { extractText?: boolean; generateSummary?: boolean }): Promise<ProcessingJob> {
    const formData = new FormData();
    formData.append('file', file);
    if (options?.extractText) formData.append('extract_text', 'true');
    if (options?.generateSummary) formData.append('generate_summary', 'true');

    const response = await this.client.post('/api/workflows/upload-pdf', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return {
      id: response.data.run_id,
      type: 'pdf',
      status: 'pending',
      filename: file.name,
      progress: 0,
      startedAt: new Date().toISOString(),
    };
  }

  async processURL(url: string, options?: { fullContent?: boolean; generateSummary?: boolean }): Promise<ProcessingJob> {
    const response = await this.client.post('/api/workflows/from-url', {
      url,
      full_content: options?.fullContent,
      generate_summary: options?.generateSummary,
    });
    
    return {
      id: response.data.run_id,
      type: 'url',
      status: 'pending',
      url,
      progress: 0,
      startedAt: new Date().toISOString(),
    };
  }

  async uploadAudio(file: File, options?: { transcribe?: boolean; summarize?: boolean }): Promise<ProcessingJob> {
    const formData = new FormData();
    formData.append('file', file);
    if (options?.transcribe) formData.append('transcribe', 'true');
    if (options?.summarize) formData.append('summarize', 'true');

    const response = await this.client.post('/api/workflows/upload-audio', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return {
      id: response.data.run_id,
      type: 'audio',
      status: 'pending',
      filename: file.name,
      progress: 0,
      startedAt: new Date().toISOString(),
    };
  }

  // Processing Job Management
  async getProcessingJob(jobId: string): Promise<ProcessingJob | null> {
    try {
      const response = await this.client.get(`/api/workflows/dag-runs/${jobId}`);
      const run = response.data;
      
      return {
        id: run.id,
        type: 'pdf', // Default, would need to track this in metadata
        status: this.mapDAGStatusToJobStatus(run.status),
        progress: this.calculateProgress(run.steps || []),
        startedAt: run.started_at,
        completedAt: run.completed_at,
        result: run.result,
        error: run.errors?.[0],
      };
    } catch (error) {
      if (error instanceof APIError && error.status === 404) {
        return null;
      }
      throw error;
    }
  }

  async listProcessingJobs(limit: number = 20, offset: number = 0): Promise<ProcessingJob[]> {
    const response = await this.client.get(`/api/workflows/dag-runs?limit=${limit}&offset=${offset}`);
    
    return (response.data.items || []).map((run: any) => ({
      id: run.id,
      type: 'pdf', // Default, would need metadata
      status: this.mapDAGStatusToJobStatus(run.status),
      filename: run.workflow_name,
      progress: run.status === 'success' ? 100 : run.status === 'failed' ? 0 : 50,
      startedAt: run.started_at,
      completedAt: run.completed_at,
    }));
  }

  // Agent Management
  async listAgents(): Promise<Agent[]> {
    // Mock data for now - would connect to actual agent registry
    return [
      {
        id: 'ingestion_agent',
        name: 'Ingestion Agent',
        type: 'ingestion',
        status: 'idle',
        performance: {
          tasksCompleted: 145,
          averageProcessingTime: 2.3,
          successRate: 98.5,
        },
      },
      {
        id: 'digest_agent',
        name: 'Digest Agent',
        type: 'analysis',
        status: 'working',
        currentTask: 'Analyzing PDF document',
        performance: {
          tasksCompleted: 89,
          averageProcessingTime: 4.1,
          successRate: 96.2,
        },
      },
      {
        id: 'summary_agent',
        name: 'Summary Agent',
        type: 'synthesis',
        status: 'idle',
        performance: {
          tasksCompleted: 203,
          averageProcessingTime: 1.8,
          successRate: 99.1,
        },
      },
    ];
  }

  async getAgent(agentId: string): Promise<Agent | null> {
    const agents = await this.listAgents();
    return agents.find(agent => agent.id === agentId) || null;
  }

  // Knowledge Repository
  async searchKnowledge(query: string, filters?: { type?: string; tags?: string[] }): Promise<KnowledgeItem[]> {
    const params = new URLSearchParams({ q: query });
    if (filters?.type) params.append('type', filters.type);
    if (filters?.tags) params.append('tags', filters.tags.join(','));

    // Mock data for now - would connect to actual knowledge base
    const mockResults: KnowledgeItem[] = [
      {
        id: '1',
        title: 'Q4 Financial Report Analysis',
        type: 'analysis',
        content: 'Comprehensive analysis of Q4 financial performance...',
        metadata: { source: 'annual_report.pdf', confidence: 0.95 },
        createdAt: '2024-01-15T10:30:00Z',
        updatedAt: '2024-01-15T10:30:00Z',
        tags: ['finance', 'quarterly', 'analysis'],
      },
      {
        id: '2',
        title: 'Market Trends Summary',
        type: 'summary',
        content: 'Key market trends identified from recent research...',
        metadata: { source: 'market_research.pdf', confidence: 0.87 },
        createdAt: '2024-01-14T14:20:00Z',
        updatedAt: '2024-01-14T14:20:00Z',
        tags: ['market', 'trends', 'research'],
      },
    ];

    return mockResults.filter(item => 
      item.title.toLowerCase().includes(query.toLowerCase()) ||
      item.content.toLowerCase().includes(query.toLowerCase())
    );
  }

  async getKnowledgeItem(id: string): Promise<KnowledgeItem | null> {
    // Mock implementation
    const items = await this.searchKnowledge('');
    return items.find(item => item.id === id) || null;
  }

  // Analytics & Insights
  async getInsights(): Promise<Insight[]> {
    // Mock data for insights dashboard
    return [
      {
        id: '1',
        title: 'Processing Volume Increase',
        description: 'Document processing volume has increased by 45% this month',
        type: 'trend',
        confidence: 0.92,
        createdAt: '2024-01-15T09:00:00Z',
        metadata: { metric: 'volume', change: '+45%', period: 'month' },
      },
      {
        id: '2',
        title: 'Recurring Theme: Sustainability',
        description: 'Sustainability topics appear in 68% of processed documents',
        type: 'pattern',
        confidence: 0.85,
        createdAt: '2024-01-14T16:30:00Z',
        metadata: { theme: 'sustainability', frequency: '68%' },
      },
      {
        id: '3',
        title: 'Optimize PDF Processing',
        description: 'Consider batch processing for documents >10MB to improve efficiency',
        type: 'recommendation',
        confidence: 0.78,
        createdAt: '2024-01-13T11:15:00Z',
        metadata: { optimization: 'batch_processing', threshold: '10MB' },
      },
    ];
  }

  async getDashboardMetrics(): Promise<{
    totalProcessed: number;
    processingTime: number;
    successRate: number;
    activeAgents: number;
    knowledgeItems: number;
    recentActivity: Array<{ id: string; type: string; title: string; timestamp: string }>;
  }> {
    // Mock dashboard metrics
    return {
      totalProcessed: 1247,
      processingTime: 2.8,
      successRate: 97.3,
      activeAgents: 3,
      knowledgeItems: 892,
      recentActivity: [
        { id: '1', type: 'pdf', title: 'Annual Report 2023.pdf', timestamp: '2024-01-15T10:45:00Z' },
        { id: '2', type: 'url', title: 'Industry Analysis Article', timestamp: '2024-01-15T10:30:00Z' },
        { id: '3', type: 'pdf', title: 'Market Research.pdf', timestamp: '2024-01-15T10:15:00Z' },
      ],
    };
  }

  // WebSocket for real-time updates
  connectWebSocket(onMessage: (data: any) => void, onError?: (error: Event) => void): WebSocket {
    if (this.wsClient) {
      this.wsClient.close();
    }

    this.wsClient = new WebSocket('ws://localhost:8000/ws');
    
    this.wsClient.onopen = () => {
      console.log('AIOS WebSocket connected');
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

  disconnectWebSocket(): void {
    if (this.wsClient) {
      this.wsClient.close();
      this.wsClient = null;
    }
  }

  // Helper methods
  private mapDAGStatusToJobStatus(dagStatus: string): ProcessingJob['status'] {
    switch (dagStatus?.toLowerCase()) {
      case 'success':
      case 'completed':
        return 'completed';
      case 'failed':
      case 'error':
        return 'failed';
      case 'running':
      case 'in_progress':
        return 'processing';
      default:
        return 'pending';
    }
  }

  private calculateProgress(steps: any[]): number {
    if (!steps.length) return 0;
    const completedSteps = steps.filter(step => 
      step.status === 'success' || step.status === 'completed'
    ).length;
    return Math.round((completedSteps / steps.length) * 100);
  }
}

// Global client instance
export const aiosClient = new AIOSAPIClient(); 
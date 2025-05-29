// Agent Marketplace Type Definitions
// Based on AGENT_MARKETPLACE_STRATEGY.md

export interface Agent {
  id: string;
  name: string;
  description: string;
  category: string[];
  capabilities: Capability[];
  pricing: PricingModel;
  author: AgentAuthor;
  metrics: PerformanceMetrics;
  compatibility: CompatibilityInfo;
  installation: InstallationPackage;
  icon?: string;
  screenshots?: string[];
  rating: number;
  reviewCount: number;
  downloadCount: number;
  featured?: boolean;
  verified?: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface Capability {
  name: string;
  description: string;
  inputTypes: string[];
  outputTypes: string[];
}

export interface PricingModel {
  type: 'free' | 'subscription' | 'usage' | 'enterprise';
  price?: number;
  currency?: string;
  period?: 'monthly' | 'yearly';
  usageUnit?: string;
  features: string[];
  limitations?: string[];
}

export interface AgentAuthor {
  id: string;
  name: string;
  avatar?: string;
  verified: boolean;
  rating: number;
  agentCount: number;
  website?: string;
  contact?: string;
}

export interface PerformanceMetrics {
  averageProcessingTime: number;
  successRate: number;
  uptime: number;
  errorRate: number;
  resourceUsage: {
    cpu: number;
    memory: number;
    storage: number;
  };
  qualityScore: number;
}

export interface CompatibilityInfo {
  minVersion: string;
  maxVersion?: string;
  dependencies: string[];
  conflicts: string[];
  requirements: {
    memory: string;
    cpu: string;
    storage: string;
  };
}

export interface InstallationPackage {
  size: string;
  downloadUrl: string;
  checksum: string;
  instructions: InstallationStep[];
  configurationOptions: ConfigurationOption[];
}

export interface InstallationStep {
  step: number;
  title: string;
  description: string;
  command?: string;
  verification?: string;
}

export interface ConfigurationOption {
  key: string;
  title: string;
  description: string;
  type: 'string' | 'number' | 'boolean' | 'select' | 'multiselect';
  required: boolean;
  default?: any;
  options?: string[];
  validation?: string;
}

export interface MarketplaceCategory {
  id: string;
  name: string;
  description: string;
  icon: string;
  agentCount: number;
  featured: boolean;
  subcategories?: MarketplaceCategory[];
}

export interface AgentReview {
  id: string;
  userId: string;
  userName: string;
  userAvatar?: string;
  rating: number;
  title: string;
  content: string;
  helpful: number;
  createdAt: string;
  verified: boolean;
  response?: {
    content: string;
    author: string;
    createdAt: string;
  };
}

export interface InstalledAgent extends Agent {
  installDate: string;
  status: 'active' | 'inactive' | 'error' | 'updating';
  configuration: Record<string, any>;
  usage: {
    totalProcessed: number;
    lastUsed: string;
    averageTime: number;
    errorCount: number;
  };
  version: string;
  autoUpdate: boolean;
}

export interface WorkflowTemplate {
  id: string;
  name: string;
  description: string;
  agents: string[];
  steps: WorkflowStep[];
  category: string;
  complexity: 'simple' | 'medium' | 'complex';
  estimatedTime: number;
  popularity: number;
}

export interface WorkflowStep {
  id: string;
  agentId: string;
  name: string;
  inputs: Record<string, any>;
  outputs: string[];
  dependencies: string[];
  configuration: Record<string, any>;
}

export interface MarketplaceSearch {
  query: string;
  filters: {
    categories: string[];
    pricing: string[];
    rating: number;
    compatibility: boolean;
    featured: boolean;
    verified: boolean;
  };
  sort: 'relevance' | 'popularity' | 'rating' | 'recent' | 'name';
  page: number;
  limit: number;
}

export interface MarketplaceStats {
  totalAgents: number;
  totalDownloads: number;
  totalDevelopers: number;
  averageRating: number;
  categoryCounts: Record<string, number>;
  recentActivity: {
    newAgents: number;
    updates: number;
    reviews: number;
  };
}

export interface DeveloperPortal {
  profile: DeveloperProfile;
  agents: Agent[];
  analytics: DeveloperAnalytics;
  earnings: DeveloperEarnings;
}

export interface DeveloperProfile {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  bio: string;
  website?: string;
  verified: boolean;
  joinDate: string;
  totalAgents: number;
  totalDownloads: number;
  averageRating: number;
}

export interface DeveloperAnalytics {
  downloads: TimeSeriesData[];
  ratings: TimeSeriesData[];
  revenue: TimeSeriesData[];
  agentPerformance: AgentPerformanceData[];
}

export interface TimeSeriesData {
  date: string;
  value: number;
}

export interface AgentPerformanceData {
  agentId: string;
  agentName: string;
  downloads: number;
  rating: number;
  revenue: number;
  growth: number;
}

export interface DeveloperEarnings {
  totalEarnings: number;
  thisMonth: number;
  lastMonth: number;
  pendingPayouts: number;
  payoutHistory: PayoutRecord[];
}

export interface PayoutRecord {
  id: string;
  amount: number;
  currency: string;
  date: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  method: string;
}

// API Response Types
export interface MarketplaceResponse<T> {
  data: T;
  pagination?: {
    page: number;
    limit: number;
    total: number;
    pages: number;
  };
  meta?: Record<string, any>;
}

export interface AgentSearchResponse extends MarketplaceResponse<Agent[]> {
  filters: {
    categories: { name: string; count: number }[];
    priceRanges: { range: string; count: number }[];
    ratings: { rating: number; count: number }[];
  };
  suggestions: string[];
}

// Component Props Types
export interface AgentCardProps {
  agent: Agent;
  variant?: 'grid' | 'list' | 'featured';
  onInstall?: (agent: Agent) => void;
  onPreview?: (agent: Agent) => void;
  installed?: boolean;
}

export interface MarketplaceFiltersProps {
  categories: MarketplaceCategory[];
  selectedFilters: MarketplaceSearch['filters'];
  onFilterChange: (filters: MarketplaceSearch['filters']) => void;
  onClearFilters: () => void;
}

export interface AgentDetailModalProps {
  agent: Agent | null;
  isOpen: boolean;
  onClose: () => void;
  onInstall: (agent: Agent) => void;
  reviews: AgentReview[];
  isInstalled?: boolean;
} 
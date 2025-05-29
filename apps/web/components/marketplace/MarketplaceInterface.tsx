import React, { useState, useEffect, useMemo } from 'react';
import AgentCard from './AgentCard';
import MarketplaceFilters from './MarketplaceFilters';
import { Agent, MarketplaceCategory, MarketplaceSearch, MarketplaceStats } from '../../types/marketplace';

interface MarketplaceInterfaceProps {
  initialAgents?: Agent[];
  categories?: MarketplaceCategory[];
  onAgentInstall?: (agent: Agent) => void;
  onAgentPreview?: (agent: Agent) => void;
  installedAgentIds?: string[];
}

const MarketplaceInterface: React.FC<MarketplaceInterfaceProps> = ({
  initialAgents = [],
  categories = [],
  onAgentInstall,
  onAgentPreview,
  installedAgentIds = []
}) => {
  const [agents, setAgents] = useState<Agent[]>(initialAgents);
  const [loading, setLoading] = useState(false);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [sortBy, setSortBy] = useState<'popularity' | 'rating' | 'recent' | 'name'>('popularity');
  
  const [search, setSearch] = useState<MarketplaceSearch>({
    query: '',
    filters: {
      categories: [],
      pricing: [],
      rating: 0,
      compatibility: false,
      featured: false,
      verified: false
    },
    sort: 'popularity',
    page: 1,
    limit: 24
  });

  // Mock marketplace stats
  const [stats] = useState<MarketplaceStats>({
    totalAgents: 127,
    totalDownloads: 45632,
    totalDevelopers: 89,
    averageRating: 4.3,
    categoryCounts: {
      'document-processing': 45,
      'data-integration': 23,
      'intelligence': 31,
      'automation': 18,
      'communication': 10
    },
    recentActivity: {
      newAgents: 12,
      updates: 8,
      reviews: 156
    }
  });

  // Filter and sort agents
  const filteredAndSortedAgents = useMemo(() => {
    let filtered = agents;

    // Apply search query
    if (search.query) {
      const query = search.query.toLowerCase();
      filtered = filtered.filter(agent =>
        agent.name.toLowerCase().includes(query) ||
        agent.description.toLowerCase().includes(query) ||
        agent.category.some(cat => cat.toLowerCase().includes(query)) ||
        agent.capabilities.some(cap => 
          cap.name.toLowerCase().includes(query) ||
          cap.description.toLowerCase().includes(query)
        )
      );
    }

    // Apply filters
    if (search.filters.categories.length > 0) {
      filtered = filtered.filter(agent =>
        agent.category.some(cat => search.filters.categories.includes(cat))
      );
    }

    if (search.filters.pricing.length > 0) {
      filtered = filtered.filter(agent =>
        search.filters.pricing.includes(agent.pricing.type)
      );
    }

    if (search.filters.rating > 0) {
      filtered = filtered.filter(agent => agent.rating >= search.filters.rating);
    }

    if (search.filters.featured) {
      filtered = filtered.filter(agent => agent.featured);
    }

    if (search.filters.verified) {
      filtered = filtered.filter(agent => agent.verified);
    }

    // Apply sorting
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'popularity':
          return b.downloadCount - a.downloadCount;
        case 'rating':
          return b.rating - a.rating;
        case 'recent':
          return new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime();
        case 'name':
          return a.name.localeCompare(b.name);
        default:
          return 0;
      }
    });

    return filtered;
  }, [agents, search, sortBy]);

  const featuredAgents = useMemo(() => {
    return agents.filter(agent => agent.featured).slice(0, 3);
  }, [agents]);

  const handleSearch = (query: string) => {
    setSearch(prev => ({ ...prev, query, page: 1 }));
  };

  const handleFilterChange = (filters: MarketplaceSearch['filters']) => {
    setSearch(prev => ({ ...prev, filters, page: 1 }));
  };

  const handleClearFilters = () => {
    setSearch(prev => ({
      ...prev,
      query: '',
      filters: {
        categories: [],
        pricing: [],
        rating: 0,
        compatibility: false,
        featured: false,
        verified: false
      },
      page: 1
    }));
  };

  const handleSortChange = (sort: typeof sortBy) => {
    setSortBy(sort);
    setSearch(prev => ({ ...prev, sort, page: 1 }));
  };

  // Mock data for demonstration
  useEffect(() => {
    if (initialAgents.length === 0) {
      // Load mock agents
      const mockAgents: Agent[] = [
        {
          id: 'legal-doc-analyzer',
          name: 'Legal Document Analyzer',
          description: 'Advanced AI agent specialized in analyzing legal documents, extracting clauses, and identifying compliance issues.',
          category: ['document-processing', 'legal'],
          capabilities: [
            { name: 'contract-analysis', description: 'Extract and analyze contract clauses', inputTypes: ['pdf', 'docx'], outputTypes: ['json', 'html'] },
            { name: 'compliance-check', description: 'Verify regulatory compliance', inputTypes: ['pdf'], outputTypes: ['report'] }
          ],
          pricing: { type: 'subscription', price: 29, currency: 'USD', period: 'monthly', features: ['Unlimited documents', '24/7 support'] },
          author: { id: 'legaltech-inc', name: 'LegalTech Inc.', verified: true, rating: 4.8, agentCount: 5 },
          metrics: { averageProcessingTime: 2.3, successRate: 99.2, uptime: 99.8, errorRate: 0.2, resourceUsage: { cpu: 15, memory: 256, storage: 50 }, qualityScore: 95 },
          compatibility: { minVersion: '2.0.0', dependencies: [], conflicts: [], requirements: { memory: '512MB', cpu: '1 core', storage: '100MB' } },
          installation: { size: '45MB', downloadUrl: '', checksum: '', instructions: [], configurationOptions: [] },
          rating: 4.8,
          reviewCount: 234,
          downloadCount: 12500,
          featured: true,
          verified: true,
          createdAt: '2024-01-15T00:00:00Z',
          updatedAt: '2024-05-20T00:00:00Z'
        },
        {
          id: 'financial-reporter',
          name: 'Financial Report Processor',
          description: 'Extracts insights from financial reports, SEC filings, and earnings statements with high accuracy.',
          category: ['document-processing', 'finance'],
          capabilities: [
            { name: 'financial-analysis', description: 'Analyze financial statements', inputTypes: ['pdf', 'excel'], outputTypes: ['dashboard'] }
          ],
          pricing: { type: 'usage', price: 0.50, currency: 'USD', usageUnit: 'per document', features: ['Pay per use', 'No commitments'] },
          author: { id: 'fintech-solutions', name: 'FinTech Solutions', verified: true, rating: 4.6, agentCount: 8 },
          metrics: { averageProcessingTime: 4.1, successRate: 97.8, uptime: 99.5, errorRate: 0.5, resourceUsage: { cpu: 25, memory: 512, storage: 100 }, qualityScore: 92 },
          compatibility: { minVersion: '2.0.0', dependencies: [], conflicts: [], requirements: { memory: '1GB', cpu: '2 cores', storage: '200MB' } },
          installation: { size: '78MB', downloadUrl: '', checksum: '', instructions: [], configurationOptions: [] },
          rating: 4.6,
          reviewCount: 189,
          downloadCount: 8900,
          featured: true,
          verified: true,
          createdAt: '2024-02-01T00:00:00Z',
          updatedAt: '2024-05-18T00:00:00Z'
        },
        {
          id: 'content-summarizer',
          name: 'Content Summarizer Pro',
          description: 'Intelligent content summarization with context preservation and key insight extraction.',
          category: ['document-processing', 'content'],
          capabilities: [
            { name: 'text-summarization', description: 'Generate concise summaries', inputTypes: ['text', 'pdf'], outputTypes: ['text', 'bullets'] }
          ],
          pricing: { type: 'free', features: ['Basic summarization', 'Community support'] },
          author: { id: 'open-ai-tools', name: 'Open AI Tools', verified: false, rating: 4.2, agentCount: 12 },
          metrics: { averageProcessingTime: 1.8, successRate: 95.5, uptime: 98.9, errorRate: 1.1, resourceUsage: { cpu: 10, memory: 128, storage: 25 }, qualityScore: 88 },
          compatibility: { minVersion: '1.8.0', dependencies: [], conflicts: [], requirements: { memory: '256MB', cpu: '1 core', storage: '50MB' } },
          installation: { size: '32MB', downloadUrl: '', checksum: '', instructions: [], configurationOptions: [] },
          rating: 4.2,
          reviewCount: 567,
          downloadCount: 23400,
          featured: false,
          verified: false,
          createdAt: '2024-03-10T00:00:00Z',
          updatedAt: '2024-05-25T00:00:00Z'
        }
      ];
      setAgents(mockAgents);
    }
  }, [initialAgents]);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header with Search */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              Agent Marketplace
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Discover and install specialized AI agents to supercharge your workflow. 
              From document analysis to data processing, find the perfect agent for your needs.
            </p>
          </div>

          {/* Search Bar */}
          <div className="max-w-2xl mx-auto">
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <input
                type="text"
                placeholder="Search agents for contract analysis, financial reporting, content summarization..."
                value={search.query}
                onChange={(e) => handleSearch(e.target.value)}
                className="block w-full pl-10 pr-3 py-4 border border-gray-300 rounded-lg leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 text-lg"
              />
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-8">
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600">{stats.totalAgents}</div>
              <div className="text-sm text-gray-600">Available Agents</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600">{stats.totalDownloads.toLocaleString()}</div>
              <div className="text-sm text-gray-600">Total Downloads</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600">{stats.totalDevelopers}</div>
              <div className="text-sm text-gray-600">Developers</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-yellow-600">{stats.averageRating.toFixed(1)}</div>
              <div className="text-sm text-gray-600">Avg Rating</div>
            </div>
          </div>
        </div>
      </div>

      {/* Featured Agents */}
      {featuredAgents.length > 0 && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Featured Agents</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {featuredAgents.map((agent) => (
              <AgentCard
                key={agent.id}
                agent={agent}
                variant="featured"
                onInstall={onAgentInstall}
                onPreview={onAgentPreview}
                installed={installedAgentIds.includes(agent.id)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Sidebar Filters */}
          <div className="lg:w-1/4">
            <MarketplaceFilters
              categories={categories}
              selectedFilters={search.filters}
              onFilterChange={handleFilterChange}
              onClearFilters={handleClearFilters}
            />
          </div>

          {/* Agent Grid */}
          <div className="lg:w-3/4">
            {/* Toolbar */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 gap-4">
              <div className="flex items-center space-x-4">
                <span className="text-gray-700">
                  {filteredAndSortedAgents.length} agents found
                </span>
                {search.query && (
                  <span className="text-sm text-gray-500">
                    for "{search.query}"
                  </span>
                )}
              </div>

              <div className="flex items-center space-x-4">
                {/* Sort Dropdown */}
                <select
                  value={sortBy}
                  onChange={(e) => handleSortChange(e.target.value as typeof sortBy)}
                  className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                >
                  <option value="popularity">Most Popular</option>
                  <option value="rating">Highest Rated</option>
                  <option value="recent">Most Recent</option>
                  <option value="name">Name A-Z</option>
                </select>

                {/* View Mode Toggle */}
                <div className="flex border border-gray-300 rounded-md">
                  <button
                    onClick={() => setViewMode('grid')}
                    className={`px-3 py-2 text-sm ${
                      viewMode === 'grid'
                        ? 'bg-blue-600 text-white'
                        : 'bg-white text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM11 13a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                    </svg>
                  </button>
                  <button
                    onClick={() => setViewMode('list')}
                    className={`px-3 py-2 text-sm ${
                      viewMode === 'list'
                        ? 'bg-blue-600 text-white'
                        : 'bg-white text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>

            {/* Agent List */}
            {loading ? (
              <div className="flex justify-center items-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              </div>
            ) : filteredAndSortedAgents.length === 0 ? (
              <div className="text-center py-12">
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <h3 className="mt-2 text-sm font-medium text-gray-900">No agents found</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Try adjusting your search criteria or browse our featured agents.
                </p>
                <div className="mt-6">
                  <button
                    onClick={handleClearFilters}
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    Clear all filters
                  </button>
                </div>
              </div>
            ) : (
              <div className={
                viewMode === 'grid'
                  ? 'grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6'
                  : 'space-y-4'
              }>
                {filteredAndSortedAgents.map((agent) => (
                  <AgentCard
                    key={agent.id}
                    agent={agent}
                    variant={viewMode}
                    onInstall={onAgentInstall}
                    onPreview={onAgentPreview}
                    installed={installedAgentIds.includes(agent.id)}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MarketplaceInterface; 
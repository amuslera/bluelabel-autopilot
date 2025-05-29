import React, { useState, useMemo } from 'react';
import { InstalledAgent, Agent } from '../../types/marketplace';

interface InstalledAgentsManagerProps {
  installedAgents: InstalledAgent[];
  onUninstall?: (agentId: string) => void;
  onConfigure?: (agentId: string, config: Record<string, any>) => void;
  onToggleStatus?: (agentId: string, active: boolean) => void;
  onViewUsage?: (agentId: string) => void;
}

const InstalledAgentsManager: React.FC<InstalledAgentsManagerProps> = ({
  installedAgents,
  onUninstall,
  onConfigure,
  onToggleStatus,
  onViewUsage
}) => {
  const [selectedAgent, setSelectedAgent] = useState<InstalledAgent | null>(null);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('list');
  const [filterStatus, setFilterStatus] = useState<'all' | 'active' | 'inactive' | 'error'>('all');

  const filteredAgents = useMemo(() => {
    if (filterStatus === 'all') return installedAgents;
    return installedAgents.filter(agent => agent.status === filterStatus);
  }, [installedAgents, filterStatus]);

  const getStatusColor = (status: InstalledAgent['status']) => {
    switch (status) {
      case 'active': return 'text-green-600 bg-green-100';
      case 'inactive': return 'text-gray-600 bg-gray-100';
      case 'error': return 'text-red-600 bg-red-100';
      case 'updating': return 'text-blue-600 bg-blue-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status: InstalledAgent['status']) => {
    switch (status) {
      case 'active':
        return (
          <svg className="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
        );
      case 'inactive':
        return (
          <svg className="w-4 h-4 text-gray-600" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 000 2h4a1 1 0 100-2H8z" clipRule="evenodd" />
          </svg>
        );
      case 'error':
        return (
          <svg className="w-4 h-4 text-red-600" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
        );
      case 'updating':
        return (
          <svg className="w-4 h-4 text-blue-600 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        );
      default:
        return null;
    }
  };

  const formatLastUsed = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);
    
    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return `${Math.floor(diffInHours)}h ago`;
    if (diffInHours < 168) return `${Math.floor(diffInHours / 24)}d ago`;
    return date.toLocaleDateString();
  };

  const AgentCard = ({ agent }: { agent: InstalledAgent }) => (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          {agent.icon ? (
            <img src={agent.icon} alt={agent.name} className="w-12 h-12 rounded-lg" />
          ) : (
            <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
              <span className="text-white font-bold">{agent.name.charAt(0)}</span>
            </div>
          )}
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{agent.name}</h3>
            <p className="text-sm text-gray-600">by {agent.author.name}</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <div className={`flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(agent.status)}`}>
            {getStatusIcon(agent.status)}
            <span className="capitalize">{agent.status}</span>
          </div>
          
          <div className="relative">
            <button
              onClick={() => setSelectedAgent(selectedAgent?.id === agent.id ? null : agent)}
              className="p-2 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
              </svg>
            </button>
            
            {selectedAgent?.id === agent.id && (
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg border border-gray-200 z-10">
                <div className="py-1">
                  <button
                    onClick={() => onToggleStatus?.(agent.id, agent.status !== 'active')}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    {agent.status === 'active' ? 'Deactivate' : 'Activate'} Agent
                  </button>
                  <button
                    onClick={() => onConfigure?.(agent.id, agent.configuration)}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    Configure
                  </button>
                  <button
                    onClick={() => onViewUsage?.(agent.id)}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    View Usage
                  </button>
                  <div className="border-t border-gray-100"></div>
                  <button
                    onClick={() => onUninstall?.(agent.id)}
                    className="block w-full text-left px-4 py-2 text-sm text-red-700 hover:bg-red-50"
                  >
                    Uninstall
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
      
      <p className="text-gray-600 text-sm mb-4 line-clamp-2">{agent.description}</p>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <div className="text-lg font-bold text-gray-900">{agent.usage.totalProcessed.toLocaleString()}</div>
          <div className="text-xs text-gray-500">Documents Processed</div>
        </div>
        <div>
          <div className="text-lg font-bold text-gray-900">{agent.usage.averageTime.toFixed(1)}s</div>
          <div className="text-xs text-gray-500">Avg Processing Time</div>
        </div>
      </div>
      
      <div className="flex items-center justify-between text-sm text-gray-500">
        <span>Last used: {formatLastUsed(agent.usage.lastUsed)}</span>
        <span>v{agent.version}</span>
      </div>
    </div>
  );

  const AgentListItem = ({ agent }: { agent: InstalledAgent }) => (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          {agent.icon ? (
            <img src={agent.icon} alt={agent.name} className="w-10 h-10 rounded-lg" />
          ) : (
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
              <span className="text-white font-bold text-sm">{agent.name.charAt(0)}</span>
            </div>
          )}
          
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-2">
              <h3 className="text-lg font-semibold text-gray-900 truncate">{agent.name}</h3>
              <div className={`flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(agent.status)}`}>
                {getStatusIcon(agent.status)}
                <span className="capitalize">{agent.status}</span>
              </div>
            </div>
            <p className="text-sm text-gray-600 truncate">{agent.description}</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-6">
          <div className="text-center">
            <div className="text-lg font-bold text-gray-900">{agent.usage.totalProcessed.toLocaleString()}</div>
            <div className="text-xs text-gray-500">Processed</div>
          </div>
          
          <div className="text-center">
            <div className="text-lg font-bold text-gray-900">{agent.usage.averageTime.toFixed(1)}s</div>
            <div className="text-xs text-gray-500">Avg Time</div>
          </div>
          
          <div className="text-center">
            <div className="text-sm text-gray-900">{formatLastUsed(agent.usage.lastUsed)}</div>
            <div className="text-xs text-gray-500">Last Used</div>
          </div>
          
          <div className="relative">
            <button
              onClick={() => setSelectedAgent(selectedAgent?.id === agent.id ? null : agent)}
              className="p-2 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
              </svg>
            </button>
            
            {selectedAgent?.id === agent.id && (
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg border border-gray-200 z-10">
                <div className="py-1">
                  <button
                    onClick={() => onToggleStatus?.(agent.id, agent.status !== 'active')}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    {agent.status === 'active' ? 'Deactivate' : 'Activate'} Agent
                  </button>
                  <button
                    onClick={() => onConfigure?.(agent.id, agent.configuration)}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    Configure
                  </button>
                  <button
                    onClick={() => onViewUsage?.(agent.id)}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    View Usage
                  </button>
                  <div className="border-t border-gray-100"></div>
                  <button
                    onClick={() => onUninstall?.(agent.id)}
                    className="block w-full text-left px-4 py-2 text-sm text-red-700 hover:bg-red-50"
                  >
                    Uninstall
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );

  const activeAgents = installedAgents.filter(agent => agent.status === 'active').length;
  const totalProcessed = installedAgents.reduce((sum, agent) => sum + agent.usage.totalProcessed, 0);
  const avgProcessingTime = installedAgents.length > 0 
    ? installedAgents.reduce((sum, agent) => sum + agent.usage.averageTime, 0) / installedAgents.length 
    : 0;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">My Agents</h1>
          
          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="text-3xl font-bold text-blue-600">{installedAgents.length}</div>
              <div className="text-sm text-gray-600">Total Agents</div>
            </div>
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="text-3xl font-bold text-green-600">{activeAgents}</div>
              <div className="text-sm text-gray-600">Active Agents</div>
            </div>
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="text-3xl font-bold text-purple-600">{totalProcessed.toLocaleString()}</div>
              <div className="text-sm text-gray-600">Total Processed</div>
            </div>
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="text-3xl font-bold text-yellow-600">{avgProcessingTime.toFixed(1)}s</div>
              <div className="text-sm text-gray-600">Avg Processing Time</div>
            </div>
          </div>
        </div>

        {/* Toolbar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 gap-4">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <label className="text-sm font-medium text-gray-700">Filter by status:</label>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value as typeof filterStatus)}
                className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                <option value="all">All ({installedAgents.length})</option>
                <option value="active">Active ({installedAgents.filter(a => a.status === 'active').length})</option>
                <option value="inactive">Inactive ({installedAgents.filter(a => a.status === 'inactive').length})</option>
                <option value="error">Error ({installedAgents.filter(a => a.status === 'error').length})</option>
              </select>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-700">
              {filteredAgents.length} agent{filteredAgents.length !== 1 ? 's' : ''}
            </span>
            
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
        {filteredAgents.length === 0 ? (
          <div className="text-center py-12">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No agents found</h3>
            <p className="mt-1 text-sm text-gray-500">
              {filterStatus === 'all' 
                ? 'Install some agents from the marketplace to get started.'
                : `No agents with ${filterStatus} status.`
              }
            </p>
            <div className="mt-6">
              <a
                href="/marketplace"
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Browse Marketplace
              </a>
            </div>
          </div>
        ) : (
          <div className={
            viewMode === 'grid'
              ? 'grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6'
              : 'space-y-4'
          }>
            {filteredAgents.map((agent) => (
              viewMode === 'grid' 
                ? <AgentCard key={agent.id} agent={agent} />
                : <AgentListItem key={agent.id} agent={agent} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default InstalledAgentsManager; 
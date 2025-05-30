import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { 
  Bot, 
  FileText, 
  Globe, 
  Mic, 
  ArrowRight, 
  Upload,
  Users,
  BarChart3,
  Clock,
  CheckCircle,
  Play,
  RefreshCw,
  TrendingUp
} from 'lucide-react';

// Types
interface RecentResult {
  jobId: string;
  agentName: string;
  agentIcon: string;
  inputType: string;
  status: 'completed' | 'processing' | 'failed';
  createdAt: string;
  completedAt?: string;
  preview?: string;
  processingTime?: number;
}

// Mock agent mapping
const agentData: Record<string, { name: string; icon: string }> = {
  '1': { name: 'Document Analyzer', icon: '📄' },
  '2': { name: 'Summarizer', icon: '📝' },
  '3': { name: 'Data Extractor', icon: '🔍' },
  '4': { name: 'Audio Transcriber', icon: '🎤' }
};

// Get input type icon
const getInputTypeIcon = (inputType: string) => {
  switch (inputType) {
    case 'file':
      return <FileText className="h-4 w-4" />;
    case 'url':
      return <Globe className="h-4 w-4" />;
    case 'text':
      return <FileText className="h-4 w-4" />;
    case 'audio':
      return <Mic className="h-4 w-4" />;
    default:
      return <FileText className="h-4 w-4" />;
  }
};

// Enhanced Result Card Component
const ResultCard: React.FC<{ result: RecentResult; onClick: () => void }> = ({ result, onClick }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-50 text-green-700 border-green-200';
      case 'processing':
        return 'bg-blue-50 text-blue-700 border-blue-200';
      case 'failed':
        return 'bg-red-50 text-red-700 border-red-200';
      default:
        return 'bg-gray-50 text-gray-700 border-gray-200';
    }
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / 60000);
    
    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <motion.div
      whileHover={{ y: -2, scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className="bg-white rounded-lg border border-gray-200 p-4 cursor-pointer hover:shadow-md transition-all duration-200"
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center space-x-3">
          <span className="text-2xl">{result.agentIcon}</span>
          <div>
            <h3 className="font-medium text-gray-900 text-sm">{result.agentName}</h3>
            <div className="flex items-center space-x-2 text-xs text-gray-500">
              {getInputTypeIcon(result.inputType)}
              <span className="capitalize">{result.inputType}</span>
            </div>
          </div>
        </div>
        <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(result.status)}`}>
          {result.status === 'completed' ? 'Complete' : 
           result.status === 'processing' ? 'Processing' : 'Failed'}
        </span>
      </div>
      
      {result.preview && (
        <p className="text-sm text-gray-600 mb-3 line-clamp-2">
          {result.preview}
        </p>
      )}
      
      <div className="flex items-center justify-between text-xs text-gray-500">
        <span>{formatTime(result.createdAt)}</span>
        {result.processingTime && (
          <span className="flex items-center space-x-1">
            <Clock className="h-3 w-3" />
            <span>{result.processingTime}s</span>
          </span>
        )}
      </div>
    </motion.div>
  );
};

// Loading State for Results
const ResultsLoadingState: React.FC = () => (
  <div className="space-y-4">
    {[1, 2, 3].map((i) => (
      <div key={i} className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="animate-pulse">
          <div className="flex items-start justify-between mb-3">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gray-200 rounded"></div>
              <div>
                <div className="h-4 bg-gray-200 rounded w-24 mb-1"></div>
                <div className="h-3 bg-gray-200 rounded w-16"></div>
              </div>
            </div>
            <div className="h-5 bg-gray-200 rounded w-16"></div>
          </div>
          <div className="h-8 bg-gray-200 rounded mb-3"></div>
          <div className="flex justify-between">
            <div className="h-3 bg-gray-200 rounded w-12"></div>
            <div className="h-3 bg-gray-200 rounded w-8"></div>
          </div>
        </div>
      </div>
    ))}
  </div>
);

// Quick Stats Component
const QuickStats: React.FC<{ results: RecentResult[] }> = ({ results }) => {
  const totalJobs = results.length;
  const completedJobs = results.filter(r => r.status === 'completed').length;
  const averageProcessingTime = results
    .filter(r => r.processingTime)
    .reduce((acc, r) => acc + (r.processingTime || 0), 0) / Math.max(1, results.filter(r => r.processingTime).length);

  const stats = [
    { 
      label: 'Total Jobs', 
      value: totalJobs.toString(), 
      icon: BarChart3, 
      color: 'text-blue-600' 
    },
    { 
      label: 'Completed', 
      value: completedJobs.toString(), 
      icon: CheckCircle, 
      color: 'text-green-600' 
    },
    { 
      label: 'Avg Time', 
      value: `${Math.round(averageProcessingTime)}s`, 
      icon: Clock, 
      color: 'text-purple-600' 
    }
  ];

  return (
    <div className="grid grid-cols-3 gap-4 mb-6">
      {stats.map((stat, index) => {
        const Icon = stat.icon;
        return (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white rounded-lg border border-gray-200 p-4 text-center"
          >
            <Icon className={`h-6 w-6 mx-auto mb-2 ${stat.color}`} />
            <div className="text-xl font-semibold text-gray-900">{stat.value}</div>
            <div className="text-sm text-gray-600">{stat.label}</div>
          </motion.div>
        );
      })}
    </div>
  );
};

// Main Dashboard Component
const Dashboard: React.FC = () => {
  const [recentResults, setRecentResults] = useState<RecentResult[]>([]);
  const [isLoadingResults, setIsLoadingResults] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  // Generate preview text from result
  const generatePreview = (result: string): string => {
    if (!result) return '';
    
    // Extract first meaningful line or sentence
    const lines = result.split('\n').filter(line => line.trim().length > 0);
    for (const line of lines) {
      if (!line.includes('=') && !line.includes('#') && line.length > 20) {
        return line.trim().substring(0, 100) + (line.length > 100 ? '...' : '');
      }
    }
    return result.substring(0, 100) + (result.length > 100 ? '...' : '');
  };

  // Fetch recent results
  const fetchRecentResults = async () => {
    try {
      // Try API first
      const response = await fetch('/api/results');
      if (response.ok) {
        const apiResults = await response.json();
        setRecentResults(apiResults);
        return;
      }
    } catch (error) {
      console.log('API not available, using localStorage');
    }

    // Fallback to localStorage
    const localResults: RecentResult[] = [];
    
    // Scan localStorage for job results
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key?.startsWith('job_')) {
        try {
          const jobData = JSON.parse(localStorage.getItem(key) || '');
          const agent = agentData[jobData.agentId];
          
          if (agent) {
            // Check if job is completed and has result
            const now = Date.now();
            const created = new Date(jobData.createdAt).getTime();
            const elapsed = (now - created) / 1000;
            
            let status = jobData.status;
            let preview = '';
            let processingTime = undefined;
            let completedAt = undefined;
            
            if (elapsed > 45) { // Job should be completed
              status = 'completed';
              
              // Generate mock result for preview
              let mockResult = '';
              switch (jobData.agentId) {
                case '1':
                  mockResult = `Document Analysis Report: This content contains structured information about AI-powered content processing with comprehensive workflow management.`;
                  break;
                case '2':
                  mockResult = `Content Summary: AI-powered content processing system with multi-input support and real-time monitoring capabilities.`;
                  break;
                case '3':
                  mockResult = `Extracted Data: Found 4 entities including AI Agent, Content Processing, and Real-time Updates with 94% confidence.`;
                  break;
                case '4':
                  mockResult = `Audio Transcription: Welcome to the AI content processing demonstration showing automated analysis capabilities.`;
                  break;
                default:
                  mockResult = `Processing completed successfully with high confidence analysis results.`;
              }
              
              preview = generatePreview(mockResult);
              processingTime = Math.floor(Math.random() * 45) + 15;
              completedAt = new Date(created + 45000).toISOString();
            } else if (elapsed > 3) {
              status = 'processing';
            }
            
            localResults.push({
              jobId: jobData.jobId,
              agentName: agent.name,
              agentIcon: agent.icon,
              inputType: jobData.inputType,
              status: status as any,
              createdAt: jobData.createdAt,
              completedAt,
              preview,
              processingTime
            });
          }
        } catch (error) {
          console.error('Error parsing job data:', error);
        }
      }
    }
    
    // Sort by creation date (newest first)
    localResults.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
    
    // Take only the most recent 10
    setRecentResults(localResults.slice(0, 10));
  };

  // Load results on component mount
  useEffect(() => {
    const loadResults = async () => {
      setIsLoadingResults(true);
      await fetchRecentResults();
      setIsLoadingResults(false);
    };
    
    loadResults();
  }, []);

  // Refresh results
  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchRecentResults();
    setRefreshing(false);
  };

  // Handle result click
  const handleResultClick = (result: RecentResult) => {
    window.location.href = `/results/${result.jobId}`;
  };

  return (
    <>
      <Head>
        <title>AIOS v2 Dashboard</title>
        <meta name="description" content="AI-Powered Content Processing Dashboard" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <div className="min-h-screen bg-gray-50 py-4 sm:py-8">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="text-center mb-8">
            <motion.h1 
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4"
            >
              Welcome to AIOS v2
            </motion.h1>
            <motion.p 
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="text-lg text-gray-600"
            >
              Intelligent content processing with AI agents
            </motion.p>
          </div>

          {/* Quick Actions */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
            >
              <Link href="/process">
                <div className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-all duration-200 cursor-pointer group">
                  <div className="flex items-center space-x-4">
                    <div className="p-3 bg-blue-100 rounded-lg group-hover:bg-blue-200 transition-colors">
                      <Upload className="h-8 w-8 text-blue-600" />
                    </div>
                    <div className="flex-1">
                      <h2 className="text-xl font-semibold text-gray-900 mb-2">Process Content</h2>
                      <p className="text-gray-600">Upload files, analyze URLs, or process text with AI agents</p>
                    </div>
                    <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-blue-600 transition-colors" />
                  </div>
                </div>
              </Link>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
            >
              <Link href="/agents">
                <div className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-all duration-200 cursor-pointer group">
                  <div className="flex items-center space-x-4">
                    <div className="p-3 bg-green-100 rounded-lg group-hover:bg-green-200 transition-colors">
                      <Users className="h-8 w-8 text-green-600" />
                    </div>
                    <div className="flex-1">
                      <h2 className="text-xl font-semibold text-gray-900 mb-2">Browse Agents</h2>
                      <p className="text-gray-600">Explore our AI agents and their specialized capabilities</p>
                    </div>
                    <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-green-600 transition-colors" />
                  </div>
                </div>
              </Link>
            </motion.div>
          </div>

          {/* Quick Stats */}
          {!isLoadingResults && recentResults.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              <QuickStats results={recentResults} />
            </motion.div>
          )}

          {/* Recent Results */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="bg-white rounded-lg border border-gray-200 p-6"
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900">Recent Results</h2>
              <div className="flex items-center space-x-3">
                <button
                  onClick={handleRefresh}
                  disabled={refreshing}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50"
                >
                  <RefreshCw className={`h-4 w-4 text-gray-600 ${refreshing ? 'animate-spin' : ''}`} />
                </button>
                {!isLoadingResults && recentResults.length > 0 && (
                  <div className="flex items-center space-x-1 text-sm text-gray-500">
                    <TrendingUp className="h-4 w-4" />
                    <span>{recentResults.length} total</span>
                  </div>
                )}
              </div>
            </div>

            {isLoadingResults ? (
              <ResultsLoadingState />
            ) : recentResults.length > 0 ? (
              <div className="space-y-4">
                {recentResults.map((result) => (
                  <ResultCard
                    key={result.jobId}
                    result={result}
                    onClick={() => handleResultClick(result)}
                  />
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <Bot className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">No results yet</h3>
                <p className="text-gray-600 mb-6">
                  Start processing content to see your results here
                </p>
                <Link href="/process">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="inline-flex items-center space-x-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
                  >
                    <Play className="h-5 w-5" />
                    <span>Get Started</span>
                  </motion.button>
                </Link>
              </div>
            )}
          </motion.div>
        </div>
      </div>
    </>
  );
};

export default Dashboard; 
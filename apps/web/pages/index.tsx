import React, { useState, useEffect, useCallback } from 'react';
import Head from 'next/head';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Upload, 
  FileText, 
  Globe, 
  Mic, 
  Bot, 
  Search, 
  TrendingUp, 
  Clock, 
  CheckCircle,
  AlertCircle,
  Settings,
  BookOpen,
  Activity,
  Users,
  Zap,
  Brain,
  Eye,
  Download,
  Filter,
  MoreHorizontal
} from 'lucide-react';
import { aiosClient, ProcessingJob, Agent, KnowledgeItem, Insight } from '../lib/api/client';

interface TabProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

// Upload Zone Component
const UploadZone: React.FC = () => {
  const [uploadedFiles, setUploadedFiles] = useState<ProcessingJob[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    setIsUploading(true);
    
    for (const file of acceptedFiles) {
      try {
        let job: ProcessingJob;
        
        if (file.type === 'application/pdf') {
          job = await aiosClient.uploadPDF(file, { extractText: true, generateSummary: true });
        } else if (file.type.startsWith('audio/')) {
          job = await aiosClient.uploadAudio(file, { transcribe: true, summarize: true });
        } else {
          // Handle other file types
          continue;
        }
        
        setUploadedFiles(prev => [...prev, job]);
      } catch (error) {
        console.error('Upload failed:', error);
      }
    }
    
    setIsUploading(false);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'audio/*': ['.mp3', '.wav', '.m4a'],
      'text/*': ['.txt', '.md'],
    },
    multiple: true,
  });

  const handleURLSubmit = async (url: string) => {
    try {
      const job = await aiosClient.processURL(url, { fullContent: true, generateSummary: true });
      setUploadedFiles(prev => [...prev, job]);
    } catch (error) {
      console.error('URL processing failed:', error);
    }
  };

  return (
    <div className="space-y-6">
      {/* Drag & Drop Zone */}
      <motion.div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200 ${
          isDragActive 
            ? 'border-blue-500 bg-blue-50' 
            : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
        }`}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        <input {...getInputProps()} />
        <Upload className="w-12 h-12 mx-auto text-gray-400 mb-4" />
        <h3 className="text-xl font-semibold text-gray-900 mb-2">
          {isDragActive ? 'Drop files here' : 'Upload your files'}
        </h3>
        <p className="text-gray-600 mb-4">
          Drag & drop PDFs, audio files, or click to browse
        </p>
        <div className="flex justify-center space-x-4 text-sm text-gray-500">
          <span className="flex items-center"><FileText className="w-4 h-4 mr-1" /> PDF</span>
          <span className="flex items-center"><Mic className="w-4 h-4 mr-1" /> Audio</span>
          <span className="flex items-center"><Globe className="w-4 h-4 mr-1" /> URL</span>
        </div>
      </motion.div>

      {/* URL Input */}
      <URLInput onSubmit={handleURLSubmit} />

      {/* Processing Jobs */}
      <ProcessingJobsList jobs={uploadedFiles} />
    </div>
  );
};

// URL Input Component
const URLInput: React.FC<{ onSubmit: (url: string) => void }> = ({ onSubmit }) => {
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;
    
    setIsLoading(true);
    await onSubmit(url);
    setUrl('');
    setIsLoading(false);
  };

  return (
    <form onSubmit={handleSubmit} className="flex space-x-2">
      <input
        type="url"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="Enter URL to process..."
        className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <button
        type="submit"
        disabled={isLoading || !url.trim()}
        className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {isLoading ? 'Processing...' : 'Process URL'}
      </button>
    </form>
  );
};

// Processing Jobs List
const ProcessingJobsList: React.FC<{ jobs: ProcessingJob[] }> = ({ jobs }) => {
  const getJobIcon = (type: ProcessingJob['type']) => {
    switch (type) {
      case 'pdf': return <FileText className="w-5 h-5" />;
      case 'audio': return <Mic className="w-5 h-5" />;
      case 'url': return <Globe className="w-5 h-5" />;
      default: return <FileText className="w-5 h-5" />;
    }
  };

  const getStatusColor = (status: ProcessingJob['status']) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-100';
      case 'processing': return 'text-blue-600 bg-blue-100';
      case 'failed': return 'text-red-600 bg-red-100';
      default: return 'text-yellow-600 bg-yellow-100';
    }
  };

  if (jobs.length === 0) return null;

  return (
    <div className="space-y-3">
      <h3 className="text-lg font-semibold text-gray-900">Processing Queue</h3>
      {jobs.map((job) => (
        <motion.div
          key={job.id}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center space-x-4 p-4 bg-white border border-gray-200 rounded-lg"
        >
          <div className="text-gray-600">
            {getJobIcon(job.type)}
          </div>
          <div className="flex-1">
            <div className="font-medium text-gray-900">
              {job.filename || job.url || 'Processing...'}
            </div>
            <div className="flex items-center space-x-2 mt-1">
              <div className="w-32 bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${job.progress}%` }}
                />
              </div>
              <span className="text-sm text-gray-500">{job.progress}%</span>
            </div>
          </div>
          <div className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(job.status)}`}>
            {job.status}
          </div>
        </motion.div>
      ))}
    </div>
  );
};

// Agent Management Console
const AgentConsole: React.FC = () => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const agentList = await aiosClient.listAgents();
        setAgents(agentList);
      } catch (error) {
        console.error('Failed to fetch agents:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAgents();
    const interval = setInterval(fetchAgents, 5000);
    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = (status: Agent['status']) => {
    switch (status) {
      case 'working': return <Activity className="w-5 h-5 text-blue-600 animate-pulse" />;
      case 'idle': return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'error': return <AlertCircle className="w-5 h-5 text-red-600" />;
      default: return <AlertCircle className="w-5 h-5 text-gray-400" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-gray-900">AI Agents</h3>
        <button className="p-2 text-gray-400 hover:text-gray-600">
          <Settings className="w-5 h-5" />
        </button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {agents.map((agent) => (
          <motion.div
            key={agent.id}
            className="p-4 bg-white border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
            whileHover={{ scale: 1.02 }}
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <Bot className="w-6 h-6 text-blue-600" />
                <h4 className="font-medium text-gray-900">{agent.name}</h4>
              </div>
              {getStatusIcon(agent.status)}
            </div>
            
            {agent.currentTask && (
              <p className="text-sm text-gray-600 mb-3">{agent.currentTask}</p>
            )}
            
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">Tasks Completed:</span>
                <span className="font-medium">{agent.performance.tasksCompleted}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Avg. Time:</span>
                <span className="font-medium">{agent.performance.averageProcessingTime}s</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Success Rate:</span>
                <span className="font-medium text-green-600">{agent.performance.successRate}%</span>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

// Knowledge Repository Browser
const KnowledgeBrowser: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [knowledgeItems, setKnowledgeItems] = useState<KnowledgeItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedType, setSelectedType] = useState<string>('all');

  const searchKnowledge = async (query: string) => {
    setLoading(true);
    try {
      const results = await aiosClient.searchKnowledge(query, {
        type: selectedType === 'all' ? undefined : selectedType
      });
      setKnowledgeItems(results);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    searchKnowledge('');
  }, [selectedType]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    searchKnowledge(searchQuery);
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-gray-900">Knowledge Repository</h3>
        <div className="flex items-center space-x-2">
          <select 
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Types</option>
            <option value="document">Documents</option>
            <option value="analysis">Analysis</option>
            <option value="summary">Summaries</option>
          </select>
          <Filter className="w-5 h-5 text-gray-400" />
        </div>
      </div>

      <form onSubmit={handleSearch} className="flex space-x-2">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search knowledge base..."
            className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <button
          type="submit"
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Search
        </button>
      </form>

      {loading ? (
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <div className="space-y-3">
          {knowledgeItems.map((item) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-4 bg-white border border-gray-200 rounded-lg hover:shadow-md transition-shadow cursor-pointer"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900 mb-1">{item.title}</h4>
                  <p className="text-sm text-gray-600 mb-3">{item.content.substring(0, 150)}...</p>
                  <div className="flex items-center space-x-3 text-xs text-gray-500">
                    <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded">{item.type}</span>
                    <span>{new Date(item.createdAt).toLocaleDateString()}</span>
                    <div className="flex space-x-1">
                      {item.tags.map((tag) => (
                        <span key={tag} className="px-2 py-1 bg-gray-100 text-gray-600 rounded">
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
                <button className="p-1 text-gray-400 hover:text-gray-600">
                  <MoreHorizontal className="w-5 h-5" />
                </button>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
};

// Analytics Dashboard
const AnalyticsDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<any>(null);
  const [insights, setInsights] = useState<Insight[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [metricsData, insightsData] = await Promise.all([
          aiosClient.getDashboardMetrics(),
          aiosClient.getInsights()
        ]);
        setMetrics(metricsData);
        setInsights(insightsData);
      } catch (error) {
        console.error('Failed to fetch analytics:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 bg-white border border-gray-200 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total Processed</p>
              <p className="text-2xl font-bold text-gray-900">{metrics?.totalProcessed}</p>
            </div>
            <FileText className="w-8 h-8 text-blue-600" />
          </div>
        </div>
        
        <div className="p-4 bg-white border border-gray-200 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Avg. Processing Time</p>
              <p className="text-2xl font-bold text-gray-900">{metrics?.processingTime}s</p>
            </div>
            <Clock className="w-8 h-8 text-green-600" />
          </div>
        </div>
        
        <div className="p-4 bg-white border border-gray-200 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Success Rate</p>
              <p className="text-2xl font-bold text-gray-900">{metrics?.successRate}%</p>
            </div>
            <CheckCircle className="w-8 h-8 text-emerald-600" />
          </div>
        </div>
        
        <div className="p-4 bg-white border border-gray-200 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Active Agents</p>
              <p className="text-2xl font-bold text-gray-900">{metrics?.activeAgents}</p>
            </div>
            <Bot className="w-8 h-8 text-purple-600" />
          </div>
        </div>
      </div>

      {/* Insights */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">AI Insights</h3>
        <div className="space-y-3">
          {insights.map((insight) => (
            <motion.div
              key={insight.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="p-4 bg-white border border-gray-200 rounded-lg"
            >
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0">
                  {insight.type === 'trend' && <TrendingUp className="w-5 h-5 text-blue-600" />}
                  {insight.type === 'pattern' && <Eye className="w-5 h-5 text-purple-600" />}
                  {insight.type === 'recommendation' && <Zap className="w-5 h-5 text-orange-600" />}
                </div>
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900">{insight.title}</h4>
                  <p className="text-sm text-gray-600 mt-1">{insight.description}</p>
                  <div className="flex items-center space-x-2 mt-2">
                    <span className="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded">
                      {Math.round(insight.confidence * 100)}% confidence
                    </span>
                    <span className="text-xs text-gray-500">
                      {new Date(insight.createdAt).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Recent Activity */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
        <div className="space-y-2">
          {metrics?.recentActivity.map((activity: any) => (
            <div key={activity.id} className="flex items-center space-x-3 p-3 bg-white border border-gray-200 rounded-lg">
              <div className="flex-shrink-0">
                {activity.type === 'pdf' && <FileText className="w-4 h-4 text-red-600" />}
                {activity.type === 'url' && <Globe className="w-4 h-4 text-blue-600" />}
                {activity.type === 'audio' && <Mic className="w-4 h-4 text-purple-600" />}
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">{activity.title}</p>
              </div>
              <div className="text-xs text-gray-500">
                {new Date(activity.timestamp).toLocaleTimeString()}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Main Component
const AIOSHomepage: React.FC = () => {
  const [activeTab, setActiveTab] = useState('upload');
  const [showOnboarding, setShowOnboarding] = useState(false);

  const tabs = [
    { id: 'upload', name: 'Upload & Process', icon: Upload },
    { id: 'agents', name: 'AI Agents', icon: Bot },
    { id: 'knowledge', name: 'Knowledge', icon: BookOpen },
    { id: 'analytics', name: 'Analytics', icon: TrendingUp },
  ];

  return (
    <>
      <Head>
        <title>BlueLabel AIOS v2 - AI Operating System</title>
        <meta name="description" content="Intelligent document processing and knowledge management system" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
        {/* Header */}
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center space-x-4">
                <Brain className="w-8 h-8 text-blue-600" />
                <h1 className="text-2xl font-bold text-gray-900">BlueLabel AIOS v2</h1>
                <span className="px-3 py-1 text-xs bg-blue-100 text-blue-800 rounded-full font-medium">
                  Beta
                </span>
              </div>
              
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => setShowOnboarding(true)}
                  className="px-4 py-2 text-sm text-blue-600 hover:text-blue-700 font-medium"
                >
                  Help & Onboarding
                </button>
                <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white text-sm font-medium">
                  U
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Navigation Tabs */}
        <nav className="bg-white border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex space-x-8">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                      activeTab === tab.id
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-center space-x-2">
                      <Icon className="w-5 h-5" />
                      <span>{tab.name}</span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.2 }}
            >
              {activeTab === 'upload' && <UploadZone />}
              {activeTab === 'agents' && <AgentConsole />}
              {activeTab === 'knowledge' && <KnowledgeBrowser />}
              {activeTab === 'analytics' && <AnalyticsDashboard />}
            </motion.div>
          </AnimatePresence>
        </main>

        {/* Onboarding Modal */}
        <OnboardingModal isOpen={showOnboarding} onClose={() => setShowOnboarding(false)} />
      </div>
    </>
  );
};

// Onboarding Modal Component
const OnboardingModal: React.FC<{ isOpen: boolean; onClose: () => void }> = ({ isOpen, onClose }) => {
  const [currentStep, setCurrentStep] = useState(0);

  const steps = [
    {
      title: 'Welcome to AIOS v2',
      content: 'Your intelligent AI Operating System for document processing and knowledge management.',
      icon: Brain,
    },
    {
      title: 'Upload & Process',
      content: 'Drag and drop PDFs, audio files, or enter URLs to automatically extract insights.',
      icon: Upload,
    },
    {
      title: 'AI Agents',
      content: 'Monitor your AI agents as they work together to process and analyze your content.',
      icon: Bot,
    },
    {
      title: 'Knowledge Base',
      content: 'Search and explore your growing knowledge repository with powerful AI-driven insights.',
      icon: BookOpen,
    },
    {
      title: 'Analytics',
      content: 'Get intelligent insights and track your system performance with real-time analytics.',
      icon: TrendingUp,
    },
  ];

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="bg-white rounded-xl max-w-md w-full p-6"
      >
        <div className="text-center mb-6">
          {React.createElement(steps[currentStep].icon, { className: "w-12 h-12 mx-auto text-blue-600 mb-4" })}
          <h3 className="text-xl font-bold text-gray-900 mb-2">{steps[currentStep].title}</h3>
          <p className="text-gray-600">{steps[currentStep].content}</p>
        </div>

        <div className="flex justify-between items-center">
          <button
            onClick={() => setCurrentStep(Math.max(0, currentStep - 1))}
            disabled={currentStep === 0}
            className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 disabled:opacity-50"
          >
            Previous
          </button>
          
          <div className="flex space-x-2">
            {steps.map((_, index) => (
              <div
                key={index}
                className={`w-2 h-2 rounded-full ${
                  index === currentStep ? 'bg-blue-600' : 'bg-gray-300'
                }`}
              />
            ))}
          </div>

          {currentStep < steps.length - 1 ? (
            <button
              onClick={() => setCurrentStep(currentStep + 1)}
              className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Next
            </button>
          ) : (
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Get Started
            </button>
          )}
        </div>
      </motion.div>
    </div>
  );
};

export default AIOSHomepage;
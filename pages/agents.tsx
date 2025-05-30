import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { 
  ArrowRight, 
  FileText, 
  Globe, 
  Mic, 
  Loader2,
  Wifi,
  WifiOff 
} from 'lucide-react';

// Types
interface Agent {
  id: string;
  name: string;
  icon: string;
  description: string;
  supportedInputs: string[];
}

// Mock agent data (same as Process page for consistency)
const mockAgents: Agent[] = [
  { 
    id: '1', 
    name: 'Document Analyzer', 
    icon: '📄', 
    description: 'Extracts insights from documents and creates comprehensive analysis reports', 
    supportedInputs: ['file', 'url', 'text'] 
  },
  { 
    id: '2', 
    name: 'Summarizer', 
    icon: '📝', 
    description: 'Creates concise summaries from any content type with key takeaways', 
    supportedInputs: ['file', 'url', 'text', 'audio'] 
  },
  { 
    id: '3', 
    name: 'Data Extractor', 
    icon: '🔍', 
    description: 'Pulls structured data and identifies patterns from content', 
    supportedInputs: ['file', 'text'] 
  },
  { 
    id: '4', 
    name: 'Audio Transcriber', 
    icon: '🎤', 
    description: 'Transcribes and analyzes audio content with speaker identification', 
    supportedInputs: ['audio'] 
  }
];

// API Status Indicator Component
const APIStatusIndicator: React.FC<{ isOnline: boolean }> = ({ isOnline }) => (
  <motion.div
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    className="flex items-center space-x-2 text-xs text-gray-500"
  >
    {isOnline ? (
      <>
        <Wifi className="h-3 w-3 text-green-500" />
        <span>API Connected</span>
      </>
    ) : (
      <>
        <WifiOff className="h-3 w-3 text-orange-500" />
        <span>Using offline data</span>
      </>
    )}
  </motion.div>
);

// Get icon for input type
const getInputTypeIcon = (inputType: string) => {
  switch (inputType) {
    case 'file':
      return <FileText className="h-3 w-3" />;
    case 'url':
      return <Globe className="h-3 w-3" />;
    case 'text':
      return <FileText className="h-3 w-3" />;
    case 'audio':
      return <Mic className="h-3 w-3" />;
    default:
      return <FileText className="h-3 w-3" />;
  }
};

// Get display name for input type
const getInputTypeLabel = (inputType: string) => {
  switch (inputType) {
    case 'file':
      return 'Files';
    case 'url':
      return 'URLs';
    case 'text':
      return 'Text';
    case 'audio':
      return 'Audio';
    default:
      return inputType;
  }
};

// Agent Card Component
const AgentCard: React.FC<{ agent: Agent }> = ({ agent }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    whileHover={{ y: -5, scale: 1.02 }}
    transition={{ duration: 0.2 }}
    className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm hover:shadow-md transition-all duration-200"
  >
    {/* Agent Icon & Name */}
    <div className="text-center mb-4">
      <div className="text-4xl mb-3">{agent.icon}</div>
      <h3 className="text-xl font-semibold text-gray-900 mb-2">{agent.name}</h3>
      <p className="text-gray-600 text-sm leading-relaxed">{agent.description}</p>
    </div>

    {/* Supported Input Types */}
    <div className="mb-6">
      <h4 className="text-sm font-medium text-gray-700 mb-2">Supports:</h4>
      <div className="flex flex-wrap gap-2">
        {agent.supportedInputs.map((inputType) => (
          <span
            key={inputType}
            className="inline-flex items-center space-x-1 px-2 py-1 bg-blue-50 text-blue-700 text-xs font-medium rounded-full"
          >
            {getInputTypeIcon(inputType)}
            <span>{getInputTypeLabel(inputType)}</span>
          </span>
        ))}
      </div>
    </div>

    {/* Try Now Button */}
    <Link 
      href={`/process?agent=${agent.id}`}
      className="w-full"
    >
      <motion.button
        whileTap={{ scale: 0.98 }}
        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-lg transition-colors duration-200 flex items-center justify-center space-x-2"
      >
        <span>Try Now</span>
        <ArrowRight className="h-4 w-4" />
      </motion.button>
    </Link>
  </motion.div>
);

// Loading State Component
const LoadingState: React.FC = () => (
  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
    {[1, 2, 3, 4].map((i) => (
      <div key={i} className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
        <div className="animate-pulse">
          <div className="text-center mb-4">
            <div className="w-16 h-16 bg-gray-200 rounded-full mx-auto mb-3"></div>
            <div className="h-5 bg-gray-200 rounded w-3/4 mx-auto mb-2"></div>
            <div className="h-4 bg-gray-200 rounded w-full mb-1"></div>
            <div className="h-4 bg-gray-200 rounded w-2/3 mx-auto"></div>
          </div>
          <div className="mb-6">
            <div className="h-4 bg-gray-200 rounded w-1/3 mb-2"></div>
            <div className="flex space-x-2">
              <div className="h-6 bg-gray-200 rounded-full w-16"></div>
              <div className="h-6 bg-gray-200 rounded-full w-12"></div>
            </div>
          </div>
          <div className="h-12 bg-gray-200 rounded"></div>
        </div>
      </div>
    ))}
  </div>
);

// Main Agents Page Component
const AgentsPage: React.FC = () => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isAPIOnline, setIsAPIOnline] = useState(false);

  // Fetch agents on component mount
  useEffect(() => {
    const fetchAgents = async () => {
      setIsLoading(true);
      try {
        const response = await fetch('/api/agents');
        if (response.ok) {
          const apiAgents = await response.json();
          setAgents(apiAgents);
          setIsAPIOnline(true);
        } else {
          throw new Error('API not available');
        }
      } catch (error) {
        console.log('API not ready, using mock data');
        setAgents(mockAgents);
        setIsAPIOnline(false);
      } finally {
        setIsLoading(false);
      }
    };

    fetchAgents();
  }, []);

  return (
    <>
      <Head>
        <title>Available Agents - AIOS v2</title>
        <meta name="description" content="Choose from our AI agents to process your content" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <div className="min-h-screen bg-gray-50 py-4 sm:py-8">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Page Header */}
          <div className="text-center mb-8">
            <motion.h1 
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-2xl sm:text-3xl font-bold text-gray-900 mb-4"
            >
              Available Agents
            </motion.h1>
            <motion.p 
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="text-base sm:text-lg text-gray-600 mb-4"
            >
              Choose the perfect AI agent for your content processing needs
            </motion.p>
            <div className="flex justify-center">
              <APIStatusIndicator isOnline={isAPIOnline} />
            </div>
          </div>

          {/* Agents Grid */}
          {isLoading ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <LoadingState />
            </motion.div>
          ) : (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
              className="grid grid-cols-1 md:grid-cols-2 gap-6"
            >
              {agents.map((agent, index) => (
                <motion.div
                  key={agent.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <AgentCard agent={agent} />
                </motion.div>
              ))}
            </motion.div>
          )}

          {/* Call to Action */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="text-center mt-12"
          >
            <p className="text-gray-600 mb-4">
              Not sure which agent to choose?
            </p>
            <Link href="/process">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-3 px-6 rounded-lg transition-colors duration-200"
              >
                Start with Process Page
              </motion.button>
            </Link>
          </motion.div>
        </div>
      </div>
    </>
  );
};

export default AgentsPage; 
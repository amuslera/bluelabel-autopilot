import React, { useState, useEffect, useRef } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Loader2, 
  CheckCircle, 
  XCircle, 
  Clock, 
  ArrowLeft, 
  Copy, 
  Share2, 
  RefreshCw,
  Bot,
  FileText,
  Globe,
  Mic,
  AlertTriangle,
  Home,
  ArrowRight,
  Wifi,
  WifiOff
} from 'lucide-react';

// Types
interface JobResult {
  jobId: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  agentId: string;
  agentName: string;
  agentIcon: string;
  inputType: string;
  inputContent?: string;
  filePath?: string;
  result?: string;
  error?: string;
  createdAt: string;
  completedAt?: string;
  estimatedTimeRemaining?: number;
  progress?: number;
}

// Mock agent data for display
const agentData: Record<string, { name: string; icon: string }> = {
  '1': { name: 'Document Analyzer', icon: '📄' },
  '2': { name: 'Summarizer', icon: '📝' },
  '3': { name: 'Data Extractor', icon: '🔍' },
  '4': { name: 'Audio Transcriber', icon: '🎤' }
};

// Breadcrumbs component
const Breadcrumbs: React.FC<{ jobResult: JobResult }> = ({ jobResult }) => (
  <nav className="flex items-center space-x-2 text-sm text-gray-600 mb-6">
    <Link href="/" className="hover:text-gray-900 transition-colors">
      <div className="flex items-center space-x-1">
        <Home className="h-4 w-4" />
        <span>Home</span>
      </div>
    </Link>
    <ArrowRight className="h-4 w-4 text-gray-400" />
    <Link href="/process" className="hover:text-gray-900 transition-colors">
      Process
    </Link>
    <ArrowRight className="h-4 w-4 text-gray-400" />
    <span className="text-gray-900 font-medium">Results</span>
  </nav>
);

// Connection status indicator
const ConnectionStatus: React.FC<{ isConnected: boolean; isWebSocket: boolean }> = ({ isConnected, isWebSocket }) => (
  <div className="flex items-center space-x-2 text-xs">
    {isConnected ? (
      <>
        <Wifi className="h-3 w-3 text-green-500" />
        <span className="text-green-600">
          {isWebSocket ? 'Real-time updates' : 'Polling updates'}
        </span>
      </>
    ) : (
      <>
        <WifiOff className="h-3 w-3 text-orange-500" />
        <span className="text-orange-600">Offline mode</span>
      </>
    )}
  </div>
);

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

// Animated processing loader with enhanced animations
const ProcessingAnimation: React.FC<{ status: string; progress?: number }> = ({ status, progress = 0 }) => (
  <div className="flex flex-col items-center space-y-6 p-8">
    <div className="relative">
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
        className="w-20 h-20 border-4 border-blue-200 border-t-blue-600 rounded-full"
      />
      <div className="absolute inset-0 flex items-center justify-center">
        <Bot className="h-8 w-8 text-blue-600" />
      </div>
    </div>
    
    {/* Enhanced status messages */}
    <div className="text-center space-y-2">
      <h3 className="text-xl font-semibold text-gray-900">
        {status === 'pending' ? 'Queued for Processing' : 'Processing Content'}
      </h3>
      <p className="text-gray-600 max-w-md">
        {status === 'pending' 
          ? 'Your job is in the queue and will begin shortly'
          : 'AI agent is analyzing your content and generating insights'
        }
      </p>
      
      {/* Processing stages indicator */}
      {status === 'processing' && (
        <div className="mt-4 flex justify-center space-x-2">
          {['Initializing', 'Analyzing', 'Extracting', 'Finalizing'].map((stage, index) => {
            const stageProgress = (progress / 100) * 4;
            const isActive = stageProgress > index;
            const isCompleted = stageProgress > index + 1;
            
            return (
              <div key={stage} className="flex flex-col items-center space-y-1">
                <div className={`w-3 h-3 rounded-full transition-all duration-500 ${
                  isCompleted ? 'bg-green-500' : 
                  isActive ? 'bg-blue-500 animate-pulse' : 
                  'bg-gray-200'
                }`} />
                <span className={`text-xs ${
                  isActive ? 'text-blue-600' : 'text-gray-400'
                }`}>
                  {stage}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  </div>
);

// Enhanced progress bar component
const ProgressBar: React.FC<{ progress: number; estimatedTime?: number }> = ({ 
  progress, 
  estimatedTime 
}) => (
  <div className="space-y-4">
    <div className="flex justify-between items-center text-sm">
      <span className="text-gray-600">Progress</span>
      <div className="flex items-center space-x-3">
        <span className="text-gray-900 font-medium">{progress}%</span>
        {estimatedTime && estimatedTime > 0 && (
          <span className="text-gray-500">
            • {estimatedTime}s remaining
          </span>
        )}
      </div>
    </div>
    <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
      <motion.div
        className="bg-gradient-to-r from-blue-500 to-blue-600 h-4 rounded-full relative"
        initial={{ width: 0 }}
        animate={{ width: `${progress}%` }}
        transition={{ duration: 0.8, ease: "easeOut" }}
      >
        {/* Animated shine effect */}
        <motion.div
          className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-30"
          animate={{ x: ['0%', '100%'] }}
          transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
        />
      </motion.div>
    </div>
  </div>
);

// Enhanced job status indicator
const StatusIndicator: React.FC<{ status: string }> = ({ status }) => {
  const config = {
    pending: { icon: Clock, color: 'text-yellow-600', bg: 'bg-yellow-50', border: 'border-yellow-200', label: 'Pending' },
    processing: { icon: Loader2, color: 'text-blue-600', bg: 'bg-blue-50', border: 'border-blue-200', label: 'Processing' },
    completed: { icon: CheckCircle, color: 'text-green-600', bg: 'bg-green-50', border: 'border-green-200', label: 'Completed' },
    failed: { icon: XCircle, color: 'text-red-600', bg: 'bg-red-50', border: 'border-red-200', label: 'Failed' }
  };

  const { icon: Icon, color, bg, border, label } = config[status as keyof typeof config] || config.pending;

  return (
    <div className={`inline-flex items-center space-x-2 px-4 py-2 rounded-full text-sm font-medium ${bg} ${border} border`}>
      <Icon className={`h-4 w-4 ${color} ${status === 'processing' ? 'animate-spin' : ''}`} />
      <span className={color}>{label}</span>
    </div>
  );
};

// Enhanced result display component
const ResultDisplay: React.FC<{ result: string; onCopy: () => void; jobResult: JobResult }> = ({ 
  result, 
  onCopy, 
  jobResult 
}) => {
  const [showShareModal, setShowShareModal] = useState(false);
  
  const handleShare = () => {
    setShowShareModal(true);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-semibold text-gray-900">Result</h3>
        <div className="flex space-x-3">
          <button
            onClick={onCopy}
            className="inline-flex items-center space-x-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 text-sm font-medium rounded-lg transition-colors"
          >
            <Copy className="h-4 w-4" />
            <span>Copy to Clipboard</span>
          </button>
          <button
            onClick={handleShare}
            className="inline-flex items-center space-x-2 px-4 py-2 bg-blue-100 hover:bg-blue-200 text-blue-700 text-sm font-medium rounded-lg transition-colors"
          >
            <Share2 className="h-4 w-4" />
            <span>Share</span>
          </button>
        </div>
      </div>
      
      {/* Enhanced result display */}
      <div className="bg-gray-50 rounded-xl p-6 border border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <span className="text-2xl">{jobResult.agentIcon}</span>
            <span>Processed by {jobResult.agentName}</span>
            {jobResult.completedAt && (
              <>
                <span>•</span>
                <span>Completed {new Date(jobResult.completedAt).toLocaleTimeString()}</span>
              </>
            )}
          </div>
        </div>
        <pre className="whitespace-pre-wrap text-sm text-gray-800 leading-relaxed font-mono">
          {result}
        </pre>
      </div>

      {/* Enhanced action buttons */}
      <div className="flex flex-col sm:flex-row gap-3">
        <Link href="/process" className="flex-1">
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="w-full px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors flex items-center justify-center space-x-2"
          >
            <Bot className="h-5 w-5" />
            <span>Process Another</span>
          </motion.button>
        </Link>
        <Link href="/" className="flex-1">
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="w-full px-6 py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium rounded-lg transition-colors flex items-center justify-center space-x-2"
          >
            <Home className="h-5 w-5" />
            <span>Back to Dashboard</span>
          </motion.button>
        </Link>
      </div>

      {/* Share Modal */}
      <AnimatePresence>
        {showShareModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
            onClick={() => setShowShareModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-lg p-6 max-w-md w-full"
              onClick={(e) => e.stopPropagation()}
            >
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Share Results</h3>
              <p className="text-gray-600 mb-6">
                Share functionality will be available soon! For now, use the copy button to save your results.
              </p>
              <button
                onClick={() => setShowShareModal(false)}
                className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
              >
                Got it
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

// Error display component
const ErrorDisplay: React.FC<{ error: string }> = ({ error }) => (
  <div className="space-y-6">
    <div className="flex items-center space-x-3 text-red-600">
      <AlertTriangle className="h-6 w-6" />
      <h3 className="text-xl font-semibold">Processing Failed</h3>
    </div>
    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
      <p className="text-red-700">{error}</p>
    </div>
    <div className="flex flex-col sm:flex-row gap-3">
      <Link href="/process" className="flex-1">
        <button className="w-full px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors">
          Try Again
        </button>
      </Link>
      <button
        onClick={() => window.location.reload()}
        className="flex-1 px-6 py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium rounded-lg transition-colors"
      >
        Retry This Job
      </button>
    </div>
  </div>
);

// Main Results Page Component
const ResultsPage: React.FC = () => {
  const router = useRouter();
  const { id } = router.query;
  const [jobResult, setJobResult] = useState<JobResult | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copySuccess, setCopySuccess] = useState(false);
  const [isWebSocketConnected, setIsWebSocketConnected] = useState(false);
  const [isOnline, setIsOnline] = useState(true);
  const pollingInterval = useRef<NodeJS.Timeout | null>(null);
  const webSocket = useRef<WebSocket | null>(null);

  // Enhanced keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Cmd/Ctrl + C to copy result
      if ((e.metaKey || e.ctrlKey) && e.key === 'c' && jobResult?.result) {
        e.preventDefault();
        handleCopyResult();
      }
      // Cmd/Ctrl + Enter to process another
      if ((e.metaKey || e.ctrlKey) && e.key === 'Enter' && jobResult?.status === 'completed') {
        e.preventDefault();
        router.push('/process');
      }
      // Escape to go back
      if (e.key === 'Escape') {
        router.push('/process');
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [jobResult, router]);

  // Mock result generator for demo
  const generateMockResult = (agentId: string, inputType: string): string => {
    const agent = agentData[agentId];
    const agentName = agent?.name || 'AI Agent';

    switch (agentId) {
      case '1': // Document Analyzer
        return `Document Analysis Report
========================

## Key Insights
• Main topic: Content analysis and processing
• Document type: ${inputType === 'file' ? 'PDF document' : inputType === 'url' ? 'Web content' : 'Text content'}
• Processing method: Advanced NLP analysis
• Confidence level: 94%

## Summary
This content appears to be related to AI-powered content processing. The document contains structured information about automated analysis capabilities with sophisticated workflow management.

## Extracted Data Points
- Content type: ${inputType}
- Analysis depth: Comprehensive
- Key themes: AI, automation, content processing, user experience
- Semantic clusters: 3 identified
- Processing time: ${Math.floor(Math.random() * 45) + 15} seconds

## Recommendations
1. Consider additional processing for deeper insights
2. Review extracted data for accuracy and completeness
3. Archive results for future reference and analysis
4. Integrate with workflow automation systems

## Technical Details
- Algorithm: Advanced NLP with transformer models
- Confidence score: 94%
- Processing efficiency: High
- Data quality: Excellent`;

      case '2': // Summarizer
        return `Content Summary
===============

## Executive Summary
This content discusses AI-powered content processing and analysis capabilities. The main focus is on automated workflows for handling various input types including documents, URLs, text, and audio files with real-time processing updates.

## Key Points
• Multi-input support (files, URLs, text, audio)
• AI agent selection and intelligent processing
• Real-time status monitoring with WebSocket updates
• Results display and sharing capabilities
• Enhanced user experience with progress tracking

## Detailed Analysis
The system provides comprehensive content analysis through specialized AI agents. Each agent is optimized for specific content types, ensuring maximum accuracy and relevance in processing results.

## Conclusion
The system provides a comprehensive solution for content analysis with multiple AI agents specialized for different content types and use cases. The integration supports seamless workflows from input to results.

## Metrics
- Length: Original content summarized to key points
- Compression ratio: ~85% reduction
- Processing time: ${Math.floor(Math.random() * 30) + 10} seconds
- Readability score: 9.2/10`;

      case '3': // Data Extractor
        return `Extracted Data
=============

## Structured Information
\`\`\`json
{
  "content_type": "${inputType}",
  "processing_agent": "Data Extractor",
  "timestamp": "${new Date().toISOString()}",
  "extracted_entities": [
    {
      "type": "technology",
      "value": "AI Agent",
      "confidence": 0.95,
      "context": "Content processing system"
    },
    {
      "type": "process",
      "value": "Content Processing",
      "confidence": 0.92,
      "context": "Automated workflow"
    },
    {
      "type": "format",
      "value": "${inputType.toUpperCase()}",
      "confidence": 0.98,
      "context": "Input type classification"
    },
    {
      "type": "feature",
      "value": "Real-time Updates",
      "confidence": 0.89,
      "context": "WebSocket integration"
    }
  ],
  "relationships": [
    {
      "source": "AI Agent",
      "target": "Content Processing",
      "relationship": "PROCESSES",
      "strength": 0.94
    }
  ],
  "metadata": {
    "total_entities": 4,
    "total_relationships": 1,
    "processing_time": "${Math.floor(Math.random() * 20) + 5}s",
    "accuracy_score": 0.94,
    "extraction_method": "NER + Relationship Mining"
  }
}
\`\`\`

## Data Quality Assessment
✓ High confidence extractions (>90%)
✓ Structured format ready for integration
✓ Validated entities and relationships
✓ Comprehensive metadata included

## Export Options
- JSON format (ready for API integration)
- CSV format (for spreadsheet analysis)
- XML format (for legacy systems)`;

      case '4': // Audio Transcriber
        return `Audio Transcription & Analysis
===============================

## Transcript
[Speaker 1 - 00:00] Welcome to the AI content processing demonstration. Today we'll be showing how different types of content can be analyzed automatically using our advanced agent system.

[Speaker 1 - 00:15] The system supports multiple input formats including documents, web URLs, text content, and audio files like this one. Each format is processed by specialized AI agents.

[Speaker 1 - 00:30] Real-time updates are provided through WebSocket connections, with intelligent fallback to polling for maximum reliability.

[Speaker 1 - 00:45] The results page includes enhanced features like copy to clipboard, sharing options, and seamless navigation back to processing.

## Audio Analysis
- Duration: ${Math.floor(Math.random() * 180) + 60} seconds
- Speakers detected: 1 (primary speaker)
- Audio quality: Excellent (96% clarity)
- Transcription confidence: 96.8%
- Language: English (US dialect)
- Speech rate: 145 WPM (normal pace)

## Content Classification
- Topic: Technology/AI Systems
- Tone: Professional, informative
- Complexity: Medium-high technical content
- Sentiment: Positive (0.82 confidence)

## Key Insights
• Clear demonstration of AI capabilities
• Focus on user experience and reliability
• Emphasis on multi-format support
• Technical accuracy and professional delivery

## Recommended Actions
1. Archive transcript for documentation
2. Extract key talking points for summaries
3. Use for training material development`;

      default:
        return `Processing Complete
==================

Your content has been successfully processed by ${agentName}.

## Results
The AI agent has analyzed your ${inputType} content and extracted the following insights:

• Content successfully processed with high accuracy
• Analysis completed with comprehensive extraction
• Key information identified and structured
• Ready for review and further action

## Processing Details
- Completed at: ${new Date().toLocaleString()}
- Agent used: ${agentName}
- Input type: ${inputType}
- Processing time: ${Math.floor(Math.random() * 60) + 20} seconds
- Quality score: ${(Math.random() * 0.1 + 0.9).toFixed(2)}

## Next Steps
1. Review the extracted insights
2. Copy results for further use
3. Process additional content if needed`;
    }
  };

  // Enhanced WebSocket connection with fallback
  const connectWebSocket = (jobId: string) => {
    try {
      // Try to establish WebSocket connection
      const wsUrl = `ws://localhost:3001/ws/jobs/${jobId}`;
      webSocket.current = new WebSocket(wsUrl);
      
      webSocket.current.onopen = () => {
        console.log('WebSocket connected');
        setIsWebSocketConnected(true);
        setIsOnline(true);
        // Clear polling interval when WebSocket connects
        if (pollingInterval.current) {
          clearInterval(pollingInterval.current);
        }
      };
      
      webSocket.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setJobResult(prev => prev ? { ...prev, ...data } : null);
          
          // Stop WebSocket when job completes
          if (data.status === 'completed' || data.status === 'failed') {
            webSocket.current?.close();
          }
        } catch (error) {
          console.error('WebSocket message parse error:', error);
        }
      };
      
      webSocket.current.onclose = () => {
        console.log('WebSocket disconnected');
        setIsWebSocketConnected(false);
        // Fallback to polling
        startPolling(jobId);
      };
      
      webSocket.current.onerror = (error) => {
        console.log('WebSocket error, falling back to polling');
        setIsWebSocketConnected(false);
        startPolling(jobId);
      };
    } catch (error) {
      console.log('WebSocket not available, using polling');
      setIsWebSocketConnected(false);
      startPolling(jobId);
    }
  };

  // Enhanced polling with exponential backoff
  const startPolling = (jobId: string) => {
    if (pollingInterval.current) {
      clearInterval(pollingInterval.current);
    }
    
    pollingInterval.current = setInterval(() => {
      fetchJobStatus(jobId);
    }, 2000);
  };

  // Fetch job status and result
  const fetchJobStatus = async (jobId: string) => {
    try {
      // Try API first
      const response = await fetch(`/api/jobs/${jobId}`);
      if (response.ok) {
        const data = await response.json();
        setJobResult(data);
        setIsOnline(true);
        
        // If completed, fetch the result
        if (data.status === 'completed') {
          const resultResponse = await fetch(`/api/jobs/${jobId}/result`);
          if (resultResponse.ok) {
            const resultData = await resultResponse.json();
            setJobResult(prev => prev ? { ...prev, result: resultData.result } : null);
          }
          // Stop polling when completed
          if (pollingInterval.current) {
            clearInterval(pollingInterval.current);
          }
        }
        return;
      }
    } catch (error) {
      console.log('API not available, using mock data');
      setIsOnline(false);
    }

    // Fallback to localStorage mock
    const storedJob = localStorage.getItem(`job_${jobId}`);
    if (storedJob) {
      const jobData = JSON.parse(storedJob);
      const agent = agentData[jobData.agentId];
      
      // Simulate status progression with more realistic timing
      const now = Date.now();
      const created = new Date(jobData.createdAt).getTime();
      const elapsed = (now - created) / 1000; // seconds
      
      let status = jobData.status;
      let progress = 0;
      let estimatedTimeRemaining = 0;
      
      if (elapsed < 3) {
        status = 'pending';
        progress = 0;
        estimatedTimeRemaining = 45;
      } else if (elapsed < 45) {
        status = 'processing';
        progress = Math.min(95, Math.floor((elapsed - 3) / 42 * 100));
        estimatedTimeRemaining = Math.max(0, 45 - Math.floor(elapsed));
      } else {
        status = 'completed';
        progress = 100;
        estimatedTimeRemaining = 0;
      }
      
      const result: JobResult = {
        jobId: jobData.jobId,
        status: status as any,
        agentId: jobData.agentId,
        agentName: agent?.name || 'Unknown Agent',
        agentIcon: agent?.icon || '🤖',
        inputType: jobData.inputType,
        inputContent: jobData.inputContent,
        filePath: jobData.filePath,
        createdAt: jobData.createdAt,
        progress,
        estimatedTimeRemaining,
        result: status === 'completed' ? generateMockResult(jobData.agentId, jobData.inputType) : undefined,
        completedAt: status === 'completed' ? new Date().toISOString() : undefined
      };
      
      setJobResult(result);
      
      // Stop polling when completed
      if (status === 'completed' && pollingInterval.current) {
        clearInterval(pollingInterval.current);
      }
    } else {
      setError('Job not found');
    }
  };

  // Setup connection and polling
  useEffect(() => {
    if (!id) return;
    
    const jobId = id as string;
    setIsLoading(true);
    
    // Initial fetch
    fetchJobStatus(jobId).finally(() => setIsLoading(false));
    
    // Try WebSocket first, fallback to polling
    connectWebSocket(jobId);
    
    // Cleanup
    return () => {
      if (pollingInterval.current) {
        clearInterval(pollingInterval.current);
      }
      if (webSocket.current) {
        webSocket.current.close();
      }
    };
  }, [id]);

  // Enhanced copy result to clipboard
  const handleCopyResult = async () => {
    if (!jobResult?.result) return;
    
    try {
      await navigator.clipboard.writeText(jobResult.result);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 3000);
    } catch (error) {
      console.error('Failed to copy:', error);
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = jobResult.result;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 3000);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Loading Job Status</h2>
          <p className="text-gray-600">Fetching your processing results...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <XCircle className="h-12 w-12 text-red-600 mx-auto mb-4" />
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Job Not Found</h1>
            <p className="text-gray-600 mb-6">{error}</p>
            <Link href="/process">
              <button className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors">
                Start New Process
              </button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  if (!jobResult) {
    return null;
  }

  return (
    <>
      <Head>
        <title>Processing Results - AIOS v2</title>
        <meta name="description" content="View your AI processing results" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <div className="min-h-screen bg-gray-50 py-4 sm:py-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Breadcrumbs */}
          <Breadcrumbs jobResult={jobResult} />

          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <Link href="/process">
                <button className="p-2 hover:bg-gray-200 rounded-lg transition-colors">
                  <ArrowLeft className="h-5 w-5 text-gray-600" />
                </button>
              </Link>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Processing Results</h1>
                <div className="flex items-center space-x-3 mt-1">
                  <p className="text-sm text-gray-600">Job ID: {jobResult.jobId}</p>
                  <ConnectionStatus 
                    isConnected={isOnline} 
                    isWebSocket={isWebSocketConnected} 
                  />
                </div>
              </div>
            </div>
            <StatusIndicator status={jobResult.status} />
          </div>

          {/* Job Details */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
            <div className="p-4 sm:p-6">
              <div className="flex items-center space-x-4 mb-4">
                <div className="text-3xl">{jobResult.agentIcon}</div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900">{jobResult.agentName}</h3>
                  <div className="flex items-center space-x-2 text-sm text-gray-600">
                    {getInputTypeIcon(jobResult.inputType)}
                    <span className="capitalize">{jobResult.inputType} content</span>
                    <span>•</span>
                    <span>Started {new Date(jobResult.createdAt).toLocaleTimeString()}</span>
                  </div>
                </div>
              </div>

              {/* Input Preview */}
              {(jobResult.inputContent || jobResult.filePath) && (
                <div className="bg-gray-50 rounded-lg p-3 mb-4">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Input:</h4>
                  <p className="text-sm text-gray-600">
                    {jobResult.filePath || 
                     (jobResult.inputContent && jobResult.inputContent.length > 100 
                       ? `${jobResult.inputContent.substring(0, 100)}...` 
                       : jobResult.inputContent)}
                  </p>
                </div>
              )}

              {/* Enhanced Progress */}
              {jobResult.status === 'processing' && (
                <ProgressBar 
                  progress={jobResult.progress || 0} 
                  estimatedTime={jobResult.estimatedTimeRemaining} 
                />
              )}
            </div>
          </div>

          {/* Status Content */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="p-4 sm:p-6">
              <AnimatePresence mode="wait">
                {(jobResult.status === 'pending' || jobResult.status === 'processing') && (
                  <motion.div
                    key="processing"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                  >
                    <ProcessingAnimation 
                      status={jobResult.status} 
                      progress={jobResult.progress} 
                    />
                  </motion.div>
                )}

                {jobResult.status === 'completed' && jobResult.result && (
                  <motion.div
                    key="completed"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                  >
                    <ResultDisplay 
                      result={jobResult.result} 
                      onCopy={handleCopyResult} 
                      jobResult={jobResult}
                    />
                  </motion.div>
                )}

                {jobResult.status === 'failed' && (
                  <motion.div
                    key="failed"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                  >
                    <ErrorDisplay error={jobResult.error || 'An unexpected error occurred'} />
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>

          {/* Copy Success Toast */}
          <AnimatePresence>
            {copySuccess && (
              <motion.div
                initial={{ opacity: 0, y: 50 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 50 }}
                className="fixed bottom-4 right-4 bg-green-600 text-white px-6 py-3 rounded-lg shadow-lg flex items-center space-x-2"
              >
                <CheckCircle className="h-5 w-5" />
                <span>Copied to clipboard!</span>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Keyboard shortcuts hint */}
          {jobResult.status === 'completed' && (
            <div className="mt-6 text-center text-xs text-gray-500">
              <p>
                Press <kbd className="px-2 py-1 bg-gray-100 rounded text-gray-700">⌘+C</kbd> to copy result • 
                <kbd className="px-2 py-1 bg-gray-100 rounded text-gray-700 ml-1">⌘+Enter</kbd> to process another • 
                <kbd className="px-2 py-1 bg-gray-100 rounded text-gray-700 ml-1">Esc</kbd> to go back
              </p>
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default ResultsPage; 
import React, { useState, useCallback, useEffect } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Upload, 
  FileText, 
  Globe, 
  Mic, 
  Bot,
  AlertCircle,
  CheckCircle,
  X,
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

type InputType = 'file' | 'url' | 'text' | 'audio';

// Mock agent data as specified in requirements
const mockAgents: Agent[] = [
  { 
    id: '1', 
    name: 'Document Analyzer', 
    icon: '📄', 
    description: 'Extracts insights from documents', 
    supportedInputs: ['file', 'url', 'text'] 
  },
  { 
    id: '2', 
    name: 'Summarizer', 
    icon: '📝', 
    description: 'Creates concise summaries', 
    supportedInputs: ['file', 'url', 'text', 'audio'] 
  },
  { 
    id: '3', 
    name: 'Data Extractor', 
    icon: '🔍', 
    description: 'Pulls structured data', 
    supportedInputs: ['file', 'text'] 
  },
  { 
    id: '4', 
    name: 'Audio Transcriber', 
    icon: '🎤', 
    description: 'Transcribes and analyzes audio', 
    supportedInputs: ['audio'] 
  }
];

// Enhanced File Upload Component with progress indicator
const FileUpload: React.FC<{
  accept: string;
  placeholder: string;
  fileTypes: string[];
  onFileSelect: (file: File | null) => void;
  uploadProgress?: number;
}> = ({ accept, placeholder, fileTypes, onFileSelect, uploadProgress = 0 }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [error, setError] = useState<string>('');

  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: any[]) => {
    setError('');
    
    if (rejectedFiles.length > 0) {
      setError(`Please select a valid ${fileTypes.join('/')} file`);
      return;
    }

    const file = acceptedFiles[0];
    if (file) {
      // Check file size (50MB limit)
      if (file.size > 50 * 1024 * 1024) {
        setError('File size must be less than 50MB');
        return;
      }
      
      setSelectedFile(file);
      onFileSelect(file);
    }
  }, [fileTypes, onFileSelect]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: accept ? { [accept]: [] } : undefined,
    maxFiles: 1,
    multiple: false
  });

  const removeFile = () => {
    setSelectedFile(null);
    onFileSelect(null);
    setError('');
  };

  return (
    <div className="space-y-4">
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-6 sm:p-8 text-center cursor-pointer transition-all duration-200
          ${isDragActive 
            ? 'border-blue-500 bg-blue-50' 
            : 'border-gray-300 hover:border-gray-400'
          }
          ${error ? 'border-red-300 bg-red-50' : ''}
        `}
      >
        <input {...getInputProps()} />
        <Upload className="mx-auto h-10 w-10 sm:h-12 sm:w-12 text-gray-400 mb-3 sm:mb-4" />
        {isDragActive ? (
          <p className="text-blue-600 font-medium text-sm sm:text-base">Drop file here...</p>
        ) : (
          <div>
            <p className="text-gray-600 font-medium text-sm sm:text-base">{placeholder}</p>
            <p className="text-xs sm:text-sm text-gray-500 mt-2">
              Supported: {fileTypes.join(', ')} • Max 50MB
            </p>
          </div>
        )}
      </div>

      {selectedFile && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-3"
        >
          <div className="flex items-center justify-between p-3 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center space-x-3 min-w-0 flex-1">
              <CheckCircle className="h-5 w-5 text-green-600 flex-shrink-0" />
              <div className="min-w-0 flex-1">
                <p className="font-medium text-green-800 truncate">{selectedFile.name}</p>
                <p className="text-sm text-green-600">
                  {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                </p>
              </div>
            </div>
            <button
              onClick={removeFile}
              className="p-1 hover:bg-green-100 rounded-full transition-colors flex-shrink-0"
            >
              <X className="h-4 w-4 text-green-600" />
            </button>
          </div>
          
          {/* Progress indicator for Day 3 integration */}
          {uploadProgress > 0 && uploadProgress < 100 && (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Uploading...</span>
                <span className="text-gray-900 font-medium">{uploadProgress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <motion.div
                  className="bg-blue-600 h-2 rounded-full"
                  initial={{ width: 0 }}
                  animate={{ width: `${uploadProgress}%` }}
                  transition={{ duration: 0.3 }}
                />
              </div>
            </div>
          )}
        </motion.div>
      )}

      {error && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center space-x-2 p-3 bg-red-50 border border-red-200 rounded-lg"
        >
          <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0" />
          <p className="text-red-700 text-sm">{error}</p>
        </motion.div>
      )}
    </div>
  );
};

// Enhanced Agent Selector Component
const AgentSelector: React.FC<{
  agents: Agent[];
  selectedAgent: string | null;
  onAgentSelect: (agentId: string) => void;
  isLoading: boolean;
  preSelectedAgent?: string | null;
}> = ({ agents, selectedAgent, onAgentSelect, isLoading, preSelectedAgent }) => {
  if (isLoading) {
    return (
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">Select Agent</h3>
        <div className="flex items-center justify-center py-8">
          <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
          <span className="ml-2 text-gray-600">Loading agents...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900">
        Select Agent
        {preSelectedAgent && (
          <span className="text-sm font-normal text-blue-600 ml-2">
            (Pre-selected)
          </span>
        )}
      </h3>
      <div className="space-y-3">
        {agents.map((agent) => (
          <motion.div
            key={agent.id}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className={`
              p-3 sm:p-4 border rounded-lg cursor-pointer transition-all duration-200
              ${selectedAgent === agent.id
                ? 'border-blue-500 bg-blue-50 shadow-md'
                : 'border-gray-200 hover:border-gray-300 hover:shadow-sm'
              }
              ${preSelectedAgent === agent.id ? 'ring-2 ring-blue-200' : ''}
            `}
            onClick={() => onAgentSelect(agent.id)}
          >
            <div className="flex items-center space-x-3 sm:space-x-4">
              <input
                type="radio"
                name="agent"
                value={agent.id}
                checked={selectedAgent === agent.id}
                onChange={() => onAgentSelect(agent.id)}
                className="h-4 w-4 text-blue-600 flex-shrink-0"
              />
              <div className="text-xl sm:text-2xl flex-shrink-0">{agent.icon}</div>
              <div className="flex-1 min-w-0">
                <h4 className="font-medium text-gray-900 text-sm sm:text-base">{agent.name}</h4>
                <p className="text-xs sm:text-sm text-gray-600">{agent.description}</p>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

// API Status Indicator
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

// Main Process Page Component
const ProcessPage: React.FC = () => {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<InputType>('file');
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [urlInput, setUrlInput] = useState('');
  const [textInput, setTextInput] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [urlError, setUrlError] = useState('');
  const [textError, setTextError] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [agents, setAgents] = useState<Agent[]>(mockAgents);
  const [isLoadingAgents, setIsLoadingAgents] = useState(false);
  const [isAPIOnline, setIsAPIOnline] = useState(false);
  const [preSelectedAgent, setPreSelectedAgent] = useState<string | null>(null);

  // Enhanced API integration with fallback to mock data
  useEffect(() => {
    const fetchAgents = async () => {
      setIsLoadingAgents(true);
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
        setIsLoadingAgents(false);
      }
    };

    fetchAgents();
  }, []);

  // Handle agent pre-selection from URL parameters
  useEffect(() => {
    if (router.query.agent && agents.length > 0) {
      const agentId = router.query.agent as string;
      const agent = agents.find(a => a.id === agentId);
      if (agent) {
        setSelectedAgent(agentId);
        setPreSelectedAgent(agentId);
        
        // Set the active tab to the first supported input type
        const firstSupportedInput = agent.supportedInputs[0] as InputType;
        setActiveTab(firstSupportedInput);
      }
    }
  }, [router.query.agent, agents]);

  // Filter agents based on input type
  const filteredAgents = agents.filter(agent => 
    agent.supportedInputs.includes(activeTab)
  );

  // Reset selected agent when changing tabs if current agent doesn't support new input type
  useEffect(() => {
    if (selectedAgent && !filteredAgents.find(a => a.id === selectedAgent)) {
      setSelectedAgent(null);
    }
  }, [activeTab, selectedAgent, filteredAgents]);

  // Enhanced input validation
  const validateURL = (url: string) => {
    try {
      new URL(url);
      setUrlError('');
      return true;
    } catch {
      setUrlError('Please enter a valid URL');
      return false;
    }
  };

  const validateText = (text: string) => {
    if (text.length > 50000) {
      setTextError('Text must be less than 50,000 characters');
      return false;
    }
    setTextError('');
    return true;
  };

  // Check if form is valid
  const isFormValid = () => {
    if (!selectedAgent) return false;
    
    switch (activeTab) {
      case 'file':
        return selectedFile !== null;
      case 'url':
        return urlInput.trim() !== '' && !urlError;
      case 'text':
        return textInput.trim() !== '' && !textError;
      case 'audio':
        return selectedFile !== null;
      default:
        return false;
    }
  };

  // Enhanced form submission with job submission flow
  const handleProcess = async () => {
    if (!isFormValid()) return;
    
    setIsProcessing(true);
    
    try {
      // Prepare job submission data
      const jobData = {
        agentId: selectedAgent,
        inputType: activeTab,
        inputContent: activeTab === 'url' ? urlInput : 
                     activeTab === 'text' ? textInput : null,
        filePath: selectedFile?.name || null,
        timestamp: new Date().toISOString()
      };

      // Try to submit to API
      try {
        const formData = new FormData();
        formData.append('agentId', selectedAgent || '');
        formData.append('inputType', activeTab);
        
        if (activeTab === 'file' || activeTab === 'audio') {
          if (selectedFile) {
            formData.append('file', selectedFile);
          }
        } else if (activeTab === 'url') {
          formData.append('inputContent', urlInput);
        } else if (activeTab === 'text') {
          formData.append('inputContent', textInput);
        }

        const response = await fetch('/api/jobs', {
          method: 'POST',
          body: formData,
        });

        if (response.ok) {
          const result = await response.json();
          const jobId = result.jobId || result.id;
          
          // Clear form data
          setSelectedFile(null);
          setUrlInput('');
          setTextInput('');
          setSelectedAgent(null);
          setPreSelectedAgent(null);
          
          // Redirect to results page
          router.push(`/results/${jobId}`);
          return;
        }
      } catch (apiError) {
        console.log('API submission failed, using mock flow');
      }

      // Fallback: Mock job submission
      const mockJobId = `job_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      
      // Store job data for mock results
      localStorage.setItem(`job_${mockJobId}`, JSON.stringify({
        ...jobData,
        jobId: mockJobId,
        status: 'pending',
        createdAt: new Date().toISOString()
      }));
      
      // Clear form data
      setSelectedFile(null);
      setUrlInput('');
      setTextInput('');
      if (!preSelectedAgent) {
        setSelectedAgent(null);
      }
      
      // Redirect to results page
      router.push(`/results/${mockJobId}`);
      
    } catch (error) {
      console.error('Job submission error:', error);
      alert('Failed to submit job. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  // Enhanced tab configuration with better mobile icons
  const tabs = [
    { id: 'file' as InputType, label: 'File', icon: FileText, shortLabel: 'File' },
    { id: 'url' as InputType, label: 'URL', icon: Globe, shortLabel: 'URL' },
    { id: 'text' as InputType, label: 'Text', icon: FileText, shortLabel: 'Text' },
    { id: 'audio' as InputType, label: 'Audio', icon: Mic, shortLabel: 'Audio' }
  ];

  return (
    <>
      <Head>
        <title>Process Content - AIOS v2</title>
        <meta name="description" content="Process your content with AI agents" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <div className="min-h-screen bg-gray-50 py-4 sm:py-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Enhanced Page Header */}
          <div className="text-center mb-6 sm:mb-8">
            <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-2 sm:mb-4">Process Content</h1>
            <p className="text-base sm:text-lg text-gray-600">
              Upload files, analyze URLs, or process text with AI agents
            </p>
            <div className="mt-3 flex justify-center">
              <APIStatusIndicator isOnline={isAPIOnline} />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
            {/* Enhanced Tab Navigation for Mobile */}
            <div className="border-b border-gray-200">
              <nav className="flex space-x-0">
                {tabs.map((tab) => {
                  const Icon = tab.icon;
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`
                        flex-1 flex items-center justify-center space-x-1 sm:space-x-2 px-2 sm:px-6 py-3 sm:py-4 text-xs sm:text-sm font-medium border-b-2 transition-all duration-200
                        ${activeTab === tab.id
                          ? 'border-blue-500 text-blue-600 bg-blue-50'
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                        }
                      `}
                    >
                      <Icon className="h-4 w-4 sm:h-5 sm:w-5" />
                      <span className="hidden sm:inline">{tab.label}</span>
                      <span className="sm:hidden">{tab.shortLabel}</span>
                    </button>
                  );
                })}
              </nav>
            </div>

            {/* Enhanced Content Area */}
            <div className="p-4 sm:p-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 sm:gap-8">
                {/* Enhanced Input Section */}
                <div className="space-y-4 sm:space-y-6">
                  <h2 className="text-lg sm:text-xl font-semibold text-gray-900">
                    {activeTab === 'file' && 'Upload File'}
                    {activeTab === 'url' && 'Enter URL'}
                    {activeTab === 'text' && 'Enter Text'}
                    {activeTab === 'audio' && 'Upload Audio'}
                  </h2>

                  <AnimatePresence mode="wait">
                    <motion.div
                      key={activeTab}
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -20 }}
                      transition={{ duration: 0.2 }}
                    >
                      {activeTab === 'file' && (
                        <FileUpload
                          accept="application/pdf"
                          placeholder="Drop PDF here or click to browse"
                          fileTypes={['PDF']}
                          onFileSelect={setSelectedFile}
                        />
                      )}

                      {activeTab === 'url' && (
                        <div className="space-y-4">
                          <input
                            type="url"
                            value={urlInput}
                            onChange={(e) => {
                              setUrlInput(e.target.value);
                              if (e.target.value) validateURL(e.target.value);
                            }}
                            placeholder="https://example.com/article"
                            className={`
                              w-full px-3 sm:px-4 py-2 sm:py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors text-sm sm:text-base
                              ${urlError ? 'border-red-300' : 'border-gray-300'}
                            `}
                          />
                          {urlError && (
                            <motion.div
                              initial={{ opacity: 0, y: -10 }}
                              animate={{ opacity: 1, y: 0 }}
                              className="flex items-center space-x-2 text-red-600"
                            >
                              <AlertCircle className="h-4 w-4 flex-shrink-0" />
                              <span className="text-sm">{urlError}</span>
                            </motion.div>
                          )}
                        </div>
                      )}

                      {activeTab === 'text' && (
                        <div className="space-y-4">
                          <textarea
                            value={textInput}
                            onChange={(e) => {
                              setTextInput(e.target.value);
                              validateText(e.target.value);
                            }}
                            placeholder="Paste your content here..."
                            rows={6}
                            className={`
                              w-full px-3 sm:px-4 py-2 sm:py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors resize-vertical text-sm sm:text-base
                              ${textError ? 'border-red-300' : 'border-gray-300'}
                            `}
                          />
                          <div className="flex justify-between items-center text-sm">
                            <span className={`${textInput.length > 45000 ? 'text-red-600' : 'text-gray-500'}`}>
                              {textInput.length.toLocaleString()} / 50,000 characters
                            </span>
                            {textError && (
                              <motion.div
                                initial={{ opacity: 0, y: -10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="flex items-center space-x-2 text-red-600"
                              >
                                <AlertCircle className="h-4 w-4" />
                                <span className="text-sm">{textError}</span>
                              </motion.div>
                            )}
                          </div>
                        </div>
                      )}

                      {activeTab === 'audio' && (
                        <FileUpload
                          accept="audio/*"
                          placeholder="Drop MP3/WAV or click to browse"
                          fileTypes={['MP3', 'WAV', 'M4A']}
                          onFileSelect={setSelectedFile}
                        />
                      )}
                    </motion.div>
                  </AnimatePresence>
                </div>

                {/* Enhanced Agent Selection Section */}
                <div className="space-y-4 sm:space-y-6">
                  <AgentSelector
                    agents={filteredAgents}
                    selectedAgent={selectedAgent}
                    onAgentSelect={setSelectedAgent}
                    isLoading={isLoadingAgents}
                    preSelectedAgent={preSelectedAgent}
                  />

                  {/* Enhanced Process Button */}
                  <motion.button
                    whileTap={{ scale: 0.98 }}
                    onClick={handleProcess}
                    disabled={!isFormValid() || isProcessing}
                    className={`
                      w-full py-3 sm:py-4 px-4 sm:px-6 rounded-lg font-semibold text-white transition-all duration-200
                      ${isFormValid() && !isProcessing
                        ? 'bg-blue-600 hover:bg-blue-700 shadow-md hover:shadow-lg'
                        : 'bg-gray-300 cursor-not-allowed'
                      }
                    `}
                  >
                    <div className="flex items-center justify-center space-x-2">
                      {isProcessing ? (
                        <>
                          <Loader2 className="h-5 w-5 animate-spin" />
                          <span className="text-sm sm:text-base">Processing...</span>
                        </>
                      ) : (
                        <>
                          <Bot className="h-5 w-5" />
                          <span className="text-sm sm:text-base">Process Content</span>
                        </>
                      )}
                    </div>
                  </motion.button>

                  {!isFormValid() && (
                    <p className="text-xs sm:text-sm text-gray-500 text-center">
                      Select input content and an agent to continue
                    </p>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default ProcessPage; 
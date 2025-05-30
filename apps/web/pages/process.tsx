import React, { useState, useCallback } from 'react';
import Head from 'next/head';
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
  X
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

// File Upload Component
const FileUpload: React.FC<{
  accept: string;
  placeholder: string;
  fileTypes: string[];
  onFileSelect: (file: File | null) => void;
}> = ({ accept, placeholder, fileTypes, onFileSelect }) => {
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
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all duration-200
          ${isDragActive 
            ? 'border-blue-500 bg-blue-50' 
            : 'border-gray-300 hover:border-gray-400'
          }
          ${error ? 'border-red-300 bg-red-50' : ''}
        `}
      >
        <input {...getInputProps()} />
        <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        {isDragActive ? (
          <p className="text-blue-600 font-medium">Drop file here...</p>
        ) : (
          <div>
            <p className="text-gray-600 font-medium">{placeholder}</p>
            <p className="text-sm text-gray-500 mt-2">
              Supported: {fileTypes.join(', ')} • Max 50MB
            </p>
          </div>
        )}
      </div>

      {selectedFile && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between p-3 bg-green-50 border border-green-200 rounded-lg"
        >
          <div className="flex items-center space-x-3">
            <CheckCircle className="h-5 w-5 text-green-600" />
            <div>
              <p className="font-medium text-green-800">{selectedFile.name}</p>
              <p className="text-sm text-green-600">
                {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
              </p>
            </div>
          </div>
          <button
            onClick={removeFile}
            className="p-1 hover:bg-green-100 rounded-full transition-colors"
          >
            <X className="h-4 w-4 text-green-600" />
          </button>
        </motion.div>
      )}

      {error && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center space-x-2 p-3 bg-red-50 border border-red-200 rounded-lg"
        >
          <AlertCircle className="h-5 w-5 text-red-600" />
          <p className="text-red-700">{error}</p>
        </motion.div>
      )}
    </div>
  );
};

// Agent Selector Component
const AgentSelector: React.FC<{
  agents: Agent[];
  selectedAgent: string | null;
  onAgentSelect: (agentId: string) => void;
}> = ({ agents, selectedAgent, onAgentSelect }) => {
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900">Select Agent</h3>
      <div className="space-y-3">
        {agents.map((agent) => (
          <motion.div
            key={agent.id}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className={`
              p-4 border rounded-lg cursor-pointer transition-all duration-200
              ${selectedAgent === agent.id
                ? 'border-blue-500 bg-blue-50 shadow-md'
                : 'border-gray-200 hover:border-gray-300 hover:shadow-sm'
              }
            `}
            onClick={() => onAgentSelect(agent.id)}
          >
            <div className="flex items-center space-x-4">
              <input
                type="radio"
                name="agent"
                value={agent.id}
                checked={selectedAgent === agent.id}
                onChange={() => onAgentSelect(agent.id)}
                className="h-4 w-4 text-blue-600"
              />
              <div className="text-2xl">{agent.icon}</div>
              <div className="flex-1">
                <h4 className="font-medium text-gray-900">{agent.name}</h4>
                <p className="text-sm text-gray-600">{agent.description}</p>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

// Main Process Page Component
const ProcessPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<InputType>('file');
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [urlInput, setUrlInput] = useState('');
  const [textInput, setTextInput] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [urlError, setUrlError] = useState('');
  const [textError, setTextError] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);

  // Filter agents based on input type
  const filteredAgents = mockAgents.filter(agent => 
    agent.supportedInputs.includes(activeTab)
  );

  // Reset selected agent when changing tabs if current agent doesn't support new input type
  React.useEffect(() => {
    if (selectedAgent && !filteredAgents.find(a => a.id === selectedAgent)) {
      setSelectedAgent(null);
    }
  }, [activeTab, selectedAgent, filteredAgents]);

  // Input validation
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

  // Handle form submission
  const handleProcess = async () => {
    setIsProcessing(true);
    
    // Mock processing delay
    setTimeout(() => {
      setIsProcessing(false);
      alert('Processing started! (This is a mock for Day 2)');
    }, 2000);
  };

  // Tab configuration
  const tabs = [
    { id: 'file' as InputType, label: 'File', icon: FileText },
    { id: 'url' as InputType, label: 'URL', icon: Globe },
    { id: 'text' as InputType, label: 'Text', icon: FileText },
    { id: 'audio' as InputType, label: 'Audio', icon: Mic }
  ];

  return (
    <>
      <Head>
        <title>Process Content - AIOS v2</title>
        <meta name="description" content="Process your content with AI agents" />
      </Head>

      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Page Header */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">Process Content</h1>
            <p className="text-lg text-gray-600">
              Upload files, analyze URLs, or process text with AI agents
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
            {/* Tab Navigation */}
            <div className="border-b border-gray-200">
              <nav className="flex space-x-0">
                {tabs.map((tab) => {
                  const Icon = tab.icon;
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`
                        flex-1 flex items-center justify-center space-x-2 px-6 py-4 text-sm font-medium border-b-2 transition-all duration-200
                        ${activeTab === tab.id
                          ? 'border-blue-500 text-blue-600 bg-blue-50'
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                        }
                      `}
                    >
                      <Icon className="h-5 w-5" />
                      <span>{tab.label}</span>
                    </button>
                  );
                })}
              </nav>
            </div>

            {/* Content Area */}
            <div className="p-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Input Section */}
                <div className="space-y-6">
                  <h2 className="text-xl font-semibold text-gray-900">
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
                              w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors
                              ${urlError ? 'border-red-300' : 'border-gray-300'}
                            `}
                          />
                          {urlError && (
                            <motion.div
                              initial={{ opacity: 0, y: -10 }}
                              animate={{ opacity: 1, y: 0 }}
                              className="flex items-center space-x-2 text-red-600"
                            >
                              <AlertCircle className="h-4 w-4" />
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
                            rows={8}
                            className={`
                              w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors resize-vertical
                              ${textError ? 'border-red-300' : 'border-gray-300'}
                            `}
                          />
                          <div className="flex justify-between items-center">
                            <span className={`text-sm ${textInput.length > 45000 ? 'text-red-600' : 'text-gray-500'}`}>
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

                {/* Agent Selection Section */}
                <div className="space-y-6">
                  <AgentSelector
                    agents={filteredAgents}
                    selectedAgent={selectedAgent}
                    onAgentSelect={setSelectedAgent}
                  />

                  {/* Process Button */}
                  <motion.button
                    whileTap={{ scale: 0.98 }}
                    onClick={handleProcess}
                    disabled={!isFormValid() || isProcessing}
                    className={`
                      w-full py-4 px-6 rounded-lg font-semibold text-white transition-all duration-200
                      ${isFormValid() && !isProcessing
                        ? 'bg-blue-600 hover:bg-blue-700 shadow-md hover:shadow-lg'
                        : 'bg-gray-300 cursor-not-allowed'
                      }
                    `}
                  >
                    <div className="flex items-center justify-center space-x-2">
                      {isProcessing ? (
                        <>
                          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                          <span>Processing...</span>
                        </>
                      ) : (
                        <>
                          <Bot className="h-5 w-5" />
                          <span>Process Content</span>
                        </>
                      )}
                    </div>
                  </motion.button>

                  {!isFormValid() && (
                    <p className="text-sm text-gray-500 text-center">
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

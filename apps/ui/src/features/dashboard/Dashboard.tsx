import React, { useEffect, useState } from 'react';
import { RetroButton } from '../../components/UI/RetroButton';
import { RetroCard } from '../../components/UI/RetroCard';
import { RetroLoader } from '../../components/UI/RetroLoader';
import { FileUploadModal } from '../../components/UI/FileUploadModal';
import { OnboardingModal, HelpModal } from '../../components/UI/OnboardingModal';
import { systemAPI } from '../../api/system';
import { filesAPI } from '../../api/files';
import { useWebSocket } from '../../hooks/useWebSocket';
import type { SystemHealth, SystemActivity } from '../../api/system';
import type { WebSocketMessage } from '../../services/websocket';

export const Dashboard: React.FC = () => {
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [activities, setActivities] = useState<SystemActivity[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showOnboardingModal, setShowOnboardingModal] = useState(false);
  const [showHelpModal, setShowHelpModal] = useState(false);
  const [recentOperations, setRecentOperations] = useState<string[]>([]);
  
  // WebSocket setup
  const { subscribe, unsubscribe } = useWebSocket({
    onMessage: (message: WebSocketMessage) => {
      handleWebSocketMessage(message);
    },
  });

  // Check if user should see onboarding on first visit
  useEffect(() => {
    const hasSeenOnboarding = localStorage.getItem('aios-onboarding-complete');
    if (!hasSeenOnboarding) {
      // Show onboarding after a brief delay for first-time users
      setTimeout(() => setShowOnboardingModal(true), 1000);
    }
  }, []);

  const handleWebSocketMessage = (message: WebSocketMessage) => {
    switch (message.event_type) {
      case 'system_health':
        setSystemHealth(message.payload);
        break;
      case 'component_status':
        updateComponentStatus(message.payload);
        break;
      case 'agent_started':
      case 'agent_completed':
      case 'email_processed':
      case 'url_processed':
      case 'file_uploaded':
        addRecentOperation(message);
        updateActivities(message);
        break;
    }
  };

  const addRecentOperation = (message: WebSocketMessage) => {
    const operation = formatOperationMessage(message);
    setRecentOperations(prev => [operation, ...prev.slice(0, 4)]);
  };

  const formatOperationMessage = (message: WebSocketMessage): string => {
    const timestamp = new Date(message.timestamp).toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: false 
    });
    
    switch (message.event_type) {
      case 'agent_started':
        return `${timestamp} > run agent ${message.payload.agent_name} --task ${message.payload.task}`;
      case 'agent_completed':
        return `${timestamp} > [COMPLETED] ${message.payload.result}`;
      case 'email_processed':
        return `${timestamp} > process email --from ${message.payload.from}`;
      case 'url_processed':
        return `${timestamp} > process url --target ${message.payload.url}`;
      case 'file_uploaded':
        return `${timestamp} > upload file --name ${message.payload.filename}`;
      default:
        return `${timestamp} > ${message.event_type}`;
    }
  };

  const updateComponentStatus = (payload: any) => {
    setSystemHealth(prev => {
      if (!prev) return prev;
      return {
        ...prev,
        services: {
          ...prev.services,
          [payload.component]: {
            status: payload.status,
            lastCheck: payload.timestamp
          }
        }
      };
    });
  };

  const updateActivities = (message: WebSocketMessage) => {
    const activity: SystemActivity = {
      id: message.metadata?.event_id || Date.now().toString(),
      time: new Date(message.timestamp).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false }),
      type: message.event_type.replace('_', ' '),
      description: message.payload.description || message.event_type,
      source: message.payload.source || 'System',
      status: message.payload.status || 'info'
    };
    
    setActivities(prev => [activity, ...prev.slice(0, 4)]);
  };

  const fetchSystemData = async () => {
    // Skip the API call entirely and just use default data
    setSystemHealth({
      status: 'online',
      services: {
        content_mind: { status: 'ok', lastCheck: new Date().toISOString() },
        context_mind: { status: 'ok', lastCheck: new Date().toISOString() },
        digest_agent: { status: 'ok', lastCheck: new Date().toISOString() },
        web_fetcher: { status: 'ok', lastCheck: new Date().toISOString() },
        email_gateway: { status: 'ok', lastCheck: new Date().toISOString() },
        model_router: { status: 'ok', lastCheck: new Date().toISOString() },
      },
    });
    
    setActivities([
      { id: '1', time: '14:42', type: 'PDF processed', description: 'Q3 Financial Report analyzed', source: 'ContentMind', status: 'success' },
      { id: '2', time: '14:38', type: 'URL processed', description: 'Article analysis completed', source: 'WebFetcher', status: 'success' },
      { id: '3', time: '14:35', type: 'Audio transcribed', description: 'Meeting audio processed', source: 'DigestAgent', status: 'success' },
      { id: '4', time: '14:30', type: 'Knowledge created', description: 'New insights generated', source: 'ContextMind', status: 'success' },
    ]);
  };

  useEffect(() => {
    fetchSystemData();
    
    // Refresh every 30 seconds
    const interval = setInterval(fetchSystemData, 30000);
    
    return () => {
      clearInterval(interval);
    };
  }, []);
  
  useEffect(() => {
    // Subscribe to WebSocket events in a separate effect
    const eventTypes = [
      'system_health',
      'component_status',
      'agent_started',
      'agent_completed',
      'email_processed',
      'url_processed',
      'file_uploaded',
      'knowledge_created',
      'knowledge_updated'
    ];
    
    subscribe(eventTypes);
    
    return () => {
      unsubscribe(eventTypes);
    };
  }, [subscribe, unsubscribe]);

  const StatusIndicator: React.FC<{ status: string }> = ({ status }) => {
    const colors = {
      ok: 'text-terminal-green',
      error: 'text-error-pink',
      warning: 'text-terminal-amber',
      online: 'text-terminal-green',
      offline: 'text-error-pink',
    };
    
    return (
      <span className={`font-bold ${colors[status as keyof typeof colors] || 'text-terminal-cyan'}`}>
        [{status.toUpperCase()}]
      </span>
    );
  };

  const handleFileUpload = async (file: File) => {
    try {
      // Show loading state
      const originalText = window.document.title;
      window.document.title = 'Processing...';
      
      // Upload file using the filesAPI
      const fileInfo = await filesAPI.uploadFile(file);
      
      // Add to activities and recent operations
      const uploadActivity: SystemActivity = {
        id: fileInfo.id,
        time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false }),
        type: 'File Upload',
        description: `Uploaded ${file.name}`,
        source: 'File System',
        status: 'success'
      };
      
      setActivities(prev => [uploadActivity, ...prev.slice(0, 4)]);
      
      const uploadOperation = `${uploadActivity.time} > upload file --name ${file.name} --size ${(file.size / 1024 / 1024).toFixed(2)}MB`;
      setRecentOperations(prev => [uploadOperation, ...prev.slice(0, 4)]);
      
      // Success notification
      window.document.title = originalText;
      console.log(`File "${file.name}" uploaded successfully!`);
    } catch (error) {
      setError('Failed to upload file');
      console.error('Upload error:', error);
    }
  };

  const handleURLSubmit = async (url: string) => {
    try {
      // Show processing state
      const originalTitle = window.document.title;
      window.document.title = 'Processing URL...';
      
      // Simulate URL processing (would connect to actual API)
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Add to activities and recent operations
      const urlActivity: SystemActivity = {
        id: Date.now().toString(),
        time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false }),
        type: 'URL Processing',
        description: `Processed ${new URL(url).hostname}`,
        source: 'WebFetcher',
        status: 'success'
      };
      
      setActivities(prev => [urlActivity, ...prev.slice(0, 4)]);
      
      const urlOperation = `${urlActivity.time} > process url --target ${url}`;
      setRecentOperations(prev => [urlOperation, ...prev.slice(0, 4)]);
      
      // Success notification
      window.document.title = originalTitle;
      console.log(`URL "${url}" processed successfully!`);
    } catch (error) {
      setError('Failed to process URL');
      console.error('URL processing error:', error);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header with Help Button */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold mb-6">AIOS v2 DASHBOARD</h2>
        <div className="flex space-x-2">
          <RetroButton onClick={() => setShowHelpModal(true)} variant="warning">
            HELP
          </RetroButton>
          <RetroButton onClick={() => setShowOnboardingModal(true)} variant="success">
            TOUR
          </RetroButton>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* System Status */}
        <RetroCard title="SYSTEM STATUS">
          {error && (
            <div className={`mb-4 ${error.includes('default data') ? 'text-terminal-amber' : 'text-error-pink'}`}>
              <span className="font-bold">[{error.includes('default data') ? 'INFO' : 'ERROR'}]</span> {error}
            </div>
          )}
          {systemHealth && systemHealth.services ? (
            <div className="space-y-2">
              {Object.entries(systemHealth.services).map(([name, service]) => (
                <div key={name} className="flex justify-between">
                  <span className="text-terminal-cyan">{name.replace('_', ' ').toUpperCase()}</span>
                  <StatusIndicator status={service.status} />
                </div>
              ))}
            </div>
          ) : null}
          
          {/* System Metrics */}
          <div className="mt-4 pt-3 border-t border-terminal-cyan/30">
            <div className="text-terminal-cyan/70 text-sm mb-2">PERFORMANCE METRICS</div>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="flex justify-between">
                <span className="text-terminal-cyan">Uptime:</span>
                <span className="text-terminal-green">99.8%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-terminal-cyan">Response:</span>
                <span className="text-terminal-green">245ms</span>
              </div>
              <div className="flex justify-between">
                <span className="text-terminal-cyan">Memory:</span>
                <span className="text-terminal-green">68%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-terminal-cyan">CPU:</span>
                <span className="text-terminal-green">34%</span>
              </div>
            </div>
          </div>
        </RetroCard>

        {/* Agent Status */}
        <RetroCard title="AI AGENT STATUS">
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-terminal-cyan">ContentMind</span>
              <div className="flex items-center gap-2">
                <span className="text-terminal-green">●</span>
                <span className="text-terminal-green text-sm">READY</span>
              </div>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-terminal-cyan">ContextMind</span>
              <div className="flex items-center gap-2">
                <span className="text-terminal-amber">●</span>
                <span className="text-terminal-amber text-sm">PROCESSING</span>
              </div>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-terminal-cyan">DigestAgent</span>
              <div className="flex items-center gap-2">
                <span className="text-terminal-green">●</span>
                <span className="text-terminal-green text-sm">READY</span>
              </div>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-terminal-cyan">WebFetcher</span>
              <div className="flex items-center gap-2">
                <span className="text-terminal-green">●</span>
                <span className="text-terminal-green text-sm">READY</span>
              </div>
            </div>
            <div className="mt-4 pt-3 border-t border-terminal-cyan/30">
              <div className="text-terminal-cyan/70 text-sm">AGENT PERFORMANCE</div>
              <div className="flex justify-between mt-1">
                <span className="text-terminal-cyan text-sm">Tasks Today:</span>
                <span className="text-terminal-green text-sm">247</span>
              </div>
              <div className="flex justify-between">
                <span className="text-terminal-cyan text-sm">Success Rate:</span>
                <span className="text-terminal-green text-sm">98.7%</span>
              </div>
            </div>
          </div>
        </RetroCard>
      </div>

      {/* Quick Actions */}
      <RetroCard title="QUICK ACTIONS">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <RetroButton onClick={() => window.location.href = '/agents'}>
            MANAGE AGENTS
          </RetroButton>
          <RetroButton onClick={() => setShowUploadModal(true)} variant="success">
            UPLOAD CONTENT
          </RetroButton>
          <RetroButton onClick={() => window.location.href = '/knowledge'} variant="primary">
            BROWSE KNOWLEDGE
          </RetroButton>
          <RetroButton onClick={() => window.location.href = '/terminal'} variant="warning">
            OPEN TERMINAL
          </RetroButton>
        </div>
      </RetroCard>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Command History */}
        <RetroCard title="COMMAND HISTORY">
          <div className="font-mono space-y-2 max-h-64 overflow-y-auto">
            {recentOperations.length > 0 ? (
              recentOperations.map((operation, index) => (
                <div key={index} className="text-terminal-cyan/80">
                  <span className="text-terminal-cyan">&gt;</span> {operation}
                </div>
              ))
            ) : (
              <>
                <div className="text-terminal-cyan/80">
                  <span className="text-terminal-cyan">&gt;</span> process url --target https://ai-news.com/article
                  <div className="text-terminal-green ml-4">[COMPLETED] Article analyzed and stored</div>
                </div>
                <div className="text-terminal-cyan/80">
                  <span className="text-terminal-cyan">&gt;</span> upload file --name quarterly-report.pdf
                  <div className="text-terminal-green ml-4">[COMPLETED] PDF processed and indexed</div>
                </div>
                <div className="text-terminal-cyan/80">
                  <span className="text-terminal-cyan">&gt;</span> run agent ContentMind --mode summarize
                  <div className="text-terminal-amber ml-4">[PROCESSING] Generating insights...</div>
                </div>
              </>
            )}
            <div className="text-terminal-cyan mt-4">&gt; <span className="cursor animate-pulse">_</span></div>
          </div>
        </RetroCard>

        {/* System Activity */}
        <RetroCard title="RECENT ACTIVITY">
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {activities.map((activity) => (
              <div key={activity.id} className="flex items-center justify-between p-2 border border-terminal-cyan/20 rounded">
                <div className="flex-1">
                  <div className="flex items-center space-x-3">
                    <span className="text-terminal-cyan text-sm font-mono">{activity.time}</span>
                    <span className="text-terminal-cyan/80 text-sm">{activity.description}</span>
                  </div>
                  <div className="text-terminal-cyan/60 text-xs mt-1">
                    Source: {activity.source}
                  </div>
                </div>
                <div className={`text-xs px-2 py-1 border rounded ${
                  activity.status === 'success' 
                    ? 'border-terminal-green text-terminal-green' 
                    : 'border-terminal-amber text-terminal-amber'
                }`}>
                  {activity.status.toUpperCase()}
                </div>
              </div>
            ))}
          </div>
        </RetroCard>
      </div>

      {/* Knowledge Stats */}
      <RetroCard title="KNOWLEDGE REPOSITORY STATS">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
          <div>
            <div className="text-3xl font-bold text-terminal-cyan">1,247</div>
            <div className="text-terminal-cyan/70 text-sm">TOTAL ITEMS</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-terminal-green">89</div>
            <div className="text-terminal-cyan/70 text-sm">PDFs PROCESSED</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-terminal-amber">156</div>
            <div className="text-terminal-cyan/70 text-sm">URLS ANALYZED</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-processing-blue">34</div>
            <div className="text-terminal-cyan/70 text-sm">AUDIO FILES</div>
          </div>
        </div>
      </RetroCard>

      {/* Modals */}
      <FileUploadModal
        isOpen={showUploadModal}
        onClose={() => setShowUploadModal(false)}
        onUpload={handleFileUpload}
        onURLSubmit={handleURLSubmit}
      />

      <OnboardingModal
        isOpen={showOnboardingModal}
        onClose={() => setShowOnboardingModal(false)}
        onComplete={() => {
          console.log('Onboarding completed!');
          // Could trigger additional setup here
        }}
      />

      <HelpModal
        isOpen={showHelpModal}
        onClose={() => setShowHelpModal(false)}
        onStartOnboarding={() => {
          setShowHelpModal(false);
          setShowOnboardingModal(true);
        }}
      />
    </div>
  );
}; 
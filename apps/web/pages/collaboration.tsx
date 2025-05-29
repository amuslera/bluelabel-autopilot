import React, { useState, useEffect, useCallback, useRef } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  Node,
  Edge,
  Connection,
  addEdge,
} from 'reactflow';
import 'reactflow/dist/style.css';

// Types for agent collaboration
interface Agent {
  id: string;
  name: string;
  status: 'idle' | 'working' | 'busy' | 'offline';
  currentTask?: string;
  expertise: string[];
  workload: number;
  lastSeen: string;
  avatar: string;
}

interface Task {
  id: string;
  title: string;
  description: string;
  status: 'pending' | 'in_progress' | 'blocked' | 'completed' | 'cancelled';
  assignee?: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  dependencies: string[];
  estimatedHours: number;
  actualHours?: number;
  tags: string[];
  dueDate?: string;
  createdAt: string;
  updatedAt: string;
}

interface ChatMessage {
  id: string;
  from: string;
  message: string;
  timestamp: string;
  type: 'message' | 'task_update' | 'system' | 'handoff';
  metadata?: any;
}

interface SprintData {
  id: string;
  name: string;
  startDate: string;
  endDate: string;
  tasks: Task[];
  velocity: number;
  burndownData: { date: string; remaining: number }[];
}

const CollaborationPage: React.FC = () => {
  // State management
  const [activeTab, setActiveTab] = useState<'overview' | 'tasks' | 'chat' | 'planning'>('overview');
  const [agents, setAgents] = useState<Agent[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [currentSprint, setCurrentSprint] = useState<SprintData | null>(null);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [newMessage, setNewMessage] = useState('');
  
  // Task dependency visualization
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  
  // Refs
  const chatEndRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);

  // Mock data initialization
  useEffect(() => {
    initializeMockData();
    connectWebSocket();
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const initializeMockData = () => {
    // Mock agents
    const mockAgents: Agent[] = [
      {
        id: 'CA',
        name: 'Cursor AI Frontend',
        status: 'working',
        currentTask: 'TASK-166A',
        expertise: ['frontend', 'ui', 'react', 'typescript'],
        workload: 85,
        lastSeen: new Date().toISOString(),
        avatar: '🎨'
      },
      {
        id: 'CB',
        name: 'Claude Backend',
        status: 'busy',
        currentTask: 'TASK-165E',
        expertise: ['backend', 'api', 'database', 'python'],
        workload: 70,
        lastSeen: new Date(Date.now() - 300000).toISOString(),
        avatar: '⚙️'
      },
      {
        id: 'CC',
        name: 'Claude QA',
        status: 'idle',
        expertise: ['testing', 'quality', 'automation', 'ci/cd'],
        workload: 30,
        lastSeen: new Date(Date.now() - 900000).toISOString(),
        avatar: '🔍'
      },
      {
        id: 'ARCH',
        name: 'Architecture Agent',
        status: 'working',
        currentTask: 'TASK-166B',
        expertise: ['architecture', 'system_design', 'planning'],
        workload: 60,
        lastSeen: new Date(Date.now() - 120000).toISOString(),
        avatar: '🏗️'
      }
    ];

    // Mock tasks
    const mockTasks: Task[] = [
      {
        id: 'TASK-166A',
        title: 'Real-time agent collaboration interface',
        description: 'Create interactive UI for real-time agent collaboration',
        status: 'in_progress',
        assignee: 'CA',
        priority: 'high',
        dependencies: [],
        estimatedHours: 3,
        actualHours: 1.5,
        tags: ['frontend', 'ui', 'collaboration'],
        dueDate: new Date(Date.now() + 86400000).toISOString(),
        createdAt: new Date(Date.now() - 3600000).toISOString(),
        updatedAt: new Date().toISOString()
      },
      {
        id: 'TASK-165E',
        title: 'Performance metrics API',
        description: 'Implement backend API for performance tracking',
        status: 'in_progress',
        assignee: 'CB',
        priority: 'medium',
        dependencies: [],
        estimatedHours: 4,
        actualHours: 2.8,
        tags: ['backend', 'api', 'metrics'],
        dueDate: new Date(Date.now() + 172800000).toISOString(),
        createdAt: new Date(Date.now() - 7200000).toISOString(),
        updatedAt: new Date(Date.now() - 1800000).toISOString()
      },
      {
        id: 'TASK-166B',
        title: 'System architecture review',
        description: 'Review and optimize current system architecture',
        status: 'in_progress',
        assignee: 'ARCH',
        priority: 'medium',
        dependencies: ['TASK-165E'],
        estimatedHours: 2,
        actualHours: 0.5,
        tags: ['architecture', 'review', 'optimization'],
        dueDate: new Date(Date.now() + 259200000).toISOString(),
        createdAt: new Date(Date.now() - 5400000).toISOString(),
        updatedAt: new Date(Date.now() - 600000).toISOString()
      },
      {
        id: 'TASK-166C',
        title: 'Integration testing framework',
        description: 'Setup automated integration testing',
        status: 'pending',
        priority: 'low',
        dependencies: ['TASK-166A', 'TASK-165E'],
        estimatedHours: 3,
        tags: ['testing', 'automation', 'integration'],
        dueDate: new Date(Date.now() + 345600000).toISOString(),
        createdAt: new Date(Date.now() - 1800000).toISOString(),
        updatedAt: new Date(Date.now() - 1800000).toISOString()
      }
    ];

    // Mock chat messages
    const mockMessages: ChatMessage[] = [
      {
        id: '1',
        from: 'ARCH',
        message: 'Starting daily coordination. Current sprint has 4 active tasks.',
        timestamp: new Date(Date.now() - 1800000).toISOString(),
        type: 'system'
      },
      {
        id: '2',
        from: 'CB',
        message: 'Performance API is 70% complete. Will need frontend integration soon.',
        timestamp: new Date(Date.now() - 1200000).toISOString(),
        type: 'message'
      },
      {
        id: '3',
        from: 'CA',
        message: 'Ready to integrate once CB finishes the metrics endpoints.',
        timestamp: new Date(Date.now() - 900000).toISOString(),
        type: 'message'
      },
      {
        id: '4',
        from: 'CB',
        message: 'Task TASK-165E updated: 80% complete',
        timestamp: new Date(Date.now() - 300000).toISOString(),
        type: 'task_update',
        metadata: { taskId: 'TASK-165E', progress: 80 }
      }
    ];

    setAgents(mockAgents);
    setTasks(mockTasks);
    setChatMessages(mockMessages);
    createTaskDependencyGraph(mockTasks);
  };

  const createTaskDependencyGraph = (tasks: Task[]) => {
    const newNodes: Node[] = tasks.map((task, index) => ({
      id: task.id,
      type: 'default',
      position: { 
        x: (index % 3) * 300 + 100, 
        y: Math.floor(index / 3) * 150 + 100 
      },
      data: {
        label: (
          <div className="p-3 min-w-[200px]">
            <div className="font-bold text-sm">{task.title}</div>
            <div className="text-xs text-gray-500 mt-1">{task.id}</div>
            <div className={`text-xs px-2 py-1 rounded mt-2 ${getTaskStatusColor(task.status)}`}>
              {task.status.replace('_', ' ').toUpperCase()}
            </div>
            {task.assignee && (
              <div className="text-xs text-gray-600 mt-1">
                Assigned: {agents.find(a => a.id === task.assignee)?.name || task.assignee}
              </div>
            )}
          </div>
        ),
        task
      }
    }));

    const newEdges: Edge[] = [];
    tasks.forEach(task => {
      task.dependencies.forEach(depId => {
        if (tasks.find(t => t.id === depId)) {
          newEdges.push({
            id: `${depId}-${task.id}`,
            source: depId,
            target: task.id,
            type: 'smoothstep',
            animated: task.status === 'blocked',
            style: { stroke: task.status === 'blocked' ? '#ef4444' : '#6b7280' }
          });
        }
      });
    });

    setNodes(newNodes);
    setEdges(newEdges);
  };

  const connectWebSocket = () => {
    // Mock WebSocket connection
    setIsConnected(true);
    
    // Simulate real-time updates
    const interval = setInterval(() => {
      if (Math.random() > 0.8) {
        addMockRealTimeUpdate();
      }
    }, 10000);

    return () => clearInterval(interval);
  };

  const addMockRealTimeUpdate = () => {
    const updateTypes = ['progress', 'status', 'message'];
    const type = updateTypes[Math.floor(Math.random() * updateTypes.length)];

    switch (type) {
      case 'progress':
        // Update task progress
        setTasks(prev => prev.map(task => {
          if (task.status === 'in_progress' && Math.random() > 0.7) {
            const currentHours = task.actualHours || 0;
            const newProgress = Math.min(currentHours + 0.1, task.estimatedHours);
            return { ...task, actualHours: newProgress, updatedAt: new Date().toISOString() };
          }
          return task;
        }));
        break;

      case 'status':
        // Update agent status
        setAgents(prev => prev.map(agent => {
          if (Math.random() > 0.8) {
            const statuses: Agent['status'][] = ['idle', 'working', 'busy'];
            const newStatus = statuses[Math.floor(Math.random() * statuses.length)];
            return { ...agent, status: newStatus, lastSeen: new Date().toISOString() };
          }
          return agent;
        }));
        break;

      case 'message':
        // Add system message
        const systemMessages = [
          'Task dependency resolved automatically',
          'Sprint velocity updated: +15%',
          'New task assignment optimized',
          'Integration checkpoint passed'
        ];
        const message = systemMessages[Math.floor(Math.random() * systemMessages.length)];
        addChatMessage('system', message, 'system');
        break;
    }
  };

  const addChatMessage = (from: string, message: string, type: ChatMessage['type'] = 'message', metadata?: any) => {
    const newMessage: ChatMessage = {
      id: Date.now().toString(),
      from,
      message,
      timestamp: new Date().toISOString(),
      type,
      metadata
    };
    setChatMessages(prev => [...prev, newMessage]);
  };

  const sendMessage = () => {
    if (newMessage.trim()) {
      addChatMessage('CA', newMessage.trim());
      setNewMessage('');
    }
  };

  const handleTaskHandoff = (task: Task, toAgent: string) => {
    setTasks(prev => prev.map(t => 
      t.id === task.id 
        ? { ...t, assignee: toAgent, updatedAt: new Date().toISOString() }
        : t
    ));
    
    const fromAgentName = agents.find(a => a.id === task.assignee)?.name || task.assignee;
    const toAgentName = agents.find(a => a.id === toAgent)?.name || toAgent;
    
    addChatMessage(
      'system', 
      `Task ${task.id} handed off from ${fromAgentName} to ${toAgentName}`,
      'handoff',
      { taskId: task.id, fromAgent: task.assignee, toAgent }
    );
  };

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  // Scroll chat to bottom on new messages
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  // Utility functions
  const getAgentStatusColor = (status: Agent['status']) => {
    switch (status) {
      case 'working': return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'busy': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'idle': return 'bg-green-100 text-green-800 border-green-300';
      case 'offline': return 'bg-gray-100 text-gray-800 border-gray-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getTaskStatusColor = (status: Task['status']) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'in_progress': return 'bg-blue-100 text-blue-800';
      case 'blocked': return 'bg-red-100 text-red-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'cancelled': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityColor = (priority: Task['priority']) => {
    switch (priority) {
      case 'critical': return 'text-red-600';
      case 'high': return 'text-orange-600';
      case 'medium': return 'text-yellow-600';
      case 'low': return 'text-green-600';
      default: return 'text-gray-600';
    }
  };

  const calculateWorkloadDistribution = () => {
    const totalWorkload = agents.reduce((sum, agent) => sum + agent.workload, 0);
    const averageWorkload = totalWorkload / agents.length;
    const deviation = Math.sqrt(
      agents.reduce((sum, agent) => sum + Math.pow(agent.workload - averageWorkload, 2), 0) / agents.length
    );
    
    return {
      average: Math.round(averageWorkload),
      deviation: Math.round(deviation),
      balanced: deviation < 15
    };
  };

  const workloadStats = calculateWorkloadDistribution();

  return (
    <>
      <Head>
        <title>Agent Collaboration Hub - Bluelabel Autopilot</title>
        <meta name="description" content="Real-time multi-agent collaboration interface" />
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
        {/* Header */}
        <div className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center space-x-4">
                <Link href="/" className="text-2xl font-bold text-gray-900 hover:text-blue-600 transition-colors">
                  🤖 Collaboration Hub
                </Link>
                <div className={`flex items-center space-x-2 px-3 py-1 rounded-full text-sm ${
                  isConnected 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  <div className={`w-2 h-2 rounded-full ${
                    isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'
                  }`}></div>
                  {isConnected ? 'Live' : 'Disconnected'}
                </div>
              </div>
              
              <div className="flex items-center space-x-4">
                <div className="text-sm text-gray-600">
                  {agents.filter(a => a.status === 'working').length} agents active
                </div>
                <div className={`text-sm font-medium ${
                  workloadStats.balanced ? 'text-green-600' : 'text-orange-600'
                }`}>
                  Workload: {workloadStats.balanced ? 'Balanced' : 'Unbalanced'}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="bg-white border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <nav className="flex space-x-8">
              {[
                { id: 'overview', name: 'Overview', icon: '📊' },
                { id: 'tasks', name: 'Task Board', icon: '📋' },
                { id: 'chat', name: 'Live Chat', icon: '💬' },
                { id: 'planning', name: 'Sprint Planning', icon: '🎯' }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <span className="mr-2">{tab.icon}</span>
                  {tab.name}
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Main Content */}
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Agent Status Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {agents.map((agent) => (
                  <div key={agent.id} className="bg-white rounded-xl shadow-lg p-6 border border-gray-200 hover:shadow-xl transition-shadow">
                    <div className="flex items-center justify-between mb-4">
                      <div className="text-3xl">{agent.avatar}</div>
                      <div className={`px-3 py-1 rounded-full text-xs font-medium border ${getAgentStatusColor(agent.status)}`}>
                        {agent.status.toUpperCase()}
                      </div>
                    </div>
                    
                    <h3 className="font-bold text-lg text-gray-900 mb-2">{agent.name}</h3>
                    <div className="text-sm text-gray-600 mb-3">ID: {agent.id}</div>
                    
                    {agent.currentTask && (
                      <div className="mb-3">
                        <div className="text-sm font-medium text-gray-700">Current Task:</div>
                        <div className="text-sm text-blue-600">{agent.currentTask}</div>
                      </div>
                    )}
                    
                    <div className="mb-3">
                      <div className="flex justify-between text-sm mb-1">
                        <span>Workload</span>
                        <span>{agent.workload}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full transition-all duration-500 ${
                            agent.workload > 80 ? 'bg-red-500' : 
                            agent.workload > 60 ? 'bg-yellow-500' : 'bg-green-500'
                          }`}
                          style={{ width: `${agent.workload}%` }}
                        ></div>
                      </div>
                    </div>
                    
                    <div className="text-xs text-gray-500">
                      Last seen: {new Date(agent.lastSeen).toLocaleTimeString()}
                    </div>
                  </div>
                ))}
              </div>

              {/* Workload Balance Chart */}
              <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
                <h3 className="text-xl font-bold text-gray-900 mb-4">Workload Distribution</h3>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div>
                    <div className="space-y-3">
                      {agents.map((agent) => (
                        <div key={agent.id} className="flex items-center space-x-3">
                          <div className="w-8 text-center">{agent.avatar}</div>
                          <div className="flex-1">
                            <div className="flex justify-between text-sm mb-1">
                              <span>{agent.name}</span>
                              <span className="font-medium">{agent.workload}%</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div 
                                className={`h-2 rounded-full transition-all duration-500 ${
                                  agent.workload > 80 ? 'bg-red-500' : 
                                  agent.workload > 60 ? 'bg-yellow-500' : 'bg-green-500'
                                }`}
                                style={{ width: `${agent.workload}%` }}
                              ></div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h4 className="font-medium text-gray-900 mb-3">Statistics</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span>Average Load:</span>
                        <span className="font-medium">{workloadStats.average}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Deviation:</span>
                        <span className="font-medium">{workloadStats.deviation}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Status:</span>
                        <span className={`font-medium ${workloadStats.balanced ? 'text-green-600' : 'text-orange-600'}`}>
                          {workloadStats.balanced ? 'Well Balanced' : 'Needs Rebalancing'}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'tasks' && (
            <div className="space-y-6">
              {/* Task Dependency Graph */}
              <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
                <div className="p-6 border-b border-gray-200">
                  <h3 className="text-xl font-bold text-gray-900">Task Dependencies</h3>
                  <p className="text-gray-600 mt-1">Drag to rearrange • Click nodes for details</p>
                </div>
                <div className="h-96">
                  <ReactFlow
                    nodes={nodes}
                    edges={edges}
                    onNodesChange={onNodesChange}
                    onEdgesChange={onEdgesChange}
                    onConnect={onConnect}
                    fitView
                  >
                    <Background />
                    <Controls />
                    <MiniMap />
                  </ReactFlow>
                </div>
              </div>

              {/* Task List */}
              <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
                <h3 className="text-xl font-bold text-gray-900 mb-4">Active Tasks</h3>
                <div className="space-y-4">
                  {tasks.map((task) => {
                    const assignedAgent = agents.find(a => a.id === task.assignee);
                    const progress = task.actualHours && task.estimatedHours 
                      ? Math.round((task.actualHours / task.estimatedHours) * 100) 
                      : 0;
                    
                    return (
                      <div key={task.id} className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors">
                        <div className="flex justify-between items-start mb-3">
                          <div className="flex-1">
                            <div className="flex items-center space-x-2 mb-1">
                              <h4 className="font-bold text-gray-900">{task.title}</h4>
                              <span className={`text-xs px-2 py-1 rounded ${getTaskStatusColor(task.status)}`}>
                                {task.status.replace('_', ' ').toUpperCase()}
                              </span>
                              <span className={`text-xs font-medium ${getPriorityColor(task.priority)}`}>
                                {task.priority.toUpperCase()}
                              </span>
                            </div>
                            <p className="text-sm text-gray-600 mb-2">{task.description}</p>
                            <div className="text-xs text-gray-500">{task.id}</div>
                          </div>
                          
                          {assignedAgent && (
                            <div className="flex items-center space-x-2 ml-4">
                              <div className="text-2xl">{assignedAgent.avatar}</div>
                              <div className="text-sm">
                                <div className="font-medium">{assignedAgent.name}</div>
                                <div className="text-gray-500">{assignedAgent.id}</div>
                              </div>
                            </div>
                          )}
                        </div>
                        
                        {task.status === 'in_progress' && task.actualHours && (
                          <div className="mb-3">
                            <div className="flex justify-between text-sm mb-1">
                              <span>Progress</span>
                              <span>{task.actualHours}h / {task.estimatedHours}h ({progress}%)</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div 
                                className="bg-blue-500 h-2 rounded-full transition-all duration-500"
                                style={{ width: `${Math.min(progress, 100)}%` }}
                              ></div>
                            </div>
                          </div>
                        )}
                        
                        <div className="flex flex-wrap gap-2 text-xs">
                          {task.tags.map((tag) => (
                            <span key={tag} className="bg-blue-100 text-blue-800 px-2 py-1 rounded">
                              {tag}
                            </span>
                          ))}
                        </div>
                        
                        {!assignedAgent && (
                          <div className="mt-3 pt-3 border-t border-gray-200">
                            <div className="flex items-center space-x-2">
                              <span className="text-sm text-gray-600">Assign to:</span>
                              {agents.filter(a => a.status !== 'offline').map((agent) => (
                                <button
                                  key={agent.id}
                                  onClick={() => handleTaskHandoff(task, agent.id)}
                                  className="text-sm bg-gray-100 hover:bg-blue-100 text-gray-700 hover:text-blue-700 px-3 py-1 rounded transition-colors"
                                >
                                  {agent.avatar} {agent.id}
                                </button>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'chat' && (
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
              {/* Chat Messages */}
              <div className="lg:col-span-3 bg-white rounded-xl shadow-lg border border-gray-200 flex flex-col h-[600px]">
                <div className="p-6 border-b border-gray-200">
                  <h3 className="text-xl font-bold text-gray-900">Live Coordination Chat</h3>
                  <p className="text-gray-600 mt-1">Real-time communication between agents</p>
                </div>
                
                <div className="flex-1 overflow-y-auto p-6 space-y-4">
                  {chatMessages.map((msg) => {
                    const fromAgent = agents.find(a => a.id === msg.from);
                    
                    return (
                      <div key={msg.id} className={`flex ${msg.from === 'CA' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                          msg.type === 'system' 
                            ? 'bg-gray-100 text-gray-700' 
                            : msg.from === 'CA'
                            ? 'bg-blue-500 text-white'
                            : 'bg-gray-200 text-gray-900'
                        }`}>
                          <div className="flex items-center space-x-2 mb-1">
                            {fromAgent && <span>{fromAgent.avatar}</span>}
                            <span className="text-xs font-medium opacity-75">
                              {msg.type === 'system' ? 'System' : fromAgent?.name || msg.from}
                            </span>
                            <span className="text-xs opacity-50">
                              {new Date(msg.timestamp).toLocaleTimeString()}
                            </span>
                          </div>
                          <p className="text-sm">{msg.message}</p>
                          {msg.type === 'task_update' && msg.metadata && (
                            <div className="text-xs opacity-75 mt-1">
                              Progress: {msg.metadata.progress}%
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                  <div ref={chatEndRef} />
                </div>
                
                <div className="p-4 border-t border-gray-200">
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      value={newMessage}
                      onChange={(e) => setNewMessage(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                      placeholder="Type a message..."
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                    />
                    <button
                      onClick={sendMessage}
                      className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                    >
                      Send
                    </button>
                  </div>
                </div>
              </div>
              
              {/* Online Agents */}
              <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
                <h4 className="font-bold text-gray-900 mb-4">Online Agents</h4>
                <div className="space-y-3">
                  {agents.filter(a => a.status !== 'offline').map((agent) => (
                    <div key={agent.id} className="flex items-center space-x-3">
                      <div className="text-2xl">{agent.avatar}</div>
                      <div className="flex-1">
                        <div className="font-medium text-sm">{agent.name}</div>
                        <div className={`text-xs px-2 py-1 rounded ${getAgentStatusColor(agent.status)}`}>
                          {agent.status}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'planning' && (
            <div className="space-y-6">
              {/* Sprint Overview */}
              <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
                <h3 className="text-xl font-bold text-gray-900 mb-4">Sprint Planning</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-blue-50 rounded-lg p-4">
                    <h4 className="font-medium text-blue-900 mb-2">Current Sprint</h4>
                    <div className="text-2xl font-bold text-blue-600">{tasks.length}</div>
                    <div className="text-sm text-blue-700">Total Tasks</div>
                  </div>
                  <div className="bg-green-50 rounded-lg p-4">
                    <h4 className="font-medium text-green-900 mb-2">Completed</h4>
                    <div className="text-2xl font-bold text-green-600">
                      {tasks.filter(t => t.status === 'completed').length}
                    </div>
                    <div className="text-sm text-green-700">Tasks Done</div>
                  </div>
                  <div className="bg-yellow-50 rounded-lg p-4">
                    <h4 className="font-medium text-yellow-900 mb-2">In Progress</h4>
                    <div className="text-2xl font-bold text-yellow-600">
                      {tasks.filter(t => t.status === 'in_progress').length}
                    </div>
                    <div className="text-sm text-yellow-700">Active Tasks</div>
                  </div>
                </div>
              </div>

              {/* Team Velocity */}
              <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
                <h3 className="text-xl font-bold text-gray-900 mb-4">Team Velocity</h3>
                <div className="text-center py-8">
                  <div className="text-4xl font-bold text-blue-600 mb-2">
                    {Math.round(tasks.reduce((sum, task) => sum + (task.actualHours || 0), 0))}h
                  </div>
                  <div className="text-gray-600">Total Hours This Sprint</div>
                  <div className="mt-4 text-sm text-gray-500">
                    Average: {Math.round(tasks.reduce((sum, task) => sum + (task.actualHours || 0), 0) / agents.length)}h per agent
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default CollaborationPage; 
import React, { useCallback, useEffect, useState } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  Node,
  Edge,
  NodeTypes,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { DAGRun } from '../types/dag';
import { convertDagToNodesAndEdges, calculateDagMetrics } from '../utils/dagUtils';
import { useDAGRun, useDAGRunUpdates } from '../lib/api/hooks';
import ErrorBoundary from './ErrorBoundary';

interface DAGGraphProps {
  runId: string;
  onNodeClick?: (node: Node) => void;
  className?: string;
}

const SkeletonNode = () => (
  <div className="animate-pulse">
    <div className="h-16 w-32 bg-gradient-to-r from-gray-200 to-gray-300 rounded-lg mb-2"></div>
    <div className="h-4 w-24 bg-gradient-to-r from-gray-200 to-gray-300 rounded"></div>
  </div>
);

const SkeletonEdge = () => (
  <div className="animate-pulse">
    <div className="h-0.5 w-32 bg-gradient-to-r from-gray-200 to-gray-300"></div>
  </div>
);

// Enhanced status colors for better demo visibility
const getStatusColor = (status: string) => {
  switch (status?.toLowerCase()) {
    case 'pending':
    case 'queued':
      return 'bg-gradient-to-r from-gray-400 to-gray-500 text-white';
    case 'running':
    case 'in_progress':
      return 'bg-gradient-to-r from-blue-500 to-blue-600 text-white animate-pulse';
    case 'success':
    case 'completed':
      return 'bg-gradient-to-r from-green-500 to-green-600 text-white';
    case 'failed':
    case 'error':
      return 'bg-gradient-to-r from-red-500 to-red-600 text-white';
    case 'retry':
    case 'retrying':
      return 'bg-gradient-to-r from-yellow-500 to-orange-500 text-white animate-bounce';
    case 'cancelled':
      return 'bg-gradient-to-r from-gray-600 to-gray-700 text-white';
    default:
      return 'bg-gradient-to-r from-gray-300 to-gray-400 text-gray-800';
  }
};

// Enhanced progress bar component
const ProgressBar = ({ progress, className = '' }: { progress: number; className?: string }) => (
  <div className={`w-full bg-gray-200 rounded-full h-3 ${className} overflow-hidden`}>
    <div
      className="bg-gradient-to-r from-blue-500 to-blue-600 h-3 rounded-full transition-all duration-500 ease-out relative"
      style={{ width: `${Math.max(0, Math.min(100, progress))}%` }}
    >
      <div className="absolute inset-0 bg-white opacity-30 animate-pulse"></div>
    </div>
  </div>
);

const DAGGraph: React.FC<DAGGraphProps> = ({
  runId,
  onNodeClick,
  className = '',
}) => {
  const { data: dagRun, error: apiError, isLoading } = useDAGRun('', runId);
  
  console.log('DAGGraph render:', { runId, dagRun, apiError, isLoading });
  const { 
    status: currentStatus,
    steps: updatedSteps,
    progress: currentProgress,
    error: wsError,
    isConnected: wsConnected
  } = useDAGRunUpdates('', runId);

  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [lastUpdateTime, setLastUpdateTime] = useState(Date.now());

  // Convert DAG run to nodes and edges
  useEffect(() => {
    if (dagRun) {
      console.log('DAGGraph: dagRun received:', dagRun);
      const { nodes: newNodes, edges: newEdges } = convertDagToNodesAndEdges(dagRun);
      console.log('DAGGraph: converted nodes:', newNodes);
      console.log('DAGGraph: converted edges:', newEdges);
      setNodes(newNodes);
      setEdges(newEdges);
      setLastUpdateTime(Date.now());
    }
  }, [dagRun]);

  // Update nodes when steps change with smooth animations
  useEffect(() => {
    if (updatedSteps && Object.keys(updatedSteps).length > 0 && nodes.length > 0) {
      const updatedNodes = nodes.map(node => {
        const step = updatedSteps[node.id];
        if (step) {
          return {
            ...node,
            data: {
              ...node.data,
              status: step.status,
              duration: step.duration,
              error: step.error,
              lastUpdate: Date.now()
            }
          };
        }
        return node;
      });
      setNodes(updatedNodes);
      setLastUpdateTime(Date.now());
    }
  }, [updatedSteps]);

  // Calculate enhanced metrics
  const metrics = currentProgress || (dagRun && Array.isArray(dagRun.steps) ? {
    totalSteps: dagRun.steps.length,
    completedSteps: dagRun.steps.filter((s: any) => s.status === 'completed' || s.status === 'SUCCESS').length,
    runningSteps: dagRun.steps.filter((s: any) => s.status === 'running' || s.status === 'RUNNING').length,
    failedSteps: dagRun.steps.filter((s: any) => s.status === 'failed' || s.status === 'FAILED').length,
    retryingSteps: dagRun.steps.filter((s: any) => s.status === 'retry' || s.status === 'RETRYING').length,
    progress: 0
  } : null);

  const progressPercentage = metrics ? 
    Math.round((metrics.completedSteps / metrics.totalSteps) * 100) : 0;

  const handleNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      if (onNodeClick) {
        onNodeClick(node);
      }
    },
    [onNodeClick]
  );

  if (isLoading) {
    return (
      <div className={`h-[600px] bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl shadow-lg p-6 ${className}`} data-testid="dag-graph">
        <div className="flex items-center justify-center h-full">
          <div className="space-y-8">
            <div className="text-center">
              <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
              <p className="text-gray-600 font-medium">Loading DAG visualization...</p>
            </div>
            <div className="flex justify-center space-x-8">
              <SkeletonNode />
              <SkeletonNode />
              <SkeletonNode />
            </div>
            <div className="flex justify-center space-x-8">
              <SkeletonEdge />
              <SkeletonEdge />
            </div>
            <div className="flex justify-center space-x-8">
              <SkeletonNode />
              <SkeletonNode />
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (apiError || wsError) {
    return (
      <div className={`h-[600px] bg-gradient-to-br from-red-50 to-red-100 rounded-xl shadow-lg p-6 ${className}`} data-testid="dag-graph">
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="w-16 h-16 bg-red-500 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-white text-2xl">⚠</span>
            </div>
            <div className="text-red-600 font-medium">
              Error: {apiError?.message || wsError || 'Failed to load DAG'}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!dagRun) {
    return (
      <div className={`h-[600px] bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl shadow-lg p-6 ${className}`} data-testid="dag-graph">
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="w-16 h-16 bg-gray-400 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-white text-2xl">📊</span>
            </div>
            <div className="text-gray-500 font-medium">No DAG found</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <div className={`h-[600px] bg-white rounded-xl shadow-lg ${className} overflow-hidden border border-gray-200`} data-testid="dag-graph">
        {/* Enhanced Status Header */}
        {metrics && (
          <div className="p-6 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-indigo-50">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-xl font-bold text-gray-900 mb-1">
                  {(dagRun as any).workflow_name || 'DAG Run'}
                </h3>
                <div className="flex items-center space-x-3">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(currentStatus || dagRun.status)}`}>
                    {currentStatus || dagRun.status}
                  </span>
                  {wsConnected && (
                    <div className="flex items-center text-green-600 text-sm">
                      <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse mr-2"></div>
                      Live Updates
                    </div>
                  )}
                </div>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-gray-900">{progressPercentage}%</div>
                <div className="text-sm text-gray-500">
                  {metrics.completedSteps}/{metrics.totalSteps} completed
                </div>
              </div>
            </div>
            
            {/* Enhanced Progress Bar */}
            <ProgressBar progress={progressPercentage} className="mb-3" />
            
            {/* Step Status Summary */}
            <div className="flex justify-between text-sm">
              <div className="flex space-x-4">
                {metrics.runningSteps > 0 && (
                  <span className="text-blue-600 font-medium">
                    🔄 {metrics.runningSteps} running
                  </span>
                )}
                {metrics.completedSteps > 0 && (
                  <span className="text-green-600 font-medium">
                    ✅ {metrics.completedSteps} completed
                  </span>
                )}
                {metrics.failedSteps > 0 && (
                  <span className="text-red-600 font-medium">
                    ❌ {metrics.failedSteps} failed
                  </span>
                )}
                {metrics.retryingSteps > 0 && (
                  <span className="text-yellow-600 font-medium">
                    🔄 {metrics.retryingSteps} retrying
                  </span>
                )}
              </div>
              <div className="text-gray-500">
                Updated {new Date(lastUpdateTime).toLocaleTimeString()}
              </div>
            </div>
          </div>
        )}
        
        {/* Enhanced ReactFlow Graph */}
        <div className="h-full bg-gradient-to-br from-slate-50 to-gray-100">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeClick={handleNodeClick}
            fitView
            attributionPosition="top-right"
            proOptions={{
              hideAttribution: true
            }}
          >
            <Background 
              color="#94a3b8" 
              gap={20} 
              size={1}
              style={{ opacity: 0.5 }}
            />
            <Controls 
              style={{ 
                button: { 
                  backgroundColor: '#fff',
                  border: '1px solid #e2e8f0',
                  color: '#475569'
                }
              }}
            />
            <MiniMap 
              style={{ 
                backgroundColor: '#f8fafc',
                border: '1px solid #e2e8f0'
              }}
              nodeColor={(node) => {
                const status = node.data?.status || 'pending';
                switch (status.toLowerCase()) {
                  case 'running': return '#3b82f6';
                  case 'completed': case 'success': return '#10b981';
                  case 'failed': case 'error': return '#ef4444';
                  case 'retry': return '#f59e0b';
                  default: return '#6b7280';
                }
              }}
            />
          </ReactFlow>
        </div>
      </div>
    </ErrorBoundary>
  );
};

export default DAGGraph; 
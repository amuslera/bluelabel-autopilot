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
    <div className="h-16 w-32 bg-gray-200 rounded-lg mb-2"></div>
    <div className="h-4 w-24 bg-gray-200 rounded"></div>
  </div>
);

const SkeletonEdge = () => (
  <div className="animate-pulse">
    <div className="h-0.5 w-32 bg-gray-200"></div>
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
    error: wsError 
  } = useDAGRunUpdates('', runId);

  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  // Convert DAG run to nodes and edges
  useEffect(() => {
    if (dagRun) {
      console.log('DAGGraph: dagRun received:', dagRun);
      const { nodes: newNodes, edges: newEdges } = convertDagToNodesAndEdges(dagRun);
      console.log('DAGGraph: converted nodes:', newNodes);
      console.log('DAGGraph: converted edges:', newEdges);
      setNodes(newNodes);
      setEdges(newEdges);
    }
  }, [dagRun]);

  // Update nodes when steps change
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
              error: step.error
            }
          };
        }
        return node;
      });
      setNodes(updatedNodes);
    }
  }, [updatedSteps]);

  // Calculate metrics
  const metrics = currentProgress || (dagRun && Array.isArray(dagRun.steps) ? {
    totalSteps: dagRun.steps.length,
    completedSteps: dagRun.steps.filter((s: any) => s.status === 'completed' || s.status === 'SUCCESS').length,
    runningSteps: dagRun.steps.filter((s: any) => s.status === 'running' || s.status === 'RUNNING').length,
    failedSteps: dagRun.steps.filter((s: any) => s.status === 'failed' || s.status === 'FAILED').length,
    progress: 0
  } : null);

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
      <div className={`h-[600px] bg-white rounded-lg p-4 ${className}`} data-testid="dag-graph">
        <div className="flex items-center justify-center h-full">
          <div className="space-y-8">
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
      <div className={`h-[600px] bg-white rounded-lg p-4 ${className}`} data-testid="dag-graph">
        <div className="flex items-center justify-center h-full">
          <div className="text-red-500">
            Error: {apiError?.message || wsError || 'Failed to load DAG'}
          </div>
        </div>
      </div>
    );
  }

  if (!dagRun) {
    return (
      <div className={`h-[600px] bg-white rounded-lg p-4 ${className}`} data-testid="dag-graph">
        <div className="flex items-center justify-center h-full">
          <div className="text-gray-500">No DAG found</div>
        </div>
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <div className={`h-[600px] bg-white rounded-lg ${className}`} data-testid="dag-graph">
        {/* Status Header */}
        {metrics && (
          <div className="p-4 border-b border-gray-200">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-medium">
                {(dagRun as any).workflow_name || 'DAG Run'} - {currentStatus || dagRun.status}
              </h3>
              <div className="text-sm text-gray-500">
                {metrics.completedSteps}/{metrics.totalSteps} steps completed
              </div>
            </div>
            {metrics.totalSteps > 0 && (
              <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${(metrics.completedSteps / metrics.totalSteps) * 100}%` }}
                />
              </div>
            )}
          </div>
        )}
        
        {/* ReactFlow Graph */}
        <div className="h-full">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeClick={handleNodeClick}
            fitView
            attributionPosition="top-right"
          >
            <Background />
            <Controls />
            <MiniMap />
          </ReactFlow>
        </div>
      </div>
    </ErrorBoundary>
  );
};

export default DAGGraph; 
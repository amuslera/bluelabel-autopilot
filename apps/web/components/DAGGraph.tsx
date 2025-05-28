import React, { useCallback, useEffect } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  Node,
  Edge,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { DAGRun } from '../types/dag';
import { convertDagToNodesAndEdges, calculateDagMetrics } from '../utils/dagUtils';
import { useDAGRun, useDAGRunUpdates } from '../lib/api/hooks';
import '../styles/dagGraph.css';

interface DAGGraphProps {
  dagId: string;
  runId: string;
  onNodeClick?: (node: Node) => void;
  className?: string;
}

const DAGGraph: React.FC<DAGGraphProps> = ({
  dagId,
  runId,
  onNodeClick,
  className = '',
}) => {
  // Fetch initial DAG run data
  const { data: dagRun, error: apiError, loading } = useDAGRun(dagId, runId);
  
  // Subscribe to real-time updates
  const { status, steps, progress, error: wsError } = useDAGRunUpdates(dagId, runId);

  // Convert DAG to nodes and edges
  const { nodes: initialNodes, edges: initialEdges } = dagRun 
    ? convertDagToNodesAndEdges(dagRun)
    : { nodes: [], edges: [] };

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  // Update nodes when steps change
  useEffect(() => {
    if (Object.keys(steps).length > 0) {
      setNodes((prevNodes) =>
        prevNodes.map((node) => {
          const step = steps[node.id];
          if (step) {
            return {
              ...node,
              data: {
                ...node.data,
                status: step.status,
                startTime: step.startTime,
                endTime: step.endTime,
                duration: step.duration,
                retryCount: step.retryCount,
                error: step.error,
              },
            };
          }
          return node;
        })
      );
    }
  }, [steps, setNodes]);

  const handleNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      if (onNodeClick) {
        onNodeClick(node);
      }
    },
    [onNodeClick]
  );

  // Calculate metrics from progress updates or DAG run
  const metrics = progress || (dagRun ? calculateDagMetrics(dagRun) : {
    totalSteps: 0,
    completedSteps: 0,
    runningSteps: 0,
    failedSteps: 0,
    completionPercentage: 0,
  });

  if (loading) {
    return (
      <div className={`dag-graph-container ${className} flex items-center justify-center`}>
        <div className="text-gray-500">Loading DAG...</div>
      </div>
    );
  }

  if (apiError || wsError) {
    return (
      <div className={`dag-graph-container ${className} flex items-center justify-center`}>
        <div className="text-red-500">
          Error: {apiError?.message || wsError || 'Failed to load DAG'}
        </div>
      </div>
    );
  }

  if (!dagRun) {
    return (
      <div className={`dag-graph-container ${className} flex items-center justify-center`}>
        <div className="text-gray-500">No DAG run found</div>
      </div>
    );
  }

  return (
    <div className={`dag-graph-container ${className}`}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={handleNodeClick}
        fitView
      >
        <Background />
        <Controls className="dag-graph-controls" />
        <MiniMap className="dag-graph-minimap" />
      </ReactFlow>
      <div className="dag-graph-metrics">
        <div>Total Steps: {metrics.totalSteps}</div>
        <div>Completed: {metrics.completedSteps}</div>
        <div>Running: {metrics.runningSteps}</div>
        <div>Failed: {metrics.failedSteps}</div>
        <div>Progress: {metrics.completionPercentage.toFixed(1)}%</div>
      </div>
    </div>
  );
};

export default DAGGraph; 
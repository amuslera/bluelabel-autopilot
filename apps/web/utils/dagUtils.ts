import { DAGRun, DAGStep } from '../types/dag';
import { Node, Edge } from 'reactflow';

export const getNodeColor = (status: string): string => {
  switch (status) {
    case 'completed':
    case 'SUCCESS':
      return '#10B981'; // green-500
    case 'running':
    case 'RUNNING':
      return '#3B82F6'; // blue-500
    case 'failed':
    case 'FAILED':
      return '#EF4444'; // red-500
    case 'pending':
    case 'PENDING':
      return '#9CA3AF'; // gray-400
    default:
      return '#6B7280'; // gray-500
  }
};

export const convertDagToNodesAndEdges = (dagRun: any): {
  nodes: Node[];
  edges: Edge[];
} => {
  const nodes: Node[] = dagRun.steps.map((step: any, index: number) => ({
    id: step.name || step.id || `step-${index}`,
    type: 'default',
    position: { x: index * 200, y: 0 },
    data: {
      label: step.name || step.id || `Step ${index + 1}`,
      status: step.status,
      duration: step.duration_ms,
      error: step.error,
    },
    style: {
      background: getNodeColor(step.status),
      color: '#FFFFFF',
      border: '1px solid #374151',
      borderRadius: '8px',
      padding: '10px',
      width: 150,
    },
  }));

  const edges: Edge[] = [];
  
  // Create sequential edges for now (can be enhanced later for complex dependencies)
  for (let i = 0; i < dagRun.steps.length - 1; i++) {
    const sourceId = dagRun.steps[i].name || dagRun.steps[i].id || `step-${i}`;
    const targetId = dagRun.steps[i + 1].name || dagRun.steps[i + 1].id || `step-${i + 1}`;
    edges.push({
      id: `${sourceId}-${targetId}`,
      source: sourceId,
      target: targetId,
      type: 'smoothstep',
      animated: dagRun.steps[i + 1].status === 'running',
      style: { stroke: '#6B7280' },
    });
  }

  return { nodes, edges };
};

export const calculateDagMetrics = (dagRun: any) => {
  const totalSteps = dagRun.steps.length;
  const completedSteps = dagRun.steps.filter(
    (step: any) => step.status === 'completed' || step.status === 'SUCCESS'
  ).length;
  const failedSteps = dagRun.steps.filter(
    (step: any) => step.status === 'failed' || step.status === 'FAILED'
  ).length;
  const runningSteps = dagRun.steps.filter(
    (step: any) => step.status === 'running' || step.status === 'RUNNING'
  ).length;

  return {
    totalSteps,
    completedSteps,
    failedSteps,
    runningSteps,
    completionPercentage: (completedSteps / totalSteps) * 100,
  };
}; 
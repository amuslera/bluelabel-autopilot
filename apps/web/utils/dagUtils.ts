import { DAGRun, DAGStep } from '../types/dag';
import { Node, Edge } from 'reactflow';

export const getNodeColor = (status: DAGStep['status']): string => {
  switch (status) {
    case 'SUCCESS':
      return '#10B981'; // green-500
    case 'RUNNING':
      return '#3B82F6'; // blue-500
    case 'FAILED':
      return '#EF4444'; // red-500
    case 'PENDING':
      return '#9CA3AF'; // gray-400
    default:
      return '#6B7280'; // gray-500
  }
};

export const convertDagToNodesAndEdges = (dagRun: DAGRun): {
  nodes: Node[];
  edges: Edge[];
} => {
  const nodes: Node[] = dagRun.steps.map((step, index) => ({
    id: step.id,
    type: 'default',
    position: { x: index * 200, y: 0 },
    data: {
      label: step.id,
      status: step.status,
      duration: step.duration,
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

  const edges: Edge[] = dagRun.steps.flatMap((step) =>
    step.dependencies.map((depId) => ({
      id: `${depId}-${step.id}`,
      source: depId,
      target: step.id,
      type: 'smoothstep',
      animated: step.status === 'RUNNING',
      style: { stroke: '#6B7280' },
    }))
  );

  return { nodes, edges };
};

export const calculateDagMetrics = (dagRun: DAGRun) => {
  const totalSteps = dagRun.steps.length;
  const completedSteps = dagRun.steps.filter(
    (step) => step.status === 'SUCCESS'
  ).length;
  const failedSteps = dagRun.steps.filter(
    (step) => step.status === 'FAILED'
  ).length;
  const runningSteps = dagRun.steps.filter(
    (step) => step.status === 'RUNNING'
  ).length;

  return {
    totalSteps,
    completedSteps,
    failedSteps,
    runningSteps,
    completionPercentage: (completedSteps / totalSteps) * 100,
  };
}; 
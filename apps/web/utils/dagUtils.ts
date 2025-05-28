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
  // Convert steps object to array
  const stepsArray = dagRun.steps 
    ? (Array.isArray(dagRun.steps) 
        ? dagRun.steps 
        : Object.values(dagRun.steps))
    : [];

  const nodes: Node[] = stepsArray.map((step: any, index: number) => ({
    id: step.step_id || step.name || step.id || `step-${index}`,
    type: 'default',
    position: { x: index * 200, y: 100 },
    data: {
      label: step.metadata?.name || step.name || step.step_id || `Step ${index + 1}`,
      status: step.status,
      duration: step.duration_seconds || step.duration_ms,
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
  for (let i = 0; i < stepsArray.length - 1; i++) {
    const sourceId = stepsArray[i].step_id || stepsArray[i].name || stepsArray[i].id || `step-${i}`;
    const targetId = stepsArray[i + 1].step_id || stepsArray[i + 1].name || stepsArray[i + 1].id || `step-${i + 1}`;
    edges.push({
      id: `${sourceId}-${targetId}`,
      source: sourceId,
      target: targetId,
      type: 'smoothstep',
      animated: stepsArray[i + 1].status === 'running',
      style: { stroke: '#6B7280' },
    });
  }

  return { nodes, edges };
};

export const calculateDagMetrics = (dagRun: any) => {
  // Convert steps object to array
  const stepsArray = dagRun.steps 
    ? (Array.isArray(dagRun.steps) 
        ? dagRun.steps 
        : Object.values(dagRun.steps))
    : [];

  const totalSteps = stepsArray.length;
  const completedSteps = stepsArray.filter(
    (step: any) => step.status === 'completed' || step.status === 'SUCCESS' || step.status === 'success'
  ).length;
  const failedSteps = stepsArray.filter(
    (step: any) => step.status === 'failed' || step.status === 'FAILED'
  ).length;
  const runningSteps = stepsArray.filter(
    (step: any) => step.status === 'running' || step.status === 'RUNNING'
  ).length;

  return {
    totalSteps,
    completedSteps,
    failedSteps,
    runningSteps,
    completionPercentage: totalSteps > 0 ? (completedSteps / totalSteps) * 100 : 0,
  };
}; 
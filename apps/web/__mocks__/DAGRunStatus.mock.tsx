import React from 'react';

interface DAGStep {
  id: string;
  status: 'pending' | 'running' | 'success' | 'failed' | 'skipped';
  [key: string]: any;
}

interface DAGRunStatusProps {
  dagRun: {
    id: string;
    dagId: string;
    runId: string;
    status: string;
    steps: DAGStep[];
    [key: string]: any;
  };
}

const DAGRunStatus: React.FC<DAGRunStatusProps> = ({ dagRun }) => {
  if (!dagRun) return null;
  
  return (
    <div data-testid="dag-run-status">
      <h3>DAG Run: {dagRun.dagId} - {dagRun.runId}</h3>
      <div>Status: {dagRun.status}</div>
      <div>
        <h4>Steps:</h4>
        <ul>
          {dagRun.steps?.map((step) => (
            <li key={step.id}>
              {step.id}: {step.status}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default DAGRunStatus;

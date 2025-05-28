import React from 'react';
import DAGGraph from '../components/DAGGraph';

export default function Home() {
  const testWorkflowId = 'd303998c-b9b0-44bb-8a0f-b12312fad026';

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="w-full">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold mb-4">DAG Graph Demo</h2>
              <DAGGraph runId={testWorkflowId} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 
import React, { useState } from 'react';
import { useRouter } from 'next/router';
import DAGGraph from '../../components/DAGGraph';
import ErrorBoundary from '../../components/ErrorBoundary';

export default function DAGRunPage() {
  const router = useRouter();
  const { runId } = router.query;
  const [graphKey, setGraphKey] = useState(0);
  const [statusKey, setStatusKey] = useState(0);

  if (!router.isReady || !runId) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  const handleGraphReset = () => {
    setGraphKey(prev => prev + 1);
  };

  const handleStatusReset = () => {
    setStatusKey(prev => prev + 1);
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="w-full">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold mb-4">DAG Graph</h2>
              <ErrorBoundary
                key={graphKey}
                onReset={handleGraphReset}
                fallback={
                  <div className="p-4 bg-red-50 rounded-lg border border-red-200">
                    <p className="text-sm text-red-700">Failed to load DAG graph. Please try again.</p>
                    <button
                      onClick={handleGraphReset}
                      className="mt-2 text-sm text-red-600 hover:text-red-800"
                    >
                      Retry
                    </button>
                  </div>
                }
              >
                <DAGGraph runId={runId as string} />
              </ErrorBoundary>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

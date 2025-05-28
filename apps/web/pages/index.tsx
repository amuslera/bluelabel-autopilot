import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { apiClient } from '../lib/api/client';

export default function Home() {
  const [runs, setRuns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchRuns() {
      try {
        const data = await apiClient.listDAGRuns('', 20, 0);
        setRuns(data || []);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchRuns();
  }, []);

  const triggerWorkflow = async () => {
    try {
      const result = await apiClient.runWorkflow('/Users/arielmuslera/Development/Projects/bluelabel-autopilot/workflows/test_simple.yaml', {});
      alert(`Workflow started! Run ID: ${result.run_id}`);
      // Refresh the list
      window.location.reload();
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold">Workflow Runs</h2>
              <button
                onClick={triggerWorkflow}
                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
              >
                Run Sample Workflow
              </button>
            </div>

            {loading && <div>Loading...</div>}
            {error && <div className="text-red-500">Error: {error}</div>}
            
            {!loading && !error && runs.length === 0 && (
              <div className="text-gray-500 text-center py-8">
                No workflow runs yet. Click "Run Sample Workflow" to start one!
              </div>
            )}

            {!loading && !error && runs.length > 0 && (
              <div className="space-y-4">
                {runs.map((run) => (
                  <Link key={run.id} href={`/dag/${run.id}`}>
                    <div className="border rounded-lg p-4 hover:bg-gray-50 cursor-pointer">
                      <div className="flex justify-between items-center">
                        <div>
                          <h3 className="font-semibold">{run.workflow_name || 'Workflow'}</h3>
                          <p className="text-sm text-gray-500">ID: {run.id}</p>
                        </div>
                        <div className="text-right">
                          <span className={`px-2 py-1 rounded text-sm ${
                            run.status === 'success' ? 'bg-green-100 text-green-800' :
                            run.status === 'failed' ? 'bg-red-100 text-red-800' :
                            run.status === 'running' ? 'bg-blue-100 text-blue-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {run.status}
                          </span>
                          <p className="text-xs text-gray-500 mt-1">
                            {new Date(run.started_at).toLocaleString()}
                          </p>
                        </div>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
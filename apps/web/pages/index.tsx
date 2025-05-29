import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { apiClient } from '../lib/api/client';

export default function Home() {
  const [runs, setRuns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [triggering, setTriggering] = useState(false);

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
    
    // Auto-refresh every 5 seconds for demo
    const interval = setInterval(fetchRuns, 5000);
    return () => clearInterval(interval);
  }, []);

  const triggerWorkflow = async (workflowType = 'simple') => {
    setTriggering(true);
    try {
      let workflowPath;
      let inputs = {};
      
      switch (workflowType) {
        case 'simple':
          workflowPath = '/Users/arielmuslera/Development/Projects/bluelabel-autopilot/workflows/test_simple.yaml';
          break;
        case 'pdf':
          workflowPath = '/Users/arielmuslera/Development/Projects/bluelabel-autopilot/workflows/pdf_ingestion_digest.yaml';
          inputs = { demo_mode: true };
          break;
        case 'url':
          workflowPath = '/Users/arielmuslera/Development/Projects/bluelabel-autopilot/workflows/url_ingestion_digest.yaml';
          inputs = { url: 'https://example.com/demo-article', demo_mode: true };
          break;
        case 'complex':
          workflowPath = '/Users/arielmuslera/Development/Projects/bluelabel-autopilot/workflows/sample_ingestion_digest.yaml';
          inputs = { demo_mode: true, complexity: 'high' };
          break;
        default:
          workflowPath = '/Users/arielmuslera/Development/Projects/bluelabel-autopilot/workflows/test_simple.yaml';
      }

      const result = await apiClient.runWorkflow(workflowPath, inputs);
      
      // Show success notification
      const notification = document.createElement('div');
      notification.className = 'fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-fade-in';
      notification.innerHTML = `
        <div class="flex items-center space-x-2">
          <span>✅</span>
          <span>Workflow started! Run ID: ${result.run_id}</span>
        </div>
      `;
      document.body.appendChild(notification);
      
      // Auto-remove notification
      setTimeout(() => {
        document.body.removeChild(notification);
      }, 5000);
      
      // Refresh the list after a short delay
      setTimeout(() => {
        window.location.reload();
      }, 1000);
    } catch (err) {
      // Show error notification
      const notification = document.createElement('div');
      notification.className = 'fixed top-4 right-4 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg z-50';
      notification.innerHTML = `
        <div class="flex items-center space-x-2">
          <span>❌</span>
          <span>Error: ${err.message}</span>
        </div>
      `;
      document.body.appendChild(notification);
      
      setTimeout(() => {
        document.body.removeChild(notification);
      }, 5000);
    } finally {
      setTriggering(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status?.toLowerCase()) {
      case 'success':
      case 'completed':
        return '✅';
      case 'failed':
      case 'error':
        return '❌';
      case 'running':
      case 'in_progress':
        return '🔄';
      case 'pending':
      case 'queued':
        return '⏳';
      default:
        return '📄';
    }
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'success':
      case 'completed':
        return 'bg-gradient-to-r from-green-100 to-green-200 text-green-800 border-green-300';
      case 'failed':
      case 'error':
        return 'bg-gradient-to-r from-red-100 to-red-200 text-red-800 border-red-300';
      case 'running':
      case 'in_progress':
        return 'bg-gradient-to-r from-blue-100 to-blue-200 text-blue-800 border-blue-300 animate-pulse';
      case 'pending':
      case 'queued':
        return 'bg-gradient-to-r from-yellow-100 to-yellow-200 text-yellow-800 border-yellow-300';
      default:
        return 'bg-gradient-to-r from-gray-100 to-gray-200 text-gray-800 border-gray-300';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      <div className="max-w-7xl mx-auto py-8 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            🚀 Bluelabel Autopilot
          </h1>
          <p className="text-xl text-gray-600">
            Real-time DAG Workflow Orchestration
          </p>
          <div className="mt-4 inline-flex items-center space-x-2 px-4 py-2 bg-green-100 text-green-800 rounded-full text-sm">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span>Live Demo Environment</span>
          </div>
        </div>

        <div className="px-4 py-6 sm:px-0">
          {/* Demo Controls */}
          <div className="bg-white rounded-xl shadow-lg p-6 mb-8 border border-gray-200">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">🎮 Demo Controls</h2>
            <p className="text-gray-600 mb-6">
              Choose a workflow type to demonstrate different capabilities of the platform
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <button
                onClick={() => triggerWorkflow('simple')}
                disabled={triggering}
                className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 disabled:from-gray-400 disabled:to-gray-500 text-white font-bold py-4 px-6 rounded-lg transition-all duration-200 transform hover:scale-105 shadow-lg"
              >
                <div className="text-2xl mb-2">⚡</div>
                <div>Quick Test</div>
                <div className="text-sm opacity-80">~5 seconds</div>
              </button>
              
              <button
                onClick={() => triggerWorkflow('pdf')}
                disabled={triggering}
                className="bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 disabled:from-gray-400 disabled:to-gray-500 text-white font-bold py-4 px-6 rounded-lg transition-all duration-200 transform hover:scale-105 shadow-lg"
              >
                <div className="text-2xl mb-2">📄</div>
                <div>PDF Analysis</div>
                <div className="text-sm opacity-80">~30 seconds</div>
              </button>
              
              <button
                onClick={() => triggerWorkflow('url')}
                disabled={triggering}
                className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 disabled:from-gray-400 disabled:to-gray-500 text-white font-bold py-4 px-6 rounded-lg transition-all duration-200 transform hover:scale-105 shadow-lg"
              >
                <div className="text-2xl mb-2">🌐</div>
                <div>URL Processing</div>
                <div className="text-sm opacity-80">~45 seconds</div>
              </button>
              
              <button
                onClick={() => triggerWorkflow('complex')}
                disabled={triggering}
                className="bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 disabled:from-gray-400 disabled:to-gray-500 text-white font-bold py-4 px-6 rounded-lg transition-all duration-200 transform hover:scale-105 shadow-lg"
              >
                <div className="text-2xl mb-2">🔧</div>
                <div>Complex Pipeline</div>
                <div className="text-sm opacity-80">~90 seconds</div>
              </button>
            </div>
            
            {triggering && (
              <div className="mt-4 text-center">
                <div className="inline-flex items-center space-x-2 text-blue-600">
                  <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                  <span>Starting workflow...</span>
                </div>
              </div>
            )}
          </div>

          {/* Workflow Runs */}
          <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900">📊 Recent Workflow Runs</h2>
              <div className="flex items-center space-x-2 text-sm text-gray-500">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                <span>Auto-refreshing every 5s</span>
              </div>
            </div>

            {loading && (
              <div className="text-center py-12">
                <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                <div className="text-gray-600">Loading workflow runs...</div>
              </div>
            )}
            
            {error && (
              <div className="text-center py-12">
                <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-red-500 text-2xl">⚠</span>
                </div>
                <div className="text-red-600 font-medium">Error: {error}</div>
              </div>
            )}
            
            {!loading && !error && runs.length === 0 && (
              <div className="text-center py-12">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-gray-400 text-2xl">📋</span>
                </div>
                <div className="text-gray-500 text-lg font-medium mb-2">No workflow runs yet</div>
                <div className="text-gray-400">Click one of the demo buttons above to start!</div>
              </div>
            )}

            {!loading && !error && runs.length > 0 && (
              <div className="space-y-4">
                {runs.map((run) => (
                  <Link key={run.id} href={`/dag/${run.id}`}>
                    <div className="border rounded-xl p-6 hover:bg-gradient-to-r hover:from-blue-50 hover:to-indigo-50 cursor-pointer transition-all duration-200 transform hover:scale-[1.02] hover:shadow-md">
                      <div className="flex justify-between items-center">
                        <div className="flex items-center space-x-4">
                          <div className="text-3xl">
                            {getStatusIcon(run.status)}
                          </div>
                          <div>
                            <h3 className="font-bold text-lg text-gray-900">
                              {run.workflow_name || 'Workflow'}
                            </h3>
                            <p className="text-sm text-gray-500 font-mono">
                              ID: {run.id}
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <span className={`px-4 py-2 rounded-full text-sm font-bold border ${getStatusColor(run.status)}`}>
                            {run.status?.toUpperCase()}
                          </span>
                          <p className="text-xs text-gray-500 mt-2">
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
      
      <style jsx>{`
        @keyframes fade-in {
          from { opacity: 0; transform: translateY(-10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in {
          animation: fade-in 0.3s ease-out;
        }
      `}</style>
    </div>
  );
}
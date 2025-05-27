import { NextPage } from 'next';
import { useRouter } from 'next/router';
import { useEffect, useState } from 'react';
import Head from 'next/head';
import DAGRunStatus from '@/components/DAGRunStatus';
import { DAGRun, generateMockDAGRun } from '@/lib/types';

const DAGRunPage: NextPage = () => {
  const router = useRouter();
  const { runId } = router.query;
  const [dagRun, setDagRun] = useState<DAGRun | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!runId) return;

    const fetchDAGRun = async () => {
      try {
        setIsLoading(true);
        
        // In a real app, you would fetch from your API:
        const response = await fetch(`/api/dag-runs/${runId}`);
        if (!response.ok) {
          if (response.status === 404) {
            setDagRun(null);
            setError(null);
            return;
          }
          throw new Error('Failed to fetch DAG run');
        }
        const data = await response.json();
        
        // For testing, fall back to mock data if no data is returned
        const mockData = data || generateMockDAGRun({ id: runId as string });
        
        setDagRun(mockData);
        setError(null);
      } catch (err) {
        console.error('Error fetching DAG run:', err);
        setError('Failed to load DAG run. Please try again later.');
        setDagRun(null);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDAGRun();
  }, [runId]);

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <Head>
        <title>DAG Run {runId} | Bluelabel Autopilot</title>
        <meta name="description" content={`Details for DAG run ${runId}`} />
      </Head>

      <div className="max-w-4xl mx-auto">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900">DAG Run Details</h1>
          <p className="mt-1 text-sm text-gray-500">
            Run ID: <span className="font-mono">{runId}</span>
          </p>
        </div>

        {isLoading ? (
          <div className="bg-white shadow overflow-hidden sm:rounded-lg p-6 text-center">
            <div className="animate-pulse flex flex-col items-center justify-center">
              <div className="h-8 w-8 bg-blue-100 rounded-full flex items-center justify-center">
                <svg className="h-5 w-5 text-blue-500 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </div>
              <p className="mt-2 text-sm text-gray-500">Loading DAG run details...</p>
            </div>
          </div>
        ) : error ? (
          <div className="bg-red-50 border-l-4 border-red-400 p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            </div>
          </div>
        ) : dagRun ? (
          <DAGRunStatus dagRun={dagRun} />
        ) : (
          <div className="bg-white shadow overflow-hidden sm:rounded-lg p-6 text-center">
            <p className="text-gray-500">No DAG run found with ID: {runId}</p>
          </div>
        )}

        <div className="mt-6">
          <button
            type="button"
            onClick={() => router.back()}
            className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <svg className="-ml-1 mr-2 h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
            Back to DAG Runs
          </button>
        </div>
      </div>
    </div>
  );
};

export default DAGRunPage;

import { useEffect } from 'react';
import { useRouter } from 'next/router';

export default function TestPage() {
  const router = useRouter();
  
  useEffect(() => {
    console.log('TestPage mounted');
    console.log('Router query:', router.query);
    
    return () => {
      console.log('TestPage unmounted');
    };
  }, [router.query]);
  
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <h1 className="text-2xl font-bold mb-4">Test Page</h1>
      <p className="mb-4">This is a test page to verify Next.js routing and rendering.</p>
      <div className="bg-white p-4 rounded shadow">
        <h2 className="text-lg font-semibold mb-2">Router Info:</h2>
        <pre className="bg-gray-100 p-2 rounded text-sm overflow-auto">
          {JSON.stringify({
            pathname: router.pathname,
            query: router.query,
            asPath: router.asPath,
          }, null, 2)}
        </pre>
      </div>
      <div className="mt-4">
        <button
          onClick={() => router.push('/dag/example-run-123')}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Go to DAG Run
        </button>
      </div>
    </div>
  );
}

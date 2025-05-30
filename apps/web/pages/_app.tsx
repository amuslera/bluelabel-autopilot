import type { AppProps } from 'next/app';
import '@/styles/globals.css';
import '@/styles/dagGraph.css';

function MyApp({ Component, pageProps }: AppProps) {
  return (
    <div className="min-h-screen bg-gray-50">
      <Component {...pageProps} />
    </div>
  );
}

export default MyApp;

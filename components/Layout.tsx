import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { motion } from 'framer-motion';
import { Sparkles, LogIn } from 'lucide-react';
import { useAuth } from '../lib/hooks/useAuth';
import UserMenu from './auth/UserMenu';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { user, isAuthenticated, logout, isLoading } = useAuth();
  const router = useRouter();

  // Don't show navigation on auth pages
  const isAuthPage = ['/login', '/register', '/reset-password'].includes(router.pathname);

  if (isAuthPage) {
    return <>{children}</>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo and Brand */}
            <Link href="/">
              <motion.div
                whileHover={{ scale: 1.05 }}
                className="flex items-center space-x-2 cursor-pointer"
              >
                <Sparkles className="h-8 w-8 text-blue-600" />
                <span className="text-xl font-bold text-gray-900">AIOS v2</span>
              </motion.div>
            </Link>

            {/* Navigation Links */}
            <nav className="hidden md:flex items-center space-x-8">
              <Link href="/">
                <motion.span
                  whileHover={{ color: '#2563eb' }}
                  className={`text-sm font-medium transition-colors cursor-pointer ${
                    router.pathname === '/' 
                      ? 'text-blue-600' 
                      : 'text-gray-700 hover:text-blue-600'
                  }`}
                >
                  Dashboard
                </motion.span>
              </Link>
              
              <Link href="/process">
                <motion.span
                  whileHover={{ color: '#2563eb' }}
                  className={`text-sm font-medium transition-colors cursor-pointer ${
                    router.pathname === '/process' 
                      ? 'text-blue-600' 
                      : 'text-gray-700 hover:text-blue-600'
                  }`}
                >
                  Process
                </motion.span>
              </Link>

              <Link href="/agents">
                <motion.span
                  whileHover={{ color: '#2563eb' }}
                  className={`text-sm font-medium transition-colors cursor-pointer ${
                    router.pathname === '/agents' 
                      ? 'text-blue-600' 
                      : 'text-gray-700 hover:text-blue-600'
                  }`}
                >
                  Agents
                </motion.span>
              </Link>
            </nav>

            {/* Authentication Section */}
            <div className="flex items-center space-x-4">
              {isLoading ? (
                <div className="h-8 w-20 bg-gray-200 rounded animate-pulse" />
              ) : isAuthenticated && user ? (
                <UserMenu user={user} onLogout={logout} />
              ) : (
                <div className="flex items-center space-x-3">
                  <Link href="/login">
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      className="flex items-center space-x-2 px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 transition-colors"
                    >
                      <LogIn className="h-4 w-4" />
                      <span>Sign In</span>
                    </motion.button>
                  </Link>
                  
                  <Link href="/register">
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors"
                    >
                      Sign Up
                    </motion.button>
                  </Link>
                </div>
              )}
            </div>

            {/* Mobile Menu Toggle */}
            <div className="md:hidden">
              <button
                type="button"
                className="p-2 rounded-md text-gray-700 hover:text-gray-900 hover:bg-gray-100 transition-colors"
                onClick={() => {
                  // TODO: Implement mobile menu
                  console.log('Mobile menu clicked');
                }}
              >
                <span className="sr-only">Open menu</span>
                <div className="w-6 h-6 flex flex-col justify-center items-center">
                  <span className="w-4 h-0.5 bg-current mb-1"></span>
                  <span className="w-4 h-0.5 bg-current mb-1"></span>
                  <span className="w-4 h-0.5 bg-current"></span>
                </div>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main>
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-auto">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex flex-col md:flex-row items-center justify-between">
            <div className="flex items-center space-x-2 mb-4 md:mb-0">
              <Sparkles className="h-5 w-5 text-blue-600" />
              <span className="text-sm text-gray-600">
                © 2024 AIOS v2. Powered by AI.
              </span>
            </div>
            
            <div className="flex items-center space-x-6 text-sm text-gray-600">
              <Link href="/terms" className="hover:text-gray-900 transition-colors">
                Terms
              </Link>
              <Link href="/privacy" className="hover:text-gray-900 transition-colors">
                Privacy
              </Link>
              <Link href="/support" className="hover:text-gray-900 transition-colors">
                Support
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Layout; 
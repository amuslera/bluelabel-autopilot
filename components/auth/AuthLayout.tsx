import React from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { Sparkles, ArrowLeft } from 'lucide-react';
import { AuthLayoutProps } from '../../lib/types/auth';

const AuthLayout: React.FC<AuthLayoutProps> = ({ 
  children, 
  title, 
  subtitle, 
  showLogo = true 
}) => {
  return (
    <>
      <Head>
        <title>{title} - AIOS v2</title>
        <meta name="description" content={subtitle || 'AIOS v2 Authentication'} />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
        {/* Background Pattern */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-50 to-indigo-100 opacity-50" />
        
        {/* Main Container */}
        <div className="relative sm:mx-auto sm:w-full sm:max-w-md">
          {/* Back Link */}
          <div className="mb-6">
            <Link href="/">
              <motion.button
                whileHover={{ x: -2 }}
                className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors"
              >
                <ArrowLeft className="h-4 w-4" />
                <span>Back to Home</span>
              </motion.button>
            </Link>
          </div>

          {/* Logo and Header */}
          {showLogo && (
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center mb-8"
            >
              <div className="flex items-center justify-center space-x-2 mb-4">
                <Sparkles className="h-8 w-8 text-blue-600" />
                <span className="text-2xl font-bold text-gray-900">AIOS v2</span>
              </div>
              
              <motion.h2
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.1 }}
                className="text-3xl font-extrabold text-gray-900 mb-2"
              >
                {title}
              </motion.h2>
              
              {subtitle && (
                <motion.p
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.2 }}
                  className="text-sm text-gray-600"
                >
                  {subtitle}
                </motion.p>
              )}
            </motion.div>
          )}

          {/* Auth Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white py-8 px-6 shadow-xl rounded-lg sm:px-10"
          >
            {children}
          </motion.div>

          {/* Footer */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="text-center mt-8"
          >
            <p className="text-xs text-gray-500">
              Secure authentication powered by AIOS v2
            </p>
          </motion.div>
        </div>
      </div>
    </>
  );
};

export default AuthLayout; 
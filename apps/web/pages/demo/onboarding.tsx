import React, { useState } from 'react';
import Head from 'next/head';
import { motion } from 'framer-motion';
import { 
  Upload, 
  FileText, 
  Users, 
  Settings, 
  BarChart3, 
  Brain,
  Zap,
  CheckCircle
} from 'lucide-react';
import ProductTour from '../../components/onboarding/ProductTour';

const OnboardingDemo: React.FC = () => {
  const [isTourEnabled, setIsTourEnabled] = useState(false);
  const [userType, setUserType] = useState<'individual' | 'team' | 'enterprise'>('individual');

  const startTour = () => {
    console.log('🚀 Starting AIOS v2 Product Tour!');
    console.log('User type:', userType);
    setIsTourEnabled(true);
  };

  const stopTour = () => {
    console.log('⏹️ Stopping AIOS v2 Product Tour');
    setIsTourEnabled(false);
  };

  return (
    <>
      <Head>
        <title>AIOS v2 - Onboarding Demo</title>
        <meta name="description" content="Experience the AIOS v2 onboarding flow" />
      </Head>

      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center">
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  AIOS v2
                </h1>
              </div>
              <div className="flex items-center space-x-4">
                <select 
                  value={userType} 
                  onChange={(e) => setUserType(e.target.value as any)}
                  className="border border-gray-300 rounded-md px-3 py-1 text-sm"
                >
                  <option value="individual">Individual</option>
                  <option value="team">Team</option>
                  <option value="enterprise">Enterprise</option>
                </select>
                <button
                  onClick={startTour}
                  className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:shadow-lg transition-all"
                >
                  Start Product Tour
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Main Dashboard */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Welcome Section */}
          <div className="dashboard-welcome mb-8">
            <div className="bg-white rounded-lg shadow-sm p-8 border">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                Welcome to AIOS v2! 🚀
              </h2>
              <p className="text-gray-600 text-lg mb-6">
                Transform your documents into insights with AI-powered processing
              </p>
              <div className="flex items-center space-x-6 text-sm text-gray-500">
                <span className="flex items-center">
                  <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                  50+ AI Agents
                </span>
                <span className="flex items-center">
                  <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                  99.8% Accuracy
                </span>
                <span className="flex items-center">
                  <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                  2.3s Average Processing
                </span>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Left Sidebar - AI Agents */}
            <div className="ai-agents-panel">
              <div className="bg-white rounded-lg shadow-sm border">
                <div className="p-6 border-b">
                  <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                    <Brain className="h-5 w-5 mr-2 text-purple-600" />
                    AI Agents
                  </h3>
                </div>
                <div className="p-6 space-y-4">
                  <div className="flex items-center p-3 bg-blue-50 rounded-lg border border-blue-200">
                    <BarChart3 className="h-8 w-8 text-blue-600 mr-3" />
                    <div>
                      <div className="font-medium text-gray-900">Data Agent</div>
                      <div className="text-sm text-gray-500">Ready</div>
                    </div>
                  </div>
                  <div className="flex items-center p-3 bg-green-50 rounded-lg border border-green-200">
                    <FileText className="h-8 w-8 text-green-600 mr-3" />
                    <div>
                      <div className="font-medium text-gray-900">Summary Agent</div>
                      <div className="text-sm text-gray-500">Ready</div>
                    </div>
                  </div>
                  <div className="flex items-center p-3 bg-purple-50 rounded-lg border border-purple-200">
                    <Zap className="h-8 w-8 text-purple-600 mr-3" />
                    <div>
                      <div className="font-medium text-gray-900">Chart Agent</div>
                      <div className="text-sm text-gray-500">Ready</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Main Content Area */}
            <div className="lg:col-span-2 space-y-6">
              {/* Upload Area */}
              <div className="upload-area">
                <div className="bg-white rounded-lg shadow-sm border">
                  <div className="p-6 border-b">
                    <h3 className="text-lg font-semibold text-gray-900">Upload Documents</h3>
                  </div>
                  <div className="p-8">
                    <div className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center hover:border-blue-400 transition-colors">
                      <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                      <h4 className="text-lg font-medium text-gray-900 mb-2">
                        Drop your documents here
                      </h4>
                      <p className="text-gray-500 mb-4">
                        Or click to browse files
                      </p>
                      <button className="get-started-button bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-lg font-medium hover:shadow-lg transition-all">
                        Choose Files
                      </button>
                      <div className="mt-4 text-sm text-gray-400">
                        Supports: PDF, Word, Excel, PowerPoint, Images
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Processing Status */}
              <div className="processing-status">
                <div className="bg-white rounded-lg shadow-sm border">
                  <div className="p-6 border-b">
                    <h3 className="text-lg font-semibold text-gray-900">Processing Status</h3>
                  </div>
                  <div className="p-6">
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <span className="text-gray-700">Ready to process documents</span>
                        <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                          Online
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div className="bg-gradient-to-r from-blue-600 to-purple-600 h-2 rounded-full w-0 transition-all duration-300"></div>
                      </div>
                      <div className="text-sm text-gray-500">
                        Upload a document to see AI processing in action
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Results Dashboard */}
              <div className="results-dashboard">
                <div className="bg-white rounded-lg shadow-sm border">
                  <div className="p-6 border-b">
                    <h3 className="text-lg font-semibold text-gray-900">Results & Insights</h3>
                  </div>
                  <div className="p-6">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="bg-gray-50 rounded-lg p-4 text-center">
                        <div className="text-2xl font-bold text-gray-400">--</div>
                        <div className="text-sm text-gray-500">Documents Processed</div>
                      </div>
                      <div className="bg-gray-50 rounded-lg p-4 text-center">
                        <div className="text-2xl font-bold text-gray-400">--</div>
                        <div className="text-sm text-gray-500">Insights Generated</div>
                      </div>
                      <div className="bg-gray-50 rounded-lg p-4 text-center">
                        <div className="text-2xl font-bold text-gray-400">--</div>
                        <div className="text-sm text-gray-500">Time Saved</div>
                      </div>
                    </div>
                    <div className="mt-6 text-center text-gray-500">
                      Your processed documents and insights will appear here
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Additional Panels for Team/Enterprise */}
          {userType !== 'individual' && (
            <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Team Collaboration Panel */}
              <div className="collaboration-panel">
                <div className="bg-white rounded-lg shadow-sm border">
                  <div className="p-6 border-b">
                    <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                      <Users className="h-5 w-5 mr-2 text-blue-600" />
                      Team Collaboration
                    </h3>
                  </div>
                  <div className="p-6">
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <span className="text-gray-700">Team Members</span>
                        <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                          3 Active
                        </span>
                      </div>
                      <div className="text-sm text-gray-500">
                        Collaborate on documents in real-time with your team
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Admin Panel for Enterprise */}
              {userType === 'enterprise' && (
                <div className="admin-panel">
                  <div className="bg-white rounded-lg shadow-sm border">
                    <div className="p-6 border-b">
                      <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                        <Settings className="h-5 w-5 mr-2 text-purple-600" />
                        Enterprise Controls
                      </h3>
                    </div>
                    <div className="p-6">
                      <div className="space-y-4">
                        <div className="flex items-center justify-between">
                          <span className="text-gray-700">Security Level</span>
                          <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                            Enterprise
                          </span>
                        </div>
                        <div className="text-sm text-gray-500">
                          Advanced admin features and analytics
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Product Tour Component */}
        <ProductTour
          isEnabled={isTourEnabled}
          onExit={stopTour}
          userType={userType}
        />

        {/* Footer */}
        <footer className="bg-white border-t mt-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="text-center text-gray-500 text-sm">
              <p>This is a demo of the AIOS v2 onboarding experience</p>
              <p className="mt-2">
                <strong>Instructions:</strong> Click "Start Product Tour" to experience the guided onboarding flow
              </p>
            </div>
          </div>
        </footer>
      </div>
    </>
  );
};

export default OnboardingDemo; 
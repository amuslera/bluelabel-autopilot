import React, { useState, useEffect } from 'react';
import { OnboardingStep } from '../../../types/onboarding';

interface WelcomeStepProps {
  onComplete: (data?: any) => void;
  isCompleted: boolean;
  stepData: OnboardingStep;
}

export const WelcomeStep: React.FC<WelcomeStepProps> = ({
  onComplete,
  isCompleted,
  stepData
}) => {
  const [userName, setUserName] = useState('');
  const [userRole, setUserRole] = useState('');
  const [primaryGoal, setPrimaryGoal] = useState('');

  useEffect(() => {
    // Auto-complete if this is just an introduction step
    if (!stepData.required) {
      setTimeout(() => {
        onComplete({
          userName: userName || 'User',
          userRole: userRole || 'General',
          primaryGoal: primaryGoal || 'Explore AIOS v2'
        });
      }, 2000);
    }
  }, [onComplete, stepData.required, userName, userRole, primaryGoal]);

  const handleComplete = () => {
    onComplete({
      userName,
      userRole,
      primaryGoal
    });
  };

  return (
    <div className="welcome-step space-y-6">
      {/* Hero section */}
      <div className="text-center">
        <div className="mx-auto w-24 h-24 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mb-6">
          <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Welcome to AIOS v2! 🚀
        </h2>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Your AI-powered operating system that transforms how you work with documents, data, and automation. 
          Let's get you set up in just a few minutes!
        </p>
      </div>

      {/* What you'll learn */}
      <div className="bg-blue-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-4">
          What you'll learn in this onboarding:
        </h3>
        <div className="grid md:grid-cols-2 gap-4">
          <div className="flex items-start space-x-3">
            <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
              <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
            </div>
            <div>
              <h4 className="font-medium text-blue-900">Upload & Process Documents</h4>
              <p className="text-sm text-blue-700">Learn to upload files and run AI processing workflows</p>
            </div>
          </div>
          
          <div className="flex items-start space-x-3">
            <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
              <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
            </div>
            <div>
              <h4 className="font-medium text-blue-900">Discover AI Agents</h4>
              <p className="text-sm text-blue-700">Explore and install specialized AI agents from our marketplace</p>
            </div>
          </div>
          
          <div className="flex items-start space-x-3">
            <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
              <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
            </div>
            <div>
              <h4 className="font-medium text-blue-900">Manage Your Workspace</h4>
              <p className="text-sm text-blue-700">Organize projects and collaborate with team members</p>
            </div>
          </div>
          
          <div className="flex items-start space-x-3">
            <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
              <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
            </div>
            <div>
              <h4 className="font-medium text-blue-900">Customize Your Experience</h4>
              <p className="text-sm text-blue-700">Set preferences and configure AIOS v2 for your workflow</p>
            </div>
          </div>
        </div>
      </div>

      {/* User personalization */}
      {stepData.required && (
        <div className="space-y-6">
          <h3 className="text-lg font-semibold text-gray-900">
            Let's personalize your experience
          </h3>
          
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="userName" className="block text-sm font-medium text-gray-700 mb-2">
                What should we call you?
              </label>
              <input
                type="text"
                id="userName"
                value={userName}
                onChange={(e) => setUserName(e.target.value)}
                placeholder="Your name"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <div>
              <label htmlFor="userRole" className="block text-sm font-medium text-gray-700 mb-2">
                What's your role?
              </label>
              <select
                id="userRole"
                value={userRole}
                onChange={(e) => setUserRole(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Select your role</option>
                <option value="business-user">Business User</option>
                <option value="data-analyst">Data Analyst</option>
                <option value="developer">Developer</option>
                <option value="researcher">Researcher</option>
                <option value="content-creator">Content Creator</option>
                <option value="project-manager">Project Manager</option>
                <option value="other">Other</option>
              </select>
            </div>
          </div>
          
          <div>
            <label htmlFor="primaryGoal" className="block text-sm font-medium text-gray-700 mb-2">
              What's your primary goal with AIOS v2?
            </label>
            <select
              id="primaryGoal"
              value={primaryGoal}
              onChange={(e) => setPrimaryGoal(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Select your primary goal</option>
              <option value="document-processing">Process and analyze documents</option>
              <option value="automation">Automate repetitive tasks</option>
              <option value="data-insights">Extract insights from data</option>
              <option value="content-creation">Create and generate content</option>
              <option value="team-collaboration">Collaborate with team members</option>
              <option value="research">Conduct research and analysis</option>
              <option value="explore">Just exploring the platform</option>
            </select>
          </div>

          <div className="flex justify-center mt-8">
            <button
              onClick={handleComplete}
              disabled={!userName || !userRole || !primaryGoal}
              className={`px-8 py-3 rounded-lg font-medium ${
                userName && userRole && primaryGoal
                  ? 'bg-blue-600 text-white hover:bg-blue-700'
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
              }`}
            >
              Let's Get Started! →
            </button>
          </div>
        </div>
      )}

      {/* Key stats */}
      <div className="border-t border-gray-200 pt-6">
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-blue-600">50+</div>
            <div className="text-sm text-gray-600">AI Agents Available</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-green-600">99.9%</div>
            <div className="text-sm text-gray-600">Uptime Guaranteed</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-purple-600">24/7</div>
            <div className="text-sm text-gray-600">Support Available</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WelcomeStep; 
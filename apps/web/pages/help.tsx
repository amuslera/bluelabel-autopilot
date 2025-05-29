import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import HelpSystem from '../components/help/HelpSystem';
import FAQSystem from '../components/help/FAQSystem';
import FeedbackSystem from '../components/help/FeedbackSystem';
import ContextualHelp from '../components/help/ContextualHelp';
import OnboardingFlowComponent from '../components/onboarding/OnboardingFlow';
import UserPreferencesComponent from '../components/settings/UserPreferences';
import { 
  OnboardingFlow, 
  UserProgress, 
  ContextualTip, 
  GuidedTour,
  UserPreferences,
  OnboardingEvent,
  HelpEvent,
  TutorialEvent
} from '../types/onboarding';
import WelcomeStep from '../components/onboarding/steps/WelcomeStep';

const HelpAndDocumentationPage: React.FC = () => {
  const [activeModal, setActiveModal] = useState<string | null>(null);
  const [user] = useState({ id: 'user-123', name: 'Demo User' }); // Mock user
  const [userProgress, setUserProgress] = useState<UserProgress>({
    userId: 'user-123',
    completedSteps: [],
    currentFlow: undefined,
    skippedSteps: [],
    lastActiveStep: undefined,
    progressSavedAt: new Date(),
    totalTimeSpent: 0
  });

  // Mock contextual tips
  const contextualTips: ContextualTip[] = [
    {
      id: 'help-button-tip',
      element: '[data-help-button]',
      title: 'Get Help Anytime',
      content: 'Click here to access help articles, FAQs, and submit feedback.',
      trigger: 'hover',
      position: 'bottom',
      priority: 5,
      showOnce: true
    },
    {
      id: 'search-tip',
      element: '[data-search]',
      title: 'Quick Search',
      content: 'Use the search bar to quickly find help articles and answers.',
      trigger: 'focus',
      position: 'bottom',
      priority: 3
    }
  ];

  // Mock onboarding flow
  const onboardingFlow: OnboardingFlow = {
    id: 'aios-v2-getting-started',
    name: 'AIOS v2 Getting Started',
    description: 'Learn the basics of AIOS v2 in just a few minutes',
    steps: [
      {
        id: 'welcome',
        title: 'Welcome to AIOS v2',
        description: 'Get introduced to the platform and set your preferences',
        component: WelcomeStep,
        required: true,
        completed: false,
        estimatedMinutes: 3,
        prerequisites: [],
        nextSteps: ['dashboard-tour']
      }
    ],
    currentStep: 0,
    totalSteps: 1,
    completionPercentage: 0,
    estimatedTotalMinutes: 3
  };

  const handleOnboardingStepComplete = (stepId: string, data?: any) => {
    setUserProgress(prev => ({
      ...prev,
      completedSteps: [...prev.completedSteps, stepId]
    }));
  };

  const handleOnboardingFlowComplete = () => {
    setActiveModal(null);
    // Show success message or redirect
  };

  const handleEvent = (event: OnboardingEvent | HelpEvent | TutorialEvent) => {
    console.log('Event tracked:', event);
    // In real implementation, send to analytics
  };

  const handlePreferencesSave = async (preferences: UserPreferences) => {
    console.log('Saving preferences:', preferences);
    // In real implementation, save to API
    setActiveModal(null);
  };

  useEffect(() => {
    // Check if user needs onboarding
    const hasCompletedOnboarding = localStorage.getItem('aios-onboarding-completed');
    if (!hasCompletedOnboarding) {
      // Optionally auto-start onboarding
      // setActiveModal('onboarding');
    }
  }, []);

  return (
    <>
      <Head>
        <title>Help & Documentation - AIOS v2</title>
        <meta name="description" content="Get help and learn how to use AIOS v2 effectively" />
      </Head>

      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center space-x-4">
                <h1 className="text-xl font-semibold text-gray-900">
                  AIOS v2 Help Center
                </h1>
              </div>
              <div className="flex items-center space-x-4">
                <button
                  data-help-button
                  onClick={() => setActiveModal('help')}
                  className="flex items-center space-x-2 px-3 py-2 text-gray-600 hover:text-gray-900"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>Help</span>
                </button>
                <button
                  onClick={() => setActiveModal('preferences')}
                  className="flex items-center space-x-2 px-3 py-2 text-gray-600 hover:text-gray-900"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  <span>Settings</span>
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Main content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Hero section */}
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Welcome to AIOS v2 Help Center
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Find answers, learn new features, and get the most out of your AI-powered operating system.
            </p>
          </div>

          {/* Quick search */}
          <div className="max-w-2xl mx-auto mb-12">
            <div className="relative">
              <input
                data-search
                type="text"
                placeholder="Search for help articles, FAQs, or topics..."
                className="w-full px-4 py-3 pl-12 text-lg border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                onFocus={() => setActiveModal('help')}
              />
              <svg className="absolute left-4 top-3.5 w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>

          {/* Quick actions */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            <button
              onClick={() => setActiveModal('onboarding')}
              className="p-6 bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow text-left"
            >
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Getting Started</h3>
              <p className="text-sm text-gray-600">Take a quick tour and learn the basics</p>
            </button>

            <button
              onClick={() => setActiveModal('help')}
              className="p-6 bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow text-left"
            >
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Browse Articles</h3>
              <p className="text-sm text-gray-600">Explore our comprehensive documentation</p>
            </button>

            <button
              onClick={() => setActiveModal('faq')}
              className="p-6 bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow text-left"
            >
              <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">FAQs</h3>
              <p className="text-sm text-gray-600">Find answers to common questions</p>
            </button>

            <button
              onClick={() => setActiveModal('feedback')}
              className="p-6 bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow text-left"
            >
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
                </svg>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Give Feedback</h3>
              <p className="text-sm text-gray-600">Report issues or suggest improvements</p>
            </button>
          </div>

          {/* Feature highlights */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 mb-12">
            <h3 className="text-xl font-semibold text-gray-900 mb-6">Popular Topics</h3>
            <div className="grid md:grid-cols-3 gap-6">
              <div>
                <h4 className="font-medium text-gray-900 mb-3">🚀 Getting Started</h4>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li><button className="hover:text-blue-600">Welcome to AIOS v2</button></li>
                  <li><button className="hover:text-blue-600">Uploading your first document</button></li>
                  <li><button className="hover:text-blue-600">Setting up your workspace</button></li>
                  <li><button className="hover:text-blue-600">Understanding AI agents</button></li>
                </ul>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-900 mb-3">🤖 AI Agents</h4>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li><button className="hover:text-blue-600">Finding and installing agents</button></li>
                  <li><button className="hover:text-blue-600">Managing agent permissions</button></li>
                  <li><button className="hover:text-blue-600">Agent pricing and billing</button></li>
                  <li><button className="hover:text-blue-600">Creating custom workflows</button></li>
                </ul>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-900 mb-3">🔧 Troubleshooting</h4>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li><button className="hover:text-blue-600">Common upload issues</button></li>
                  <li><button className="hover:text-blue-600">Agent installation problems</button></li>
                  <li><button className="hover:text-blue-600">Performance optimization</button></li>
                  <li><button className="hover:text-blue-600">Contact support</button></li>
                </ul>
              </div>
            </div>
          </div>

          {/* Contact support */}
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-8 text-white text-center">
            <h3 className="text-xl font-semibold mb-4">Still need help?</h3>
            <p className="mb-6 opacity-90">
              Can't find what you're looking for? Our support team is here to help.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={() => setActiveModal('feedback')}
                className="px-6 py-3 bg-white text-blue-600 rounded-lg font-medium hover:bg-gray-100 transition-colors"
              >
                Contact Support
              </button>
              <button
                onClick={() => setActiveModal('feedback')}
                className="px-6 py-3 border border-white text-white rounded-lg font-medium hover:bg-white hover:bg-opacity-10 transition-colors"
              >
                Report a Bug
              </button>
            </div>
          </div>
        </main>

        {/* Contextual Help */}
        <ContextualHelp
          tips={contextualTips}
          onTipDismiss={(tipId) => console.log('Tip dismissed:', tipId)}
          userId={user.id}
        />

        {/* Modals */}
        {activeModal === 'onboarding' && (
          <OnboardingFlowComponent
            flow={onboardingFlow}
            userProgress={userProgress}
            onStepComplete={handleOnboardingStepComplete}
            onFlowComplete={handleOnboardingFlowComplete}
            onEvent={handleEvent}
          />
        )}

        {activeModal === 'help' && (
          <HelpSystem
            isOpen={true}
            onClose={() => setActiveModal(null)}
            onEvent={handleEvent}
            userId={user.id}
          />
        )}

        {activeModal === 'faq' && (
          <FAQSystem
            isOpen={true}
            onClose={() => setActiveModal(null)}
            userId={user.id}
            currentContext={{ 'first-visit': true }}
          />
        )}

        {activeModal === 'feedback' && (
          <FeedbackSystem
            isOpen={true}
            onClose={() => setActiveModal(null)}
            userId={user.id}
            currentPage="help"
          />
        )}

        {activeModal === 'preferences' && (
          <UserPreferencesComponent
            isOpen={true}
            onClose={() => setActiveModal(null)}
            userId={user.id}
            onSave={handlePreferencesSave}
          />
        )}
      </div>
    </>
  );
};

export default HelpAndDocumentationPage; 
import React, { useState, useEffect, useCallback } from 'react';
import { OnboardingFlow, OnboardingStep, UserProgress, OnboardingEvent } from '../../types/onboarding';

interface OnboardingFlowProps {
  flow: OnboardingFlow;
  userProgress: UserProgress;
  onStepComplete: (stepId: string, data?: any) => void;
  onFlowComplete: () => void;
  onEvent: (event: OnboardingEvent) => void;
  className?: string;
}

export const OnboardingFlowComponent: React.FC<OnboardingFlowProps> = ({
  flow,
  userProgress,
  onStepComplete,
  onFlowComplete,
  onEvent,
  className = ''
}) => {
  const [currentStepIndex, setCurrentStepIndex] = useState(flow.currentStep);
  const [isStepCompleted, setIsStepCompleted] = useState(false);
  const [stepStartTime, setStepStartTime] = useState<Date | null>(null);
  const [showExitConfirmation, setShowExitConfirmation] = useState(false);

  const currentStep = flow.steps[currentStepIndex];
  const isLastStep = currentStepIndex === flow.steps.length - 1;
  const canProceed = isStepCompleted || !currentStep?.required;

  // Track step start time for analytics
  useEffect(() => {
    if (currentStep) {
      const startTime = new Date();
      setStepStartTime(startTime);
      
      onEvent({
        type: 'step_started',
        stepId: currentStep.id,
        flowId: flow.id,
        userId: userProgress.userId,
        timestamp: startTime
      });
    }
  }, [currentStepIndex, currentStep, flow.id, userProgress.userId, onEvent]);

  // Check if step is already completed
  useEffect(() => {
    if (currentStep && userProgress.completedSteps.includes(currentStep.id)) {
      setIsStepCompleted(true);
    } else {
      setIsStepCompleted(false);
    }
  }, [currentStep, userProgress.completedSteps]);

  const handleStepComplete = useCallback((data?: any) => {
    if (!currentStep) return;

    const duration = stepStartTime ? Date.now() - stepStartTime.getTime() : 0;
    
    onEvent({
      type: 'step_completed',
      stepId: currentStep.id,
      flowId: flow.id,
      userId: userProgress.userId,
      timestamp: new Date(),
      duration,
      metadata: data
    });

    onStepComplete(currentStep.id, data);
    setIsStepCompleted(true);
  }, [currentStep, flow.id, userProgress.userId, stepStartTime, onEvent, onStepComplete]);

  const handleNextStep = useCallback(() => {
    if (!canProceed) return;

    if (isLastStep) {
      onEvent({
        type: 'flow_completed',
        flowId: flow.id,
        userId: userProgress.userId,
        timestamp: new Date()
      });
      onFlowComplete();
    } else {
      setCurrentStepIndex(prev => prev + 1);
    }
  }, [canProceed, isLastStep, flow.id, userProgress.userId, onEvent, onFlowComplete]);

  const handlePreviousStep = useCallback(() => {
    if (currentStepIndex > 0) {
      setCurrentStepIndex(prev => prev - 1);
    }
  }, [currentStepIndex]);

  const handleSkipStep = useCallback(() => {
    if (!currentStep) return;

    onEvent({
      type: 'step_skipped',
      stepId: currentStep.id,
      flowId: flow.id,
      userId: userProgress.userId,
      timestamp: new Date()
    });

    if (isLastStep) {
      onFlowComplete();
    } else {
      setCurrentStepIndex(prev => prev + 1);
    }
  }, [currentStep, flow.id, userProgress.userId, isLastStep, onEvent, onFlowComplete]);

  const handleExit = useCallback(() => {
    onEvent({
      type: 'flow_abandoned',
      flowId: flow.id,
      userId: userProgress.userId,
      timestamp: new Date(),
      metadata: { currentStep: currentStepIndex, totalSteps: flow.steps.length }
    });
    setShowExitConfirmation(false);
    // Parent component should handle the actual exit
  }, [flow.id, flow.steps.length, userProgress.userId, currentStepIndex, onEvent]);

  const progressPercentage = ((currentStepIndex + 1) / flow.steps.length) * 100;

  if (!currentStep) {
    return null;
  }

  return (
    <div className={`onboarding-flow ${className}`}>
      {/* Overlay */}
      <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
        
        {/* Main onboarding modal */}
        <div className="bg-white rounded-lg shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
          
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h1 className="text-2xl font-bold">{flow.name}</h1>
                <p className="text-blue-100 mt-1">{flow.description}</p>
              </div>
              <button
                onClick={() => setShowExitConfirmation(true)}
                className="text-white hover:text-gray-200 text-xl font-bold"
                aria-label="Exit onboarding"
              >
                ×
              </button>
            </div>
            
            {/* Progress bar */}
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Step {currentStepIndex + 1} of {flow.steps.length}</span>
                <span>{Math.round(progressPercentage)}% Complete</span>
              </div>
              <div className="w-full bg-blue-500 bg-opacity-30 rounded-full h-2">
                <div
                  className="bg-white rounded-full h-2 transition-all duration-300"
                  style={{ width: `${progressPercentage}%` }}
                />
              </div>
            </div>
          </div>

          {/* Content area */}
          <div className="p-6 flex-1 overflow-y-auto">
            <div className="mb-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                {currentStep.title}
              </h2>
              <p className="text-gray-600 mb-4">
                {currentStep.description}
              </p>
              
              {/* Estimated time */}
              <div className="flex items-center text-sm text-gray-500 mb-6">
                <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
                </svg>
                Estimated time: {currentStep.estimatedMinutes} minutes
              </div>
            </div>

            {/* Step component */}
            <div className="step-content">
              {React.createElement(currentStep.component, {
                onComplete: handleStepComplete,
                isCompleted: isStepCompleted,
                stepData: currentStep
              })}
            </div>

            {/* Step completion indicator */}
            {isStepCompleted && (
              <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-center">
                  <svg className="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span className="text-green-800 font-medium">Step completed!</span>
                </div>
              </div>
            )}
          </div>

          {/* Footer with navigation */}
          <div className="border-t border-gray-200 p-6 bg-gray-50">
            <div className="flex justify-between items-center">
              
              {/* Previous button */}
              <button
                onClick={handlePreviousStep}
                disabled={currentStepIndex === 0}
                className={`px-4 py-2 rounded-lg font-medium ${
                  currentStepIndex === 0
                    ? 'text-gray-400 cursor-not-allowed'
                    : 'text-gray-700 hover:bg-gray-200'
                }`}
              >
                Previous
              </button>

              {/* Center buttons */}
              <div className="flex space-x-3">
                {!currentStep.required && (
                  <button
                    onClick={handleSkipStep}
                    className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                  >
                    Skip
                  </button>
                )}
                
                {/* Next/Complete button */}
                <button
                  onClick={handleNextStep}
                  disabled={!canProceed}
                  className={`px-6 py-2 rounded-lg font-medium ${
                    canProceed
                      ? 'bg-blue-600 text-white hover:bg-blue-700'
                      : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  }`}
                >
                  {isLastStep ? 'Complete Onboarding' : 'Next'}
                </button>
              </div>

              {/* Step indicator */}
              <div className="text-sm text-gray-500">
                {currentStepIndex + 1} / {flow.steps.length}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Exit confirmation modal */}
      {showExitConfirmation && (
        <div className="fixed inset-0 bg-black bg-opacity-60 z-60 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Exit Onboarding?
            </h3>
            <p className="text-gray-600 mb-6">
              Your progress will be saved, and you can continue later from where you left off.
            </p>
            <div className="flex space-x-3 justify-end">
              <button
                onClick={() => setShowExitConfirmation(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
              >
                Continue Onboarding
              </button>
              <button
                onClick={handleExit}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
              >
                Exit
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default OnboardingFlowComponent; 
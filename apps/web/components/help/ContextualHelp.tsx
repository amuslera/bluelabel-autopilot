import React, { useState, useEffect, useRef, useCallback } from 'react';
import { ContextualTip, GuidedTour, TutorialStep } from '../../types/onboarding';

interface ContextualHelpProps {
  tips: ContextualTip[];
  activeTour?: GuidedTour;
  onTourComplete?: (tourId: string) => void;
  onTourSkip?: (tourId: string) => void;
  onTipDismiss?: (tipId: string) => void;
  userId: string;
}

interface TooltipProps {
  tip: ContextualTip;
  targetElement: HTMLElement;
  onDismiss: () => void;
  isVisible: boolean;
}

const Tooltip: React.FC<TooltipProps> = ({ tip, targetElement, onDismiss, isVisible }) => {
  const tooltipRef = useRef<HTMLDivElement>(null);
  const [position, setPosition] = useState({ top: 0, left: 0 });
  const [actualPosition, setActualPosition] = useState<'top' | 'bottom' | 'left' | 'right'>('top');

  useEffect(() => {
    if (!targetElement || !tooltipRef.current || !isVisible) return;

    const updatePosition = () => {
      const targetRect = targetElement.getBoundingClientRect();
      const tooltipRect = tooltipRef.current!.getBoundingClientRect();
      const windowWidth = window.innerWidth;
      const windowHeight = window.innerHeight;
      
      let newPosition = { top: 0, left: 0 };
      let finalPosition = tip.position;
      
      // Calculate initial position based on preferred position
      switch (tip.position) {
        case 'top':
          newPosition = {
            top: targetRect.top - tooltipRect.height - 12,
            left: targetRect.left + (targetRect.width / 2) - (tooltipRect.width / 2)
          };
          break;
        case 'bottom':
          newPosition = {
            top: targetRect.bottom + 12,
            left: targetRect.left + (targetRect.width / 2) - (tooltipRect.width / 2)
          };
          break;
        case 'left':
          newPosition = {
            top: targetRect.top + (targetRect.height / 2) - (tooltipRect.height / 2),
            left: targetRect.left - tooltipRect.width - 12
          };
          break;
        case 'right':
          newPosition = {
            top: targetRect.top + (targetRect.height / 2) - (tooltipRect.height / 2),
            left: targetRect.right + 12
          };
          break;
      }
      
      // Adjust if tooltip would go outside viewport
      if (newPosition.left < 12) {
        newPosition.left = 12;
        if (tip.position === 'left') {
          finalPosition = 'right';
          newPosition.left = targetRect.right + 12;
        }
      }
      if (newPosition.left + tooltipRect.width > windowWidth - 12) {
        newPosition.left = windowWidth - tooltipRect.width - 12;
        if (tip.position === 'right') {
          finalPosition = 'left';
          newPosition.left = targetRect.left - tooltipRect.width - 12;
        }
      }
      if (newPosition.top < 12) {
        newPosition.top = 12;
        if (tip.position === 'top') {
          finalPosition = 'bottom';
          newPosition.top = targetRect.bottom + 12;
        }
      }
      if (newPosition.top + tooltipRect.height > windowHeight - 12) {
        newPosition.top = windowHeight - tooltipRect.height - 12;
        if (tip.position === 'bottom') {
          finalPosition = 'top';
          newPosition.top = targetRect.top - tooltipRect.height - 12;
        }
      }
      
      setPosition(newPosition);
      setActualPosition(finalPosition);
    };

    updatePosition();
    window.addEventListener('resize', updatePosition);
    window.addEventListener('scroll', updatePosition);
    
    return () => {
      window.removeEventListener('resize', updatePosition);
      window.removeEventListener('scroll', updatePosition);
    };
  }, [targetElement, tip.position, isVisible]);

  if (!isVisible) return null;

  return (
    <div
      ref={tooltipRef}
      className="fixed z-50 max-w-sm bg-gray-900 text-white text-sm rounded-lg shadow-lg"
      style={{
        top: position.top,
        left: position.left,
        opacity: isVisible ? 1 : 0,
        transition: 'opacity 0.2s ease-in-out'
      }}
    >
      {/* Arrow */}
      <div
        className={`absolute w-3 h-3 bg-gray-900 transform rotate-45 ${
          actualPosition === 'top' ? 'bottom-0 left-1/2 -translate-x-1/2 translate-y-1/2' :
          actualPosition === 'bottom' ? 'top-0 left-1/2 -translate-x-1/2 -translate-y-1/2' :
          actualPosition === 'left' ? 'right-0 top-1/2 translate-x-1/2 -translate-y-1/2' :
          'left-0 top-1/2 -translate-x-1/2 -translate-y-1/2'
        }`}
      />
      
      {/* Content */}
      <div className="p-4 relative z-10">
        <div className="flex justify-between items-start mb-2">
          <h4 className="font-semibold text-white">{tip.title}</h4>
          <button
            onClick={onDismiss}
            className="text-gray-300 hover:text-white ml-2"
            aria-label="Dismiss tip"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <p className="text-gray-200">{tip.content}</p>
        
        {tip.priority > 7 && (
          <div className="mt-3 flex items-center text-yellow-300">
            <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <span className="text-xs">Important</span>
          </div>
        )}
      </div>
    </div>
  );
};

interface TourStepOverlayProps {
  step: TutorialStep;
  stepNumber: number;
  totalSteps: number;
  targetElement?: HTMLElement;
  onNext: () => void;
  onPrevious: () => void;
  onSkip: () => void;
  onComplete: () => void;
  canGoBack: boolean;
  isLastStep: boolean;
}

const TourStepOverlay: React.FC<TourStepOverlayProps> = ({
  step,
  stepNumber,
  totalSteps,
  targetElement,
  onNext,
  onPrevious,
  onSkip,
  onComplete,
  canGoBack,
  isLastStep
}) => {
  const [highlight, setHighlight] = useState<DOMRect | null>(null);

  useEffect(() => {
    if (targetElement) {
      setHighlight(targetElement.getBoundingClientRect());
      
      // Scroll element into view
      targetElement.scrollIntoView({
        behavior: 'smooth',
        block: 'center',
        inline: 'center'
      });
      
      // Add highlight class
      targetElement.classList.add('tour-highlight');
      
      return () => {
        targetElement.classList.remove('tour-highlight');
      };
    }
  }, [targetElement]);

  return (
    <div className="fixed inset-0 z-50">
      {/* Overlay with hole for highlighted element */}
      <div 
        className="absolute inset-0 bg-black bg-opacity-60"
        style={{
          clipPath: highlight 
            ? `polygon(0% 0%, 0% 100%, ${highlight.left - 8}px 100%, ${highlight.left - 8}px ${highlight.top - 8}px, ${highlight.right + 8}px ${highlight.top - 8}px, ${highlight.right + 8}px ${highlight.bottom + 8}px, ${highlight.left - 8}px ${highlight.bottom + 8}px, ${highlight.left - 8}px 100%, 100% 100%, 100% 0%)`
            : undefined
        }}
      />
      
      {/* Step content */}
      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white rounded-lg shadow-2xl max-w-md w-full mx-4">
        <div className="p-6">
          {/* Header */}
          <div className="flex justify-between items-start mb-4">
            <div>
              <div className="text-sm text-gray-500 mb-1">
                Step {stepNumber} of {totalSteps}
              </div>
              <h3 className="text-lg font-semibold text-gray-900">{step.title}</h3>
            </div>
            <button
              onClick={onSkip}
              className="text-gray-400 hover:text-gray-600"
              aria-label="Skip tour"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          {/* Progress bar */}
          <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(stepNumber / totalSteps) * 100}%` }}
            />
          </div>
          
          {/* Content */}
          <p className="text-gray-600 mb-6">{step.description}</p>
          
          {/* Media */}
          {step.media && (
            <div className="mb-6">
              {step.media.type === 'image' && (
                <img
                  src={step.media.url}
                  alt={step.media.alt}
                  className="w-full rounded-lg"
                />
              )}
              {step.media.type === 'video' && (
                <video
                  src={step.media.url}
                  poster={step.media.thumbnail}
                  controls
                  className="w-full rounded-lg"
                />
              )}
              {step.media.type === 'gif' && (
                <img
                  src={step.media.url}
                  alt={step.media.alt}
                  className="w-full rounded-lg"
                />
              )}
            </div>
          )}
          
          {/* Action hint */}
          {step.action && (
            <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-center space-x-2 text-blue-800">
                {step.action === 'click' && (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.121 2.122" />
                  </svg>
                )}
                {step.action === 'hover' && (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 11.5V14m0-2.5v-6a1.5 1.5 0 113 0m-3 6a1.5 1.5 0 00-3 0v2a7.5 7.5 0 0015 0v-5a1.5 1.5 0 00-3 0m-6-3V11m0-5.5v-1a1.5 1.5 0 013 0v1m0 0V11m0-5.5T6.5 15.5" />
                  </svg>
                )}
                {step.action === 'type' && (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                )}
                <span className="text-sm font-medium">
                  {step.action === 'click' && 'Click the highlighted element'}
                  {step.action === 'hover' && 'Hover over the highlighted element'}
                  {step.action === 'type' && 'Type in the highlighted field'}
                  {step.action === 'wait' && 'Wait for the action to complete'}
                  {step.action === 'highlight' && 'Notice the highlighted area'}
                </span>
              </div>
            </div>
          )}
        </div>
        
        {/* Footer */}
        <div className="border-t border-gray-200 p-4 flex justify-between items-center">
          <button
            onClick={onPrevious}
            disabled={!canGoBack}
            className={`px-4 py-2 rounded-lg font-medium ${
              canGoBack 
                ? 'text-gray-700 hover:bg-gray-100' 
                : 'text-gray-400 cursor-not-allowed'
            }`}
          >
            Previous
          </button>
          
          <div className="flex space-x-2">
            <button
              onClick={onSkip}
              className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
            >
              Skip Tour
            </button>
            <button
              onClick={isLastStep ? onComplete : onNext}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              {isLastStep ? 'Complete Tour' : 'Next'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export const ContextualHelp: React.FC<ContextualHelpProps> = ({
  tips,
  activeTour,
  onTourComplete,
  onTourSkip,
  onTipDismiss,
  userId
}) => {
  const [visibleTips, setVisibleTips] = useState<Set<string>>(new Set());
  const [currentTourStep, setCurrentTourStep] = useState(0);
  const [dismissedTips, setDismissedTips] = useState<Set<string>>(new Set());
  const observerRef = useRef<IntersectionObserver | null>(null);

  // Initialize intersection observer for element visibility
  useEffect(() => {
    observerRef.current = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          const tipId = entry.target.getAttribute('data-tip-id');
          if (tipId) {
            setVisibleTips(prev => {
              const newSet = new Set(prev);
              if (entry.isIntersecting) {
                newSet.add(tipId);
              } else {
                newSet.delete(tipId);
              }
              return newSet;
            });
          }
        });
      },
      { threshold: 0.5 }
    );

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, []);

  // Monitor DOM for tip target elements
  useEffect(() => {
    const checkForTipElements = () => {
      tips.forEach(tip => {
        if (dismissedTips.has(tip.id)) return;
        
        const element = document.querySelector(tip.element) as HTMLElement;
        if (element && !element.hasAttribute('data-tip-id')) {
          element.setAttribute('data-tip-id', tip.id);
          
          // Set up trigger
          switch (tip.trigger) {
            case 'hover':
              element.addEventListener('mouseenter', () => showTip(tip.id));
              element.addEventListener('mouseleave', () => hideTip(tip.id));
              break;
            case 'click':
              element.addEventListener('click', () => showTip(tip.id));
              break;
            case 'focus':
              element.addEventListener('focus', () => showTip(tip.id));
              element.addEventListener('blur', () => hideTip(tip.id));
              break;
            case 'first-visit':
              // Show immediately if first visit
              const hasSeenTip = localStorage.getItem(`tip-seen-${tip.id}`);
              if (!hasSeenTip) {
                showTip(tip.id);
                localStorage.setItem(`tip-seen-${tip.id}`, 'true');
              }
              break;
            case 'error':
              // Would be triggered by error conditions
              break;
          }
          
          if (observerRef.current) {
            observerRef.current.observe(element);
          }
        }
      });
    };

    // Check immediately and set up mutation observer
    checkForTipElements();
    
    const mutationObserver = new MutationObserver(() => {
      setTimeout(checkForTipElements, 100);
    });
    
    mutationObserver.observe(document.body, {
      childList: true,
      subtree: true
    });

    return () => {
      mutationObserver.disconnect();
    };
  }, [tips, dismissedTips]);

  const showTip = useCallback((tipId: string) => {
    setVisibleTips(prev => new Set([...prev, tipId]));
  }, []);

  const hideTip = useCallback((tipId: string) => {
    setVisibleTips(prev => {
      const newSet = new Set(prev);
      newSet.delete(tipId);
      return newSet;
    });
  }, []);

  const dismissTip = useCallback((tipId: string) => {
    setDismissedTips(prev => new Set([...prev, tipId]));
    hideTip(tipId);
    onTipDismiss?.(tipId);
    
    const tip = tips.find(t => t.id === tipId);
    if (tip?.showOnce) {
      localStorage.setItem(`tip-dismissed-${tipId}`, 'true');
    }
  }, [tips, hideTip, onTipDismiss]);

  // Tour navigation
  const handleTourNext = useCallback(() => {
    if (activeTour && currentTourStep < activeTour.steps.length - 1) {
      setCurrentTourStep(prev => prev + 1);
    }
  }, [activeTour, currentTourStep]);

  const handleTourPrevious = useCallback(() => {
    if (currentTourStep > 0) {
      setCurrentTourStep(prev => prev - 1);
    }
  }, [currentTourStep]);

  const handleTourComplete = useCallback(() => {
    if (activeTour) {
      onTourComplete?.(activeTour.id);
      setCurrentTourStep(0);
    }
  }, [activeTour, onTourComplete]);

  const handleTourSkip = useCallback(() => {
    if (activeTour) {
      onTourSkip?.(activeTour.id);
      setCurrentTourStep(0);
    }
  }, [activeTour, onTourSkip]);

  // Get currently visible tips
  const visibleTipComponents = tips
    .filter(tip => visibleTips.has(tip.id) && !dismissedTips.has(tip.id))
    .map(tip => {
      const element = document.querySelector(tip.element) as HTMLElement;
      if (!element) return null;

      return (
        <Tooltip
          key={tip.id}
          tip={tip}
          targetElement={element}
          onDismiss={() => dismissTip(tip.id)}
          isVisible={true}
        />
      );
    })
    .filter(Boolean);

  // Get current tour step
  const currentStep = activeTour?.steps[currentTourStep];
  const tourTargetElement = currentStep?.targetElement 
    ? document.querySelector(currentStep.targetElement) as HTMLElement
    : undefined;

  return (
    <>
      {/* Contextual tips */}
      {visibleTipComponents}
      
      {/* Guided tour */}
      {activeTour && currentStep && (
        <TourStepOverlay
          step={currentStep}
          stepNumber={currentTourStep + 1}
          totalSteps={activeTour.steps.length}
          targetElement={tourTargetElement}
          onNext={handleTourNext}
          onPrevious={handleTourPrevious}
          onSkip={handleTourSkip}
          onComplete={handleTourComplete}
          canGoBack={currentTourStep > 0}
          isLastStep={currentTourStep === activeTour.steps.length - 1}
        />
      )}
      
      {/* CSS for highlighting tour elements */}
      <style jsx global>{`
        .tour-highlight {
          position: relative;
          z-index: 51;
          border-radius: 4px;
          box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.5);
        }
      `}</style>
    </>
  );
};

export default ContextualHelp; 
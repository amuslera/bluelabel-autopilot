import React, { useState } from 'react';
import { RetroCard } from './RetroCard';
import { RetroButton } from './RetroButton';

interface OnboardingModalProps {
  isOpen: boolean;
  onClose: () => void;
  onComplete?: () => void;
}

interface OnboardingStep {
  id: number;
  title: string;
  content: string;
  icon: string;
  tips?: string[];
  action?: {
    label: string;
    description: string;
  };
}

const onboardingSteps: OnboardingStep[] = [
  {
    id: 1,
    title: 'WELCOME TO AIOS v2',
    content: 'Your AI Operating System for intelligent document processing and knowledge management. AIOS v2 uses advanced AI agents to automatically process, analyze, and organize your content.',
    icon: '🚀',
    tips: [
      'Retro terminal interface for ultimate efficiency',
      'Real-time processing with live status updates',
      'Intelligent knowledge extraction and organization'
    ]
  },
  {
    id: 2,
    title: 'UPLOAD & PROCESS CONTENT',
    content: 'Upload PDFs, audio files, or process web URLs to extract valuable insights. Our AI agents will automatically analyze your content and add it to your knowledge base.',
    icon: '📄',
    tips: [
      'Supported: PDF, Audio (MP3/WAV/M4A), Text, Word docs',
      'Drag & drop files or click to browse',
      'Enter URLs to process web content',
      'Real-time processing status updates'
    ],
    action: {
      label: 'TRY UPLOAD',
      description: 'Click the UPLOAD FILE button in the dashboard'
    }
  },
  {
    id: 3,
    title: 'AI AGENTS AT WORK',
    content: 'Monitor your AI agents as they process content in real-time. Each agent specializes in different tasks: content extraction, analysis, summarization, and knowledge organization.',
    icon: '🤖',
    tips: [
      'ContentMind: Extracts and analyzes text content',
      'ContextMind: Provides contextual understanding',
      'DigestAgent: Creates summaries and insights',
      'WebFetcher: Processes web URLs and articles'
    ],
    action: {
      label: 'VIEW AGENTS',
      description: 'Navigate to [AGENTS] tab to see agent status'
    }
  },
  {
    id: 4,
    title: 'KNOWLEDGE REPOSITORY',
    content: 'Search and explore your growing knowledge base. All processed content is automatically organized with tags, summaries, and metadata for easy retrieval.',
    icon: '📚',
    tips: [
      'Full-text search across all content',
      'Filter by content type and tags',
      'Export knowledge items in multiple formats',
      'View processing history and sources'
    ],
    action: {
      label: 'EXPLORE KNOWLEDGE',
      description: 'Visit [KNOWLEDGE] tab to browse your content'
    }
  },
  {
    id: 5,
    title: 'TERMINAL & ADVANCED FEATURES',
    content: 'Use the terminal interface for direct system control and advanced operations. Access logs, run custom commands, and monitor system performance.',
    icon: '💻',
    tips: [
      'Direct agent control via command line',
      'System logs and debugging information',
      'Real-time activity monitoring',
      'Custom workflow automation'
    ],
    action: {
      label: 'OPEN TERMINAL',
      description: 'Click [TERMINAL] to access command interface'
    }
  },
  {
    id: 6,
    title: 'YOU\'RE READY TO GO!',
    content: 'AIOS v2 is now ready for action. Start by uploading some content or processing a URL to see the system in action. Need help? Access this guide anytime from the main menu.',
    icon: '✅',
    tips: [
      'Start with a simple PDF or article URL',
      'Watch the agents process your content',
      'Explore the knowledge repository',
      'Use the help system for detailed guides'
    ]
  }
];

export const OnboardingModal: React.FC<OnboardingModalProps> = ({
  isOpen,
  onClose,
  onComplete,
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [hasSeenOnboarding, setHasSeenOnboarding] = useState(false);

  React.useEffect(() => {
    // Check if user has seen onboarding before
    const hasSeenBefore = localStorage.getItem('aios-onboarding-complete');
    setHasSeenOnboarding(!!hasSeenBefore);
  }, []);

  const handleNext = () => {
    if (currentStep < onboardingSteps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      handleComplete();
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleComplete = () => {
    localStorage.setItem('aios-onboarding-complete', 'true');
    setHasSeenOnboarding(true);
    onComplete?.();
    onClose();
  };

  const handleSkip = () => {
    handleComplete();
  };

  if (!isOpen) return null;

  const step = onboardingSteps[currentStep];
  const isLastStep = currentStep === onboardingSteps.length - 1;
  const isFirstStep = currentStep === 0;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-50">
      <div className="w-full max-w-2xl mx-4">
        <RetroCard title={`AIOS v2 ONBOARDING - STEP ${currentStep + 1}/${onboardingSteps.length}`}>
          <div className="space-y-6">
            {/* Step Content */}
            <div className="text-center">
              <div className="text-6xl mb-4">{step.icon}</div>
              <h2 className="text-2xl font-bold text-terminal-cyan mb-4">
                {step.title}
              </h2>
              <p className="text-terminal-cyan/80 leading-relaxed mb-6">
                {step.content}
              </p>
            </div>

            {/* Tips Section */}
            {step.tips && (
              <div className="bg-terminal-cyan/5 border border-terminal-cyan/30 p-4 rounded">
                <h3 className="text-terminal-cyan font-bold mb-3">💡 KEY FEATURES:</h3>
                <ul className="space-y-2">
                  {step.tips.map((tip, index) => (
                    <li key={index} className="text-terminal-cyan/80 text-sm flex items-start">
                      <span className="text-terminal-green mr-2">▶</span>
                      {tip}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Action Section */}
            {step.action && (
              <div className="bg-terminal-amber/10 border border-terminal-amber/30 p-4 rounded">
                <h3 className="text-terminal-amber font-bold mb-2">⚡ TRY IT NOW:</h3>
                <p className="text-terminal-amber/80 text-sm">
                  {step.action.description}
                </p>
              </div>
            )}

            {/* Progress Bar */}
            <div className="w-full bg-terminal-dark border border-terminal-cyan/30 rounded">
              <div 
                className="h-2 bg-terminal-cyan transition-all duration-300 rounded"
                style={{ width: `${((currentStep + 1) / onboardingSteps.length) * 100}%` }}
              />
            </div>

            {/* Step Indicators */}
            <div className="flex justify-center space-x-2">
              {onboardingSteps.map((_, index) => (
                <button
                  key={index}
                  onClick={() => setCurrentStep(index)}
                  className={`w-3 h-3 rounded-full border-2 transition-all ${
                    index === currentStep
                      ? 'border-terminal-cyan bg-terminal-cyan'
                      : index < currentStep
                      ? 'border-terminal-green bg-terminal-green'
                      : 'border-terminal-cyan/30'
                  }`}
                />
              ))}
            </div>

            {/* Navigation Buttons */}
            <div className="flex justify-between items-center pt-4">
              <div className="flex space-x-2">
                {!isFirstStep && (
                  <RetroButton onClick={handlePrevious}>
                    ← PREVIOUS
                  </RetroButton>
                )}
                <RetroButton variant="error" onClick={handleSkip}>
                  SKIP GUIDE
                </RetroButton>
              </div>

              <div className="flex space-x-2">
                {isLastStep ? (
                  <RetroButton variant="success" onClick={handleComplete}>
                    START USING AIOS →
                  </RetroButton>
                ) : (
                  <RetroButton variant="primary" onClick={handleNext}>
                    NEXT →
                  </RetroButton>
                )}
              </div>
            </div>

            {/* First Time User Badge */}
            {!hasSeenOnboarding && currentStep === 0 && (
              <div className="text-center pt-2">
                <span className="inline-block px-3 py-1 text-xs bg-terminal-green/20 border border-terminal-green text-terminal-green rounded">
                  FIRST TIME USER DETECTED
                </span>
              </div>
            )}
          </div>
        </RetroCard>
      </div>
    </div>
  );
};

// Help System Component for quick reference
export const HelpModal: React.FC<{
  isOpen: boolean;
  onClose: () => void;
  onStartOnboarding?: () => void;
}> = ({ isOpen, onClose, onStartOnboarding }) => {
  const [selectedSection, setSelectedSection] = useState<string>('overview');

  const helpSections = {
    overview: {
      title: 'SYSTEM OVERVIEW',
      content: `AIOS v2 is your intelligent AI Operating System designed for automated content processing and knowledge management.

KEY COMPONENTS:
• AI Agents: Specialized processors for different content types
• Knowledge Repository: Organized storage with intelligent search
• Real-time Processing: Live status updates and monitoring
• Multi-format Support: PDFs, audio, URLs, and text documents`
    },
    upload: {
      title: 'CONTENT UPLOAD',
      content: `Upload and process various content types:

FILE UPLOAD:
• PDF Documents: Automatic text extraction and analysis
• Audio Files: Transcription and content analysis
• Text Documents: Direct processing and organization
• Word Documents: Full content extraction

URL PROCESSING:
• Web Articles: Content extraction and summarization
• PDF Links: Download and process automatically
• Media Files: Extract and analyze multimedia content`
    },
    agents: {
      title: 'AI AGENTS',
      content: `Monitor and control AI agents:

CONTENTMIND:
• Primary content extraction and analysis
• Handles text processing and initial insights

CONTEXTMIND:
• Provides contextual understanding
• Cross-references with existing knowledge

DIGESTAGENT:
• Creates summaries and key insights
• Generates actionable recommendations

WEBFETCHER:
• Processes web URLs and online content
• Handles remote content retrieval`
    },
    knowledge: {
      title: 'KNOWLEDGE BASE',
      content: `Search and manage your knowledge repository:

SEARCH FEATURES:
• Full-text search across all content
• Tag-based filtering and organization
• Content type filtering (docs, articles, etc.)
• Advanced metadata search

ORGANIZATION:
• Automatic tagging and categorization
• Source tracking and provenance
• Processing history and timestamps
• Export capabilities (JSON, PDF, Markdown)`
    },
    terminal: {
      title: 'TERMINAL INTERFACE',
      content: `Advanced control via terminal:

COMMANDS:
• run agent [name] --task [description]
• process email --from [address]
• fetch knowledge --tag [tag-name]
• check inbox --filter [criteria]

FEATURES:
• Direct agent control and automation
• System logs and debugging
• Real-time activity monitoring
• Custom workflow scripting`
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-50">
      <div className="w-full max-w-4xl mx-4">
        <RetroCard title="AIOS v2 HELP SYSTEM">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {/* Help Navigation */}
            <div className="space-y-2">
              {Object.entries(helpSections).map(([key, section]) => (
                <button
                  key={key}
                  onClick={() => setSelectedSection(key)}
                  className={`w-full text-left px-3 py-2 border transition-colors ${
                    selectedSection === key
                      ? 'border-terminal-cyan bg-terminal-cyan/20 text-terminal-cyan'
                      : 'border-terminal-cyan/30 text-terminal-cyan/70 hover:border-terminal-cyan/70'
                  }`}
                >
                  {section.title}
                </button>
              ))}
              
              <div className="pt-4 border-t border-terminal-cyan/30">
                <RetroButton 
                  onClick={onStartOnboarding}
                  variant="success"
                  className="w-full mb-2"
                >
                  RESTART TOUR
                </RetroButton>
              </div>
            </div>

            {/* Help Content */}
            <div className="md:col-span-3">
              <div className="bg-terminal-dark/50 border border-terminal-cyan/30 p-6 rounded">
                <h3 className="text-terminal-cyan font-bold text-xl mb-4">
                  {helpSections[selectedSection as keyof typeof helpSections].title}
                </h3>
                <div className="text-terminal-cyan/80 whitespace-pre-line leading-relaxed">
                  {helpSections[selectedSection as keyof typeof helpSections].content}
                </div>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="flex justify-between items-center pt-6 mt-6 border-t border-terminal-cyan/30">
            <div className="text-terminal-cyan/60 text-sm">
              AIOS v2 - AI Operating System | Need more help? Check the documentation.
            </div>
            <RetroButton onClick={onClose}>
              CLOSE HELP
            </RetroButton>
          </div>
        </RetroCard>
      </div>
    </div>
  );
}; 
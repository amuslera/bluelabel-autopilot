// Core onboarding and user documentation system types for AIOS v2

export interface OnboardingStep {
  id: string;
  title: string;
  description: string;
  component: React.ComponentType<any>;
  required: boolean;
  completed: boolean;
  estimatedMinutes: number;
  prerequisites?: string[];
  nextSteps?: string[];
}

export interface OnboardingFlow {
  id: string;
  name: string;
  description: string;
  steps: OnboardingStep[];
  currentStep: number;
  totalSteps: number;
  completionPercentage: number;
  estimatedTotalMinutes: number;
}

export interface UserProgress {
  userId: string;
  completedSteps: string[];
  currentFlow?: string;
  skippedSteps: string[];
  lastActiveStep?: string;
  progressSavedAt: Date;
  totalTimeSpent: number;
}

// Help System Types
export interface HelpArticle {
  id: string;
  title: string;
  content: string;
  category: HelpCategory;
  tags: string[];
  searchKeywords: string[];
  lastUpdated: Date;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  estimatedReadTime: number;
  relatedArticles: string[];
  upvotes: number;
  downvotes: number;
}

export interface HelpCategory {
  id: string;
  name: string;
  description: string;
  icon: string;
  color: string;
  priority: number;
  articleCount: number;
}

export interface SearchResult {
  article: HelpArticle;
  relevanceScore: number;
  matchedKeywords: string[];
  excerpt: string;
}

// Tutorial System Types
export interface TutorialStep {
  id: string;
  title: string;
  description: string;
  targetElement?: string;
  position: 'top' | 'bottom' | 'left' | 'right' | 'center';
  action?: 'click' | 'hover' | 'type' | 'wait' | 'highlight';
  actionData?: any;
  optional: boolean;
  media?: TutorialMedia;
}

export interface TutorialMedia {
  type: 'image' | 'video' | 'gif' | 'interactive';
  url: string;
  alt: string;
  thumbnail?: string;
  duration?: number;
}

export interface Tutorial {
  id: string;
  title: string;
  description: string;
  category: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  estimatedMinutes: number;
  steps: TutorialStep[];
  prerequisites?: string[];
  objectives: string[];
  completionCriteria: string[];
  tags: string[];
}

// Contextual Help Types
export interface ContextualTip {
  id: string;
  element: string;
  title: string;
  content: string;
  trigger: 'hover' | 'click' | 'focus' | 'first-visit' | 'error';
  position: 'top' | 'bottom' | 'left' | 'right';
  priority: number;
  showOnce?: boolean;
  conditions?: ContextualCondition[];
}

export interface ContextualCondition {
  type: 'user-level' | 'feature-flag' | 'page-visits' | 'time-on-page';
  operator: 'equals' | 'greater-than' | 'less-than' | 'contains';
  value: any;
}

export interface GuidedTour {
  id: string;
  name: string;
  description: string;
  targetPage: string;
  steps: TutorialStep[];
  autoStart: boolean;
  canSkip: boolean;
  showProgress: boolean;
  onComplete?: () => void;
}

// FAQ System Types
export interface FAQItem {
  id: string;
  question: string;
  answer: string;
  category: string;
  tags: string[];
  helpful: number;
  notHelpful: number;
  lastUpdated: Date;
  relatedFAQs: string[];
  searchKeywords: string[];
  contextualTriggers?: string[];
}

export interface FAQCategory {
  id: string;
  name: string;
  description: string;
  icon: string;
  priority: number;
  itemCount: number;
}

export interface DynamicFAQ {
  userAction: string;
  suggestedFAQs: string[];
  context: Record<string, any>;
  timestamp: Date;
}

// User Feedback Types
export interface FeedbackSubmission {
  id: string;
  userId: string;
  type: 'bug' | 'feature' | 'improvement' | 'compliment' | 'question';
  category: string;
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  reproducible: boolean;
  steps?: string[];
  expectedBehavior?: string;
  actualBehavior?: string;
  browser?: string;
  device?: string;
  screenshot?: string;
  attachments?: string[];
  status: 'submitted' | 'reviewed' | 'in-progress' | 'resolved' | 'closed';
  submittedAt: Date;
  updatedAt: Date;
  assignedTo?: string;
  response?: string;
  publicResponse?: boolean;
}

export interface SupportRequest {
  id: string;
  userId: string;
  subject: string;
  message: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  category: string;
  status: 'open' | 'waiting' | 'resolved' | 'closed';
  createdAt: Date;
  updatedAt: Date;
  responses: SupportResponse[];
  satisfaction?: number;
  tags: string[];
}

export interface SupportResponse {
  id: string;
  author: string;
  message: string;
  isStaffResponse: boolean;
  timestamp: Date;
  attachments?: string[];
}

// Accessibility Types
export interface AccessibilityPreferences {
  userId: string;
  highContrast: boolean;
  largeText: boolean;
  reducedMotion: boolean;
  screenReader: boolean;
  keyboardNavigation: boolean;
  colorBlindAssist: boolean;
  audioDescriptions: boolean;
  textToSpeech: boolean;
  customTheme?: string;
  fontSize: 'small' | 'medium' | 'large' | 'extra-large';
}

export interface KeyboardShortcut {
  id: string;
  key: string;
  modifiers: string[];
  action: string;
  description: string;
  category: string;
  enabled: boolean;
  customizable: boolean;
}

// User Preferences Types
export interface UserPreferences {
  userId: string;
  general: GeneralPreferences;
  notifications: NotificationPreferences;
  accessibility: AccessibilityPreferences;
  onboarding: OnboardingPreferences;
  privacy: PrivacyPreferences;
  interface: InterfacePreferences;
  updatedAt: Date;
}

export interface GeneralPreferences {
  language: string;
  timezone: string;
  dateFormat: string;
  timeFormat: '12h' | '24h';
  theme: 'light' | 'dark' | 'auto' | 'custom';
  autoSave: boolean;
  confirmActions: boolean;
}

export interface NotificationPreferences {
  email: boolean;
  push: boolean;
  inApp: boolean;
  desktop: boolean;
  sms: boolean;
  categories: {
    [key: string]: boolean;
  };
  frequency: 'immediate' | 'hourly' | 'daily' | 'weekly';
  quietHours: {
    enabled: boolean;
    start: string;
    end: string;
  };
}

export interface OnboardingPreferences {
  showTips: boolean;
  autoStartTours: boolean;
  showProgress: boolean;
  skipCompleted: boolean;
  reminderFrequency: 'never' | 'daily' | 'weekly' | 'monthly';
  preferredLearningStyle: 'visual' | 'text' | 'interactive' | 'video';
}

export interface PrivacyPreferences {
  analytics: boolean;
  crashReporting: boolean;
  usageData: boolean;
  personalizedContent: boolean;
  thirdPartySharing: boolean;
  dataRetention: '30days' | '1year' | '2years' | 'indefinite';
}

export interface InterfacePreferences {
  sidebarCollapsed: boolean;
  defaultView: 'grid' | 'list' | 'card';
  itemsPerPage: number;
  showPreview: boolean;
  compactMode: boolean;
  animationsEnabled: boolean;
  tooltipsEnabled: boolean;
  breadcrumbsEnabled: boolean;
}

// Event Types for Analytics
export interface OnboardingEvent {
  type: 'step_started' | 'step_completed' | 'step_skipped' | 'flow_completed' | 'flow_abandoned';
  stepId?: string;
  flowId: string;
  userId: string;
  timestamp: Date;
  duration?: number;
  metadata?: Record<string, any>;
}

export interface HelpEvent {
  type: 'search' | 'article_viewed' | 'article_rated' | 'category_browsed';
  query?: string;
  articleId?: string;
  categoryId?: string;
  userId: string;
  timestamp: Date;
  metadata?: Record<string, any>;
}

export interface TutorialEvent {
  type: 'tutorial_started' | 'tutorial_completed' | 'tutorial_abandoned' | 'step_completed';
  tutorialId: string;
  stepId?: string;
  userId: string;
  timestamp: Date;
  completionPercentage?: number;
  metadata?: Record<string, any>;
} 
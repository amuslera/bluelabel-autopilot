import React, { useState, useRef, useCallback } from 'react';
import { FeedbackSubmission, SupportRequest } from '../../types/onboarding';

interface FeedbackSystemProps {
  isOpen: boolean;
  onClose: () => void;
  userId: string;
  currentPage?: string;
  userAgent?: string;
}

type FeedbackType = 'bug' | 'feature' | 'improvement' | 'compliment' | 'question';

export const FeedbackSystem: React.FC<FeedbackSystemProps> = ({
  isOpen,
  onClose,
  userId,
  currentPage = '',
  userAgent = ''
}) => {
  const [activeTab, setActiveTab] = useState<'feedback' | 'support'>('feedback');
  const [feedbackType, setFeedbackType] = useState<FeedbackType>('bug');
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    severity: 'medium' as 'low' | 'medium' | 'high' | 'critical',
    reproducible: false,
    steps: [''],
    expectedBehavior: '',
    actualBehavior: '',
    category: '',
    priority: 'medium' as 'low' | 'medium' | 'high' | 'urgent'
  });
  const [attachments, setAttachments] = useState<File[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const feedbackTypes = [
    {
      id: 'bug' as FeedbackType,
      name: 'Bug Report',
      description: 'Report a problem or error',
      icon: '🐛',
      color: 'red'
    },
    {
      id: 'feature' as FeedbackType,
      name: 'Feature Request',
      description: 'Suggest a new feature',
      icon: '💡',
      color: 'blue'
    },
    {
      id: 'improvement' as FeedbackType,
      name: 'Improvement',
      description: 'Suggest an enhancement',
      icon: '⚡',
      color: 'yellow'
    },
    {
      id: 'compliment' as FeedbackType,
      name: 'Compliment',
      description: 'Share positive feedback',
      icon: '🎉',
      color: 'green'
    },
    {
      id: 'question' as FeedbackType,
      name: 'Question',
      description: 'Ask for help or clarification',
      icon: '❓',
      color: 'purple'
    }
  ];

  const supportCategories = [
    'Account & Billing',
    'Document Processing',
    'AI Agents',
    'Integrations',
    'Performance Issues',
    'Security & Privacy',
    'Technical Support',
    'Other'
  ];

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleStepChange = (index: number, value: string) => {
    const newSteps = [...formData.steps];
    newSteps[index] = value;
    setFormData(prev => ({
      ...prev,
      steps: newSteps
    }));
  };

  const addStep = () => {
    setFormData(prev => ({
      ...prev,
      steps: [...prev.steps, '']
    }));
  };

  const removeStep = (index: number) => {
    if (formData.steps.length > 1) {
      const newSteps = formData.steps.filter((_, i) => i !== index);
      setFormData(prev => ({
        ...prev,
        steps: newSteps
      }));
    }
  };

  const handleFileSelect = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    const maxSize = 10 * 1024 * 1024; // 10MB
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf', 'text/plain'];
    
    const validFiles = files.filter(file => {
      if (file.size > maxSize) {
        alert(`File ${file.name} is too large. Maximum size is 10MB.`);
        return false;
      }
      if (!allowedTypes.includes(file.type)) {
        alert(`File ${file.name} is not supported. Allowed types: JPG, PNG, GIF, PDF, TXT.`);
        return false;
      }
      return true;
    });

    setAttachments(prev => [...prev, ...validFiles].slice(0, 5)); // Max 5 files
  }, []);

  const removeAttachment = (index: number) => {
    setAttachments(prev => prev.filter((_, i) => i !== index));
  };

  const captureScreenshot = useCallback(() => {
    // In a real implementation, this would use a screen capture API
    // For now, we'll just show how it would work
    alert('Screenshot capture would be implemented here using screen capture APIs.');
  }, []);

  const collectSystemInfo = () => {
    return {
      userAgent: navigator.userAgent,
      url: window.location.href,
      timestamp: new Date().toISOString(),
      viewport: `${window.innerWidth}x${window.innerHeight}`,
      screen: `${window.screen.width}x${window.screen.height}`,
      language: navigator.language,
      platform: navigator.platform,
      cookieEnabled: navigator.cookieEnabled,
      onlineStatus: navigator.onLine
    };
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const systemInfo = collectSystemInfo();
      
      if (activeTab === 'feedback') {
        const feedback: Partial<FeedbackSubmission> = {
          userId,
          type: feedbackType,
          category: formData.category || feedbackTypes.find(t => t.id === feedbackType)?.name || '',
          title: formData.title,
          description: formData.description,
          severity: formData.severity,
          reproducible: formData.reproducible,
          steps: formData.steps.filter(step => step.trim()),
          expectedBehavior: formData.expectedBehavior,
          actualBehavior: formData.actualBehavior,
          browser: systemInfo.userAgent,
          device: systemInfo.platform,
          attachments: attachments.map(f => f.name),
          status: 'submitted',
          submittedAt: new Date(),
          updatedAt: new Date()
        };

        console.log('Submitting feedback:', feedback);
        // In real implementation, send to API
        
      } else {
        const support: Partial<SupportRequest> = {
          userId,
          subject: formData.title,
          message: formData.description,
          priority: formData.priority,
          category: formData.category,
          status: 'open',
          createdAt: new Date(),
          updatedAt: new Date(),
          responses: [],
          tags: [feedbackType, currentPage].filter(Boolean)
        };

        console.log('Submitting support request:', support);
        // In real implementation, send to API
      }

      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      setIsSubmitted(true);
      
    } catch (error) {
      console.error('Submission error:', error);
      alert('Failed to submit. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      severity: 'medium',
      reproducible: false,
      steps: [''],
      expectedBehavior: '',
      actualBehavior: '',
      category: '',
      priority: 'medium'
    });
    setAttachments([]);
    setIsSubmitted(false);
    setFeedbackType('bug');
    setActiveTab('feedback');
  };

  const handleClose = () => {
    resetForm();
    onClose();
  };

  if (!isOpen) return null;

  const selectedType = feedbackTypes.find(t => t.id === feedbackType);

  if (isSubmitted) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-2xl max-w-md w-full p-8 text-center">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            {activeTab === 'feedback' ? 'Feedback Submitted!' : 'Support Request Created!'}
          </h3>
          <p className="text-gray-600 mb-6">
            {activeTab === 'feedback' 
              ? 'Thank you for your feedback. Our team will review it and get back to you if needed.'
              : 'Your support request has been created. Our team will respond within 24 hours.'
            }
          </p>
          <div className="space-y-3">
            <button
              onClick={resetForm}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
            >
              Submit Another
            </button>
            <button
              onClick={handleClose}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden">
        
        {/* Header */}
        <div className="border-b border-gray-200 p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Get Help</h2>
            <button
              onClick={handleClose}
              className="text-gray-400 hover:text-gray-600"
              aria-label="Close feedback"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          {/* Tabs */}
          <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setActiveTab('feedback')}
              className={`flex-1 py-2 px-3 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'feedback'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Give Feedback
            </button>
            <button
              onClick={() => setActiveTab('support')}
              className={`flex-1 py-2 px-3 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'support'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Get Support
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[70vh]">
          <form onSubmit={handleSubmit} className="space-y-6">
            
            {/* Feedback Type Selection */}
            {activeTab === 'feedback' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  What type of feedback do you have?
                </label>
                <div className="grid grid-cols-2 gap-3">
                  {feedbackTypes.map((type) => (
                    <button
                      key={type.id}
                      type="button"
                      onClick={() => setFeedbackType(type.id)}
                      className={`p-3 border rounded-lg text-left transition-colors ${
                        feedbackType === type.id
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="flex items-center space-x-2 mb-1">
                        <span className="text-lg">{type.icon}</span>
                        <span className="font-medium text-gray-900">{type.name}</span>
                      </div>
                      <p className="text-sm text-gray-600">{type.description}</p>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Category Selection for Support */}
            {activeTab === 'support' && (
              <div>
                <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-2">
                  Category *
                </label>
                <select
                  id="category"
                  value={formData.category}
                  onChange={(e) => handleInputChange('category', e.target.value)}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Select a category</option>
                  {supportCategories.map((category) => (
                    <option key={category} value={category}>{category}</option>
                  ))}
                </select>
              </div>
            )}

            {/* Priority for Support */}
            {activeTab === 'support' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Priority
                </label>
                <div className="flex space-x-3">
                  {['low', 'medium', 'high', 'urgent'].map((priority) => (
                    <label key={priority} className="flex items-center">
                      <input
                        type="radio"
                        name="priority"
                        value={priority}
                        checked={formData.priority === priority}
                        onChange={(e) => handleInputChange('priority', e.target.value)}
                        className="mr-2"
                      />
                      <span className="text-sm capitalize">{priority}</span>
                    </label>
                  ))}
                </div>
              </div>
            )}

            {/* Title/Subject */}
            <div>
              <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
                {activeTab === 'feedback' ? 'Title' : 'Subject'} *
              </label>
              <input
                type="text"
                id="title"
                value={formData.title}
                onChange={(e) => handleInputChange('title', e.target.value)}
                placeholder={
                  activeTab === 'feedback' 
                    ? `Brief description of your ${selectedType?.name.toLowerCase()}`
                    : 'Brief description of your issue'
                }
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Description */}
            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
                {activeTab === 'feedback' ? 'Description' : 'Message'} *
              </label>
              <textarea
                id="description"
                value={formData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                rows={4}
                placeholder={
                  activeTab === 'feedback'
                    ? 'Provide detailed information about your feedback...'
                    : 'Describe your issue or question in detail...'
                }
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Bug-specific fields */}
            {activeTab === 'feedback' && feedbackType === 'bug' && (
              <>
                {/* Severity */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Severity
                  </label>
                  <div className="flex space-x-3">
                    {['low', 'medium', 'high', 'critical'].map((severity) => (
                      <label key={severity} className="flex items-center">
                        <input
                          type="radio"
                          name="severity"
                          value={severity}
                          checked={formData.severity === severity}
                          onChange={(e) => handleInputChange('severity', e.target.value)}
                          className="mr-2"
                        />
                        <span className="text-sm capitalize">{severity}</span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Reproducible */}
                <div>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={formData.reproducible}
                      onChange={(e) => handleInputChange('reproducible', e.target.checked)}
                      className="mr-2"
                    />
                    <span className="text-sm font-medium text-gray-700">
                      This issue is reproducible
                    </span>
                  </label>
                </div>

                {/* Steps to reproduce */}
                {formData.reproducible && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Steps to reproduce
                    </label>
                    {formData.steps.map((step, index) => (
                      <div key={index} className="flex items-center space-x-2 mb-2">
                        <span className="text-sm text-gray-500 w-6">{index + 1}.</span>
                        <input
                          type="text"
                          value={step}
                          onChange={(e) => handleStepChange(index, e.target.value)}
                          placeholder="Describe this step"
                          className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        />
                        {formData.steps.length > 1 && (
                          <button
                            type="button"
                            onClick={() => removeStep(index)}
                            className="text-red-500 hover:text-red-700"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                          </button>
                        )}
                      </div>
                    ))}
                    <button
                      type="button"
                      onClick={addStep}
                      className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                    >
                      + Add Step
                    </button>
                  </div>
                )}

                {/* Expected vs Actual Behavior */}
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="expectedBehavior" className="block text-sm font-medium text-gray-700 mb-2">
                      Expected behavior
                    </label>
                    <textarea
                      id="expectedBehavior"
                      value={formData.expectedBehavior}
                      onChange={(e) => handleInputChange('expectedBehavior', e.target.value)}
                      rows={3}
                      placeholder="What should happen?"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label htmlFor="actualBehavior" className="block text-sm font-medium text-gray-700 mb-2">
                      Actual behavior
                    </label>
                    <textarea
                      id="actualBehavior"
                      value={formData.actualBehavior}
                      onChange={(e) => handleInputChange('actualBehavior', e.target.value)}
                      rows={3}
                      placeholder="What actually happens?"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                </div>
              </>
            )}

            {/* Attachments */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Attachments
              </label>
              <div className="space-y-3">
                <div className="flex space-x-2">
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    className="flex items-center space-x-2 px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.586-6.586a4 4 0 00-5.656-5.656l-6.586 6.586a6 6 0 108.486 8.486L20.5 13" />
                    </svg>
                    <span className="text-sm">Attach File</span>
                  </button>
                  <button
                    type="button"
                    onClick={captureScreenshot}
                    className="flex items-center space-x-2 px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    <span className="text-sm">Screenshot</span>
                  </button>
                </div>
                
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  accept=".jpg,.jpeg,.png,.gif,.pdf,.txt"
                  onChange={handleFileSelect}
                  className="hidden"
                />
                
                <p className="text-xs text-gray-500">
                  Supported formats: JPG, PNG, GIF, PDF, TXT. Max size: 10MB each. Max 5 files.
                </p>
                
                {attachments.length > 0 && (
                  <div className="space-y-2">
                    {attachments.map((file, index) => (
                      <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                        <div className="flex items-center space-x-2">
                          <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                          <span className="text-sm text-gray-700">{file.name}</span>
                          <span className="text-xs text-gray-500">
                            ({(file.size / 1024 / 1024).toFixed(1)} MB)
                          </span>
                        </div>
                        <button
                          type="button"
                          onClick={() => removeAttachment(index)}
                          className="text-red-500 hover:text-red-700"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </form>
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 p-6 bg-gray-50">
          <div className="flex justify-between items-center">
            <p className="text-sm text-gray-500">
              {activeTab === 'feedback' 
                ? 'Your feedback helps us improve AIOS v2'
                : 'We typically respond within 24 hours'
              }
            </p>
            <div className="flex space-x-3">
              <button
                type="button"
                onClick={handleClose}
                className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleSubmit}
                disabled={isSubmitting || !formData.title || !formData.description}
                className={`px-6 py-2 rounded-lg font-medium ${
                  isSubmitting || !formData.title || !formData.description
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                }`}
              >
                {isSubmitting ? (
                  <div className="flex items-center space-x-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>Submitting...</span>
                  </div>
                ) : (
                  `Submit ${activeTab === 'feedback' ? 'Feedback' : 'Request'}`
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FeedbackSystem; 
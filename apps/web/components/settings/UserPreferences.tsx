import React, { useState, useEffect } from 'react';
import { UserPreferences, AccessibilityPreferences, KeyboardShortcut } from '../../types/onboarding';

interface UserPreferencesProps {
  isOpen: boolean;
  onClose: () => void;
  userId: string;
  currentPreferences?: UserPreferences;
  onSave: (preferences: UserPreferences) => void;
}

const defaultPreferences: UserPreferences = {
  userId: '',
  general: {
    language: 'en',
    timezone: 'UTC',
    dateFormat: 'MM/dd/yyyy',
    timeFormat: '12h',
    theme: 'light',
    autoSave: true,
    confirmActions: true
  },
  notifications: {
    email: true,
    push: true,
    inApp: true,
    desktop: false,
    sms: false,
    categories: {
      'system-updates': true,
      'document-processing': true,
      'agent-notifications': true,
      'collaboration': true,
      'billing': true,
      'security': true
    },
    frequency: 'immediate',
    quietHours: {
      enabled: false,
      start: '22:00',
      end: '08:00'
    }
  },
  accessibility: {
    userId: '',
    highContrast: false,
    largeText: false,
    reducedMotion: false,
    screenReader: false,
    keyboardNavigation: true,
    colorBlindAssist: false,
    audioDescriptions: false,
    textToSpeech: false,
    fontSize: 'medium'
  },
  onboarding: {
    showTips: true,
    autoStartTours: true,
    showProgress: true,
    skipCompleted: true,
    reminderFrequency: 'weekly',
    preferredLearningStyle: 'interactive'
  },
  privacy: {
    analytics: true,
    crashReporting: true,
    usageData: true,
    personalizedContent: true,
    thirdPartySharing: false,
    dataRetention: '2years'
  },
  interface: {
    sidebarCollapsed: false,
    defaultView: 'grid',
    itemsPerPage: 20,
    showPreview: true,
    compactMode: false,
    animationsEnabled: true,
    tooltipsEnabled: true,
    breadcrumbsEnabled: true
  },
  updatedAt: new Date()
};

export const UserPreferencesComponent: React.FC<UserPreferencesProps> = ({
  isOpen,
  onClose,
  userId,
  currentPreferences,
  onSave
}) => {
  const [preferences, setPreferences] = useState<UserPreferences>(
    currentPreferences || { ...defaultPreferences, userId }
  );
  const [activeTab, setActiveTab] = useState('general');
  const [hasChanges, setHasChanges] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const tabs = [
    { id: 'general', name: 'General', icon: '⚙️' },
    { id: 'notifications', name: 'Notifications', icon: '🔔' },
    { id: 'accessibility', name: 'Accessibility', icon: '♿' },
    { id: 'onboarding', name: 'Learning', icon: '🎓' },
    { id: 'privacy', name: 'Privacy', icon: '🔒' },
    { id: 'interface', name: 'Interface', icon: '🎨' }
  ];

  useEffect(() => {
    if (currentPreferences) {
      setPreferences(currentPreferences);
    }
  }, [currentPreferences]);

  const updatePreference = (section: keyof UserPreferences, field: string, value: any) => {
    setPreferences(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value
      }
    }));
    setHasChanges(true);
  };

  const updateNestedPreference = (section: keyof UserPreferences, subsection: string, field: string, value: any) => {
    setPreferences(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [subsection]: {
          ...(prev[section] as any)[subsection],
          [field]: value
        }
      }
    }));
    setHasChanges(true);
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const updatedPreferences = {
        ...preferences,
        updatedAt: new Date()
      };
      await onSave(updatedPreferences);
      setHasChanges(false);
    } catch (error) {
      console.error('Failed to save preferences:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const resetToDefaults = () => {
    setPreferences({ ...defaultPreferences, userId });
    setHasChanges(true);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex">
        
        {/* Sidebar */}
        <div className="w-64 bg-gray-50 border-r border-gray-200 flex flex-col">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">Settings</h2>
            <p className="text-sm text-gray-600 mt-1">Customize your AIOS v2 experience</p>
          </div>
          
          <nav className="flex-1 p-4">
            <div className="space-y-1">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${
                    activeTab === tab.id
                      ? 'bg-blue-100 text-blue-900'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <span className="text-lg">{tab.icon}</span>
                  <span className="font-medium">{tab.name}</span>
                </button>
              ))}
            </div>
          </nav>
          
          <div className="p-4 border-t border-gray-200">
            <button
              onClick={resetToDefaults}
              className="w-full px-3 py-2 text-sm text-gray-600 hover:text-gray-800 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Reset to Defaults
            </button>
          </div>
        </div>

        {/* Main content */}
        <div className="flex-1 flex flex-col">
          {/* Header */}
          <div className="border-b border-gray-200 p-6 flex justify-between items-center">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                {tabs.find(t => t.id === activeTab)?.name} Settings
              </h3>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
              aria-label="Close settings"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-6">
            {/* General Settings */}
            {activeTab === 'general' && (
              <div className="space-y-6">
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Language
                    </label>
                    <select
                      value={preferences.general.language}
                      onChange={(e) => updatePreference('general', 'language', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="en">English</option>
                      <option value="es">Español</option>
                      <option value="fr">Français</option>
                      <option value="de">Deutsch</option>
                      <option value="ja">日本語</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Timezone
                    </label>
                    <select
                      value={preferences.general.timezone}
                      onChange={(e) => updatePreference('general', 'timezone', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="UTC">UTC</option>
                      <option value="America/New_York">Eastern Time</option>
                      <option value="America/Chicago">Central Time</option>
                      <option value="America/Denver">Mountain Time</option>
                      <option value="America/Los_Angeles">Pacific Time</option>
                    </select>
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Date Format
                    </label>
                    <select
                      value={preferences.general.dateFormat}
                      onChange={(e) => updatePreference('general', 'dateFormat', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="MM/dd/yyyy">MM/dd/yyyy</option>
                      <option value="dd/MM/yyyy">dd/MM/yyyy</option>
                      <option value="yyyy-MM-dd">yyyy-MM-dd</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Time Format
                    </label>
                    <div className="flex space-x-4">
                      <label className="flex items-center">
                        <input
                          type="radio"
                          name="timeFormat"
                          value="12h"
                          checked={preferences.general.timeFormat === '12h'}
                          onChange={(e) => updatePreference('general', 'timeFormat', e.target.value)}
                          className="mr-2"
                        />
                        12 hour
                      </label>
                      <label className="flex items-center">
                        <input
                          type="radio"
                          name="timeFormat"
                          value="24h"
                          checked={preferences.general.timeFormat === '24h'}
                          onChange={(e) => updatePreference('general', 'timeFormat', e.target.value)}
                          className="mr-2"
                        />
                        24 hour
                      </label>
                    </div>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Theme
                  </label>
                  <div className="grid grid-cols-3 gap-4">
                    {['light', 'dark', 'auto'].map((theme) => (
                      <label key={theme} className="flex items-center space-x-2 p-3 border rounded-lg cursor-pointer">
                        <input
                          type="radio"
                          name="theme"
                          value={theme}
                          checked={preferences.general.theme === theme}
                          onChange={(e) => updatePreference('general', 'theme', e.target.value)}
                        />
                        <span className="capitalize">{theme}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <div className="space-y-4">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={preferences.general.autoSave}
                      onChange={(e) => updatePreference('general', 'autoSave', e.target.checked)}
                      className="mr-3"
                    />
                    <div>
                      <div className="font-medium text-gray-900">Auto-save documents</div>
                      <div className="text-sm text-gray-600">Automatically save your work as you type</div>
                    </div>
                  </label>
                  
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={preferences.general.confirmActions}
                      onChange={(e) => updatePreference('general', 'confirmActions', e.target.checked)}
                      className="mr-3"
                    />
                    <div>
                      <div className="font-medium text-gray-900">Confirm destructive actions</div>
                      <div className="text-sm text-gray-600">Show confirmation dialogs for delete operations</div>
                    </div>
                  </label>
                </div>
              </div>
            )}

            {/* Accessibility Settings */}
            {activeTab === 'accessibility' && (
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Font Size
                  </label>
                  <div className="grid grid-cols-4 gap-3">
                    {['small', 'medium', 'large', 'extra-large'].map((size) => (
                      <label key={size} className="flex items-center space-x-2 p-3 border rounded-lg cursor-pointer">
                        <input
                          type="radio"
                          name="fontSize"
                          value={size}
                          checked={preferences.accessibility.fontSize === size}
                          onChange={(e) => updatePreference('accessibility', 'fontSize', e.target.value)}
                        />
                        <span className="text-sm capitalize">{size.replace('-', ' ')}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={preferences.accessibility.highContrast}
                        onChange={(e) => updatePreference('accessibility', 'highContrast', e.target.checked)}
                        className="mr-3"
                      />
                      <div>
                        <div className="font-medium text-gray-900">High contrast mode</div>
                        <div className="text-sm text-gray-600">Increase contrast for better visibility</div>
                      </div>
                    </label>
                    
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={preferences.accessibility.reducedMotion}
                        onChange={(e) => updatePreference('accessibility', 'reducedMotion', e.target.checked)}
                        className="mr-3"
                      />
                      <div>
                        <div className="font-medium text-gray-900">Reduce motion</div>
                        <div className="text-sm text-gray-600">Minimize animations and transitions</div>
                      </div>
                    </label>
                    
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={preferences.accessibility.keyboardNavigation}
                        onChange={(e) => updatePreference('accessibility', 'keyboardNavigation', e.target.checked)}
                        className="mr-3"
                      />
                      <div>
                        <div className="font-medium text-gray-900">Enhanced keyboard navigation</div>
                        <div className="text-sm text-gray-600">Improve keyboard accessibility features</div>
                      </div>
                    </label>
                  </div>
                  
                  <div className="space-y-4">
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={preferences.accessibility.colorBlindAssist}
                        onChange={(e) => updatePreference('accessibility', 'colorBlindAssist', e.target.checked)}
                        className="mr-3"
                      />
                      <div>
                        <div className="font-medium text-gray-900">Color blind assistance</div>
                        <div className="text-sm text-gray-600">Alternative color indicators</div>
                      </div>
                    </label>
                    
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={preferences.accessibility.textToSpeech}
                        onChange={(e) => updatePreference('accessibility', 'textToSpeech', e.target.checked)}
                        className="mr-3"
                      />
                      <div>
                        <div className="font-medium text-gray-900">Text-to-speech</div>
                        <div className="text-sm text-gray-600">Enable text-to-speech functionality</div>
                      </div>
                    </label>
                    
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={preferences.accessibility.screenReader}
                        onChange={(e) => updatePreference('accessibility', 'screenReader', e.target.checked)}
                        className="mr-3"
                      />
                      <div>
                        <div className="font-medium text-gray-900">Screen reader optimization</div>
                        <div className="text-sm text-gray-600">Optimize for screen reader software</div>
                      </div>
                    </label>
                  </div>
                </div>
              </div>
            )}

            {/* Privacy Settings */}
            {activeTab === 'privacy' && (
              <div className="space-y-6">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-start space-x-3">
                    <svg className="w-5 h-5 text-blue-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <div>
                      <h4 className="font-medium text-blue-900">Your data, your choice</h4>
                      <p className="text-sm text-blue-700 mt-1">
                        These settings help us improve AIOS v2 while respecting your privacy. You can change these settings at any time.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={preferences.privacy.analytics}
                      onChange={(e) => updatePreference('privacy', 'analytics', e.target.checked)}
                      className="mr-3"
                    />
                    <div>
                      <div className="font-medium text-gray-900">Usage analytics</div>
                      <div className="text-sm text-gray-600">Help us improve by sharing anonymous usage data</div>
                    </div>
                  </label>
                  
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={preferences.privacy.crashReporting}
                      onChange={(e) => updatePreference('privacy', 'crashReporting', e.target.checked)}
                      className="mr-3"
                    />
                    <div>
                      <div className="font-medium text-gray-900">Crash reporting</div>
                      <div className="text-sm text-gray-600">Automatically report crashes to help us fix issues</div>
                    </div>
                  </label>
                  
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={preferences.privacy.personalizedContent}
                      onChange={(e) => updatePreference('privacy', 'personalizedContent', e.target.checked)}
                      className="mr-3"
                    />
                    <div>
                      <div className="font-medium text-gray-900">Personalized content</div>
                      <div className="text-sm text-gray-600">Show personalized recommendations and content</div>
                    </div>
                  </label>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Data retention period
                  </label>
                  <select
                    value={preferences.privacy.dataRetention}
                    onChange={(e) => updatePreference('privacy', 'dataRetention', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="30days">30 days</option>
                    <option value="1year">1 year</option>
                    <option value="2years">2 years</option>
                    <option value="indefinite">Indefinite</option>
                  </select>
                </div>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="border-t border-gray-200 p-6 bg-gray-50">
            <div className="flex justify-between items-center">
              <div className="text-sm text-gray-500">
                {hasChanges ? 'You have unsaved changes' : 'All changes saved'}
              </div>
              <div className="flex space-x-3">
                <button
                  onClick={onClose}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSave}
                  disabled={!hasChanges || isSaving}
                  className={`px-6 py-2 rounded-lg font-medium ${
                    hasChanges && !isSaving
                      ? 'bg-blue-600 text-white hover:bg-blue-700'
                      : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  }`}
                >
                  {isSaving ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserPreferencesComponent; 
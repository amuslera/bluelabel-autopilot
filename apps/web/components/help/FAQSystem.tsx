import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { FAQItem, FAQCategory, DynamicFAQ } from '../../types/onboarding';

interface FAQSystemProps {
  isOpen: boolean;
  onClose: () => void;
  userId: string;
  currentContext?: Record<string, any>;
  suggestedFAQs?: string[];
}

// Mock FAQ data
const mockFAQCategories: FAQCategory[] = [
  {
    id: 'getting-started',
    name: 'Getting Started',
    description: 'Basic questions about using AIOS v2',
    icon: '🚀',
    priority: 1,
    itemCount: 12
  },
  {
    id: 'document-processing',
    name: 'Document Processing',
    description: 'Questions about uploading and processing files',
    icon: '📄',
    priority: 2,
    itemCount: 15
  },
  {
    id: 'ai-agents',
    name: 'AI Agents',
    description: 'Questions about the agent marketplace',
    icon: '🤖',
    priority: 3,
    itemCount: 18
  },
  {
    id: 'billing',
    name: 'Billing & Plans',
    description: 'Questions about pricing and subscriptions',
    icon: '💳',
    priority: 4,
    itemCount: 8
  },
  {
    id: 'troubleshooting',
    name: 'Troubleshooting',
    description: 'Common issues and solutions',
    icon: '🔧',
    priority: 5,
    itemCount: 20
  },
  {
    id: 'integrations',
    name: 'Integrations',
    description: 'Connecting with third-party services',
    icon: '🔗',
    priority: 6,
    itemCount: 10
  }
];

const mockFAQItems: FAQItem[] = [
  {
    id: 'what-is-aios',
    question: 'What is AIOS v2?',
    answer: `AIOS v2 is an AI-powered operating system that transforms how you work with documents, data, and automation. It provides:

• **Document Processing**: Upload and analyze any document type with AI
• **Agent Marketplace**: Access to 50+ specialized AI agents
• **Workflow Automation**: Create custom automated processes
• **Real-time Collaboration**: Work seamlessly with your team

AIOS v2 is designed to boost productivity by automating repetitive tasks and providing intelligent insights from your data.`,
    category: 'getting-started',
    tags: ['overview', 'introduction', 'features'],
    helpful: 89,
    notHelpful: 3,
    lastUpdated: new Date('2024-01-15'),
    relatedFAQs: ['how-to-get-started', 'pricing-plans'],
    searchKeywords: ['what is', 'aios', 'introduction', 'overview', 'features'],
    contextualTriggers: ['first-visit', 'dashboard-load']
  },
  {
    id: 'how-to-upload-document',
    question: 'How do I upload and process a document?',
    answer: `Uploading and processing documents in AIOS v2 is simple:

**Step 1: Navigate to Upload**
Click the "Upload" button in the main navigation or drag files directly onto the dashboard.

**Step 2: Select Files**
Choose files from your computer. We support:
- PDF documents
- Microsoft Word (.docx, .doc)
- Excel spreadsheets (.xlsx, .xls)
- Text files (.txt, .md)
- Images (JPG, PNG, GIF)

**Step 3: Choose Processing Options**
- **Quick Analysis**: Basic extraction and OCR
- **Advanced Processing**: Deep analysis with AI agents
- **Custom Workflow**: Apply specific agent combinations

**Step 4: Start Processing**
Click "Process" and monitor progress in real-time.

**Tips for Better Results:**
• Ensure documents are clear and readable
• Use descriptive filenames
• Group related documents together`,
    category: 'document-processing',
    tags: ['upload', 'process', 'documents', 'how-to'],
    helpful: 156,
    notHelpful: 8,
    lastUpdated: new Date('2024-01-12'),
    relatedFAQs: ['supported-file-types', 'processing-options'],
    searchKeywords: ['upload', 'document', 'process', 'file', 'how to'],
    contextualTriggers: ['upload-page-visit', 'file-upload-error']
  },
  {
    id: 'agent-marketplace-basics',
    question: 'How do I find and install AI agents?',
    answer: `The Agent Marketplace makes it easy to discover and install specialized AI agents:

**Finding Agents:**
1. Navigate to the Marketplace tab
2. Browse by category (Document Processing, Data Analysis, etc.)
3. Use search filters by rating, price, or functionality
4. Read reviews and ratings from other users

**Installing Agents:**
1. Click on an agent to view details
2. Review pricing and permissions
3. Click "Install" or "Subscribe"
4. Follow the setup wizard if required

**Managing Installed Agents:**
• View all installed agents in your dashboard
• Configure agent settings and permissions
• Monitor usage and billing
• Uninstall agents you no longer need

**Popular Agent Categories:**
• **Document Processing**: OCR, extraction, summarization
• **Data Analysis**: Charts, insights, predictions
• **Content Creation**: Writing, editing, translation
• **Automation**: Workflows, integrations, scheduling`,
    category: 'ai-agents',
    tags: ['marketplace', 'agents', 'install', 'discover'],
    helpful: 203,
    notHelpful: 12,
    lastUpdated: new Date('2024-01-10'),
    relatedFAQs: ['agent-pricing', 'agent-permissions'],
    searchKeywords: ['agent', 'marketplace', 'install', 'find', 'discover'],
    contextualTriggers: ['marketplace-visit', 'agent-install-error']
  },
  {
    id: 'pricing-plans',
    question: 'What are the pricing plans?',
    answer: `AIOS v2 offers flexible pricing to suit different needs:

**Free Tier**
• 5 document uploads per month
• Access to basic agents
• 1GB storage
• Community support

**Professional ($29/month)**
• Unlimited document uploads
• Access to all agents
• 100GB storage
• Priority support
• Advanced workflows

**Enterprise (Custom)**
• Everything in Professional
• Dedicated agents
• Custom integrations
• SLA guarantees
• Dedicated support manager

**Agent Marketplace Pricing:**
• Many agents are free
• Premium agents: $5-50/month
• Usage-based agents: $0.01-1.00 per use
• Revenue sharing: 70% to developers, 25% to platform, 5% to community

**Billing Details:**
• Monthly or annual billing
• Cancel anytime
• 14-day free trial for paid plans
• No setup fees`,
    category: 'billing',
    tags: ['pricing', 'plans', 'billing', 'cost'],
    helpful: 178,
    notHelpful: 15,
    lastUpdated: new Date('2024-01-08'),
    relatedFAQs: ['free-trial', 'payment-methods'],
    searchKeywords: ['price', 'cost', 'plan', 'billing', 'subscription'],
    contextualTriggers: ['billing-page-visit', 'upgrade-prompt']
  },
  {
    id: 'data-security',
    question: 'How secure is my data?',
    answer: `Data security is our top priority. Here's how we protect your information:

**Encryption:**
• All data encrypted in transit (TLS 1.3)
• Data encrypted at rest (AES-256)
• End-to-end encryption for sensitive documents

**Access Controls:**
• Multi-factor authentication
• Role-based permissions
• Regular access reviews
• Zero-trust architecture

**Compliance:**
• SOC 2 Type II certified
• GDPR compliant
• HIPAA available for Enterprise
• Regular security audits

**Data Handling:**
• Your data is never used to train AI models
• No data sharing with third parties
• Right to data deletion
• Data portability options

**Infrastructure:**
• Hosted on secure cloud providers
• Regular backups and disaster recovery
• 24/7 security monitoring
• Incident response procedures

**Transparency:**
• Regular security reports
• Privacy policy updates
• Security incident notifications
• Data processing agreements available`,
    category: 'troubleshooting',
    tags: ['security', 'privacy', 'encryption', 'compliance'],
    helpful: 234,
    notHelpful: 7,
    lastUpdated: new Date('2024-01-05'),
    relatedFAQs: ['gdpr-compliance', 'data-deletion'],
    searchKeywords: ['security', 'privacy', 'safe', 'encryption', 'data protection'],
    contextualTriggers: ['security-concern', 'data-upload']
  }
];

export const FAQSystem: React.FC<FAQSystemProps> = ({
  isOpen,
  onClose,
  userId,
  currentContext,
  suggestedFAQs = []
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [expandedFAQ, setExpandedFAQ] = useState<string | null>(null);
  const [searchResults, setSearchResults] = useState<FAQItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [helpfulVotes, setHelpfulVotes] = useState<Record<string, boolean>>({});
  const [showSuggested, setShowSuggested] = useState(true);

  // Search functionality
  const performSearch = useCallback((query: string, category: string = 'all') => {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }

    setIsLoading(true);
    
    setTimeout(() => {
      const results: Array<FAQItem & { relevanceScore: number }> = [];
      const queryLower = query.toLowerCase();
      
      mockFAQItems.forEach(faq => {
        if (category !== 'all' && faq.category !== category) {
          return;
        }

        let relevanceScore = 0;
        
        // Check question match
        if (faq.question.toLowerCase().includes(queryLower)) {
          relevanceScore += 10;
        }
        
        // Check answer match
        if (faq.answer.toLowerCase().includes(queryLower)) {
          relevanceScore += 5;
        }
        
        // Check keywords match
        faq.searchKeywords.forEach(keyword => {
          if (keyword.toLowerCase().includes(queryLower)) {
            relevanceScore += 3;
          }
        });
        
        // Check tags match
        faq.tags.forEach(tag => {
          if (tag.toLowerCase().includes(queryLower)) {
            relevanceScore += 2;
          }
        });
        
        if (relevanceScore > 0) {
          results.push({ ...faq, relevanceScore });
        }
      });
      
      results.sort((a, b) => b.relevanceScore - a.relevanceScore);
      setSearchResults(results);
      setIsLoading(false);
    }, 300);
  }, []);

  // Debounced search
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (searchQuery) {
        performSearch(searchQuery, selectedCategory);
      } else {
        setSearchResults([]);
      }
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [searchQuery, selectedCategory, performSearch]);

  // Get contextual FAQs based on current context
  const contextualFAQs = useMemo(() => {
    if (!currentContext) return [];
    
    return mockFAQItems.filter(faq => 
      faq.contextualTriggers?.some(trigger => 
        currentContext[trigger] === true
      )
    ).slice(0, 3);
  }, [currentContext]);

  // Get suggested FAQs
  const suggestedFAQItems = useMemo(() => {
    return mockFAQItems.filter(faq => suggestedFAQs.includes(faq.id));
  }, [suggestedFAQs]);

  // Filter FAQs by category
  const filteredFAQs = useMemo(() => {
    if (selectedCategory === 'all') return mockFAQItems;
    return mockFAQItems.filter(faq => faq.category === selectedCategory);
  }, [selectedCategory]);

  const handleCategoryClick = (categoryId: string) => {
    setSelectedCategory(categoryId);
    setSearchQuery('');
    setExpandedFAQ(null);
  };

  const handleFAQClick = (faqId: string) => {
    setExpandedFAQ(expandedFAQ === faqId ? null : faqId);
  };

  const handleHelpfulVote = (faqId: string, helpful: boolean) => {
    setHelpfulVotes(prev => ({
      ...prev,
      [faqId]: helpful
    }));
    
    // In real implementation, this would update the FAQ vote counts
    console.log(`FAQ ${faqId} voted as ${helpful ? 'helpful' : 'not helpful'}`);
  };

  if (!isOpen) return null;

  const displayFAQs = searchQuery ? searchResults : filteredFAQs;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-2xl w-full max-w-5xl max-h-[90vh] overflow-hidden flex">
        
        {/* Sidebar */}
        <div className="w-80 bg-gray-50 border-r border-gray-200 flex flex-col">
          <div className="p-6 border-b border-gray-200">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-gray-900">
                Frequently Asked Questions
              </h2>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600"
                aria-label="Close FAQ"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            {/* Search */}
            <div className="relative">
              <input
                type="text"
                placeholder="Search FAQs..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <svg className="absolute left-3 top-2.5 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>
          
          {/* Categories */}
          <div className="flex-1 overflow-y-auto p-6">
            <div className="space-y-2">
              <button
                onClick={() => handleCategoryClick('all')}
                className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
                  selectedCategory === 'all' 
                    ? 'bg-blue-100 text-blue-900' 
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium">All Questions</span>
                  <span className="text-sm text-gray-500">{mockFAQItems.length}</span>
                </div>
              </button>
              
              {mockFAQCategories.map((category) => (
                <button
                  key={category.id}
                  onClick={() => handleCategoryClick(category.id)}
                  className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
                    selectedCategory === category.id 
                      ? 'bg-blue-100 text-blue-900' 
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <span>{category.icon}</span>
                      <span className="font-medium">{category.name}</span>
                    </div>
                    <span className="text-sm text-gray-500">{category.itemCount}</span>
                  </div>
                  <p className="text-sm text-gray-500 mt-1">{category.description}</p>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Main content */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <div className="flex-1 overflow-y-auto p-8">
            
            {/* Suggested FAQs */}
            {!searchQuery && (contextualFAQs.length > 0 || suggestedFAQItems.length > 0) && showSuggested && (
              <div className="mb-8">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">
                    {contextualFAQs.length > 0 ? 'Suggested for You' : 'Popular Questions'}
                  </h3>
                  <button
                    onClick={() => setShowSuggested(false)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
                
                <div className="grid gap-4 mb-6">
                  {(contextualFAQs.length > 0 ? contextualFAQs : suggestedFAQItems).map((faq) => (
                    <div
                      key={faq.id}
                      onClick={() => handleFAQClick(faq.id)}
                      className="border border-blue-200 bg-blue-50 rounded-lg p-4 cursor-pointer hover:bg-blue-100 transition-colors"
                    >
                      <h4 className="font-medium text-blue-900 mb-2">{faq.question}</h4>
                      <p className="text-sm text-blue-700">
                        {faq.answer.substring(0, 120)}...
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Search results or category FAQs */}
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {searchQuery ? `Search Results for "${searchQuery}"` : 
                 selectedCategory === 'all' ? 'All Questions' : 
                 mockFAQCategories.find(c => c.id === selectedCategory)?.name}
              </h3>
              <p className="text-gray-600">
                {searchQuery && displayFAQs.length > 0 ? `${displayFAQs.length} questions found` :
                 searchQuery && displayFAQs.length === 0 ? 'No questions found' :
                 `${displayFAQs.length} questions available`}
              </p>
            </div>
            
            {isLoading ? (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              </div>
            ) : displayFAQs.length > 0 ? (
              <div className="space-y-4">
                {displayFAQs.map((faq) => (
                  <div
                    key={faq.id}
                    className="border border-gray-200 rounded-lg overflow-hidden"
                  >
                    <button
                      onClick={() => handleFAQClick(faq.id)}
                      className="w-full px-6 py-4 text-left hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex items-center justify-between">
                        <h4 className="font-medium text-gray-900 pr-4">{faq.question}</h4>
                        <div className="flex items-center space-x-2">
                          <div className="flex items-center text-sm text-gray-500">
                            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
                            </svg>
                            <span>{faq.helpful}</span>
                          </div>
                          <svg
                            className={`w-5 h-5 text-gray-400 transition-transform ${
                              expandedFAQ === faq.id ? 'rotate-180' : ''
                            }`}
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                          </svg>
                        </div>
                      </div>
                    </button>
                    
                    {expandedFAQ === faq.id && (
                      <div className="px-6 pb-6 border-t border-gray-100">
                        <div className="pt-4">
                          <div className="prose max-w-none text-gray-700">
                            {faq.answer.split('\n').map((line, index) => {
                              if (line.startsWith('**') && line.endsWith('**')) {
                                return <h4 key={index} className="font-semibold mt-4 mb-2">{line.slice(2, -2)}</h4>;
                              } else if (line.startsWith('• ')) {
                                return <li key={index} className="ml-4">{line.slice(2)}</li>;
                              } else if (line.trim() === '') {
                                return <br key={index} />;
                              } else {
                                return <p key={index} className="mb-3">{line}</p>;
                              }
                            })}
                          </div>
                          
                          {/* Tags */}
                          {faq.tags.length > 0 && (
                            <div className="flex flex-wrap gap-2 mt-4 mb-4">
                              {faq.tags.map((tag) => (
                                <span key={tag} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                                  {tag}
                                </span>
                              ))}
                            </div>
                          )}
                          
                          {/* Was this helpful */}
                          <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                            <div className="flex items-center space-x-4">
                              <span className="text-sm text-gray-500">Was this helpful?</span>
                              <div className="flex space-x-2">
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleHelpfulVote(faq.id, true);
                                  }}
                                  className={`flex items-center space-x-1 px-3 py-1 border rounded-lg transition-colors ${
                                    helpfulVotes[faq.id] === true
                                      ? 'border-green-500 bg-green-50 text-green-700'
                                      : 'border-gray-300 hover:bg-gray-50'
                                  }`}
                                >
                                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
                                  </svg>
                                  <span className="text-sm">Yes</span>
                                </button>
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleHelpfulVote(faq.id, false);
                                  }}
                                  className={`flex items-center space-x-1 px-3 py-1 border rounded-lg transition-colors ${
                                    helpfulVotes[faq.id] === false
                                      ? 'border-red-500 bg-red-50 text-red-700'
                                      : 'border-gray-300 hover:bg-gray-50'
                                  }`}
                                >
                                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14H5.236a2 2 0 01-1.789-2.894l3.5-7A2 2 0 018.736 3h4.018c.163 0 .326.02.485.06L17 4m-7 10v2a2 2 0 002 2h.095c.5 0 .905-.405.905-.905 0-.714.211-1.412.608-2.006L17 13V4m-7 10h2m5-10H5a2 2 0 00-2 2v6a2 2 0 002 2h2.5" />
                                  </svg>
                                  <span className="text-sm">No</span>
                                </button>
                              </div>
                            </div>
                            <div className="text-sm text-gray-500">
                              Updated: {faq.lastUpdated.toLocaleDateString()}
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <svg className="mx-auto w-12 h-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <h3 className="text-lg font-medium text-gray-900 mb-2">No questions found</h3>
                <p className="text-gray-600">Try adjusting your search terms or browse different categories.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default FAQSystem; 
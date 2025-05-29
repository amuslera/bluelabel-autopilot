import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { HelpArticle, HelpCategory, SearchResult, HelpEvent } from '../../types/onboarding';

interface HelpSystemProps {
  isOpen: boolean;
  onClose: () => void;
  onEvent: (event: HelpEvent) => void;
  userId: string;
  defaultCategory?: string;
  defaultSearch?: string;
}

// Mock data - in real implementation, this would come from an API
const mockCategories: HelpCategory[] = [
  {
    id: 'getting-started',
    name: 'Getting Started',
    description: 'Basic concepts and first steps',
    icon: '🚀',
    color: 'blue',
    priority: 1,
    articleCount: 8
  },
  {
    id: 'document-processing',
    name: 'Document Processing',
    description: 'Upload, process, and analyze documents',
    icon: '📄',
    color: 'green',
    priority: 2,
    articleCount: 12
  },
  {
    id: 'ai-agents',
    name: 'AI Agents',
    description: 'Discover and manage AI agents',
    icon: '🤖',
    color: 'purple',
    priority: 3,
    articleCount: 15
  },
  {
    id: 'workflows',
    name: 'Workflows',
    description: 'Create and manage automated workflows',
    icon: '⚡',
    color: 'yellow',
    priority: 4,
    articleCount: 10
  },
  {
    id: 'collaboration',
    name: 'Collaboration',
    description: 'Work with team members',
    icon: '👥',
    color: 'indigo',
    priority: 5,
    articleCount: 6
  },
  {
    id: 'troubleshooting',
    name: 'Troubleshooting',
    description: 'Solve common issues and errors',
    icon: '🔧',
    color: 'red',
    priority: 6,
    articleCount: 9
  }
];

const mockArticles: HelpArticle[] = [
  {
    id: 'welcome-to-aios',
    title: 'Welcome to AIOS v2',
    content: `# Welcome to AIOS v2

AIOS v2 is your AI-powered operating system that revolutionizes how you work with documents, data, and automation.

## Key Features

- **Document Processing**: Upload and analyze any document type
- **AI Agent Marketplace**: Access 50+ specialized AI agents
- **Workflow Automation**: Create custom automated processes
- **Real-time Collaboration**: Work seamlessly with your team

## Getting Started

1. Complete the onboarding process
2. Upload your first document
3. Explore the agent marketplace
4. Create your first workflow

Ready to transform your productivity? Let's begin!`,
    category: mockCategories[0],
    tags: ['introduction', 'overview', 'basics'],
    searchKeywords: ['welcome', 'introduction', 'overview', 'getting started', 'first time'],
    lastUpdated: new Date('2024-01-15'),
    difficulty: 'beginner',
    estimatedReadTime: 3,
    relatedArticles: ['first-document-upload', 'marketplace-basics'],
    upvotes: 245,
    downvotes: 8
  },
  {
    id: 'first-document-upload',
    title: 'How to Upload Your First Document',
    content: `# Uploading Your First Document

Learn how to upload and process documents in AIOS v2.

## Supported File Types

- PDF documents
- Microsoft Word (.docx, .doc)
- Excel spreadsheets (.xlsx, .xls)
- Text files (.txt, .md)
- Images (JPG, PNG, GIF)

## Upload Process

1. **Navigate to Dashboard**: Click the "Upload" button in the main navigation
2. **Select Files**: Choose files from your computer or drag and drop
3. **Choose Processing**: Select which AI agents to apply
4. **Start Processing**: Click "Process" to begin analysis

## Processing Options

### Quick Analysis
- Basic document extraction
- Text recognition (OCR)
- Basic insights

### Advanced Processing
- Deep content analysis
- Entity extraction
- Sentiment analysis
- Custom agent applications

## Best Practices

- Ensure documents are clear and readable
- Use descriptive filenames
- Group related documents together
- Review processing results carefully

Need help? Contact our support team!`,
    category: mockCategories[1],
    tags: ['upload', 'documents', 'processing', 'beginner'],
    searchKeywords: ['upload', 'document', 'file', 'process', 'first', 'how to'],
    lastUpdated: new Date('2024-01-10'),
    difficulty: 'beginner',
    estimatedReadTime: 5,
    relatedArticles: ['welcome-to-aios', 'document-formats'],
    upvotes: 189,
    downvotes: 12
  },
  // Add more mock articles...
];

export const HelpSystem: React.FC<HelpSystemProps> = ({
  isOpen,
  onClose,
  onEvent,
  userId,
  defaultCategory,
  defaultSearch = ''
}) => {
  const [searchQuery, setSearchQuery] = useState(defaultSearch);
  const [selectedCategory, setSelectedCategory] = useState<string>(defaultCategory || 'all');
  const [selectedArticle, setSelectedArticle] = useState<HelpArticle | null>(null);
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showAdvancedSearch, setShowAdvancedSearch] = useState(false);

  // Search functionality
  const performSearch = useCallback((query: string, category: string = 'all') => {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }

    setIsLoading(true);
    
    // Simulate API call delay
    setTimeout(() => {
      const results: SearchResult[] = [];
      const queryLower = query.toLowerCase();
      
      mockArticles.forEach(article => {
        // Skip if category filter doesn't match
        if (category !== 'all' && article.category.id !== category) {
          return;
        }

        let relevanceScore = 0;
        const matchedKeywords: string[] = [];
        
        // Check title match
        if (article.title.toLowerCase().includes(queryLower)) {
          relevanceScore += 10;
          matchedKeywords.push('title');
        }
        
        // Check content match
        if (article.content.toLowerCase().includes(queryLower)) {
          relevanceScore += 5;
          matchedKeywords.push('content');
        }
        
        // Check keywords match
        article.searchKeywords.forEach(keyword => {
          if (keyword.toLowerCase().includes(queryLower)) {
            relevanceScore += 3;
            matchedKeywords.push(keyword);
          }
        });
        
        // Check tags match
        article.tags.forEach(tag => {
          if (tag.toLowerCase().includes(queryLower)) {
            relevanceScore += 2;
            matchedKeywords.push(tag);
          }
        });
        
        if (relevanceScore > 0) {
          // Create excerpt
          const contentLower = article.content.toLowerCase();
          const queryIndex = contentLower.indexOf(queryLower);
          let excerpt = '';
          
          if (queryIndex !== -1) {
            const start = Math.max(0, queryIndex - 50);
            const end = Math.min(article.content.length, queryIndex + 150);
            excerpt = '...' + article.content.slice(start, end) + '...';
          } else {
            excerpt = article.content.slice(0, 150) + '...';
          }
          
          results.push({
            article,
            relevanceScore,
            matchedKeywords: [...new Set(matchedKeywords)],
            excerpt
          });
        }
      });
      
      // Sort by relevance score
      results.sort((a, b) => b.relevanceScore - a.relevanceScore);
      
      setSearchResults(results);
      setIsLoading(false);
      
      // Track search event
      onEvent({
        type: 'search',
        query,
        userId,
        timestamp: new Date(),
        metadata: { 
          resultsCount: results.length,
          category 
        }
      });
    }, 300);
  }, [onEvent, userId]);

  // Debounced search
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (searchQuery) {
        performSearch(searchQuery, selectedCategory);
      }
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [searchQuery, selectedCategory, performSearch]);

  const handleArticleClick = (article: HelpArticle) => {
    setSelectedArticle(article);
    onEvent({
      type: 'article_viewed',
      articleId: article.id,
      userId,
      timestamp: new Date()
    });
  };

  const handleCategoryClick = (categoryId: string) => {
    setSelectedCategory(categoryId);
    setSearchQuery('');
    setSelectedArticle(null);
    
    onEvent({
      type: 'category_browsed',
      categoryId,
      userId,
      timestamp: new Date()
    });
  };

  const handleRateArticle = (articleId: string, helpful: boolean) => {
    // In real implementation, this would update the article rating
    onEvent({
      type: 'article_rated',
      articleId,
      userId,
      timestamp: new Date(),
      metadata: { helpful }
    });
  };

  const filteredArticles = useMemo(() => {
    if (selectedCategory === 'all') return mockArticles;
    return mockArticles.filter(article => article.category.id === selectedCategory);
  }, [selectedCategory]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-2xl w-full max-w-6xl max-h-[90vh] overflow-hidden flex">
        
        {/* Sidebar */}
        <div className="w-80 bg-gray-50 border-r border-gray-200 flex flex-col">
          {/* Header */}
          <div className="p-6 border-b border-gray-200">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-gray-900">Help & Support</h2>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600"
                aria-label="Close help"
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
                placeholder="Search help articles..."
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
                  <span className="font-medium">All Articles</span>
                  <span className="text-sm text-gray-500">{mockArticles.length}</span>
                </div>
              </button>
              
              {mockCategories.map((category) => (
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
                    <span className="text-sm text-gray-500">{category.articleCount}</span>
                  </div>
                  <p className="text-sm text-gray-500 mt-1">{category.description}</p>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Main content */}
        <div className="flex-1 flex flex-col">
          {selectedArticle ? (
            /* Article view */
            <div className="flex-1 overflow-y-auto">
              <div className="p-8">
                {/* Back button */}
                <button
                  onClick={() => setSelectedArticle(null)}
                  className="flex items-center text-blue-600 hover:text-blue-700 mb-6"
                >
                  <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                  Back to results
                </button>
                
                {/* Article header */}
                <div className="mb-6">
                  <div className="flex items-center space-x-2 text-sm text-gray-500 mb-2">
                    <span>{selectedArticle.category.icon}</span>
                    <span>{selectedArticle.category.name}</span>
                    <span>•</span>
                    <span>{selectedArticle.estimatedReadTime} min read</span>
                    <span>•</span>
                    <span className={`px-2 py-1 rounded text-xs ${
                      selectedArticle.difficulty === 'beginner' ? 'bg-green-100 text-green-800' :
                      selectedArticle.difficulty === 'intermediate' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {selectedArticle.difficulty}
                    </span>
                  </div>
                  <h1 className="text-3xl font-bold text-gray-900 mb-4">{selectedArticle.title}</h1>
                </div>
                
                {/* Article content */}
                <div className="prose max-w-none">
                  {selectedArticle.content.split('\n').map((line, index) => {
                    if (line.startsWith('# ')) {
                      return <h1 key={index} className="text-2xl font-bold mt-8 mb-4">{line.slice(2)}</h1>;
                    } else if (line.startsWith('## ')) {
                      return <h2 key={index} className="text-xl font-bold mt-6 mb-3">{line.slice(3)}</h2>;
                    } else if (line.startsWith('### ')) {
                      return <h3 key={index} className="text-lg font-bold mt-4 mb-2">{line.slice(4)}</h3>;
                    } else if (line.startsWith('- ')) {
                      return <li key={index} className="ml-4">{line.slice(2)}</li>;
                    } else if (line.trim() === '') {
                      return <br key={index} />;
                    } else {
                      return <p key={index} className="mb-4">{line}</p>;
                    }
                  })}
                </div>
                
                {/* Article footer */}
                <div className="mt-8 pt-6 border-t border-gray-200">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <span className="text-sm text-gray-500">Was this helpful?</span>
                      <div className="flex space-x-2">
                        <button
                          onClick={() => handleRateArticle(selectedArticle.id, true)}
                          className="flex items-center space-x-1 px-3 py-1 border border-gray-300 rounded-lg hover:bg-gray-50"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
                          </svg>
                          <span className="text-sm">Yes ({selectedArticle.upvotes})</span>
                        </button>
                        <button
                          onClick={() => handleRateArticle(selectedArticle.id, false)}
                          className="flex items-center space-x-1 px-3 py-1 border border-gray-300 rounded-lg hover:bg-gray-50"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14H5.236a2 2 0 01-1.789-2.894l3.5-7A2 2 0 018.736 3h4.018c.163 0 .326.02.485.06L17 4m-7 10v2a2 2 0 002 2h.095c.5 0 .905-.405.905-.905 0-.714.211-1.412.608-2.006L17 13V4m-7 10h2m5-10H5a2 2 0 00-2 2v6a2 2 0 002 2h2.5" />
                          </svg>
                          <span className="text-sm">No ({selectedArticle.downvotes})</span>
                        </button>
                      </div>
                    </div>
                    <div className="text-sm text-gray-500">
                      Last updated: {selectedArticle.lastUpdated.toLocaleDateString()}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            /* Article list view */
            <div className="flex-1 overflow-y-auto p-8">
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {searchQuery ? `Search Results for "${searchQuery}"` : 
                   selectedCategory === 'all' ? 'All Articles' : 
                   mockCategories.find(c => c.id === selectedCategory)?.name}
                </h3>
                <p className="text-gray-600">
                  {searchQuery && searchResults.length > 0 ? `${searchResults.length} articles found` :
                   searchQuery && searchResults.length === 0 ? 'No articles found' :
                   `${filteredArticles.length} articles available`}
                </p>
              </div>
              
              {isLoading ? (
                <div className="flex items-center justify-center py-12">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                </div>
              ) : searchQuery ? (
                /* Search results */
                <div className="space-y-6">
                  {searchResults.map((result) => (
                    <div
                      key={result.article.id}
                      onClick={() => handleArticleClick(result.article)}
                      className="border border-gray-200 rounded-lg p-6 hover:border-blue-300 hover:shadow-md cursor-pointer transition-all"
                    >
                      <div className="flex items-start justify-between mb-3">
                        <h4 className="text-lg font-semibold text-blue-600 hover:text-blue-700">
                          {result.article.title}
                        </h4>
                        <div className="flex items-center space-x-2 text-sm text-gray-500">
                          <span>{result.article.category.icon}</span>
                          <span>{result.article.estimatedReadTime} min</span>
                        </div>
                      </div>
                      <p className="text-gray-600 mb-3">{result.excerpt}</p>
                      <div className="flex items-center justify-between">
                        <div className="flex flex-wrap gap-2">
                          {result.matchedKeywords.slice(0, 3).map((keyword) => (
                            <span key={keyword} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                              {keyword}
                            </span>
                          ))}
                        </div>
                        <div className="text-sm text-gray-500">
                          Relevance: {Math.round((result.relevanceScore / 10) * 100)}%
                        </div>
                      </div>
                    </div>
                  ))}
                  
                  {searchResults.length === 0 && (
                    <div className="text-center py-12">
                      <svg className="mx-auto w-12 h-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6-4h6m2 5.291A7.962 7.962 0 0112 15c-2.34 0-4.29-1.009-5.824-2.562M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                      </svg>
                      <h3 className="text-lg font-medium text-gray-900 mb-2">No articles found</h3>
                      <p className="text-gray-600">Try adjusting your search terms or browse categories instead.</p>
                    </div>
                  )}
                </div>
              ) : (
                /* Category articles */
                <div className="grid gap-6">
                  {filteredArticles.map((article) => (
                    <div
                      key={article.id}
                      onClick={() => handleArticleClick(article)}
                      className="border border-gray-200 rounded-lg p-6 hover:border-blue-300 hover:shadow-md cursor-pointer transition-all"
                    >
                      <div className="flex items-start justify-between mb-3">
                        <h4 className="text-lg font-semibold text-blue-600 hover:text-blue-700">
                          {article.title}
                        </h4>
                        <div className="flex items-center space-x-2 text-sm text-gray-500">
                          <span>{article.category.icon}</span>
                          <span>{article.estimatedReadTime} min</span>
                          <span className={`px-2 py-1 rounded text-xs ${
                            article.difficulty === 'beginner' ? 'bg-green-100 text-green-800' :
                            article.difficulty === 'intermediate' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {article.difficulty}
                          </span>
                        </div>
                      </div>
                      <p className="text-gray-600 mb-3">
                        {article.content.substring(0, 150)}...
                      </p>
                      <div className="flex items-center justify-between">
                        <div className="flex flex-wrap gap-2">
                          {article.tags.slice(0, 3).map((tag) => (
                            <span key={tag} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                              {tag}
                            </span>
                          ))}
                        </div>
                        <div className="flex items-center space-x-2 text-sm text-gray-500">
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
                          </svg>
                          <span>{article.upvotes}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default HelpSystem; 
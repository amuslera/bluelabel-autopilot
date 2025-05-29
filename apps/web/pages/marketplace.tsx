import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import MarketplaceInterface from '../components/marketplace/MarketplaceInterface';
import { Agent, MarketplaceCategory } from '../types/marketplace';

const MarketplacePage: React.FC = () => {
  const [installedAgents, setInstalledAgents] = useState<string[]>([]);

  // Mock categories data
  const mockCategories: MarketplaceCategory[] = [
    {
      id: 'document-processing',
      name: 'Document Processing',
      description: 'Agents specialized in analyzing and processing various document types',
      icon: '📄',
      agentCount: 45,
      featured: true
    },
    {
      id: 'data-integration',
      name: 'Data Integration',
      description: 'Connect and synchronize data from external sources',
      icon: '🔗',
      agentCount: 23,
      featured: true
    },
    {
      id: 'intelligence',
      name: 'Intelligence & Analytics',
      description: 'Advanced analysis and insight generation capabilities',
      icon: '🧠',
      agentCount: 31,
      featured: true
    },
    {
      id: 'automation',
      name: 'Workflow Automation',
      description: 'Process orchestration and automation agents',
      icon: '⚙️',
      agentCount: 18,
      featured: false
    },
    {
      id: 'communication',
      name: 'Communication',
      description: 'Email, messaging, and notification management',
      icon: '💬',
      agentCount: 10,
      featured: false
    },
    {
      id: 'legal',
      name: 'Legal & Compliance',
      description: 'Legal document analysis and compliance checking',
      icon: '⚖️',
      agentCount: 12,
      featured: false
    },
    {
      id: 'finance',
      name: 'Financial Analysis',
      description: 'Financial reporting and analysis specialists',
      icon: '💰',
      agentCount: 15,
      featured: false
    },
    {
      id: 'content',
      name: 'Content Management',
      description: 'Content creation, editing, and management tools',
      icon: '✍️',
      agentCount: 8,
      featured: false
    }
  ];

  // Extended mock agents data
  const mockAgents: Agent[] = [
    {
      id: 'legal-doc-analyzer',
      name: 'Legal Document Analyzer',
      description: 'Advanced AI agent specialized in analyzing legal documents, extracting clauses, and identifying compliance issues. Perfect for law firms and corporate legal departments.',
      category: ['document-processing', 'legal'],
      capabilities: [
        { name: 'contract-analysis', description: 'Extract and analyze contract clauses', inputTypes: ['pdf', 'docx'], outputTypes: ['json', 'html'] },
        { name: 'compliance-check', description: 'Verify regulatory compliance', inputTypes: ['pdf'], outputTypes: ['report'] },
        { name: 'clause-extraction', description: 'Identify key contract terms', inputTypes: ['pdf', 'docx'], outputTypes: ['structured-data'] }
      ],
      pricing: { type: 'subscription', price: 29, currency: 'USD', period: 'monthly', features: ['Unlimited documents', '24/7 support', 'Advanced analytics'] },
      author: { id: 'legaltech-inc', name: 'LegalTech Inc.', verified: true, rating: 4.8, agentCount: 5 },
      metrics: { averageProcessingTime: 2.3, successRate: 99.2, uptime: 99.8, errorRate: 0.2, resourceUsage: { cpu: 15, memory: 256, storage: 50 }, qualityScore: 95 },
      compatibility: { minVersion: '2.0.0', dependencies: [], conflicts: [], requirements: { memory: '512MB', cpu: '1 core', storage: '100MB' } },
      installation: { size: '45MB', downloadUrl: '', checksum: '', instructions: [], configurationOptions: [] },
      rating: 4.8,
      reviewCount: 234,
      downloadCount: 12500,
      featured: true,
      verified: true,
      createdAt: '2024-01-15T00:00:00Z',
      updatedAt: '2024-05-20T00:00:00Z'
    },
    {
      id: 'financial-reporter',
      name: 'Financial Report Processor',
      description: 'Extracts insights from financial reports, SEC filings, and earnings statements with high accuracy. Essential for financial analysts and investment firms.',
      category: ['document-processing', 'finance'],
      capabilities: [
        { name: 'financial-analysis', description: 'Analyze financial statements', inputTypes: ['pdf', 'excel'], outputTypes: ['dashboard'] },
        { name: 'sec-filing-parser', description: 'Parse SEC filings and extract key metrics', inputTypes: ['html', 'pdf'], outputTypes: ['structured-data'] }
      ],
      pricing: { type: 'usage', price: 0.50, currency: 'USD', usageUnit: 'per document', features: ['Pay per use', 'No commitments', 'Volume discounts'] },
      author: { id: 'fintech-solutions', name: 'FinTech Solutions', verified: true, rating: 4.6, agentCount: 8 },
      metrics: { averageProcessingTime: 4.1, successRate: 97.8, uptime: 99.5, errorRate: 0.5, resourceUsage: { cpu: 25, memory: 512, storage: 100 }, qualityScore: 92 },
      compatibility: { minVersion: '2.0.0', dependencies: [], conflicts: [], requirements: { memory: '1GB', cpu: '2 cores', storage: '200MB' } },
      installation: { size: '78MB', downloadUrl: '', checksum: '', instructions: [], configurationOptions: [] },
      rating: 4.6,
      reviewCount: 189,
      downloadCount: 8900,
      featured: true,
      verified: true,
      createdAt: '2024-02-01T00:00:00Z',
      updatedAt: '2024-05-18T00:00:00Z'
    },
    {
      id: 'content-summarizer',
      name: 'Content Summarizer Pro',
      description: 'Intelligent content summarization with context preservation and key insight extraction. Great for research and content management workflows.',
      category: ['document-processing', 'content'],
      capabilities: [
        { name: 'text-summarization', description: 'Generate concise summaries', inputTypes: ['text', 'pdf'], outputTypes: ['text', 'bullets'] },
        { name: 'key-insights', description: 'Extract key insights and themes', inputTypes: ['text', 'pdf'], outputTypes: ['insights'] }
      ],
      pricing: { type: 'free', features: ['Basic summarization', 'Community support', '100 documents/month'] },
      author: { id: 'open-ai-tools', name: 'Open AI Tools', verified: false, rating: 4.2, agentCount: 12 },
      metrics: { averageProcessingTime: 1.8, successRate: 95.5, uptime: 98.9, errorRate: 1.1, resourceUsage: { cpu: 10, memory: 128, storage: 25 }, qualityScore: 88 },
      compatibility: { minVersion: '1.8.0', dependencies: [], conflicts: [], requirements: { memory: '256MB', cpu: '1 core', storage: '50MB' } },
      installation: { size: '32MB', downloadUrl: '', checksum: '', instructions: [], configurationOptions: [] },
      rating: 4.2,
      reviewCount: 567,
      downloadCount: 23400,
      featured: false,
      verified: false,
      createdAt: '2024-03-10T00:00:00Z',
      updatedAt: '2024-05-25T00:00:00Z'
    },
    {
      id: 'crm-integrator',
      name: 'CRM Data Integrator',
      description: 'Seamlessly connect and synchronize data between AIOS and popular CRM systems like Salesforce, HubSpot, and Pipedrive.',
      category: ['data-integration', 'automation'],
      capabilities: [
        { name: 'salesforce-sync', description: 'Bi-directional Salesforce integration', inputTypes: ['api'], outputTypes: ['crm-data'] },
        { name: 'contact-enrichment', description: 'Enhance contact data with external sources', inputTypes: ['contacts'], outputTypes: ['enriched-contacts'] }
      ],
      pricing: { type: 'subscription', price: 49, currency: 'USD', period: 'monthly', features: ['Multiple CRM support', 'Real-time sync', 'Data mapping'] },
      author: { id: 'integration-experts', name: 'Integration Experts', verified: true, rating: 4.7, agentCount: 3 },
      metrics: { averageProcessingTime: 0.8, successRate: 98.9, uptime: 99.9, errorRate: 0.1, resourceUsage: { cpu: 5, memory: 64, storage: 20 }, qualityScore: 94 },
      compatibility: { minVersion: '2.1.0', dependencies: ['api-connector'], conflicts: [], requirements: { memory: '128MB', cpu: '1 core', storage: '30MB' } },
      installation: { size: '25MB', downloadUrl: '', checksum: '', instructions: [], configurationOptions: [] },
      rating: 4.7,
      reviewCount: 145,
      downloadCount: 6700,
      featured: true,
      verified: true,
      createdAt: '2024-02-20T00:00:00Z',
      updatedAt: '2024-05-22T00:00:00Z'
    },
    {
      id: 'sentiment-analyzer',
      name: 'Advanced Sentiment Analyzer',
      description: 'Analyze emotional tone and sentiment in text documents, emails, and social media content with enterprise-grade accuracy.',
      category: ['intelligence', 'content'],
      capabilities: [
        { name: 'sentiment-detection', description: 'Detect positive/negative sentiment', inputTypes: ['text'], outputTypes: ['sentiment-score'] },
        { name: 'emotion-analysis', description: 'Identify specific emotions', inputTypes: ['text'], outputTypes: ['emotion-profile'] }
      ],
      pricing: { type: 'usage', price: 0.02, currency: 'USD', usageUnit: 'per 1000 characters', features: ['Real-time processing', 'Batch processing', 'API access'] },
      author: { id: 'ai-analytics', name: 'AI Analytics Corp', verified: true, rating: 4.4, agentCount: 7 },
      metrics: { averageProcessingTime: 0.5, successRate: 96.8, uptime: 99.3, errorRate: 0.7, resourceUsage: { cpu: 8, memory: 96, storage: 15 }, qualityScore: 91 },
      compatibility: { minVersion: '1.9.0', dependencies: [], conflicts: [], requirements: { memory: '192MB', cpu: '1 core', storage: '40MB' } },
      installation: { size: '28MB', downloadUrl: '', checksum: '', instructions: [], configurationOptions: [] },
      rating: 4.4,
      reviewCount: 298,
      downloadCount: 15600,
      featured: false,
      verified: true,
      createdAt: '2024-03-01T00:00:00Z',
      updatedAt: '2024-05-15T00:00:00Z'
    },
    {
      id: 'email-automation',
      name: 'Smart Email Automation',
      description: 'Intelligent email processing, categorization, and automated response generation for enhanced productivity.',
      category: ['automation', 'communication'],
      capabilities: [
        { name: 'email-classification', description: 'Categorize emails automatically', inputTypes: ['email'], outputTypes: ['categories'] },
        { name: 'auto-response', description: 'Generate contextual responses', inputTypes: ['email'], outputTypes: ['draft-response'] }
      ],
      pricing: { type: 'subscription', price: 19, currency: 'USD', period: 'monthly', features: ['Unlimited emails', 'Custom rules', 'Analytics'] },
      author: { id: 'productivity-tools', name: 'Productivity Tools Inc', verified: false, rating: 4.1, agentCount: 6 },
      metrics: { averageProcessingTime: 1.2, successRate: 94.2, uptime: 98.7, errorRate: 1.3, resourceUsage: { cpu: 12, memory: 128, storage: 35 }, qualityScore: 86 },
      compatibility: { minVersion: '2.0.0', dependencies: ['email-connector'], conflicts: [], requirements: { memory: '256MB', cpu: '1 core', storage: '60MB' } },
      installation: { size: '38MB', downloadUrl: '', checksum: '', instructions: [], configurationOptions: [] },
      rating: 4.1,
      reviewCount: 421,
      downloadCount: 18900,
      featured: false,
      verified: false,
      createdAt: '2024-01-25T00:00:00Z',
      updatedAt: '2024-05-10T00:00:00Z'
    }
  ];

  const handleAgentInstall = (agent: Agent) => {
    // Mock installation process
    console.log(`Installing agent: ${agent.name}`);
    
    // Simulate installation delay
    setTimeout(() => {
      setInstalledAgents(prev => [...prev, agent.id]);
      
      // Show success notification (you could integrate with a toast library)
      alert(`${agent.name} has been successfully installed!`);
    }, 2000);
  };

  const handleAgentPreview = (agent: Agent) => {
    // Mock preview functionality
    console.log(`Previewing agent: ${agent.name}`);
    
    // This would open a modal or navigate to a detail page
    // For now, just show agent details in an alert
    alert(`Preview: ${agent.name}\n\n${agent.description}\n\nCapabilities: ${agent.capabilities.map(c => c.name).join(', ')}`);
  };

  // Load installed agents from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('installed-agents');
    if (saved) {
      try {
        setInstalledAgents(JSON.parse(saved));
      } catch (error) {
        console.error('Failed to load installed agents:', error);
      }
    }
  }, []);

  // Save installed agents to localStorage when changed
  useEffect(() => {
    localStorage.setItem('installed-agents', JSON.stringify(installedAgents));
  }, [installedAgents]);

  return (
    <>
      <Head>
        <title>Agent Marketplace - AIOS v2</title>
        <meta 
          name="description" 
          content="Discover and install specialized AI agents for document processing, data integration, and workflow automation. Transform your productivity with AIOS v2." 
        />
        <meta name="keywords" content="AI agents, marketplace, automation, document processing, data integration, AIOS" />
        <meta property="og:title" content="Agent Marketplace - AIOS v2" />
        <meta property="og:description" content="Discover and install specialized AI agents to supercharge your workflow" />
        <meta property="og:type" content="website" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="min-h-screen">
        {/* Navigation */}
        <nav className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <h1 className="text-2xl font-bold text-blue-600">AIOS v2</h1>
                </div>
                <div className="hidden md:block ml-10">
                  <div className="flex items-baseline space-x-4">
                    <a
                      href="/"
                      className="text-gray-500 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium"
                    >
                      Dashboard
                    </a>
                    <a
                      href="/marketplace"
                      className="bg-blue-100 text-blue-700 px-3 py-2 rounded-md text-sm font-medium"
                    >
                      Marketplace
                    </a>
                    <a
                      href="/agents"
                      className="text-gray-500 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium"
                    >
                      My Agents
                    </a>
                    <a
                      href="/workflows"
                      className="text-gray-500 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium"
                    >
                      Workflows
                    </a>
                  </div>
                </div>
              </div>
              <div className="flex items-center">
                <div className="flex items-center space-x-4">
                  <span className="text-sm text-gray-600">
                    {installedAgents.length} agents installed
                  </span>
                  <div className="h-8 w-8 bg-blue-600 rounded-full flex items-center justify-center">
                    <span className="text-white text-sm font-bold">U</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main>
          <MarketplaceInterface
            initialAgents={mockAgents}
            categories={mockCategories}
            onAgentInstall={handleAgentInstall}
            onAgentPreview={handleAgentPreview}
            installedAgentIds={installedAgents}
          />
        </main>

        {/* Footer */}
        <footer className="bg-gray-50 border-t border-gray-200">
          <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
              <div className="md:col-span-2">
                <h3 className="text-lg font-bold text-gray-900 mb-4">AIOS v2 Agent Marketplace</h3>
                <p className="text-gray-600 mb-4">
                  The definitive platform for AI agent discovery and deployment. 
                  Transform your workflow with specialized agents built by the community.
                </p>
                <div className="flex space-x-4">
                  <div className="text-sm">
                    <strong className="text-gray-900">127</strong>
                    <span className="text-gray-600"> agents</span>
                  </div>
                  <div className="text-sm">
                    <strong className="text-gray-900">89</strong>
                    <span className="text-gray-600"> developers</span>
                  </div>
                  <div className="text-sm">
                    <strong className="text-gray-900">45K+</strong>
                    <span className="text-gray-600"> downloads</span>
                  </div>
                </div>
              </div>
              
              <div>
                <h4 className="text-sm font-semibold text-gray-900 mb-4">Categories</h4>
                <ul className="space-y-2 text-sm">
                  <li><a href="#" className="text-gray-600 hover:text-blue-600">Document Processing</a></li>
                  <li><a href="#" className="text-gray-600 hover:text-blue-600">Data Integration</a></li>
                  <li><a href="#" className="text-gray-600 hover:text-blue-600">Intelligence & Analytics</a></li>
                  <li><a href="#" className="text-gray-600 hover:text-blue-600">Automation</a></li>
                </ul>
              </div>
              
              <div>
                <h4 className="text-sm font-semibold text-gray-900 mb-4">Developer</h4>
                <ul className="space-y-2 text-sm">
                  <li><a href="#" className="text-gray-600 hover:text-blue-600">Create Agent</a></li>
                  <li><a href="#" className="text-gray-600 hover:text-blue-600">Developer Portal</a></li>
                  <li><a href="#" className="text-gray-600 hover:text-blue-600">Documentation</a></li>
                  <li><a href="#" className="text-gray-600 hover:text-blue-600">API Reference</a></li>
                </ul>
              </div>
            </div>
            
            <div className="mt-8 pt-8 border-t border-gray-200">
              <p className="text-sm text-gray-600 text-center">
                © 2024 AIOS v2. All rights reserved. Building the future of AI-powered productivity.
              </p>
            </div>
          </div>
        </footer>
      </div>
    </>
  );
};

export default MarketplacePage; 
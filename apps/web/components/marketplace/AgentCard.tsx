import React from 'react';
import { Agent, AgentCardProps } from '../../types/marketplace';

const AgentCard: React.FC<AgentCardProps> = ({ 
  agent, 
  variant = 'grid', 
  onInstall, 
  onPreview, 
  installed = false 
}) => {
  const formatPrice = (pricing: Agent['pricing']) => {
    if (pricing.type === 'free') return 'Free';
    if (pricing.type === 'enterprise') return 'Enterprise';
    if (pricing.price) {
      const period = pricing.period === 'yearly' ? '/year' : '/month';
      return `$${pricing.price}${period}`;
    }
    return 'Contact for pricing';
  };

  const getStatusColor = (rating: number) => {
    if (rating >= 4.5) return 'text-green-600';
    if (rating >= 4.0) return 'text-blue-600';
    if (rating >= 3.5) return 'text-yellow-600';
    return 'text-gray-600';
  };

  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }, (_, i) => (
      <svg
        key={i}
        className={`w-4 h-4 ${i < Math.floor(rating) ? 'text-yellow-400' : 'text-gray-300'}`}
        fill="currentColor"
        viewBox="0 0 20 20"
      >
        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
      </svg>
    ));
  };

  if (variant === 'featured') {
    return (
      <div className="relative bg-gradient-to-br from-blue-50 to-indigo-100 rounded-xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 border border-blue-200">
        <div className="absolute top-4 right-4">
          <div className="bg-blue-600 text-white px-3 py-1 rounded-full text-xs font-semibold">
            Featured
          </div>
        </div>
        
        <div className="flex items-start space-x-4">
          <div className="flex-shrink-0">
            {agent.icon ? (
              <img src={agent.icon} alt={agent.name} className="w-16 h-16 rounded-lg" />
            ) : (
              <div className="w-16 h-16 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                <span className="text-white font-bold text-xl">{agent.name.charAt(0)}</span>
              </div>
            )}
          </div>
          
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-2 mb-2">
              <h3 className="text-xl font-bold text-gray-900 truncate">{agent.name}</h3>
              {agent.verified && (
                <svg className="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              )}
            </div>
            
            <p className="text-gray-600 text-sm mb-3 line-clamp-2">{agent.description}</p>
            
            <div className="flex items-center space-x-4 mb-4">
              <div className="flex items-center space-x-1">
                {renderStars(agent.rating)}
                <span className={`text-sm font-medium ${getStatusColor(agent.rating)}`}>
                  {agent.rating.toFixed(1)}
                </span>
                <span className="text-gray-500 text-sm">({agent.reviewCount})</span>
              </div>
              
              <div className="text-sm text-gray-500">
                {agent.downloadCount.toLocaleString()} downloads
              </div>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="text-lg font-bold text-gray-900">
                {formatPrice(agent.pricing)}
              </div>
              
              <div className="flex space-x-2">
                {onPreview && (
                  <button
                    onClick={() => onPreview(agent)}
                    className="px-4 py-2 text-blue-600 border border-blue-600 rounded-lg hover:bg-blue-50 transition-colors text-sm font-medium"
                  >
                    Preview
                  </button>
                )}
                {onInstall && (
                  <button
                    onClick={() => onInstall(agent)}
                    disabled={installed}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                      installed
                        ? 'bg-green-100 text-green-800 cursor-not-allowed'
                        : 'bg-blue-600 text-white hover:bg-blue-700'
                    }`}
                  >
                    {installed ? 'Installed' : 'Install'}
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (variant === 'list') {
    return (
      <div className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200 p-4 border border-gray-200">
        <div className="flex items-center space-x-4">
          <div className="flex-shrink-0">
            {agent.icon ? (
              <img src={agent.icon} alt={agent.name} className="w-12 h-12 rounded-lg" />
            ) : (
              <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                <span className="text-white font-bold">{agent.name.charAt(0)}</span>
              </div>
            )}
          </div>
          
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-2">
              <h3 className="text-lg font-semibold text-gray-900 truncate">{agent.name}</h3>
              {agent.verified && (
                <svg className="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              )}
            </div>
            <p className="text-gray-600 text-sm mt-1 line-clamp-1">{agent.description}</p>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-1">
              {renderStars(agent.rating)}
              <span className={`text-sm font-medium ${getStatusColor(agent.rating)}`}>
                {agent.rating.toFixed(1)}
              </span>
            </div>
            
            <div className="text-lg font-bold text-gray-900">
              {formatPrice(agent.pricing)}
            </div>
            
            <div className="flex space-x-2">
              {onPreview && (
                <button
                  onClick={() => onPreview(agent)}
                  className="px-3 py-1 text-blue-600 border border-blue-600 rounded hover:bg-blue-50 transition-colors text-sm"
                >
                  Preview
                </button>
              )}
              {onInstall && (
                <button
                  onClick={() => onInstall(agent)}
                  disabled={installed}
                  className={`px-3 py-1 rounded text-sm transition-colors ${
                    installed
                      ? 'bg-green-100 text-green-800 cursor-not-allowed'
                      : 'bg-blue-600 text-white hover:bg-blue-700'
                  }`}
                >
                  {installed ? 'Installed' : 'Install'}
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Default grid variant
  return (
    <div className="bg-white rounded-lg shadow-sm hover:shadow-lg transition-all duration-300 p-6 border border-gray-200 group cursor-pointer">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          {agent.icon ? (
            <img src={agent.icon} alt={agent.name} className="w-12 h-12 rounded-lg" />
          ) : (
            <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
              <span className="text-white font-bold">{agent.name.charAt(0)}</span>
            </div>
          )}
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-lg font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                {agent.name}
              </h3>
              {agent.verified && (
                <svg className="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              )}
            </div>
            <p className="text-sm text-gray-600">{agent.author.name}</p>
          </div>
        </div>
        
        {agent.featured && (
          <div className="bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full text-xs font-semibold">
            Featured
          </div>
        )}
      </div>
      
      <p className="text-gray-600 text-sm mb-4 line-clamp-3">{agent.description}</p>
      
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-1">
          {renderStars(agent.rating)}
          <span className={`text-sm font-medium ${getStatusColor(agent.rating)}`}>
            {agent.rating.toFixed(1)}
          </span>
          <span className="text-gray-500 text-sm">({agent.reviewCount})</span>
        </div>
        
        <div className="text-sm text-gray-500">
          {agent.downloadCount.toLocaleString()} installs
        </div>
      </div>
      
      <div className="flex items-center justify-between">
        <div className="text-lg font-bold text-gray-900">
          {formatPrice(agent.pricing)}
        </div>
        
        <div className="flex space-x-2">
          {onPreview && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onPreview(agent);
              }}
              className="px-3 py-1 text-blue-600 border border-blue-600 rounded hover:bg-blue-50 transition-colors text-sm"
            >
              Preview
            </button>
          )}
          {onInstall && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onInstall(agent);
              }}
              disabled={installed}
              className={`px-3 py-1 rounded text-sm transition-colors ${
                installed
                  ? 'bg-green-100 text-green-800 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              {installed ? 'Installed' : 'Install'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default AgentCard; 
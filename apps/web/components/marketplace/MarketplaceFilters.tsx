import React, { useState } from 'react';
import { MarketplaceFiltersProps, MarketplaceCategory } from '../../types/marketplace';

const MarketplaceFilters: React.FC<MarketplaceFiltersProps> = ({
  categories,
  selectedFilters,
  onFilterChange,
  onClearFilters
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  
  const pricingOptions = [
    { value: 'free', label: 'Free' },
    { value: 'subscription', label: 'Subscription' },
    { value: 'usage', label: 'Pay per use' },
    { value: 'enterprise', label: 'Enterprise' }
  ];

  const handleCategoryChange = (categoryId: string) => {
    const newCategories = selectedFilters.categories.includes(categoryId)
      ? selectedFilters.categories.filter(id => id !== categoryId)
      : [...selectedFilters.categories, categoryId];
    
    onFilterChange({
      ...selectedFilters,
      categories: newCategories
    });
  };

  const handlePricingChange = (pricingType: string) => {
    const newPricing = selectedFilters.pricing.includes(pricingType)
      ? selectedFilters.pricing.filter(type => type !== pricingType)
      : [...selectedFilters.pricing, pricingType];
    
    onFilterChange({
      ...selectedFilters,
      pricing: newPricing
    });
  };

  const handleRatingChange = (rating: number) => {
    onFilterChange({
      ...selectedFilters,
      rating: selectedFilters.rating === rating ? 0 : rating
    });
  };

  const handleToggleChange = (key: keyof typeof selectedFilters, value: boolean) => {
    onFilterChange({
      ...selectedFilters,
      [key]: value
    });
  };

  const getActiveFilterCount = () => {
    return (
      selectedFilters.categories.length +
      selectedFilters.pricing.length +
      (selectedFilters.rating > 0 ? 1 : 0) +
      (selectedFilters.compatibility ? 1 : 0) +
      (selectedFilters.featured ? 1 : 0) +
      (selectedFilters.verified ? 1 : 0)
    );
  };

  const activeFilterCount = getActiveFilterCount();

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      {/* Mobile Filter Toggle */}
      <div className="lg:hidden p-4 border-b border-gray-200">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center justify-between w-full text-left"
        >
          <span className="font-medium text-gray-900">
            Filters {activeFilterCount > 0 && `(${activeFilterCount})`}
          </span>
          <div className="flex items-center space-x-2">
            {activeFilterCount > 0 && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onClearFilters();
                }}
                className="text-sm text-blue-600 hover:text-blue-700"
              >
                Clear
              </button>
            )}
            <svg
              className={`w-5 h-5 transform transition-transform ${
                isExpanded ? 'rotate-180' : ''
              }`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </button>
      </div>

      {/* Filter Content */}
      <div className={`${isExpanded ? 'block' : 'hidden'} lg:block`}>
        <div className="p-6 space-y-6">
          {/* Clear Filters Button - Desktop */}
          <div className="hidden lg:flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900">Filters</h3>
            {activeFilterCount > 0 && (
              <button
                onClick={onClearFilters}
                className="text-sm text-blue-600 hover:text-blue-700 font-medium"
              >
                Clear all ({activeFilterCount})
              </button>
            )}
          </div>

          {/* Categories */}
          <div>
            <h4 className="text-sm font-medium text-gray-900 mb-3">Categories</h4>
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {categories.map((category) => (
                <label key={category.id} className="flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={selectedFilters.categories.includes(category.id)}
                    onChange={() => handleCategoryChange(category.id)}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <div className="ml-3 flex items-center justify-between flex-1">
                    <span className="text-sm text-gray-700">{category.name}</span>
                    <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                      {category.agentCount}
                    </span>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Pricing */}
          <div>
            <h4 className="text-sm font-medium text-gray-900 mb-3">Pricing</h4>
            <div className="space-y-2">
              {pricingOptions.map((option) => (
                <label key={option.value} className="flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={selectedFilters.pricing.includes(option.value)}
                    onChange={() => handlePricingChange(option.value)}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <span className="ml-3 text-sm text-gray-700">{option.label}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Rating */}
          <div>
            <h4 className="text-sm font-medium text-gray-900 mb-3">Rating</h4>
            <div className="space-y-2">
              {[4, 3, 2, 1].map((rating) => (
                <label key={rating} className="flex items-center cursor-pointer">
                  <input
                    type="radio"
                    name="rating"
                    checked={selectedFilters.rating === rating}
                    onChange={() => handleRatingChange(rating)}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                  />
                  <div className="ml-3 flex items-center">
                    <div className="flex items-center">
                      {Array.from({ length: 5 }, (_, i) => (
                        <svg
                          key={i}
                          className={`w-4 h-4 ${
                            i < rating ? 'text-yellow-400' : 'text-gray-300'
                          }`}
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                        </svg>
                      ))}
                    </div>
                    <span className="ml-2 text-sm text-gray-700">
                      {rating}+ stars
                    </span>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Special Filters */}
          <div>
            <h4 className="text-sm font-medium text-gray-900 mb-3">Special</h4>
            <div className="space-y-3">
              <label className="flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={selectedFilters.featured}
                  onChange={(e) => handleToggleChange('featured', e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <div className="ml-3 flex items-center">
                  <span className="text-sm text-gray-700">Featured</span>
                  <div className="ml-2 bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full text-xs font-semibold">
                    ⭐
                  </div>
                </div>
              </label>

              <label className="flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={selectedFilters.verified}
                  onChange={(e) => handleToggleChange('verified', e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <div className="ml-3 flex items-center">
                  <span className="text-sm text-gray-700">Verified</span>
                  <svg className="ml-2 w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                </div>
              </label>

              <label className="flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={selectedFilters.compatibility}
                  onChange={(e) => handleToggleChange('compatibility', e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <div className="ml-3 flex items-center">
                  <span className="text-sm text-gray-700">Compatible with my system</span>
                  <svg className="ml-2 w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </label>
            </div>
          </div>

          {/* Active Filters Summary */}
          {activeFilterCount > 0 && (
            <div className="pt-4 border-t border-gray-200">
              <div className="flex flex-wrap gap-2">
                {selectedFilters.categories.map((categoryId) => {
                  const category = categories.find(c => c.id === categoryId);
                  return category ? (
                    <span
                      key={categoryId}
                      className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                    >
                      {category.name}
                      <button
                        onClick={() => handleCategoryChange(categoryId)}
                        className="ml-1 inline-flex items-center justify-center w-4 h-4 text-blue-400 hover:text-blue-600"
                      >
                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </span>
                  ) : null;
                })}
                
                {selectedFilters.pricing.map((pricingType) => {
                  const option = pricingOptions.find(o => o.value === pricingType);
                  return option ? (
                    <span
                      key={pricingType}
                      className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800"
                    >
                      {option.label}
                      <button
                        onClick={() => handlePricingChange(pricingType)}
                        className="ml-1 inline-flex items-center justify-center w-4 h-4 text-green-400 hover:text-green-600"
                      >
                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </span>
                  ) : null;
                })}

                {selectedFilters.rating > 0 && (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                    {selectedFilters.rating}+ stars
                    <button
                      onClick={() => handleRatingChange(0)}
                      className="ml-1 inline-flex items-center justify-center w-4 h-4 text-yellow-400 hover:text-yellow-600"
                    >
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </span>
                )}

                {selectedFilters.featured && (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                    Featured
                    <button
                      onClick={() => handleToggleChange('featured', false)}
                      className="ml-1 inline-flex items-center justify-center w-4 h-4 text-purple-400 hover:text-purple-600"
                    >
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </span>
                )}

                {selectedFilters.verified && (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
                    Verified
                    <button
                      onClick={() => handleToggleChange('verified', false)}
                      className="ml-1 inline-flex items-center justify-center w-4 h-4 text-indigo-400 hover:text-indigo-600"
                    >
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </span>
                )}

                {selectedFilters.compatibility && (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">
                    Compatible
                    <button
                      onClick={() => handleToggleChange('compatibility', false)}
                      className="ml-1 inline-flex items-center justify-center w-4 h-4 text-emerald-400 hover:text-emerald-600"
                    >
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </span>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MarketplaceFilters; 
import React, { useState } from 'react';
import { DAGStep } from '@/lib/types';
import { format } from 'date-fns';
import { 
  ClipboardDocumentIcon, 
  DocumentArrowDownIcon, 
  ChevronDownIcon, 
  ChevronUpIcon,
  CodeBracketIcon,
  DocumentTextIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

interface DAGStepOutputProps {
  step: DAGStep;
}

const DAGStepOutput: React.FC<DAGStepOutputProps> = ({ step }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  
  // Use the step's output or create a mock one if not available
  const output = step.output || {
    type: step.error ? 'error' : 'text',
    content: step.error || 'No output available',
    timestamp: step.endTime || new Date().toISOString(),
  };

  const handleCopyToClipboard = () => {
    if (output.content) {
      navigator.clipboard.writeText(output.content);
      // Could add a toast notification here
    }
  };

  const handleDownload = () => {
    if (output.type === 'file' && output.downloadUrl) {
      // In a real app, this would trigger a file download
      window.open(output.downloadUrl, '_blank');
    } else if (output.type === 'file') {
      console.log(`Downloading ${output.content}`);
      // Could add a toast notification here
    }
  };

  const getOutputIcon = () => {
    switch (output.type) {
      case 'file':
        return <DocumentTextIcon className="h-4 w-4 text-blue-500" />;
      case 'error':
        return <ExclamationTriangleIcon className="h-4 w-4 text-red-500" />;
      case 'json':
        return <CodeBracketIcon className="h-4 w-4 text-purple-500" />;
      default:
        return <DocumentTextIcon className="h-4 w-4 text-gray-500" />;
    }
  };

  return (
    <div className="mt-2 border-t border-gray-100 pt-2">
      <button
        type="button"
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex w-full items-center justify-between text-left text-sm font-medium text-gray-700 hover:text-gray-900"
      >
        <div className="flex items-center">
          {getOutputIcon()}
          <span className="ml-2">
            {output.type === 'error' ? 'Error Details' : 'Step Output'}
            {output.type === 'file' && (
              <span className="ml-2 text-xs font-normal text-gray-500">
                {output.size || 'File'}
              </span>
            )}
          </span>
        </div>
        {isExpanded ? (
          <ChevronUpIcon className="h-4 w-4 text-gray-500" />
        ) : (
          <ChevronDownIcon className="h-4 w-4 text-gray-500" />
        )}
      </button>
      
      {isExpanded && (
        <div className={`mt-2 rounded-md p-3 text-sm ${
          output.type === 'error' 
            ? 'bg-red-50 text-red-800' 
            : 'bg-gray-50 text-gray-800'
        }`}>
          <div className="flex items-start justify-between">
            <div className="flex-1 min-w-0">
              {output.type === 'file' ? (
                <div className="flex items-center">
                  <span className="truncate font-mono">{output.content}</span>
                  {output.size && (
                    <span className="ml-2 text-xs opacity-75">({output.size})</span>
                  )}
                </div>
              ) : (
                <div className={`whitespace-pre-wrap break-words ${
                  output.type === 'error' ? 'font-mono text-sm' : ''
                }`}>
                  {output.content}
                </div>
              )}
              <div className="mt-1 text-xs opacity-75">
                {output.timestamp && (
                  <span>Generated at {format(new Date(output.timestamp), 'MMM d, yyyy HH:mm:ss')}</span>
                )}
              </div>
            </div>
            <div className="ml-2 flex-shrink-0 flex space-x-1">
              <button
                type="button"
                onClick={handleCopyToClipboard}
                className={`${
                  output.type === 'error' 
                    ? 'text-red-600 hover:text-red-800' 
                    : 'text-gray-400 hover:text-gray-600'
                }`}
                title="Copy to clipboard"
              >
                <ClipboardDocumentIcon className="h-4 w-4" />
              </button>
              {output.type === 'file' && (
                <button
                  type="button"
                  onClick={handleDownload}
                  className="text-gray-400 hover:text-gray-600"
                  title="Download file"
                >
                  <DocumentArrowDownIcon className="h-4 w-4" />
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DAGStepOutput;

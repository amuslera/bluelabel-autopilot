import React, { useState } from 'react';
import { DAGRun, DAGStep, DAGStatus } from '@/lib/types';
import { formatDistanceToNow, parseISO, format } from 'date-fns';
import { ChevronDownIcon, ChevronUpIcon } from '@heroicons/react/24/outline';

interface DAGRunStatusProps {
  dagRun: DAGRun;
  className?: string;
}

const statusColors: Record<DAGStatus, string> = {
  pending: 'bg-gray-200 text-gray-800',
  running: 'bg-blue-100 text-blue-800',
  success: 'bg-green-100 text-green-800',
  failed: 'bg-red-100 text-red-800',
  skipped: 'bg-yellow-100 text-yellow-800',
};

const statusIcons: Record<DAGStatus, React.ReactNode> = {
  pending: (
    <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
    </svg>
  ),
  running: (
    <svg className="h-4 w-4 animate-spin" fill="currentColor" viewBox="0 0 20 20">
      <path fillRule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clipRule="evenodd" />
    </svg>
  ),
  success: (
    <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
    </svg>
  ),
  failed: (
    <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
      <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
    </svg>
  ),
  skipped: (
    <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
    </svg>
  ),
};

const formatDuration = (ms?: number): string => {
  if (typeof ms !== 'number' || isNaN(ms) || ms < 0) return '--';
  
  const seconds = Math.floor((ms / 1000) % 60);
  const minutes = Math.floor((ms / (1000 * 60)) % 60);
  const hours = Math.floor(ms / (1000 * 60 * 60));

  const parts = [];
  if (hours > 0) parts.push(`${hours}h`);
  if (minutes > 0 || hours > 0) parts.push(`${minutes}m`);
  parts.push(`${seconds}s`);

  return parts.join(' ');
};

import DAGStepOutput from './DAGStepOutput';

const StepRow: React.FC<{ step: DAGStep }> = ({ step }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const statusColor = statusColors[step.status] || 'bg-gray-100 text-gray-800';
  const icon = statusIcons[step.status] || null;
  const hasOutput = step.output || step.error;

  return (
    <div className="border-b border-gray-100">
      <div 
        className={`flex items-center py-3 px-4 ${hasOutput ? 'cursor-pointer hover:bg-gray-50' : ''}`}
        onClick={hasOutput ? () => setIsExpanded(!isExpanded) : undefined}
      >
        <div className="flex-1 min-w-0">
          <div className="flex items-center">
            <div className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusColor} mr-3`}>
              {icon}
              <span className="ml-1 capitalize">{step.status}</span>
            </div>
            <h4 className="text-sm font-medium text-gray-900 truncate">
              {step.name}
            </h4>
          </div>
          <div className="mt-1 text-xs text-gray-500">
            {step.startTime ? (
              <span>
                {format(parseISO(step.startTime), 'MMM d, yyyy HH:mm:ss')}
                {step.endTime && (
                  <>
                    {' → '}
                    {format(parseISO(step.endTime), 'MMM d, yyyy HH:mm:ss')}
                  </>
                )}
              </span>
            ) : (
              'Not started'
            )}
          </div>
        </div>
        <div className="ml-4 flex-shrink-0 flex flex-col items-end">
          <span className="text-xs font-medium text-gray-500">
            {step.retryCount > 0 ? `${step.retryCount} retries` : 'No retries'}
          </span>
          <span className="text-xs text-gray-400">
            {formatDuration(step.duration)}
          </span>
        </div>
        {hasOutput && (
          <div className="ml-2">
            {isExpanded ? (
              <ChevronUpIcon className="h-4 w-4 text-gray-500" />
            ) : (
              <ChevronDownIcon className="h-4 w-4 text-gray-500" />
            )}
          </div>
        )}
      </div>
      {isExpanded && hasOutput && (
        <div className="px-4 pb-3 -mt-1">
          <DAGStepOutput step={step} />
        </div>
      )}
    </div>
  );
};

const DAGRunStatusComponent: React.FC<DAGRunStatusProps> = ({ dagRun, className = '' }) => {
  const statusColor = statusColors[dagRun.status] || 'bg-gray-100 text-gray-800';
  const icon = statusIcons[dagRun.status] || null;

  return (
    <div className={`bg-white shadow overflow-hidden sm:rounded-lg ${className}`}>
      <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h3 className="text-lg leading-6 font-medium text-gray-900">
              {dagRun.dagId} <span className="text-gray-500">#{dagRun.runId}</span>
            </h3>
            <p className="mt-1 max-w-2xl text-sm text-gray-500">
              {dagRun.metadata?.description || 'No description available'}
            </p>
          </div>
          <div className="mt-2 sm:mt-0">
            <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${statusColor}`}>
              {icon}
              <span className="ml-1 capitalize">{dagRun.status}</span>
            </div>
          </div>
        </div>
        
        <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div>
            <dt className="text-xs font-medium text-gray-500">Started</dt>
            <dd className="mt-1 text-sm text-gray-900">
              {dagRun.startDate ? (
                <time dateTime={dagRun.startDate}>
                  {formatDistanceToNow(parseISO(dagRun.startDate))} ago
                </time>
              ) : '--'}
            </dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-gray-500">Duration</dt>
            <dd className="mt-1 text-sm text-gray-900">
              {formatDuration(
                dagRun.startDate && dagRun.endDate
                  ? new Date(dagRun.endDate).getTime() - new Date(dagRun.startDate).getTime()
                  : undefined
              )}
            </dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-gray-500">Execution Date</dt>
            <dd className="mt-1 text-sm text-gray-900">
              {dagRun.executionDate ? format(parseISO(dagRun.executionDate), 'MMM d, yyyy HH:mm:ss') : '--'}
            </dd>
          </div>
        </div>
      </div>

      <div className="divide-y divide-gray-200">
        <div className="px-4 py-3 bg-gray-50 border-b border-gray-200">
          <h4 className="text-sm font-medium text-gray-900">Steps</h4>
        </div>
        {dagRun.steps.length > 0 ? (
          dagRun.steps.map((step) => (
            <StepRow key={step.id} step={step} />
          ))
        ) : (
          <div className="px-4 py-8 text-center">
            <p className="text-sm text-gray-500">No steps found in this DAG run.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default DAGRunStatusComponent;

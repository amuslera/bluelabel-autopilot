import React, { useState } from 'react';
import { RetroCard } from './RetroCard';
import { RetroButton } from './RetroButton';

interface FileUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUpload: (file: File) => void;
  onURLSubmit?: (url: string) => void;
}

type UploadMode = 'file' | 'url';

export const FileUploadModal: React.FC<FileUploadModalProps> = ({
  isOpen,
  onClose,
  onUpload,
  onURLSubmit,
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [uploadMode, setUploadMode] = useState<UploadMode>('file');
  const [url, setUrl] = useState('');
  const [processing, setProcessing] = useState(false);

  // Supported file types for AIOS v2
  const supportedTypes = {
    'application/pdf': '.pdf',
    'audio/mp3': '.mp3',
    'audio/wav': '.wav',
    'audio/m4a': '.m4a',
    'audio/mpeg': '.mp3',
    'audio/webm': '.webm',
    'audio/ogg': '.ogg',
    'text/plain': '.txt',
    'text/markdown': '.md',
    'application/msword': '.doc',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx'
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (isFileTypeSupported(file)) {
        setSelectedFile(file);
      } else {
        alert('Unsupported file type. Please select a PDF, audio file, or text document.');
      }
    }
  };

  const isFileTypeSupported = (file: File): boolean => {
    return Object.keys(supportedTypes).includes(file.type) || 
           Object.values(supportedTypes).some(ext => file.name.toLowerCase().endsWith(ext));
  };

  const getFileTypeCategory = (file: File): string => {
    if (file.type.includes('pdf')) return 'PDF Document';
    if (file.type.includes('audio')) return 'Audio File';
    if (file.type.includes('text') || file.name.endsWith('.md')) return 'Text Document';
    if (file.type.includes('word')) return 'Word Document';
    return 'Document';
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (isFileTypeSupported(file)) {
        setSelectedFile(file);
      } else {
        alert('Unsupported file type. Please select a PDF, audio file, or text document.');
      }
    }
  };

  const handleUpload = async () => {
    if (selectedFile) {
      setProcessing(true);
      try {
        await onUpload(selectedFile);
        setSelectedFile(null);
        onClose();
      } catch (error) {
        console.error('Upload error:', error);
      } finally {
        setProcessing(false);
      }
    }
  };

  const handleURLSubmit = async () => {
    if (url.trim() && onURLSubmit) {
      setProcessing(true);
      try {
        await onURLSubmit(url.trim());
        setUrl('');
        onClose();
      } catch (error) {
        console.error('URL processing error:', error);
      } finally {
        setProcessing(false);
      }
    }
  };

  const isValidURL = (string: string): boolean => {
    try {
      new URL(string);
      return true;
    } catch (_) {
      return false;
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
      <div className="w-full max-w-lg">
        <RetroCard title="UPLOAD CONTENT">
          {/* Mode Selection */}
          <div className="flex mb-6 border-2 border-terminal-cyan">
            <button
              onClick={() => setUploadMode('file')}
              className={`flex-1 py-2 px-4 font-bold transition-colors ${
                uploadMode === 'file'
                  ? 'bg-terminal-cyan text-terminal-dark'
                  : 'text-terminal-cyan hover:bg-terminal-cyan/20'
              }`}
            >
              FILE UPLOAD
            </button>
            <button
              onClick={() => setUploadMode('url')}
              className={`flex-1 py-2 px-4 font-bold transition-colors ${
                uploadMode === 'url'
                  ? 'bg-terminal-cyan text-terminal-dark'
                  : 'text-terminal-cyan hover:bg-terminal-cyan/20'
              }`}
            >
              URL PROCESS
            </button>
          </div>

          {uploadMode === 'file' ? (
            // File Upload Mode
            <>
              <div
                className={`border-2 border-dashed ${
                  dragOver ? 'border-green-400 bg-green-400/10' : 'border-cyan-400'
                } p-8 text-center transition-all duration-200`}
                onDragOver={(e) => {
                  e.preventDefault();
                  setDragOver(true);
                }}
                onDragLeave={() => setDragOver(false)}
                onDrop={handleDrop}
              >
                <input
                  type="file"
                  onChange={handleFileSelect}
                  className="hidden"
                  id="file-upload"
                  accept={Object.keys(supportedTypes).join(',')}
                />
                <label htmlFor="file-upload" className="cursor-pointer">
                  <div className="text-cyan-400 mb-4">
                    {selectedFile ? (
                      <>
                        <div className="text-green-400 text-lg font-bold mb-2">✓ FILE SELECTED</div>
                        <div className="text-cyan-400 font-mono">{selectedFile.name}</div>
                        <div className="text-sm mt-2 text-cyan-400/70">
                          {getFileTypeCategory(selectedFile)} • {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                        </div>
                      </>
                    ) : (
                      <>
                        <div className="text-2xl mb-4">📄</div>
                        <div className="font-bold mb-2">DROP FILE HERE OR CLICK TO SELECT</div>
                        <div className="text-sm text-cyan-400/70">
                          Supported: PDF, Audio (MP3, WAV, M4A), Text, Word docs
                        </div>
                      </>
                    )}
                  </div>
                </label>
              </div>

              {/* File Type Info */}
              <div className="mt-4 p-3 border border-terminal-cyan/30 bg-terminal-cyan/5">
                <div className="text-terminal-cyan text-sm font-bold mb-2">SUPPORTED FORMATS:</div>
                <div className="grid grid-cols-2 gap-2 text-xs text-terminal-cyan/80">
                  <div>📄 PDF Documents</div>
                  <div>🎵 Audio Files (MP3, WAV, M4A)</div>
                  <div>📝 Text Documents</div>
                  <div>📋 Word Documents</div>
                </div>
              </div>
            </>
          ) : (
            // URL Processing Mode
            <div className="space-y-4">
              <div>
                <label className="block text-terminal-cyan font-bold mb-2">
                  ENTER URL TO PROCESS:
                </label>
                <input
                  type="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://example.com/article-or-document"
                  className="w-full px-4 py-3 bg-terminal-dark border-2 border-terminal-cyan text-terminal-cyan 
                    placeholder-terminal-cyan/50 outline-none focus:border-green-400 focus:retro-glow
                    font-mono"
                />
              </div>

              <div className="p-3 border border-terminal-cyan/30 bg-terminal-cyan/5">
                <div className="text-terminal-cyan text-sm font-bold mb-2">URL PROCESSING:</div>
                <div className="text-xs text-terminal-cyan/80 space-y-1">
                  <div>• Extracts text content from web pages</div>
                  <div>• Downloads and processes PDF links</div>
                  <div>• Generates summaries and insights</div>
                  <div>• Supports articles, docs, and media files</div>
                </div>
              </div>

              {url && !isValidURL(url) && (
                <div className="text-error-pink text-sm">
                  ⚠ Please enter a valid URL starting with http:// or https://
                </div>
              )}
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex justify-between mt-6">
            <RetroButton variant="error" onClick={onClose} disabled={processing}>
              CANCEL
            </RetroButton>
            
            {uploadMode === 'file' ? (
              <RetroButton
                variant="primary"
                onClick={handleUpload}
                disabled={!selectedFile || processing}
              >
                {processing ? 'UPLOADING...' : 'UPLOAD & PROCESS'}
              </RetroButton>
            ) : (
              <RetroButton
                variant="success"
                onClick={handleURLSubmit}
                disabled={!url.trim() || !isValidURL(url) || processing || !onURLSubmit}
              >
                {processing ? 'PROCESSING...' : 'PROCESS URL'}
              </RetroButton>
            )}
          </div>

          {processing && (
            <div className="mt-4 text-center">
              <div className="text-terminal-cyan/70 text-sm animate-pulse">
                Processing content with AI agents...
              </div>
              <div className="mt-2 text-xs text-terminal-cyan/50">
                This may take a few moments depending on content size
              </div>
            </div>
          )}
        </RetroCard>
      </div>
    </div>
  );
}; 
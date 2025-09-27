import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { MonacoEditor } from '@/components/editor/MonacoEditor';
import { MermaidPreview } from '@/components/editor/MermaidPreview';
import { Header } from '@/components/layout/Header';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { ArrowLeft, Save, Download, Share2 } from 'lucide-react';

// Mock file data
const mockFileContent = `# User Journey Flowchart

This document outlines the user journey for our application.

## Login Flow

\`\`\`mermaid
graph TD
    A[User visits site] --> B{Is logged in?}
    B -->|Yes| C[Redirect to Dashboard]
    B -->|No| D[Show Login Form]
    D --> E[User enters credentials]
    E --> F{Valid credentials?}
    F -->|Yes| G[Create session]
    F -->|No| H[Show error message]
    G --> C
    H --> D
\`\`\`

## Dashboard Navigation

\`\`\`mermaid
graph LR
    A[Dashboard] --> B[My Files]
    A --> C[Team Files]
    A --> D[Admin Panel]
    B --> E[Create New File]
    B --> F[Edit Existing]
    C --> G[Join Team]
    C --> H[Browse Team Files]
\`\`\`

## File Management Process

The file management system allows users to:
- Create new UML diagrams
- Edit existing files
- Share with team members
- Export in multiple formats
`;

export default function FileEditor() {
  const { fileId } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  
  const [content, setContent] = useState(mockFileContent);
  const [fileName, setFileName] = useState('User Journey Flowchart.md');
  const [isAutoSaving, setIsAutoSaving] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date>(new Date());

  // Auto-save functionality
  useEffect(() => {
    if (!content) return;

    const autoSaveTimer = setTimeout(async () => {
      setIsAutoSaving(true);
      // Mock API call - replace with real backend
      await new Promise(resolve => setTimeout(resolve, 500));
      setLastSaved(new Date());
      setIsAutoSaving(false);
    }, 2000);

    return () => clearTimeout(autoSaveTimer);
  }, [content]);

  const handleSave = async () => {
    setIsAutoSaving(true);
    try {
      // Mock API call - replace with real backend
      await new Promise(resolve => setTimeout(resolve, 500));
      setLastSaved(new Date());
      toast({
        title: "File saved",
        description: "Your changes have been saved successfully.",
      });
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Save failed",
        description: "Unable to save file. Please try again.",
      });
    } finally {
      setIsAutoSaving(false);
    }
  };

  const handleDownload = () => {
    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    toast({
      title: "File downloaded",
      description: `${fileName} has been downloaded to your computer.`,
    });
  };

  const formatLastSaved = (date: Date): string => {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min${diffMins > 1 ? 's' : ''} ago`;
    
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    
    return date.toLocaleDateString();
  };

  return (
    <div className="flex flex-col h-screen bg-background">
      <Header />
      
      {/* Editor Header */}
      <div className="border-b bg-card/50 backdrop-blur-md">
        <div className="flex items-center justify-between px-6 py-4">
          <div className="flex items-center space-x-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate('/dashboard')}
              className="hover:bg-accent transition-fast"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Dashboard
            </Button>
            
            <div className="flex flex-col">
              <h1 className="text-xl font-semibold text-foreground">{fileName}</h1>
              <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                <span>
                  {isAutoSaving ? 'Saving...' : `Saved ${formatLastSaved(lastSaved)}`}
                </span>
                {isAutoSaving && (
                  <div className="h-2 w-2 bg-primary rounded-full animate-pulse" />
                )}
              </div>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <Button
              onClick={handleSave}
              size="sm"
              disabled={isAutoSaving}
              className="bg-primary hover:bg-primary-hover transition-fast shadow-elegant-sm"
            >
              <Save className="h-4 w-4 mr-2" />
              Save
            </Button>
            
            <Button
              onClick={handleDownload}
              variant="outline"
              size="sm"
              className="transition-fast"
            >
              <Download className="h-4 w-4 mr-2" />
              Download
            </Button>
            
            <Button
              variant="outline"
              size="sm"
              className="transition-fast"
            >
              <Share2 className="h-4 w-4 mr-2" />
              Share
            </Button>
          </div>
        </div>
      </div>

      {/* Editor Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel - Monaco Editor */}
        <div className="flex-1 p-6 bg-muted/30">
          <div className="h-full">
            <MonacoEditor
              value={content}
              onChange={setContent}
              language="markdown"
              theme="vs-dark"
            />
          </div>
        </div>

        {/* Right Panel - Mermaid Preview */}
        <div className="flex-1 p-6 bg-background border-l">
          <div className="h-full">
            <MermaidPreview content={content} />
          </div>
        </div>
      </div>
    </div>
  );
}
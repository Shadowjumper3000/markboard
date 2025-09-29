import { MermaidPreview } from '@/components/editor/MermaidPreview';
import { MonacoEditor } from '@/components/editor/MonacoEditor';
import { SimpleMermaidToolbar } from '@/components/editor/SimpleMermaidToolbar';
import { Header } from '@/components/layout/Header';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useToast } from '@/hooks/use-toast';
import { apiService } from '@/lib/api';
import { ArrowLeft, Check, Download, Edit3, Loader2, Share2, X } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';



export default function FileEditor() {
  const { fileId } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  
  const [content, setContent] = useState('');
  const [fileName, setFileName] = useState('');
  const [isAutoSaving, setIsAutoSaving] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [lastSaved, setLastSaved] = useState<Date>(new Date());
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [isEditingFileName, setIsEditingFileName] = useState(false);
  const [editedFileName, setEditedFileName] = useState('');

  // Template insertion handler
  const handleTemplateInsert = (templateContent: string) => {
    const newContent = content + (content && !content.endsWith('\n') ? '\n\n' : '\n') + templateContent + '\n';
    setContent(newContent);
    
    toast({
      title: "Template inserted",
      description: "Mermaid template has been added to your document.",
    });
  };



  // Load file data when component mounts or fileId changes
  useEffect(() => {
    const loadFile = async () => {
      if (!fileId) {
        navigate('/dashboard');
        return;
      }

      try {
        setIsLoading(true);
        const fileData = await apiService.getFile(fileId);
        
        setContent(fileData.content || '');
        // Store the full file name (with extension) for editing
        setFileName(fileData.name);
        setLastSaved(new Date(fileData.updated_at));
        setHasUnsavedChanges(false);
        
      } catch (error) {
        console.error('Error loading file:', error);
        toast({
          variant: "destructive",
          title: "Error loading file",
          description: error instanceof Error ? error.message : "Failed to load file content.",
        });
        navigate('/dashboard');
      } finally {
        setIsLoading(false);
      }
    };

    loadFile();
  }, [fileId, navigate, toast]);

  // Auto-save functionality
  useEffect(() => {
    if (!content || isLoading || !fileId || !hasUnsavedChanges) return;

    const autoSaveTimer = setTimeout(async () => {
      await handleSave(true); // Auto-save
    }, 2000);

    return () => clearTimeout(autoSaveTimer);
  }, [content, isLoading, fileId, hasUnsavedChanges]);

  // Track content changes
  useEffect(() => {
    setHasUnsavedChanges(true);
  }, [content]);

  const handleSave = async (isAutoSave = false) => {
    if (!fileId || isAutoSaving) return;

    setIsAutoSaving(true);
    try {
      await apiService.updateFile(fileId, { content });
      setLastSaved(new Date());
      setHasUnsavedChanges(false);
      
      if (!isAutoSave) {
        toast({
          title: "File saved",
          description: "Your changes have been saved successfully.",
        });
      }
    } catch (error) {
      console.error('Error saving file:', error);
      toast({
        variant: "destructive",
        title: "Save failed",
        description: error instanceof Error ? error.message : "Unable to save file. Please try again.",
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



  const handleStartEditing = () => {
    setIsEditingFileName(true);
    // Show file name without .md extension for editing
    const displayName = fileName.toLowerCase().endsWith('.md') ? fileName.slice(0, -3) : fileName;
    setEditedFileName(displayName);
  };

  const handleSaveFileName = async () => {
    if (!fileId || !editedFileName.trim()) {
      setIsEditingFileName(false);
      return;
    }

    try {
      const trimmedName = editedFileName.trim();
      // Ensure .md extension is preserved
      const finalName = trimmedName.toLowerCase().endsWith('.md') ? trimmedName : `${trimmedName}.md`;
      
      if (finalName === fileName) {
        setIsEditingFileName(false);
        return;
      }

      await apiService.updateFile(fileId, { name: finalName });
      setFileName(finalName);
      setIsEditingFileName(false);
      toast({
        title: "File renamed",
        description: "The file name has been updated successfully.",
      });
    } catch (error) {
      console.error('Error updating file name:', error);
      toast({
        variant: "destructive",
        title: "Rename failed",
        description: error instanceof Error ? error.message : "Unable to rename file. Please try again.",
      });
    }
  };

  const handleCancelEditing = () => {
    setIsEditingFileName(false);
    setEditedFileName('');
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

  // Show loading spinner while file is loading
  if (isLoading) {
    return (
      <div className="flex h-screen w-full bg-background items-center justify-center">
        <div className="text-center space-y-4">
          <Loader2 className="h-8 w-8 animate-spin mx-auto text-primary" />
          <p className="text-muted-foreground">Loading file...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen w-full bg-background">
      <main className="flex-1 flex flex-col overflow-hidden">
          <Header />
          
          {/* Editor Header */}
          <div className="border-b bg-card/50 backdrop-blur-md">
            <div className="flex items-center justify-between px-6 py-4">
              <div className="flex items-center space-x-4 group">
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
                  <div className="flex items-center space-x-2">
                    {isEditingFileName ? (
                      <div className="flex items-center space-x-2">
                        <Input
                          value={editedFileName}
                          onChange={(e) => setEditedFileName(e.target.value)}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') {
                              handleSaveFileName();
                            } else if (e.key === 'Escape') {
                              handleCancelEditing();
                            }
                          }}
                          className="text-xl font-semibold bg-background border-input"
                          autoFocus
                        />
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={handleSaveFileName}
                          className="h-8 w-8 p-0"
                        >
                          <Check className="h-4 w-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={handleCancelEditing}
                          className="h-8 w-8 p-0"
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                    ) : (
                      <div className="flex items-center space-x-2">
                        <h1 className="text-xl font-semibold text-foreground">
                          {fileName.toLowerCase().endsWith('.md') ? fileName.slice(0, -3) : fileName}
                        </h1>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={handleStartEditing}
                          className="h-8 w-8 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
                        >
                          <Edit3 className="h-4 w-4" />
                        </Button>
                      </div>
                    )}
                  </div>
                  <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                    <span>
                      {isAutoSaving ? 'Saving...' : hasUnsavedChanges ? 'Unsaved changes' : `Saved ${formatLastSaved(lastSaved)}`}
                    </span>
                    {isAutoSaving && (
                      <Loader2 className="h-3 w-3 animate-spin" />
                    )}
                    {hasUnsavedChanges && !isAutoSaving && (
                      <div className="h-2 w-2 bg-yellow-500 rounded-full" />
                    )}
                  </div>
                </div>
              </div>
              
              <div className="flex items-center space-x-3">
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
            <div className="flex-1 flex flex-col bg-muted/30">
              {/* Template Toolbar */}
              <SimpleMermaidToolbar onTemplateInsert={handleTemplateInsert} />
              
              {/* Editor */}
              <div className="flex-1 p-6 pt-0">
                <div className="h-full">
                  <MonacoEditor
                    value={content}
                    onChange={setContent}
                    language="markdown"
                    theme="vs-dark"
                  />
                </div>
              </div>
            </div>

            {/* Right Panel - Mermaid Preview */}
            <div className="flex-1 p-6 bg-background border-l">
              <div className="h-full">
                <MermaidPreview content={content} />
              </div>
            </div>
          </div>
        </main>
      </div>
  );
}
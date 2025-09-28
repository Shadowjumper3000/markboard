import { MermaidPreview } from '@/components/editor/MermaidPreview';
import { MonacoEditor } from '@/components/editor/MonacoEditor';
import { AppSidebar } from '@/components/layout/AppSidebar';
import { Header } from '@/components/layout/Header';
import { Button } from '@/components/ui/button';
import { SidebarProvider } from '@/components/ui/sidebar';
import { useToast } from '@/hooks/use-toast';
import { apiService } from '@/lib/api';
import { ArrowLeft, Download, Loader2, Share2 } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

interface Team {
  id: number;
  name: string;
  description: string;
  owner_id: number;
  file_count?: number;
}

interface FileItem {
  id: string;
  name: string;
  team: string;
  team_id?: number;
  team_name?: string;
  lastModified: string;
  size: string;
  starred: boolean;
  type: 'personal' | 'team';
  author: string;
  owner_id?: number;
}

export default function FileEditor() {
  const { fileId } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  
  const [content, setContent] = useState('');
  const [fileName, setFileName] = useState('');
  const [isAutoSaving, setIsAutoSaving] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [lastSaved, setLastSaved] = useState<Date>(new Date());
  const [selectedTeam, setSelectedTeam] = useState<string | null>(null);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [teams, setTeams] = useState<Team[]>([]);
  const [files, setFiles] = useState<FileItem[]>([]);

  // Load teams and files data
  useEffect(() => {
    const fetchTeams = async () => {
      try {
        const data = await apiService.listTeams();
        setTeams(data.teams || []);
      } catch (error) {
        console.error('Error fetching teams:', error);
      }
    };

    const fetchFiles = async () => {
      try {
        const data = await apiService.listFiles();
        
        // Convert backend file format to frontend FileItem format
        const convertedFiles: FileItem[] = data.files?.map((file: any) => {
          // Calculate time difference for lastModified
          const updatedAt = new Date(file.updated_at);
          const now = new Date();
          const diffMs = now.getTime() - updatedAt.getTime();
          const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
          const diffDays = Math.floor(diffHours / 24);
          
          let lastModified = 'Just now';
          if (diffHours < 1) {
            const diffMinutes = Math.floor(diffMs / (1000 * 60));
            lastModified = diffMinutes <= 1 ? 'Just now' : `${diffMinutes} minutes ago`;
          } else if (diffHours < 24) {
            lastModified = diffHours === 1 ? '1 hour ago' : `${diffHours} hours ago`;
          } else if (diffDays === 1) {
            lastModified = '1 day ago';
          } else {
            lastModified = `${diffDays} days ago`;
          }

          // Find team name from teams data
          const team = teams.find(t => t.id === file.team_id);
          const teamName = team ? team.name : (file.team_id ? `Team ${file.team_id}` : 'Personal');

          return {
            id: file.id.toString(),
            name: file.name,
            team: teamName,
            team_id: file.team_id,
            team_name: teamName,
            lastModified,
            size: file.size_formatted || '0 B',
            starred: false,
            type: file.team_id ? 'team' : 'personal',
            author: 'Unknown',
            owner_id: file.owner_id,
          };
        }) || [];

        setFiles(convertedFiles);
      } catch (error) {
        console.error('Error fetching files:', error);
      }
    };

    fetchTeams();
    fetchFiles();
  }, []);

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

  const handleFileSelect = (fileId: string) => {
    navigate(`/editor/${fileId}`);
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
    <SidebarProvider defaultOpen={false}>
      <div className="flex h-screen w-full bg-background">
        <AppSidebar 
          selectedTeam={selectedTeam}
          onTeamSelect={setSelectedTeam}
          onFileSelect={handleFileSelect}
          teams={teams}
          files={files}
        />
        
        <main className="flex-1 flex flex-col overflow-hidden">
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
        </main>
      </div>
    </SidebarProvider>
  );
}
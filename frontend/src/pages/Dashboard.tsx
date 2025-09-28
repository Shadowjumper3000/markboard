import { FileGrid, FileItem } from '@/components/files/FileGrid';
import { AppSidebar } from '@/components/layout/AppSidebar';
import { Header } from '@/components/layout/Header';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { SidebarProvider } from '@/components/ui/sidebar';
import { useToast } from '@/hooks/use-toast';
import { apiService } from '@/lib/api';
import { Filter, Grid, List, Search } from 'lucide-react';
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

// Utility function to format file name for display (hide .md extension)
const formatDisplayName = (fileName: string): string => {
  if (fileName.toLowerCase().endsWith('.md')) {
    return fileName.slice(0, -3);
  }
  return fileName;
};

interface Team {
  id: number;
  name: string;
  description: string;
  owner_id: number;
  file_count?: number;
}

interface User {
  id: number;
  email: string;
  is_admin: boolean;
}

export default function Dashboard() {
  const [selectedTeam, setSelectedTeam] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [files, setFiles] = useState<FileItem[]>([]);
  const [teams, setTeams] = useState<Team[]>([]);
  const [users, setUsers] = useState<Record<number, User>>({});
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();
  const navigate = useNavigate();

  // Filter files based on selected team and search query
  const filteredFiles = files.filter(file => {
    let matchesTeam;
    if (!selectedTeam) {
      // Show all files
      matchesTeam = true;
    } else if (selectedTeam === 'personal') {
      // Show only personal files (no team_id)
      matchesTeam = !file.team_id;
    } else {
      // Show only files from specific team
      matchesTeam = file.team_id && file.team_id.toString() === selectedTeam;
    }
    
    const matchesSearch = file.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         (file.team_name && file.team_name.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesTeam && matchesSearch;
  });

  const fetchTeams = async () => {
    try {
      const data = await apiService.listTeams();
      setTeams(data.teams || []);
    } catch (error) {
      console.error('Error fetching teams:', error);
    }
  };

  const fetchUsers = async () => {
    try {
      const data = await apiService.getAdminUsers();
      const usersMap: Record<number, User> = {};
      data.users?.forEach((user: User) => {
        usersMap[user.id] = user;
      });
      setUsers(usersMap);
    } catch (error) {
      console.error('Error fetching users:', error);
      // It's okay if this fails - we'll just show 'Unknown' for authors
    }
  };

  const fetchFiles = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      if (!token) {
        toast({
          title: "Authentication Error",
          description: "Please log in to view your files.",
          variant: "destructive",
        });
        return;
      }

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
          name: formatDisplayName(file.name),
          team: teamName,
          team_id: file.team_id,
          team_name: teamName,
          lastModified,
          starred: false, // Not implemented in backend yet
          type: file.team_id ? 'team' : 'personal',
          owner_id: file.owner_id,
        };
      }) || [];

      setFiles(convertedFiles);

    } catch (error) {
      console.error('Error fetching files:', error);
      toast({
        title: "Error",
        description: "Failed to load files.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTeams();
    fetchUsers();
  }, []);

  useEffect(() => {
    fetchFiles();
  }, [teams]);

  function getTeamName(teamId: string): string {
    if (teamId === 'personal') {
      return 'Personal Files';
    }
    const team = teams.find(t => t.id.toString() === teamId);
    return team ? team.name : 'Unknown Team';
  }

  const handleFileSelect = (fileId: string) => {
    navigate(`/editor/${fileId}`);
  };

  const handleFileDelete = async (fileId: string) => {
    try {
      await apiService.deleteFile(fileId);
      toast({
        title: "File deleted",
        description: "The file has been moved to trash.",
      });
      // Refresh the files list
      fetchFiles();
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to delete file.",
        variant: "destructive",
      });
    }
  };

  const handleFileToggleStar = (fileId: string) => {
    const file = files.find(f => f.id === fileId);
    toast({
      title: file?.starred ? "Removed from starred" : "Added to starred",
      description: `${file?.name} ${file?.starred ? 'removed from' : 'added to'} your starred files.`,
    });
    // TODO: Implement starring functionality in backend
  };

  return (
    <SidebarProvider defaultOpen={true}>
      <div className="flex h-screen w-full bg-background">
        <AppSidebar 
          selectedTeam={selectedTeam}
          onTeamSelect={setSelectedTeam}
          onFileSelect={handleFileSelect}
          teams={teams}
          files={files}
          onTeamsChange={fetchTeams}
        />
        
        <main className="flex-1 flex flex-col overflow-hidden">
          <Header />
          
          <div className="flex-1 overflow-auto">
            <div className="container mx-auto p-6 space-y-6">
              {/* Page Header */}
              <div className="flex flex-col space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h1 className="text-3xl font-bold tracking-tight text-foreground">
                      {selectedTeam ? getTeamName(selectedTeam) : 'All Files'}
                    </h1>
                    <p className="text-muted-foreground">
                      {filteredFiles.length} file{filteredFiles.length !== 1 ? 's' : ''} available
                    </p>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Button
                      variant={viewMode === 'grid' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setViewMode('grid')}
                      className="transition-fast"
                    >
                      <Grid className="h-4 w-4" />
                    </Button>
                    <Button
                      variant={viewMode === 'list' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setViewMode('list')}
                      className="transition-fast"
                    >
                      <List className="h-4 w-4" />
                    </Button>
                  </div>
                </div>

                {/* Search and Filters */}
                <div className="flex items-center space-x-4">
                    <div className="relative flex-1 max-w-md">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Search files..."
                      value={searchQuery}
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearchQuery(e.target.value)}
                      className="pl-10 transition-fast focus:shadow-elegant-sm"
                    />
                    </div>
                  <Button variant="outline" size="sm" className="transition-fast">
                    <Filter className="h-4 w-4 mr-2" />
                    Filter
                  </Button>
                </div>
              </div>

              {/* Files Grid */}
              {loading ? (
                <div className="text-center py-12">
                  <div className="text-muted-foreground">Loading files...</div>
                </div>
              ) : filteredFiles.length > 0 ? (
                <FileGrid
                  files={filteredFiles}
                  onFileSelect={handleFileSelect}
                  onFileDelete={handleFileDelete}
                  onFileToggleStar={handleFileToggleStar}
                />
              ) : (
                <div className="text-center py-12">
                  <div className="text-muted-foreground mb-4">
                    {searchQuery ? 'No files match your search.' : 'No files found.'}
                  </div>
                  <Button onClick={() => setSearchQuery('')} variant="outline">
                    Clear Search
                  </Button>
                </div>
              )}
            </div>
          </div>
        </main>
      </div>
    </SidebarProvider>
  );
}
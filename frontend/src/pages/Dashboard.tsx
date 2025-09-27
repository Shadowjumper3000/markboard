import React, { useState } from 'react';
import { SidebarProvider } from '@/components/ui/sidebar';
import { Header } from '@/components/layout/Header';
import { AppSidebar } from '@/components/layout/AppSidebar';
import { FileGrid, FileItem } from '@/components/files/FileGrid';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useToast } from '@/hooks/use-toast';
import { Search, Filter, Grid, List } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

// Mock data - replace with real API calls
const mockFiles: FileItem[] = [
  {
    id: '1',
    name: 'User Journey Flowchart.md',
    team: 'Product Team',
    lastModified: '2 hours ago',
    size: '2.4 KB',
    starred: true,
    type: 'team',
    author: 'Sarah Chen',
  },
  {
    id: '2',
    name: 'System Architecture Overview.md',
    team: 'Engineering',
    lastModified: '1 day ago',
    size: '5.7 KB',
    starred: false,
    type: 'team',
    author: 'Mike Johnson',
  },
  {
    id: '3',
    name: 'API Documentation.md',
    team: 'Engineering',
    lastModified: '3 days ago',
    size: '8.2 KB',
    starred: true,
    type: 'team',
    author: 'Alex Rodriguez',
  },
  {
    id: '4',
    name: 'Component Library Structure.md',
    team: 'Design System',
    lastModified: '1 week ago',
    size: '3.1 KB',
    starred: false,
    type: 'team',
    author: 'Lisa Park',
  },
  {
    id: '5',
    name: 'Personal Notes.md',
    team: 'Personal',
    lastModified: '5 minutes ago',
    size: '1.2 KB',
    starred: false,
    type: 'personal',
    author: 'You',
  },
];

export default function Dashboard() {
  const [selectedTeam, setSelectedTeam] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const { toast } = useToast();
  const navigate = useNavigate();

  // Filter files based on selected team and search query
  const filteredFiles = mockFiles.filter(file => {
    const matchesTeam = !selectedTeam || file.team === getTeamName(selectedTeam);
    const matchesSearch = file.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         file.team.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesTeam && matchesSearch;
  });

  function getTeamName(teamId: string): string {
    const teams: Record<string, string> = {
      '1': 'Product Team',
      '2': 'Engineering',
      '3': 'Design System',
    };
    return teams[teamId] || '';
  }

  const handleFileSelect = (fileId: string) => {
    navigate(`/editor/${fileId}`);
  };

  const handleFileDelete = (fileId: string) => {
    toast({
      title: "File deleted",
      description: "The file has been moved to trash.",
    });
  };

  const handleFileToggleStar = (fileId: string) => {
    const file = mockFiles.find(f => f.id === fileId);
    toast({
      title: file?.starred ? "Removed from starred" : "Added to starred",
      description: `${file?.name} ${file?.starred ? 'removed from' : 'added to'} your starred files.`,
    });
  };

  return (
    <SidebarProvider defaultOpen={true}>
      <div className="flex h-screen w-full bg-background">
        <AppSidebar 
          selectedTeam={selectedTeam}
          onTeamSelect={setSelectedTeam}
          onFileSelect={handleFileSelect}
        />
        
        <div className="flex-1 flex flex-col overflow-hidden">
          <Header />
          
          <main className="flex-1 overflow-auto">
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
                      onChange={(e) => setSearchQuery(e.target.value)}
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
              {filteredFiles.length > 0 ? (
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
          </main>
        </div>
      </div>
    </SidebarProvider>
  );
}
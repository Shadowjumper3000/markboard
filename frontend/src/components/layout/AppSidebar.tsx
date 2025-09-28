import { Badge } from '@/components/ui/badge';
import {
    Sidebar,
    SidebarContent,
    SidebarGroup,
    SidebarGroupContent,
    SidebarGroupLabel,
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
    useSidebar,
} from '@/components/ui/sidebar';
import { useAuth } from '@/contexts/AuthContext';
import { Clock, FileText, Folders, Star, Users } from 'lucide-react';

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

interface AppSidebarProps {
  selectedTeam?: string | null;
  onTeamSelect: (teamId: string | null) => void;
  onFileSelect: (fileId: string) => void;
  teams?: Team[];
  files?: FileItem[];
}

export function AppSidebar({ selectedTeam, onTeamSelect, onFileSelect, teams = [], files = [] }: AppSidebarProps) {
  const { user } = useAuth();
  const { state } = useSidebar();
  const collapsed = state === 'collapsed';

  const filteredFiles = selectedTeam 
    ? files.filter(file => file.team_id && file.team_id.toString() === selectedTeam)
    : files;

  return (
    <Sidebar className={`border-r bg-sidebar ${collapsed ? 'w-16' : 'w-sidebar'}`} collapsible="icon">
      <SidebarContent className="p-4">
        {/* My Teams Section */}
        <SidebarGroup>
          <SidebarGroupLabel className="flex items-center gap-2 text-sidebar-foreground font-medium">
            <Users className="h-4 w-4" />
            {!collapsed && 'My Teams'}
          </SidebarGroupLabel>
          <SidebarGroupContent className="mt-2">
            <SidebarMenu className="space-y-1">
              {/* All Files Option */}
              <SidebarMenuItem>
                <SidebarMenuButton
                  onClick={() => onTeamSelect(null)}
                  className={`w-full justify-start transition-fast hover:bg-sidebar-accent ${
                    !selectedTeam ? 'bg-sidebar-accent text-sidebar-accent-foreground' : ''
                  }`}
                >
                  <Folders className="h-4 w-4 mr-3" />
                  {!collapsed && (
                    <div className="flex items-center justify-between w-full">
                      <span>All Files</span>
                      <Badge variant="secondary" className="ml-2 text-xs">
                        {files.length}
                      </Badge>
                    </div>
                  )}
                </SidebarMenuButton>
              </SidebarMenuItem>

              {/* Team Options */}
              {teams.map((team) => (
                <SidebarMenuItem key={team.id}>
                  <SidebarMenuButton
                    onClick={() => onTeamSelect(team.id.toString())}
                    className={`w-full justify-start transition-fast hover:bg-sidebar-accent ${
                      selectedTeam === team.id.toString() ? 'bg-sidebar-accent text-sidebar-accent-foreground' : ''
                    }`}
                  >
                    <div className="h-3 w-3 rounded-full bg-blue-500 mr-3" />
                    {!collapsed && (
                      <div className="flex items-center justify-between w-full">
                        <span className="truncate">{team.name}</span>
                        <Badge variant="secondary" className="ml-2 text-xs">
                          {team.file_count || 0}
                        </Badge>
                      </div>
                    )}
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        {/* Recent Files Section */}
        <SidebarGroup className="mt-6">
          <SidebarGroupLabel className="flex items-center gap-2 text-sidebar-foreground font-medium">
            <Clock className="h-4 w-4" />
            {!collapsed && 'Recent Files'}
          </SidebarGroupLabel>
          <SidebarGroupContent className="mt-2">
            <SidebarMenu className="space-y-1">
              {filteredFiles.slice(0, collapsed ? 3 : 6).map((file) => (
                <SidebarMenuItem key={file.id}>
                  <SidebarMenuButton
                    onClick={() => onFileSelect(file.id)}
                    className="w-full justify-start transition-fast hover:bg-sidebar-accent group"
                  >
                    <FileText className="h-4 w-4 mr-3 text-muted-foreground group-hover:text-foreground" />
                    {!collapsed && (
                      <div className="flex items-center justify-between w-full min-w-0">
                        <div className="flex flex-col min-w-0">
                          <div className="flex items-center gap-2">
                            <span className="text-sm truncate">{file.name}</span>
                            {file.starred && (
                              <Star className="h-3 w-3 text-yellow-500 fill-current" />
                            )}
                          </div>
                          <span className="text-xs text-muted-foreground truncate">
                            {file.lastModified}
                          </span>
                        </div>
                      </div>
                    )}
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  );
}
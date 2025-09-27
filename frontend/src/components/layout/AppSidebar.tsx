import React, { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
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
import { Badge } from '@/components/ui/badge';
import { Folders, Users, FileText, Star, Clock } from 'lucide-react';

// Mock data - replace with real API calls
const mockTeams = [
  { id: '1', name: 'Product Team', fileCount: 12, color: 'bg-blue-500' },
  { id: '2', name: 'Engineering', fileCount: 28, color: 'bg-green-500' },
  { id: '3', name: 'Design System', fileCount: 8, color: 'bg-purple-500' },
];

const mockFiles = [
  { id: '1', name: 'User Journey.md', team: 'Product Team', lastModified: '2 hours ago', starred: true },
  { id: '2', name: 'System Architecture.md', team: 'Engineering', lastModified: '1 day ago', starred: false },
  { id: '3', name: 'API Documentation.md', team: 'Engineering', lastModified: '3 days ago', starred: true },
  { id: '4', name: 'Component Library.md', team: 'Design System', lastModified: '1 week ago', starred: false },
];

interface AppSidebarProps {
  selectedTeam?: string | null;
  onTeamSelect: (teamId: string | null) => void;
  onFileSelect: (fileId: string) => void;
}

export function AppSidebar({ selectedTeam, onTeamSelect, onFileSelect }: AppSidebarProps) {
  const { user } = useAuth();
  const { state } = useSidebar();
  const collapsed = state === 'collapsed';

  const filteredFiles = selectedTeam 
    ? mockFiles.filter(file => file.team === mockTeams.find(t => t.id === selectedTeam)?.name)
    : mockFiles;

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
                        {mockFiles.length}
                      </Badge>
                    </div>
                  )}
                </SidebarMenuButton>
              </SidebarMenuItem>

              {/* Team Options */}
              {mockTeams.map((team) => (
                <SidebarMenuItem key={team.id}>
                  <SidebarMenuButton
                    onClick={() => onTeamSelect(team.id)}
                    className={`w-full justify-start transition-fast hover:bg-sidebar-accent ${
                      selectedTeam === team.id ? 'bg-sidebar-accent text-sidebar-accent-foreground' : ''
                    }`}
                  >
                    <div className={`h-3 w-3 rounded-full ${team.color} mr-3`} />
                    {!collapsed && (
                      <div className="flex items-center justify-between w-full">
                        <span className="truncate">{team.name}</span>
                        <Badge variant="secondary" className="ml-2 text-xs">
                          {team.fileCount}
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
import { CreateFileModal } from '@/components/files/CreateFileModal';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { SidebarTrigger, useSidebar } from '@/components/ui/sidebar';
import { useAuth } from '@/contexts/AuthContext';
import { apiService } from '@/lib/api';
import { ArrowLeft, FileText, Home, LogOut, Plus, Settings, Shield } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';

// Safe hook to use sidebar context - returns null if not within SidebarProvider
function useSidebarSafe() {
  try {
    return useSidebar();
  } catch {
    return null;
  }
}

interface Team {
  id: number;
  name: string;
  description: string;
  owner_id: number;
  file_count?: number;
}

export function Header() {
  const { user, logout } = useAuth();
  const sidebarContext = useSidebarSafe();
  const location = useLocation();
  const isAdminPage = location.pathname === '/admin';
  const isEditorPage = location.pathname.startsWith('/editor/');
  const isDashboardPage = location.pathname === '/dashboard';
  
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [teams, setTeams] = useState<Team[]>([]);

  // Fetch teams when component mounts
  useEffect(() => {
    const fetchTeams = async () => {
      try {
        const data = await apiService.listTeams();
        setTeams(data.teams || []);
      } catch (error) {
        console.error('Error fetching teams:', error);
      }
    };

    fetchTeams();
  }, []);

  const handleNewFile = () => {
    setIsCreateModalOpen(true);
  };

  const handleCreateModalSuccess = () => {
    // Refresh the page or trigger a refresh in parent component
    if (isDashboardPage) {
      window.location.reload();
    }
  };

  return (
    <header className="h-header border-b bg-card/50 backdrop-blur-md sticky top-0 z-50">
      <div className="flex h-full items-center justify-between px-6">
        {/* Left section */}
        <div className="flex items-center space-x-4">
          {sidebarContext && !isEditorPage && (
            <SidebarTrigger className="hover:bg-accent transition-fast" />
          )}
          
          {isAdminPage ? (
            <Link to="/dashboard" className="flex items-center space-x-2 hover:opacity-80 transition-fast">
              <ArrowLeft className="h-5 w-5 text-primary" />
              <span className="text-lg font-semibold text-foreground">Back to Dashboard</span>
            </Link>
          ) : (
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <FileText className="h-6 w-6 text-primary" />
                <span className="text-xl font-bold text-foreground">UML Editor</span>
              </div>
              {!isDashboardPage && !isEditorPage && (
                <Link to="/">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="hover:bg-accent transition-fast"
                  >
                    <Home className="h-4 w-4 mr-2" />
                    Home
                  </Button>
                </Link>
              )}
            </div>
          )}
        </div>

        {/* Center section - hide file actions on admin and editor pages */}
        {!isAdminPage && !isEditorPage && (
          <div className="flex items-center space-x-3">
            <Button
              onClick={handleNewFile}
              size="sm"
              className="bg-primary hover:bg-primary-hover transition-fast shadow-elegant-sm"
            >
              <Plus className="h-4 w-4 mr-2" />
              New File
            </Button>
          </div>
        )}

        {/* Right section */}
        <div className="flex items-center space-x-4">
          {/* Admin Dashboard Link - only show if not already on admin page */}
          {user?.role === 'admin' && !isAdminPage && (
            <Link to="/admin">
              <Button
                variant="ghost"
                size="sm"
                className="hover:bg-accent transition-fast"
              >
                <Shield className="h-4 w-4 mr-2" />
                Admin Dashboard
              </Button>
            </Link>
          )}

          {/* User Menu */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                className="relative h-10 w-10 rounded-full hover:bg-accent transition-fast"
              >
                <Avatar className="h-10 w-10">
                  <AvatarFallback className="bg-gradient-primary text-primary-foreground font-medium">
                    {user?.name?.charAt(0).toUpperCase() || 'U'}
                  </AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-56" align="end">
              <DropdownMenuLabel className="font-normal">
                <div className="flex flex-col space-y-1">
                  <p className="text-sm font-medium">{user?.name}</p>
                  <p className="text-xs text-muted-foreground">{user?.email}</p>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem className="cursor-pointer">
                <Settings className="mr-2 h-4 w-4" />
                <span>Profile Settings</span>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                className="cursor-pointer text-destructive focus:text-destructive"
                onClick={logout}
              >
                <LogOut className="mr-2 h-4 w-4" />
                <span>Log out</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      {/* Create File Modal */}
      <CreateFileModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSuccess={handleCreateModalSuccess}
        teams={teams}
      />
    </header>
  );
}
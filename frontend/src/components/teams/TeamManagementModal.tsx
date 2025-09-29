import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs';
import { Textarea } from '@/components/ui/textarea';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/hooks/use-toast';
import { apiService } from '@/lib/api';
import { Crown, Plus, Search, Settings, UserPlus, Users, X } from 'lucide-react';
import React, { useEffect, useState } from 'react';

const MAX_TEAM_NAME_LENGTH = 20;
const MAX_TEAM_DESCRIPTION_LENGTH = 100;
interface Team {
  id: number;
  name: string;
  description: string;
  owner_id: number;
  file_count?: number;
  member_count?: number;
  role?: string;
}

interface TeamManagementModalProps {
  children: React.ReactNode;
  teams: Team[];
  onTeamsChange: () => void;
}

export function TeamManagementModal({ children, teams, onTeamsChange }: TeamManagementModalProps) {
  const [open, setOpen] = useState(false);
  const [newTeamName, setNewTeamName] = useState('');
  const [newTeamDescription, setNewTeamDescription] = useState('');
  const [joinTeamCode, setJoinTeamCode] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  const [isJoining, setIsJoining] = useState(false);
  const [availableTeams, setAvailableTeams] = useState<Team[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLeaving, setIsLeaving] = useState(false);
  const [isDisbanding, setIsDisbanding] = useState(false);
  const [selectedTeam, setSelectedTeam] = useState<Team | null>(null);
  const [isUserPopupOpen, setIsUserPopupOpen] = useState(false);
  const [teamUsers, setTeamUsers] = useState([]);
  const { toast } = useToast();
  const { user } = useAuth();

  // Filter available teams based on search
  const filteredAvailableTeams = availableTeams.filter(team =>
    team.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    team.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleCreateTeam = async () => {
    if (!newTeamName.trim()) {
      toast({
        title: "Error",
        description: "Team name is required.",
        variant: "destructive",
      });
      return;
    }

    if (newTeamName.length > MAX_TEAM_NAME_LENGTH) {
      toast({
        title: "Error",
        description: `Team name cannot exceed ${MAX_TEAM_NAME_LENGTH} characters.`,
        variant: "destructive",
      });
      return;
    }

    if (newTeamDescription.length > MAX_TEAM_DESCRIPTION_LENGTH) {
      toast({
        title: "Error",
        description: `Team description cannot exceed ${MAX_TEAM_DESCRIPTION_LENGTH} characters.`,
        variant: "destructive",
      });
      return;
    }

    if (user?.role !== 'admin' && teams.length >= 3) {
      toast({
        title: "Limit Reached",
        description: "You can only create up to 3 teams.",
        variant: "destructive",
      });
      return;
    }

    setIsCreating(true);
    try {
      await apiService.createTeam({
        name: newTeamName.trim(),
        description: newTeamDescription.trim(),
      });

      toast({
        title: "Team created",
        description: `${newTeamName} has been created successfully.`,
      });

      setNewTeamName('');
      setNewTeamDescription('');
      onTeamsChange();
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to create team.",
        variant: "destructive",
      });
    } finally {
      setIsCreating(false);
    }
  };

  const handleJoinTeam = async (teamId: number) => {
    setIsJoining(true);
    try {
      await apiService.joinTeam(teamId);

      toast({
        title: "Joined team",
        description: "You have successfully joined the team.",
      });

      onTeamsChange();
      loadAvailableTeams();
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to join team.",
        variant: "destructive",
      });
    } finally {
      setIsJoining(false);
    }
  };

  const handleLeaveTeam = async (teamId: number, teamName: string) => {
    setIsLeaving(true);
    try {
      await apiService.leaveTeam(teamId);

      toast({
        title: "Left team",
        description: `You have successfully left ${teamName}.`,
      });

      onTeamsChange();
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to leave team.",
        variant: "destructive",
      });
    } finally {
      setIsLeaving(false);
    }
  };

  const handleDisbandTeam = async (teamId: number, teamName: string) => {
    setIsDisbanding(true);
    try {
      await apiService.disbandTeam(teamId);

      toast({
        title: "Team disbanded",
        description: `${teamName} has been successfully disbanded.`,
      });

      onTeamsChange();
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to disband team.",
        variant: "destructive",
      });
    } finally {
      setIsDisbanding(false);
    }
  };

  const loadAvailableTeams = async () => {
    try {
      const response = await apiService.getAvailableTeams();
      setAvailableTeams(response.teams || []);
    } catch (error) {
      console.error('Error loading available teams:', error);
    }
  };

  const loadTeamUsers = async (teamId: number) => {
    try {
      const response = await apiService.getTeamUsers(teamId);
      setTeamUsers(response.users || []);
    } catch (error) {
      console.error('Error loading team users:', error);
    }
  };

  const handleOpenUserPopup = (team: Team) => {
    setSelectedTeam(team);
    loadTeamUsers(team.id);
    setIsUserPopupOpen(true);
  };

  const handleKickUser = async (userId: number) => {
    if (!selectedTeam) return;

    try {
      await apiService.kickUserFromTeam(selectedTeam.id, userId);
      toast({
        title: 'User kicked',
        description: 'The user has been removed from the team.',
      });
      loadTeamUsers(selectedTeam.id);
    } catch (error) {
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Failed to kick user.',
        variant: 'destructive',
      });
    }
  };

  useEffect(() => {
    if (open) {
      loadAvailableTeams();
    }
  }, [open]);

  // Update the CSS for team cards to make them square
  const teamCardStyle = "aspect-square flex flex-col justify-between";

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {children}
      </DialogTrigger>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Team Management
          </DialogTitle>
        </DialogHeader>

        <Tabs defaultValue="my-teams" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="my-teams">My Teams</TabsTrigger>
            <TabsTrigger value="create">Create Team</TabsTrigger>
            <TabsTrigger value="join">Join Team</TabsTrigger>
          </TabsList>

          <TabsContent value="my-teams" className="space-y-4">
            <div className="space-y-3">
              {teams.length === 0 ? (
                <div className="text-center py-8">
                  <Users className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">You're not a member of any teams yet.</p>
                  <p className="text-sm text-muted-foreground mt-2">
                    Create a new team or join an existing one to get started.
                  </p>
                </div>
              ) : (
                teams.map((team) => (
                  <Card key={team.id} className={teamCardStyle}>
                    <CardHeader className="pb-3">
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-lg flex items-center gap-2">
                          {team.name}
                          {team.role === 'admin' && (
                            <Crown className="h-4 w-4 text-yellow-500" />
                          )}
                        </CardTitle>
                        <Badge variant="secondary">
                          {team.file_count || 0} files
                        </Badge>
                      </div>
                      {team.description && (
                        <CardDescription>{team.description}</CardDescription>
                      )}
                    </CardHeader>
                    <CardContent className="pt-0">
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-sm text-muted-foreground">
                          {team.member_count || 0} members
                        </span>
                        <Badge variant={team.role === 'admin' ? 'default' : 'secondary'}>
                          {team.role || 'member'}
                        </Badge>
                      </div>
                      
                      <div className="flex items-center gap-2">
                        {team.owner_id.toString() === user?.id ? (
                          <AlertDialog>
                            <AlertDialogTrigger asChild>
                              <Button 
                                variant="destructive" 
                                size="sm"
                                className="flex-1"
                                disabled={isDisbanding}
                              >
                                <Trash2 className="h-4 w-4 mr-2" />
                                Disband Team
                              </Button>
                            </AlertDialogTrigger>
                            <AlertDialogContent>
                              <AlertDialogHeader>
                                <AlertDialogTitle>Disband Team</AlertDialogTitle>
                                <AlertDialogDescription>
                                  Are you sure you want to disband "{team.name}"? This action cannot be undone. 
                                  All team members will be removed and the team will be permanently deleted.
                                  {team.file_count && team.file_count > 0 && (
                                    <span className="block mt-2 font-medium text-destructive">
                                      This team has {team.file_count} files. Move or delete all files before disbanding.
                                    </span>
                                  )}
                                </AlertDialogDescription>
                              </AlertDialogHeader>
                              <AlertDialogFooter>
                                <AlertDialogCancel>Cancel</AlertDialogCancel>
                                <AlertDialogAction
                                  onClick={() => handleDisbandTeam(team.id, team.name)}
                                  className="bg-destructive hover:bg-destructive/90"
                                  disabled={isDisbanding || (team.file_count && team.file_count > 0)}
                                >
                                  {isDisbanding ? 'Disbanding...' : 'Disband Team'}
                                </AlertDialogAction>
                              </AlertDialogFooter>
                            </AlertDialogContent>
                          </AlertDialog>
                        ) : (
                          <AlertDialog>
                            <AlertDialogTrigger asChild>
                              <Button 
                                variant="outline" 
                                size="sm"
                                className="flex-1"
                                disabled={isLeaving}
                              >
                                <LogOut className="h-4 w-4 mr-2" />
                                Leave Team
                              </Button>
                            </AlertDialogTrigger>
                            <AlertDialogContent>
                              <AlertDialogHeader>
                                <AlertDialogTitle>Leave Team</AlertDialogTitle>
                                <AlertDialogDescription>
                                  Are you sure you want to leave "{team.name}"? You will lose access to all team files 
                                  and will need to be re-invited to join again.
                                </AlertDialogDescription>
                              </AlertDialogHeader>
                              <AlertDialogFooter>
                                <AlertDialogCancel>Cancel</AlertDialogCancel>
                                <AlertDialogAction
                                  onClick={() => handleLeaveTeam(team.id, team.name)}
                                  disabled={isLeaving}
                                >
                                  {isLeaving ? 'Leaving...' : 'Leave Team'}
                                </AlertDialogAction>
                              </AlertDialogFooter>
                            </AlertDialogContent>
                          </AlertDialog>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </TabsContent>

          <TabsContent value="create" className="space-y-4">
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="team-name">Team Name</Label>
                <Input
                  id="team-name"
                  value={newTeamName}
                  onChange={(e) => setNewTeamName(e.target.value)}
                  placeholder="Enter team name"
                  maxLength={100}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="team-description">Description (Optional)</Label>
                <Textarea
                  id="team-description"
                  value={newTeamDescription}
                  onChange={(e) => setNewTeamDescription(e.target.value)}
                  placeholder="Describe your team's purpose"
                  rows={3}
                  maxLength={500}
                />
              </div>
              <Button
                onClick={handleCreateTeam}
                disabled={isCreating || !newTeamName.trim()}
                className="w-full"
              >
                {isCreating ? (
                  <>Creating...</>
                ) : (
                  <>
                    <Plus className="h-4 w-4 mr-2" />
                    Create Team
                  </>
                )}
              </Button>
            </div>
          </TabsContent>

          <TabsContent value="join" className="space-y-4">
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="search">Search Teams</Label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="search"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search for teams to join"
                    className="pl-10"
                  />
                </div>
              </div>

              <div className="space-y-3 max-h-60 overflow-y-auto">
                {filteredAvailableTeams.length === 0 ? (
                  <div className="text-center py-8">
                    <UserPlus className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                    <p className="text-muted-foreground">
                      {searchQuery ? 'No teams match your search.' : 'No available teams to join.'}
                    </p>
                  </div>
                ) : (
                  filteredAvailableTeams.map((team) => (
                    <Card key={team.id} className={teamCardStyle}>
                    <Card key={team.id} className={teamCardStyle}>
                      <CardHeader className="pb-3">
                        <div className="flex items-center justify-between">
                          <CardTitle className="text-base">{team.name}</CardTitle>
                          <Button
                            size="sm"
                            onClick={() => handleJoinTeam(team.id)}
                            disabled={isJoining}
                          >
                            {isJoining ? 'Joining...' : 'Join'}
                          </Button>
                        </div>
                        {team.description && (
                          <CardDescription className="text-sm">
                            {team.description}
                          </CardDescription>
                        )}
                      </CardHeader>
                      <CardContent className="pt-0">
                        <div className="flex items-center justify-between text-sm text-muted-foreground">
                          <span>{team.member_count || 0} members</span>
                          <span>{team.file_count || 0} files</span>
                        </div>
                      </CardContent>
                    </Card>
                  ))
                )}
              </div>
            </div>
          </TabsContent>
        </Tabs>

        {/* User Management Popup */}
        {selectedTeam && (
          <Dialog open={isUserPopupOpen} onOpenChange={setIsUserPopupOpen}>
            <DialogContent className="max-w-md">
              <DialogHeader>
                <DialogTitle>Manage Users in {selectedTeam.name}</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                {teamUsers.map((user) => (
                  <div key={user.id} className="flex items-center justify-between">
                    <span>{user.name}</span>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => handleKickUser(user.id)}
                    >
                      <X className="h-4 w-4" />
                      Kick
                    </Button>
                  </div>
                ))}
              </div>
            </DialogContent>
          </Dialog>
        )}
      </DialogContent>
    </Dialog>
  );
}
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger
} from '@/components/ui/tabs';
import { Textarea } from '@/components/ui/textarea';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/hooks/use-toast';
import { apiService } from '@/lib/api';
import { Team } from '@/types';
import { Check, Copy, Crown, Plus, Settings, UserPlus, Users, X } from 'lucide-react';
import React, { useEffect, useState } from 'react';

const MAX_TEAM_NAME_LENGTH = 20;
const MAX_TEAM_DESCRIPTION_LENGTH = 100;


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
  const [isLeaving, setIsLeaving] = useState(false);
  const [copiedCode, setCopiedCode] = useState<string | null>(null);
  const [isDisbanding, setIsDisbanding] = useState(false);
  const [selectedTeam, setSelectedTeam] = useState<Team | null>(null);
  const [isUserPopupOpen, setIsUserPopupOpen] = useState(false);
  const [teamUsers, setTeamUsers] = useState([]);
  const { toast } = useToast();
  const { user } = useAuth();

  const handleJoinByCode = async () => {
    if (!joinTeamCode.trim()) {
      toast({
        title: "Error",
        description: "Please enter an invite code.",
        variant: "destructive",
      });
      return;
    }

    setIsJoining(true);
    try {
      const response = await apiService.joinTeamByCode(joinTeamCode.trim());

      toast({
        title: "Joined team",
        description: response.message,
      });

      setJoinTeamCode('');
      onTeamsChange();
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

    try {
      const teamCountResponse = await apiService.getUserTeamCount();
      if (user?.role !== 'admin' && teamCountResponse.count >= 3) {
        toast({
          title: "Limit Reached",
          description: "You can only create up to 3 teams.",
          variant: "destructive",
        });
        return;
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to validate team count. Please try again later.",
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

  const handleCopyInviteCode = async (code: string) => {
    try {
      await navigator.clipboard.writeText(code);
      setCopiedCode(code);
      toast({
        title: "Copied!",
        description: "Invite code copied to clipboard.",
      });
      setTimeout(() => setCopiedCode(null), 2000);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to copy invite code.",
        variant: "destructive",
      });
    }
  };

  const loadTeamUsers = async (teamId: number) => {
    try {
      const response = await apiService.getTeamUsers(teamId);
      // Add a 'name' property for each user (use email prefix as fallback)
      const usersWithName = (response.users || []).map((user) => ({
        ...user,
        name: user.name || (user.email ? user.email.split('@')[0].replace(/\./g, ' ').replace(/(^|\s)\S/g, l => l.toUpperCase()) : 'Unknown'),
      }));
      setTeamUsers(usersWithName);
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



  // Adjust the teamCardStyle to make the cards smaller and more compact
  const teamCardStyle = "flex flex-col justify-between items-center p-3 bg-card shadow-md hover:shadow-lg transition-shadow rounded-md";

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
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {teams.map((team) => (
                    <Card key={team.id} className={teamCardStyle}>
                      <CardHeader className="pb-2">
                        <div className="flex items-center justify-between">
                          <CardTitle className="text-lg flex items-center gap-2">
                            {team.name}
                            {team.role === 'admin' && (
                              <Crown className="h-4 w-4 text-yellow-500" />
                            )}
                          </CardTitle>
                          <Badge variant="secondary" label={`${team.file_count || 0} files`} />
                        </div>
                        {team.description && (
                          <CardDescription>{team.description}</CardDescription>
                        )}
                      </CardHeader>
                      <CardContent className="pt-0 flex flex-col gap-2">
                        {/* Show invite code for team owners */}
                        {team.role === 'admin' && team.invite_code && (
                          <div className="mb-2 p-2 bg-muted rounded-md">
                            <div className="flex items-center justify-between gap-2">
                              <div className="flex-1">
                                <p className="text-xs text-muted-foreground mb-1">Invite Code</p>
                                <code className="text-sm font-mono font-semibold">{team.invite_code}</code>
                              </div>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleCopyInviteCode(team.invite_code!)}
                                className="h-8 w-8 p-0"
                              >
                                {copiedCode === team.invite_code ? (
                                  <Check className="h-4 w-4 text-green-500" />
                                ) : (
                                  <Copy className="h-4 w-4" />
                                )}
                              </Button>
                            </div>
                          </div>
                        )}
                        <div className="flex items-center justify-between text-sm text-muted-foreground">
                          <span>{team.member_count || 0} members</span>
                          {team.role === 'admin' && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleOpenUserPopup(team)}
                            >
                              <Settings className="h-4 w-4" />
                            </Button>
                          )}
                        </div>
                        {/* Disband Team button logic */}
                        {team.role === 'admin' && (
                          <Button
                            variant="destructive"
                            size="sm"
                            className="mt-2"
                            disabled={isDisbanding}
                            onClick={() => {
                              if (team.member_count === 1) {
                                if (window.confirm('Disbanding this team will also delete all files associated with it. Are you sure you want to continue?')) {
                                  handleDisbandTeam(team.id, team.name);
                                }
                              } else if (team.file_count > 0) {
                                window.alert('You must delete or move all files before disbanding a team with multiple members.');
                              } else {
                                if (window.confirm('Are you sure you want to disband this team?')) {
                                  handleDisbandTeam(team.id, team.name);
                                }
                              }
                            }}
                          >
                            {isDisbanding ? 'Disbanding...' : 'Disband Team'}
                          </Button>
                        )}
                      </CardContent>
                    </Card>
                  ))}
                </div>
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
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setNewTeamName(e.target.value)}
                  placeholder="Enter team name"
                  maxLength={100}
                />
                </div>
                <div className="space-y-2">
                <Label htmlFor="team-description">Description (Optional)</Label>
                <Textarea
                  id="team-description"
                  value={newTeamDescription}
                  onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setNewTeamDescription(e.target.value)}
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
              <div className="text-center py-6">
                <UserPlus className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">Join a Team</h3>
                <p className="text-sm text-muted-foreground mb-6">
                  Enter an invite code to join a team.
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="invite-code">Invite Code</Label>
                <Input
                  id="invite-code"
                  value={joinTeamCode}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setJoinTeamCode(e.target.value.toUpperCase())}
                  placeholder="Enter invite code"
                  maxLength={12}
                  className="font-mono uppercase"
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      handleJoinByCode();
                    }
                  }}
                />
                <p className="text-xs text-muted-foreground">
                  Ask a team admin for an invite code to join their team.
                </p>
              </div>

              <Button
                onClick={handleJoinByCode}
                disabled={isJoining || !joinTeamCode.trim()}
                className="w-full"
              >
                {isJoining ? (
                  <>Joining...</>
                ) : (
                  <>
                    <UserPlus className="h-4 w-4 mr-2" />
                    Join Team
                  </>
                )}
              </Button>
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
                {teamUsers.map((teamUser) => {
                  const isCurrentUser = teamUser.id === Number(user?.id);
                  return (
                    <div key={teamUser.id} className="flex items-center justify-between">
                      <span>
                        {teamUser.name}
                        {isCurrentUser && (
                          <span className="ml-2 text-sm text-muted-foreground">(you)</span>
                        )}
                      </span>
                      {!isCurrentUser && (
                        <Button
                          variant="destructive"
                          size="sm"
                          onClick={() => handleKickUser(teamUser.id)}
                        >
                          <X className="h-4 w-4" />
                          Kick
                        </Button>
                      )}
                    </div>
                  );
                })}
              </div>
            </DialogContent>
          </Dialog>
        )}
      </DialogContent>
    </Dialog>
  );
}
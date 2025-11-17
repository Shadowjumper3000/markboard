import { Header } from '@/components/layout/Header';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table';
import { useToast } from '@/hooks/use-toast';
import { apiService } from '@/lib/api';
import { Activity, Clock, FileText, Search, TrendingUp, Users, UserPlus, Building } from 'lucide-react';
import { useEffect, useState } from 'react';

interface User {
  id: number;
  email: string;
  is_admin: boolean;
  file_count: number;
  team_count: number;
  status: string;
  last_active: string;
  created_at: string;
  last_login: string | null;
}

interface Team {
  id: number;
  name: string;
  description: string;
  owner_id: number;
  owner_email: string;
  file_count: number;
  member_count: number;
  created_at: string;
}

interface Activity {
  id: number;
  user_id: number;
  action: string;
  resource_type: string;
  resource_id: number | null;
  details: string;
  created_at: string;
  user_email?: string;
}

interface Stats {
  totalUsers: number;
  activeUsers: number;
  totalFiles: number;
  totalTeams: number;
  recentActivity: number;
}

export default function AdminDashboard() {
  const [userSearchQuery, setUserSearchQuery] = useState('');
  const [teamSearchQuery, setTeamSearchQuery] = useState('');
  const [users, setUsers] = useState<User[]>([]);
  const [teams, setTeams] = useState<Team[]>([]);
  const [activities, setActivities] = useState<Activity[]>([]);
  const [stats, setStats] = useState<Stats>({
    totalUsers: 0,
    activeUsers: 0,
    totalFiles: 0,
    totalTeams: 0,
    recentActivity: 0,
  });
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  const filteredUsers = users.filter(user => {
    const emailMatch = user.email.toLowerCase().includes(userSearchQuery.toLowerCase());
    return emailMatch;
  });

  const filteredTeams = teams.filter(team => {
    const nameMatch = team.name.toLowerCase().includes(teamSearchQuery.toLowerCase());
    const ownerMatch = team.owner_email.toLowerCase().includes(teamSearchQuery.toLowerCase());
    return nameMatch || ownerMatch;
  });

  const fetchAdminData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      if (!token) {
        toast({
          title: "Authentication Error",
          description: "Please log in to access admin dashboard.",
          variant: "destructive",
        });
        return;
      }

      // Fetch users, teams, activities, and stats in parallel using API service
      const [usersData, teamsData, activitiesData, statsData] = await Promise.all([
        apiService.getAdminUsers(),
        apiService.getAdminTeams(),
        apiService.getAdminActivity(20),
        apiService.getAdminStats(),
      ]);

      setUsers(usersData.users || []);
      setTeams(teamsData.teams || []);
      setActivities(activitiesData.activities || []);
      setStats({
        totalUsers: statsData.totalUsers || 0,
        activeUsers: statsData.activeUsers || 0,
        totalFiles: statsData.totalFiles || 0,
        totalTeams: statsData.totalTeams || 0,
        recentActivity: statsData.recentActivity || 0,
      });

    } catch (error) {
      console.error('Error fetching admin data:', error);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to load admin dashboard data.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAdminData();
  }, []);

  const getActivityIcon = (action: string) => {
    switch (action) {
      case 'user_created':
        return <UserPlus className="h-4 w-4 text-green-500" />;
      case 'team_created':
        return <Building className="h-4 w-4 text-blue-500" />;
      case 'team_joined':
        return <Users className="h-4 w-4 text-purple-500" />;
      default:
        return <Activity className="h-4 w-4 text-muted-foreground" />;
    }
  };

  const formatActivityMessage = (activity: Activity) => {
    switch (activity.action) {
      case 'user_created':
        return 'User account created';
      case 'team_created':
        return activity.details || 'Created a team';
      case 'team_joined':
        return activity.details || 'Joined a team';
      default:
        return activity.details || activity.action;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="flex flex-col h-screen bg-background">
      <Header />
      
      <main className="flex-1 overflow-auto">
        <div className="container mx-auto p-6 space-y-6">
          {/* Page Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold tracking-tight text-foreground">
                Admin Dashboard
              </h1>
              <p className="text-muted-foreground">
                Monitor users, teams, files, and system activity
              </p>
            </div>
          </div>

          {/* Statistics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="bg-gradient-card border-0 shadow-elegant-md">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Total Users
                </CardTitle>
                <Users className="h-4 w-4 text-primary" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-foreground">{stats.totalUsers}</div>
                <p className="text-xs text-success flex items-center mt-1">
                  <TrendingUp className="h-3 w-3 mr-1" />
                  {stats.activeUsers} active
                </p>
              </CardContent>
            </Card>

            <Card className="bg-gradient-card border-0 shadow-elegant-md">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Total Teams
                </CardTitle>
                <Building className="h-4 w-4 text-primary" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-foreground">{stats.totalTeams}</div>
                <p className="text-xs text-muted-foreground mt-1">
                  Active teams
                </p>
              </CardContent>
            </Card>

            <Card className="bg-gradient-card border-0 shadow-elegant-md">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Total Files
                </CardTitle>
                <FileText className="h-4 w-4 text-primary" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-foreground">{stats.totalFiles}</div>
                <p className="text-xs text-muted-foreground mt-1">
                  Across all users
                </p>
              </CardContent>
            </Card>

            <Card className="bg-gradient-card border-0 shadow-elegant-md">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Recent Activity
                </CardTitle>
                <Activity className="h-4 w-4 text-primary" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-foreground">{stats.recentActivity}</div>
                <p className="text-xs text-success flex items-center mt-1">
                  <TrendingUp className="h-3 w-3 mr-1" />
                  Last 7 days
                </p>
              </CardContent>
            </Card>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Users Table */}
            <Card className="bg-card border-0 shadow-elegant-md lg:col-span-2">
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>User Management</span>
                  <div className="relative w-64">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Search users..."
                      value={userSearchQuery}
                      onChange={(e) => setUserSearchQuery(e.target.value)}
                      className="pl-10 h-9"
                    />
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>User</TableHead>
                      <TableHead>Files</TableHead>
                      <TableHead>Teams</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Last Active</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {loading ? (
                      <TableRow>
                        <TableCell colSpan={5} className="text-center py-8">
                          <div className="text-sm text-muted-foreground">Loading users...</div>
                        </TableCell>
                      </TableRow>
                    ) : filteredUsers.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={5} className="text-center py-8">
                          <div className="text-sm text-muted-foreground">
                            {userSearchQuery ? 'No users match your search.' : 'No users found.'}
                          </div>
                        </TableCell>
                      </TableRow>
                    ) : (
                      filteredUsers.map((user) => (
                        <TableRow key={user.id}>
                          <TableCell>
                            <div className="flex flex-col">
                              <div className="flex items-center gap-2">
                                <span className="font-medium">{user.email}</span>
                                {user.is_admin && (
                                  <Badge variant="secondary" className="text-xs">Admin</Badge>
                                )}
                              </div>
                              <span className="text-xs text-muted-foreground">
                                Joined {formatDate(user.created_at)}
                              </span>
                            </div>
                          </TableCell>
                          <TableCell>
                            <Badge variant="secondary" className="text-xs">
                              {user.file_count}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <Badge variant="secondary" className="text-xs">
                              {user.team_count}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <Badge 
                              variant={user.status === 'active' ? 'default' : 'secondary'}
                              className="capitalize text-xs"
                            >
                              {user.status}
                            </Badge>
                          </TableCell>
                          <TableCell className="text-sm text-muted-foreground">
                            {user.last_active}
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>

            {/* Recent Activity */}
            <Card className="bg-card border-0 shadow-elegant-md">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="h-5 w-5" />
                  Recent Activity
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {loading ? (
                    <div className="text-center py-4">
                      <div className="text-sm text-muted-foreground">Loading activities...</div>
                    </div>
                  ) : activities.length === 0 ? (
                    <div className="text-center py-4">
                      <div className="text-sm text-muted-foreground">No recent activity</div>
                    </div>
                  ) : (
                    activities.map((activity) => (
                    <div key={activity.id} className="flex items-start space-x-3">
                      <div className="mt-1">
                        {getActivityIcon(activity.action)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-foreground">
                          {activity.user_email}
                        </p>
                        <p className="text-sm text-muted-foreground">
                          {formatActivityMessage(activity)}
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">
                          {formatDate(activity.created_at)}
                        </p>
                      </div>
                    </div>
                  )))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Teams Table */}
          <Card className="bg-card border-0 shadow-elegant-md">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Team Management</span>
                <div className="relative w-64">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search teams..."
                    value={teamSearchQuery}
                    onChange={(e) => setTeamSearchQuery(e.target.value)}
                    className="pl-10 h-9"
                  />
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Team</TableHead>
                    <TableHead>Owner</TableHead>
                    <TableHead>Members</TableHead>
                    <TableHead>Files</TableHead>
                    <TableHead>Created</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {loading ? (
                    <TableRow>
                      <TableCell colSpan={5} className="text-center py-8">
                        <div className="text-sm text-muted-foreground">Loading teams...</div>
                      </TableCell>
                    </TableRow>
                  ) : filteredTeams.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={5} className="text-center py-8">
                        <div className="text-sm text-muted-foreground">
                          {teamSearchQuery ? 'No teams match your search.' : 'No teams found.'}
                        </div>
                      </TableCell>
                    </TableRow>
                  ) : (
                    filteredTeams.map((team) => (
                      <TableRow key={team.id}>
                        <TableCell>
                          <div className="flex flex-col">
                            <span className="font-medium">{team.name}</span>
                            {team.description && (
                              <span className="text-sm text-muted-foreground">{team.description}</span>
                            )}
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="text-sm">{team.owner_email}</div>
                        </TableCell>
                        <TableCell>
                          <Badge variant="secondary" className="text-xs">
                            {team.member_count}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Badge variant="secondary" className="text-xs">
                            {team.file_count}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-sm text-muted-foreground">
                          {formatDate(team.created_at)}
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
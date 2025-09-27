import React, { useState } from 'react';
import { Header } from '@/components/layout/Header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Input } from '@/components/ui/input';
import { Users, FileText, Activity, Search, TrendingUp, Clock } from 'lucide-react';

// Mock data for admin dashboard
const mockUsers = [
  {
    id: '1',
    email: 'sarah.chen@example.com',
    name: 'Sarah Chen',
    role: 'user',
    createdAt: '2024-01-15',
    fileCount: 12,
    lastActive: '2 hours ago',
    status: 'active',
  },
  {
    id: '2',
    email: 'mike.johnson@example.com',
    name: 'Mike Johnson',
    role: 'user',
    createdAt: '2024-01-10',
    fileCount: 28,
    lastActive: '1 day ago',
    status: 'active',
  },
  {
    id: '3',
    email: 'alex.rodriguez@example.com',
    name: 'Alex Rodriguez',
    role: 'user',
    createdAt: '2024-01-08',
    fileCount: 15,
    lastActive: '3 days ago',
    status: 'active',
  },
  {
    id: '4',
    email: 'lisa.park@example.com',
    name: 'Lisa Park',
    role: 'user',
    createdAt: '2024-01-05',
    fileCount: 7,
    lastActive: '1 week ago',
    status: 'inactive',
  },
];

const mockRecentActivity = [
  {
    id: '1',
    type: 'file_created',
    user: 'Sarah Chen',
    action: 'created file "New API Documentation.md"',
    timestamp: '2 hours ago',
  },
  {
    id: '2',
    type: 'file_edited',
    user: 'Mike Johnson',
    action: 'edited "System Architecture.md"',
    timestamp: '4 hours ago',
  },
  {
    id: '3',
    type: 'login',
    user: 'Alex Rodriguez',
    action: 'logged into the system',
    timestamp: '6 hours ago',
  },
  {
    id: '4',
    type: 'file_shared',
    user: 'Lisa Park',
    action: 'shared "Component Library.md" with Product Team',
    timestamp: '1 day ago',
  },
];

export default function AdminDashboard() {
  const [searchQuery, setSearchQuery] = useState('');

  const filteredUsers = mockUsers.filter(user =>
    user.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    user.email.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const totalFiles = mockUsers.reduce((sum, user) => sum + user.fileCount, 0);
  const activeUsers = mockUsers.filter(user => user.status === 'active').length;

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'file_created':
        return <FileText className="h-4 w-4 text-green-500" />;
      case 'file_edited':
        return <FileText className="h-4 w-4 text-blue-500" />;
      case 'login':
        return <Activity className="h-4 w-4 text-purple-500" />;
      case 'file_shared':
        return <Users className="h-4 w-4 text-orange-500" />;
      default:
        return <Activity className="h-4 w-4 text-muted-foreground" />;
    }
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
                Monitor user activity and system metrics
              </p>
            </div>
          </div>

          {/* Statistics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card className="bg-gradient-card border-0 shadow-elegant-md">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Total Users
                </CardTitle>
                <Users className="h-4 w-4 text-primary" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-foreground">{mockUsers.length}</div>
                <p className="text-xs text-success flex items-center mt-1">
                  <TrendingUp className="h-3 w-3 mr-1" />
                  {activeUsers} active users
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
                <div className="text-2xl font-bold text-foreground">{totalFiles}</div>
                <p className="text-xs text-muted-foreground mt-1">
                  Across all teams
                </p>
              </CardContent>
            </Card>

            <Card className="bg-gradient-card border-0 shadow-elegant-md">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Activity Score
                </CardTitle>
                <Activity className="h-4 w-4 text-primary" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-foreground">94%</div>
                <p className="text-xs text-success flex items-center mt-1">
                  <TrendingUp className="h-3 w-3 mr-1" />
                  +12% from last week
                </p>
              </CardContent>
            </Card>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Users Table */}
            <Card className="bg-card border-0 shadow-elegant-md">
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>User Management</span>
                  <div className="relative w-64">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Search users..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
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
                      <TableHead>Status</TableHead>
                      <TableHead>Last Active</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredUsers.map((user) => (
                      <TableRow key={user.id}>
                        <TableCell>
                          <div className="flex flex-col">
                            <span className="font-medium">{user.name}</span>
                            <span className="text-sm text-muted-foreground">{user.email}</span>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant="secondary" className="text-xs">
                            {user.fileCount}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Badge 
                            variant={user.status === 'active' ? 'default' : 'secondary'}
                            className="capitalize"
                          >
                            {user.status}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-sm text-muted-foreground">
                          {user.lastActive}
                        </TableCell>
                      </TableRow>
                    ))}
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
                  {mockRecentActivity.map((activity) => (
                    <div key={activity.id} className="flex items-start space-x-3">
                      <div className="mt-1">
                        {getActivityIcon(activity.type)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-foreground">
                          {activity.user}
                        </p>
                        <p className="text-sm text-muted-foreground">
                          {activity.action}
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">
                          {activity.timestamp}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}
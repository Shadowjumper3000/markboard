export interface Team {
  id: number;
  name: string;
  description: string;
  owner_id: number;
  file_count?: number;
  member_count?: number;
  role?: string;
  created_at: string;
}

export interface User {
  id: number;
  email: string;
  is_admin: boolean;
  created_at: string;
  last_login: string | null;
}

export interface FileItem {
  id: string;
  name: string;
  content?: string;
  team: string;
  team_id?: number;
  team_name?: string;
  lastModified: string;
  created_at?: string;
  updated_at?: string;
  starred: boolean;
  type: 'personal' | 'team';
}
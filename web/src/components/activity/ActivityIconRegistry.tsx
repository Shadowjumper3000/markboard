/**
 * Activity icon registry - follows Open/Closed Principle
 * New activity types can be added without modifying existing code
 */

import { FileText, Users, Shield, Trash2, Edit, Plus, UserPlus, UserMinus, type LucideIcon } from 'lucide-react';

export interface ActivityIconConfig {
  icon: LucideIcon;
  color: string;
  bgColor?: string;
}

export const ACTIVITY_ICONS: Record<string, ActivityIconConfig> = {
  // File operations
  file_created: {
    icon: FileText,
    color: 'text-green-500',
    bgColor: 'bg-green-50'
  },
  file_edited: {
    icon: Edit,
    color: 'text-blue-500',
    bgColor: 'bg-blue-50'
  },
  file_deleted: {
    icon: Trash2,
    color: 'text-red-500',
    bgColor: 'bg-red-50'
  },
  file_viewed: {
    icon: FileText,
    color: 'text-gray-500',
    bgColor: 'bg-gray-50'
  },

  // Team operations
  team_created: {
    icon: Plus,
    color: 'text-green-500',
    bgColor: 'bg-green-50'
  },
  team_joined: {
    icon: UserPlus,
    color: 'text-blue-500',
    bgColor: 'bg-blue-50'
  },
  team_left: {
    icon: UserMinus,
    color: 'text-orange-500',
    bgColor: 'bg-orange-50'
  },
  team_deleted: {
    icon: Trash2,
    color: 'text-red-500',
    bgColor: 'bg-red-50'
  },

  // User operations
  user_login: {
    icon: Shield,
    color: 'text-green-500',
    bgColor: 'bg-green-50'
  },
  user_logout: {
    icon: Shield,
    color: 'text-gray-500',
    bgColor: 'bg-gray-50'
  },
  user_registered: {
    icon: UserPlus,
    color: 'text-green-500',
    bgColor: 'bg-green-50'
  },

  // Admin operations
  admin_action: {
    icon: Shield,
    color: 'text-purple-500',
    bgColor: 'bg-purple-50'
  },
};

// Default icon for unknown activity types
export const DEFAULT_ACTIVITY_ICON: ActivityIconConfig = {
  icon: FileText,
  color: 'text-gray-400',
  bgColor: 'bg-gray-50'
};

/**
 * Get icon configuration for an activity type
 * @param activityType - The type of activity
 * @returns Icon configuration with fallback to default
 */
export function getActivityIcon(activityType: string): ActivityIconConfig {
  return ACTIVITY_ICONS[activityType] || DEFAULT_ACTIVITY_ICON;
}

/**
 * Register a new activity icon type
 * @param activityType - The activity type identifier
 * @param config - The icon configuration
 */
export function registerActivityIcon(activityType: string, config: ActivityIconConfig): void {
  ACTIVITY_ICONS[activityType] = config;
}
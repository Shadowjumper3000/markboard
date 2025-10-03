/**
 * File formatting utilities - follows Single Responsibility Principle
 */

import { TIME_CONSTANTS } from '@/constants';

export interface BackendFile {
  id: number;
  name: string;
  file_size: number;
  size_formatted: string;
  mime_type: string;
  owner_id: number;
  team_id: number | null;
  created_at: string;
  updated_at: string;
}

export interface FileItem {
  id: number;
  name: string;
  size: string;
  lastModified: string;
  type: string;
  owner_id: number;
  team_id: number | null;
}

/**
 * Convert backend file format to frontend FileItem format
 */
export function convertBackendFileToFileItem(file: BackendFile): FileItem {
  // Calculate time difference for lastModified
  const updatedAt = new Date(file.updated_at);
  const now = new Date();
  const diffMs = now.getTime() - updatedAt.getTime();
  
  let lastModified: string;
  
  if (diffMs < TIME_CONSTANTS.MINUTE_MS) {
    lastModified = 'Just now';
  } else if (diffMs < TIME_CONSTANTS.HOUR_MS) {
    const minutes = Math.floor(diffMs / TIME_CONSTANTS.MINUTE_MS);
    lastModified = `${minutes} minute${minutes !== 1 ? 's' : ''} ago`;
  } else if (diffMs < TIME_CONSTANTS.DAY_MS) {
    const hours = Math.floor(diffMs / TIME_CONSTANTS.HOUR_MS);
    lastModified = `${hours} hour${hours !== 1 ? 's' : ''} ago`;
  } else if (diffMs < TIME_CONSTANTS.WEEK_MS) {
    const days = Math.floor(diffMs / TIME_CONSTANTS.DAY_MS);
    lastModified = `${days} day${days !== 1 ? 's' : ''} ago`;
  } else {
    // Format as date for older files
    lastModified = updatedAt.toLocaleDateString();
  }

  return {
    id: file.id,
    name: formatDisplayName(file.name),
    size: file.size_formatted,
    lastModified,
    type: file.mime_type,
    owner_id: file.owner_id,
    team_id: file.team_id,
  };
}

/**
 * Convert multiple backend files to FileItems
 */
export function convertBackendFilesToFileItems(files: BackendFile[]): FileItem[] {
  return files.map(convertBackendFileToFileItem);
}

/**
 * Format display name by removing .md extension
 */
export function formatDisplayName(fileName: string): string {
  if (fileName.toLowerCase().endsWith('.md')) {
    return fileName.slice(0, -3);
  }
  return fileName;
}
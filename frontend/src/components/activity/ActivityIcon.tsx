/**
 * Activity icon component that uses the registry
 */

import React from 'react';
import { getActivityIcon } from './ActivityIconRegistry';

interface ActivityIconProps {
  activityType: string;
  size?: 'sm' | 'md' | 'lg';
  showBackground?: boolean;
  className?: string;
}

const sizeClasses = {
  sm: 'h-3 w-3',
  md: 'h-4 w-4', 
  lg: 'h-5 w-5'
};

export function ActivityIcon({ 
  activityType, 
  size = 'md', 
  showBackground = false,
  className = '' 
}: ActivityIconProps) {
  const config = getActivityIcon(activityType);
  const IconComponent = config.icon;
  
  const iconClasses = `${sizeClasses[size]} ${config.color} ${className}`;
  
  if (showBackground) {
    return (
      <div className={`p-2 rounded-full ${config.bgColor || 'bg-gray-50'}`}>
        <IconComponent className={iconClasses} />
      </div>
    );
  }
  
  return <IconComponent className={iconClasses} />;
}
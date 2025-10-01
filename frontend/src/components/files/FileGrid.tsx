import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Download, MoreHorizontal, Star, Trash2 } from 'lucide-react';

export interface FileItem {
  id: string;
  name: string;
  team: string;
  lastModified: string;
  starred: boolean;
  type: 'personal' | 'team';
}

interface FileGridProps {
  files: FileItem[];
  onFileSelect: (fileId: string) => void;
  onFileDelete: (fileId: string) => void;
  onFileToggleStar: (fileId: string) => void;
}

export function FileGrid({ files, onFileSelect, onFileDelete, onFileToggleStar }: FileGridProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {files.map((file) => (
        <Card 
          key={file.id}
          className="group hover:shadow-elegant-md transition-smooth cursor-pointer bg-gradient-card border-0"
          onClick={() => onFileSelect(file.id)}
        >
          <CardContent className="p-6">
            {/* File Header */}
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center space-x-2">
                {file.starred && (
                  <Star className="h-4 w-4 text-yellow-500 fill-current" />
                )}
              </div>
              
              <DropdownMenu>
                <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="opacity-0 group-hover:opacity-100 transition-fast hover:bg-accent"
                  >
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  {/* Removed Edit Option */}
                  <DropdownMenuItem onClick={(e) => {
                    e.stopPropagation();
                    onFileToggleStar(file.id);
                  }}>
                    <Star className="mr-2 h-4 w-4" />
                    {file.starred ? 'Unstar' : 'Star'}
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={(e) => e.stopPropagation()}>
                    <Download className="mr-2 h-4 w-4" />
                    Download
                  </DropdownMenuItem>
                  <DropdownMenuItem 
                    className="text-destructive focus:text-destructive"
                    onClick={(e) => {
                      e.stopPropagation();
                      onFileDelete(file.id);
                    }}
                  >
                    <Trash2 className="mr-2 h-4 w-4" />
                    Delete
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>

            {/* File Info */}
            <div className="space-y-3">
              <div>
                <h3 className="font-semibold text-foreground line-clamp-1 mb-1">
                  {file.name}
                </h3>
                <div className="flex items-center space-x-2">
                  <Badge 
                    variant={file.type === 'team' ? 'default' : 'secondary'}
                    className="text-xs"
                  >
                    {file.team}
                  </Badge>
                </div>
              </div>

              <div className="text-xs text-muted-foreground">
                Modified {file.lastModified}
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
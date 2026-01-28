import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useToast } from '@/hooks/use-toast';
import { useFileDownload } from '@/hooks/useFileDownload';
import { apiService } from '@/lib/api';
import { FileItem } from '@/types';
import { Download, Edit, FileImage, FileText as FileTextIcon, MoreHorizontal, Star, Trash2 } from 'lucide-react';
import React from 'react';

interface FileGridProps {
  files: FileItem[];
  onFileSelect: (fileId: string) => void;
  onFileDelete: (fileId: string) => void;
  onFileToggleStar: (fileId: string) => void;
}

export function FileGrid({ files, onFileSelect, onFileDelete, onFileToggleStar }: FileGridProps) {
  const { toast } = useToast();
  const { downloadMd, downloadPng } = useFileDownload();

  const handleDownloadMd = async (file: FileItem, e: MouseEvent) => {
    await downloadMd(file, e);
  };

  const handleDownloadPng = async (file: FileItem, e: MouseEvent) => {
    await downloadPng(file, e);
  };

  const handleDownloadBoth = async (file: FileItem, e: MouseEvent) => {
    e.stopPropagation();
    // Download MD file
    await downloadMd(file, e);
    
    // Download PNG file with a small delay
    setTimeout(() => {
      downloadPng(file, e);
    }, 500);
  };

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
                  <DropdownMenuSeparator />
                  
                  <DropdownMenuSub>
                    <DropdownMenuSubTrigger>
                      <Download className="mr-2 h-4 w-4" />
                      Download
                    </DropdownMenuSubTrigger>
                    <DropdownMenuSubContent>
                      <DropdownMenuItem onClick={(e) => handleDownloadMd(file, e)}>
                        <FileTextIcon className="mr-2 h-4 w-4" />
                        Download as .md
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={(e) => handleDownloadPng(file, e)}>
                        <FileImage className="mr-2 h-4 w-4" />
                        Download as .png
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem onClick={(e) => handleDownloadBoth(file, e)}>
                        <Download className="mr-2 h-4 w-4" />
                        Download both formats
                      </DropdownMenuItem>
                    </DropdownMenuSubContent>
                  </DropdownMenuSub>

                  <DropdownMenuSeparator />

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
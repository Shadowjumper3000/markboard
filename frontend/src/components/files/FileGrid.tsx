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
import { apiService } from '@/lib/api';
import { renderMermaidToPng } from '@/lib/mermaidToPng';
import { Download, Edit, FileImage, FileText as FileTextIcon, MoreHorizontal, Star, Trash2 } from 'lucide-react';
import React from 'react';

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
  const { toast } = useToast();

  const handleDownloadMd = async (file: FileItem, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      // Fetch file content
      const fileData = await apiService.getFile(file.id);
      const blob = new Blob([fileData.content], { type: 'text/markdown' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = fileData.name;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      toast({
        title: "Markdown downloaded",
        description: `${fileData.name} has been downloaded to your computer.`,
      });
    } catch (error) {
      console.error('Error downloading file:', error);
      toast({
        variant: "destructive",
        title: "Download failed",
        description: "Unable to download the file. Please try again.",
      });
    }
  };

  const handleDownloadPng = async (file: FileItem, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      // Fetch file content and render as PNG
      const fileData = await apiService.getFile(file.id);
      const pngBlob = await renderMermaidToPng(fileData.content);
      if (pngBlob) {
        const url = URL.createObjectURL(pngBlob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${fileData.name.replace('.md', '.png')}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        toast({
          title: "PNG downloaded",
          description: `${fileData.name.replace('.md', '.png')} has been downloaded to your computer.`,
        });
      } else {
        toast({
          variant: "destructive",
          title: "Download failed",
          description: "No Mermaid diagrams found to export as PNG.",
        });
      }
    } catch (error) {
      console.error('Error downloading PNG:', error);
      toast({
        variant: "destructive",
        title: "Download failed",
        description: "Unable to generate PNG from diagrams.",
      });
    }
  };

  const handleDownloadBoth = async (file: FileItem, e: React.MouseEvent) => {
    e.stopPropagation();
    // Download MD file
    await handleDownloadMd(file, e);
    
    // Download PNG file with a small delay
    setTimeout(() => {
      handleDownloadPng(file, e);
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
                  <DropdownMenuItem onClick={(e) => {
                    e.stopPropagation();
                    onFileSelect(file.id);
                  }}>
                    <Edit className="mr-2 h-4 w-4" />
                    Edit
                  </DropdownMenuItem>
                  {/* Star/Unstar removed from dropdown */}
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
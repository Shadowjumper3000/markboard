import React from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
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
import { Download, Edit, FileImage, FileText as FileTextIcon, MoreHorizontal, Trash2 } from 'lucide-react';
import { FileItem } from './FileGrid';
import { apiService } from '@/lib/api';
import { renderMermaidToPng } from '@/lib/mermaidToPng';
import { useToast } from '@/hooks/use-toast';

interface FileListProps {
  files: FileItem[];
  onFileSelect: (id: string) => void;
  onFileDelete: (id: string) => void;
}

export function FileList({ files, onFileSelect, onFileDelete }: FileListProps) {
  const { toast } = useToast();

  const handleDownloadMd = async (file: FileItem, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
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
    await handleDownloadMd(file, e);
    setTimeout(() => {
      handleDownloadPng(file, e);
    }, 500);
  };

  return (
    <div className="divide-y rounded-lg border bg-card">
      {files.map((file) => (
        <div
          key={file.id}
          className="flex items-center justify-between px-4 py-3 hover:bg-accent cursor-pointer transition"
          onClick={() => onFileSelect(file.id)}
        >
          <div className="flex items-center gap-3 min-w-0">
            <FileTextIcon className="h-5 w-5 text-muted-foreground" />
            <span className="truncate font-medium">{file.name}</span>
            <Badge variant={file.type === 'team' ? 'default' : 'secondary'} className="text-xs">
              {file.team}
            </Badge>
            <span className="text-xs text-muted-foreground ml-2 truncate">{file.lastModified}</span>
          </div>
          <div className="flex items-center gap-2">
            <DropdownMenu>
              <DropdownMenuTrigger asChild onClick={e => e.stopPropagation()}>
                <Button variant="ghost" size="icon">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={e => {
                  e.stopPropagation();
                  onFileSelect(file.id);
                }}>
                  <Edit className="mr-2 h-4 w-4" />
                  Edit
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuSub>
                  <DropdownMenuSubTrigger>
                    <Download className="mr-2 h-4 w-4" />
                    Download
                  </DropdownMenuSubTrigger>
                  <DropdownMenuSubContent>
                    <DropdownMenuItem onClick={e => handleDownloadMd(file, e)}>
                      <FileTextIcon className="mr-2 h-4 w-4" />
                      Download as .md
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={e => handleDownloadPng(file, e)}>
                      <FileImage className="mr-2 h-4 w-4" />
                      Download as .png
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem onClick={e => handleDownloadBoth(file, e)}>
                      <Download className="mr-2 h-4 w-4" />
                      Download both formats
                    </DropdownMenuItem>
                  </DropdownMenuSubContent>
                </DropdownMenuSub>
                <DropdownMenuSeparator />
                <DropdownMenuItem className="text-destructive focus:text-destructive" onClick={e => {
                  e.stopPropagation();
                  onFileDelete(file.id);
                }}>
                  <Trash2 className="mr-2 h-4 w-4" />
                  Delete
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      ))}
    </div>
  );
}

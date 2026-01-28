import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
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
import { FileItem } from '@/types';
import { Download, Edit, FileImage, FileText as FileTextIcon, MoreHorizontal, Trash2 } from 'lucide-react';
import React from 'react';

interface FileListProps {
  files: FileItem[];
  onFileSelect: (id: string) => void;
  onFileDelete: (id: string) => void;
  onFileToggleStar: (id: string) => void;
}

export function FileList({ files, onFileSelect, onFileDelete, onFileToggleStar }: FileListProps) {
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
    await downloadMd(file, e);
    setTimeout(() => {
      downloadPng(file, e);
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

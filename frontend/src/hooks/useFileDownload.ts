import { useToast } from './use-toast';
import { FileItem } from '@/types';
import { renderMermaidToPng } from '@/lib/mermaidToPng';

export function useFileDownload() {
  const { toast } = useToast();

  const downloadMd = async (file: FileItem, e?: MouseEvent) => {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }

    try {
      // If file doesn't have content, fetch it from API
      let content = file.content;
      let fileName = file.name;
      
      if (!content) {
        const { apiService } = await import('@/lib/api');
        const fileData = await apiService.getFile(file.id);
        content = fileData.content;
        fileName = fileData.name;
      }

      const blob = new Blob([content], { type: 'text/markdown' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = fileName.endsWith('.md') ? fileName : `${fileName}.md`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      toast({
        title: "Download successful",
        description: `${fileName} has been downloaded`,
      });
    } catch (error) {
      console.error('Download failed:', error);
      toast({
        title: "Download failed",
        description: "There was an error downloading the file",
        variant: "destructive",
      });
    }
  };

  const downloadPng = async (file: FileItem, e?: MouseEvent) => {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }

    try {
      toast({
        title: "Generating PNG...",
        description: "Please wait while we generate your diagram",
      });

      // If file doesn't have content, fetch it from API
      let content = file.content;
      let fileName = file.name;
      
      if (!content) {
        const { apiService } = await import('@/lib/api');
        const fileData = await apiService.getFile(file.id);
        content = fileData.content;
        fileName = fileData.name;
      }

      const pngBlob = await renderMermaidToPng(content);
      const url = URL.createObjectURL(pngBlob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${fileName.replace('.md', '')}.png`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      toast({
        title: "Download successful",
        description: `${fileName.replace('.md', '')}.png has been downloaded`,
      });
    } catch (error) {
      console.error('PNG generation failed:', error);
      toast({
        title: "PNG generation failed",
        description: "There was an error generating the PNG file",
        variant: "destructive",
      });
    }
  };

  return { downloadMd, downloadPng };
}
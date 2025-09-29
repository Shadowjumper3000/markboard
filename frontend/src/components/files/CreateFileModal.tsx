import { Button } from '@/components/ui/button';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Textarea } from '@/components/ui/textarea';
import { useToast } from '@/hooks/use-toast';
import { apiService } from '@/lib/api';
import { FileText, Upload, User, Users } from 'lucide-react';
import React, { useState } from 'react';

interface Team {
  id: number;
  name: string;
  description: string;
  owner_id: number;
  file_count?: number;
}

interface CreateFileModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  teams: Team[];
}

export function CreateFileModal({ isOpen, onClose, onSuccess, teams }: CreateFileModalProps) {
  const [activeTab, setActiveTab] = useState<'new' | 'upload'>('new');
  const [fileName, setFileName] = useState('');
  const [fileContent, setFileContent] = useState('');
  const [selectedTeam, setSelectedTeam] = useState<string>('personal');
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const handleClose = () => {
    // Reset form state
    setActiveTab('new');
    setFileName('');
    setFileContent('');
    setSelectedTeam('personal');
    setUploadFile(null);
    setIsLoading(false);
    onClose();
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Validate file type (only markdown files)
      if (!file.name.toLowerCase().endsWith('.md')) {
        toast({
          title: 'Invalid file type',
          description: 'Please upload a .md (Markdown) file.',
          variant: 'destructive',
        });
        return;
      }

      setUploadFile(file);
      setFileName(file.name);

      // Read file content
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target?.result as string;
        setFileContent(content);
      };
      reader.readAsText(file);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!fileName.trim()) {
      toast({
        title: 'File name required',
        description: 'Please enter a file name.',
        variant: 'destructive',
      });
      return;
    }

    setIsLoading(true);

    try {
      // Ensure .md extension
      let finalFileName = fileName.trim();
      if (!finalFileName.toLowerCase().endsWith('.md')) {
        finalFileName += '.md';
      }

      const data: {
        name: string;
        content?: string;
        team_id?: number;
      } = {
        name: finalFileName,
        content: fileContent || '# ' + finalFileName.replace('.md', '') + '\n\nStart writing your content here...',
      };

      // Add team_id if not personal
      if (selectedTeam !== 'personal') {
        data.team_id = parseInt(selectedTeam);
      }

      await apiService.createFile(data);

      toast({
        title: 'File created',
        description: `${finalFileName} has been created successfully.`,
      });

      onSuccess();
      handleClose();
    } catch (error) {
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Failed to create file.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Create New File
          </DialogTitle>
          <DialogDescription>
            Create a new markdown file or upload an existing one.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit}>
          <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as 'new' | 'upload')}>
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="new" className="flex items-center gap-2">
                <FileText className="h-4 w-4" />
                New File
              </TabsTrigger>
              <TabsTrigger value="upload" className="flex items-center gap-2">
                <Upload className="h-4 w-4" />
                Upload File
              </TabsTrigger>
            </TabsList>

            <div className="space-y-4 mt-4">
              {/* Team Selection */}
              <div className="space-y-2">
                <Label htmlFor="team-select">Location</Label>
                <Select value={selectedTeam} onValueChange={setSelectedTeam}>
                  <SelectTrigger id="team-select">
                    <SelectValue placeholder="Select location" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="personal">
                      <div className="flex items-center gap-2">
                        <User className="h-4 w-4" />
                        Personal Files
                      </div>
                    </SelectItem>
                    {teams.map((team) => (
                      <SelectItem key={team.id} value={team.id.toString()}>
                        <div className="flex items-center gap-2">
                          <Users className="h-4 w-4" />
                          {team.name}
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <TabsContent value="new" className="space-y-4 mt-0">
                <div className="space-y-2">
                  <Label htmlFor="file-name">File Name</Label>
                  <Input
                    id="file-name"
                    placeholder="Enter file name (e.g., 'My Document')"
                    value={fileName}
                    onChange={(e) => setFileName(e.target.value)}
                    disabled={isLoading}
                  />
                  <p className="text-sm text-muted-foreground">
                    .md extension will be added automatically
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="file-content">Initial Content (Optional)</Label>
                  <Textarea
                    id="file-content"
                    placeholder="Enter initial markdown content..."
                    value={fileContent}
                    onChange={(e) => setFileContent(e.target.value)}
                    rows={6}
                    disabled={isLoading}
                  />
                </div>
              </TabsContent>

              <TabsContent value="upload" className="space-y-4 mt-0">
                <div className="space-y-2">
                  <Label htmlFor="file-upload">Upload Markdown File</Label>
                  <Input
                    id="file-upload"
                    type="file"
                    accept=".md"
                    onChange={handleFileUpload}
                    disabled={isLoading}
                  />
                  <p className="text-sm text-muted-foreground">
                    Only .md (Markdown) files are supported
                  </p>
                </div>

                {uploadFile && (
                  <div className="space-y-2">
                    <Label htmlFor="uploaded-file-name">File Name</Label>
                    <Input
                      id="uploaded-file-name"
                      value={fileName}
                      onChange={(e) => setFileName(e.target.value)}
                      disabled={isLoading}
                    />
                  </div>
                )}

                {uploadFile && fileContent && (
                  <div className="space-y-2">
                    <Label>File Preview</Label>
                    <Textarea
                      value={fileContent}
                      onChange={(e) => setFileContent(e.target.value)}
                      rows={6}
                      disabled={isLoading}
                    />
                  </div>
                )}
              </TabsContent>
            </div>
          </Tabs>

          <DialogFooter className="mt-6">
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading || !fileName.trim()}>
              {isLoading ? 'Creating...' : 'Create File'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
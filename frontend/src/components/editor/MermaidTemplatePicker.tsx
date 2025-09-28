import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
    Command,
    CommandEmpty,
    CommandGroup,
    CommandInput,
    CommandItem,
} from '@/components/ui/command';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from '@/components/ui/dialog';
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from '@/components/ui/popover';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
    BarChart3,
    Database,
    FileText,
    GitBranch,
    Map,
    PieChart,
    Users,
    Workflow,
    Zap
} from 'lucide-react';
import React, { useState } from 'react';
import { MERMAID_TEMPLATES, MermaidTemplate } from './MermaidTemplates';

interface MermaidTemplatePickerProps {
  onTemplateSelect: (template: MermaidTemplate) => void;
  trigger?: React.ReactNode;
}

const CATEGORY_ICONS = {
  sequence: Users,
  flowchart: Workflow,
  erd: Database,
  class: FileText,
  state: GitBranch,
  gantt: BarChart3,
  pie: PieChart,
  journey: Map
};

const CATEGORY_NAMES = {
  sequence: 'Sequence Diagrams',
  flowchart: 'Flowcharts',
  erd: 'Entity Relationship',
  class: 'Class Diagrams',
  state: 'State Diagrams',
  gantt: 'Gantt Charts',
  pie: 'Pie Charts',
  journey: 'User Journey'
};

export function MermaidTemplatePicker({ onTemplateSelect, trigger }: MermaidTemplatePickerProps) {
  const [open, setOpen] = useState(false);
  const [previewTemplate, setPreviewTemplate] = useState<MermaidTemplate | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  const handleTemplateSelect = (template: MermaidTemplate) => {
    onTemplateSelect(template);
    setOpen(false);
  };

  const categorizedTemplates = MERMAID_TEMPLATES.reduce((acc, template) => {
    if (!acc[template.category]) {
      acc[template.category] = [];
    }
    acc[template.category].push(template);
    return acc;
  }, {} as Record<string, MermaidTemplate[]>);

  const filteredTemplates = selectedCategory === 'all' 
    ? MERMAID_TEMPLATES 
    : categorizedTemplates[selectedCategory] || [];

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || (
          <Button variant="outline" size="sm">
            <Zap className="h-4 w-4 mr-2" />
            Insert Template
          </Button>
        )}
      </DialogTrigger>
      
      <DialogContent className="max-w-6xl h-[80vh] flex flex-col">
        <DialogHeader>
          <DialogTitle>Mermaid Diagram Templates</DialogTitle>
          <DialogDescription>
            Choose from pre-built templates to quickly create diagrams
          </DialogDescription>
        </DialogHeader>

        <div className="flex-1 flex gap-6 overflow-hidden">
          {/* Template Selection */}
          <div className="w-1/2 flex flex-col">
            <Tabs value={selectedCategory} onValueChange={setSelectedCategory} className="flex-1 flex flex-col">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="all">All</TabsTrigger>
                <TabsTrigger value="sequence">Sequence</TabsTrigger>
                <TabsTrigger value="flowchart">Flow</TabsTrigger>
                <TabsTrigger value="erd">ERD</TabsTrigger>
              </TabsList>
              
              <div className="flex-1 mt-4">
                <ScrollArea className="h-full">
                  <div className="space-y-2">
                    {filteredTemplates.map((template) => {
                      const IconComponent = CATEGORY_ICONS[template.category];
                      return (
                        <div
                          key={template.id}
                          className={`p-3 border rounded-lg cursor-pointer transition-colors hover:bg-accent ${
                            previewTemplate?.id === template.id ? 'border-primary bg-accent' : ''
                          }`}
                          onClick={() => setPreviewTemplate(template)}
                        >
                          <div className="flex items-start justify-between mb-2">
                            <div className="flex items-center gap-2">
                              <IconComponent className="h-4 w-4 text-muted-foreground" />
                              <h4 className="font-medium text-sm">{template.name}</h4>
                            </div>
                            <Badge variant="secondary" className="text-xs">
                              {template.category}
                            </Badge>
                          </div>
                          <p className="text-xs text-muted-foreground">{template.description}</p>
                        </div>
                      );
                    })}
                  </div>
                </ScrollArea>
              </div>
            </Tabs>
          </div>

          {/* Template Preview */}
          <div className="w-1/2 flex flex-col">
            {previewTemplate ? (
              <div className="flex-1 flex flex-col">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="font-semibold">{previewTemplate.name}</h3>
                    <p className="text-sm text-muted-foreground">{previewTemplate.description}</p>
                  </div>
                  <Button onClick={() => handleTemplateSelect(previewTemplate)}>
                    Use Template
                  </Button>
                </div>
                
                <div className="flex-1 border rounded-lg overflow-hidden">
                  <ScrollArea className="h-full">
                    <div className="p-4">
                      <pre className="text-xs text-muted-foreground whitespace-pre-wrap font-mono">
                        {previewTemplate.insertText}
                      </pre>
                    </div>
                  </ScrollArea>
                </div>
              </div>
            ) : (
              <div className="flex-1 flex items-center justify-center border rounded-lg border-dashed">
                <div className="text-center text-muted-foreground">
                  <FileText className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p>Select a template to preview</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

// Quick access popover for commonly used templates
export function QuickTemplatePopover({ onTemplateSelect }: { onTemplateSelect: (template: MermaidTemplate) => void }) {
  const [open, setOpen] = useState(false);

  const quickTemplates = MERMAID_TEMPLATES.filter(t => 
    ['seq-basic', 'flow-basic', 'erd-basic'].includes(t.id)
  );

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button variant="ghost" size="sm">
          <Zap className="h-4 w-4 mr-2" />
          Quick Templates
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-80" align="start">
        <Command>
          <CommandInput placeholder="Search templates..." />
          <CommandEmpty>No templates found.</CommandEmpty>
          <CommandGroup heading="Quick Templates">
            {quickTemplates.map((template) => {
              const IconComponent = CATEGORY_ICONS[template.category];
              return (
                <CommandItem
                  key={template.id}
                  onSelect={() => {
                    onTemplateSelect(template);
                    setOpen(false);
                  }}
                >
                  <IconComponent className="mr-2 h-4 w-4" />
                  <div className="flex flex-col">
                    <span className="font-medium">{template.name}</span>
                    <span className="text-xs text-muted-foreground">{template.description}</span>
                  </div>
                </CommandItem>
              );
            })}
          </CommandGroup>
          <CommandGroup heading="All Templates">
            <CommandItem
              onSelect={() => setOpen(false)}
            >
              <FileText className="mr-2 h-4 w-4" />
              <span>Browse all templates...</span>
            </CommandItem>
          </CommandGroup>
        </Command>
      </PopoverContent>
    </Popover>
  );
}
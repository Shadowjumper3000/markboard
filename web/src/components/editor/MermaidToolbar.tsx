import { MERMAID_TEMPLATES, MermaidTemplate } from './MermaidTemplates';

interface MermaidToolbarProps {
  onTemplateInsert: (template: MermaidTemplate) => void;
}

export function MermaidToolbar({ onTemplateInsert }: MermaidToolbarProps) {
  const quickTemplates = MERMAID_TEMPLATES.filter(t => 
    ['seq-basic', 'flow-basic', 'erd-basic'].includes(t.id)
  );

  const handleTemplateClick = (template: MermaidTemplate) => {
    onTemplateInsert(template);
  };

  return (
    <div className="flex flex-wrap gap-2 p-3 bg-muted/30 border-b">
      <div className="text-sm font-medium text-muted-foreground mr-4">Quick Templates:</div>
      
      {quickTemplates.map((template) => (
        <button
          key={template.id}
          onClick={() => handleTemplateClick(template)}
          className="px-3 py-1 text-xs bg-background border rounded-md hover:bg-accent hover:text-accent-foreground transition-colors"
          title={template.description}
        >
          {template.name}
        </button>
      ))}
      
      <div className="flex-1" />
      
      <details className="relative">
        <summary className="px-3 py-1 text-xs bg-background border rounded-md hover:bg-accent hover:text-accent-foreground cursor-pointer transition-colors">
          All Templates ▼
        </summary>
        <div className="absolute right-0 top-full mt-1 w-80 max-h-96 bg-background border rounded-lg shadow-lg overflow-y-auto z-50">
          <div className="p-2">
            {Object.entries(
              MERMAID_TEMPLATES.reduce((acc, template) => {
                if (!acc[template.category]) acc[template.category] = [];
                acc[template.category].push(template);
                return acc;
              }, {} as Record<string, MermaidTemplate[]>)
            ).map(([category, templates]) => (
              <div key={category} className="mb-3">
                <div className="text-xs font-medium text-muted-foreground mb-1 px-2 capitalize">
                  {category} Diagrams
                </div>
                {templates.map((template) => (
                  <button
                    key={template.id}
                    onClick={() => handleTemplateClick(template)}
                    className="w-full text-left px-2 py-1 text-xs hover:bg-accent hover:text-accent-foreground rounded transition-colors"
                    title={template.description}
                  >
                    {template.name}
                  </button>
                ))}
              </div>
            ))}
          </div>
        </div>
      </details>
    </div>
  );
}

// Autocomplete suggestions data that can be used with Monaco Editor
export const MERMAID_AUTOCOMPLETE_DATA = {
  // Diagram starters
  diagramTypes: [
    {
      label: 'sequence',
      insertText: 'sequenceDiagram\n    participant A as Alice\n    participant B as Bob\n    A->>B: Hello\n    B-->>A: Hi!',
      detail: 'Create a sequence diagram'
    },
    {
      label: 'flowchart-td',
      insertText: 'flowchart TD\n    A[Start] --> B{Decision?}\n    B -->|Yes| C[Action]\n    B -->|No| D[Alternative]\n    C --> E[End]\n    D --> E',
      detail: 'Create a top-down flowchart'
    },
    {
      label: 'flowchart-lr',
      insertText: 'flowchart LR\n    A[Start] --> B[Process] --> C[End]',
      detail: 'Create a left-right flowchart'
    },
    {
      label: 'erd',
      insertText: 'erDiagram\n    USER {\n        int id PK\n        string name\n        string email\n    }\n    ORDER {\n        int id PK\n        int user_id FK\n        decimal total\n    }\n    USER ||--o{ ORDER : places',
      detail: 'Create an entity relationship diagram'
    }
  ],

  // Common keywords
  keywords: {
    sequence: ['participant', 'actor', 'note', 'activate', 'deactivate', 'loop', 'alt', 'else', 'opt', 'par', 'and', 'critical', 'break'],
    flowchart: ['subgraph', 'end', 'click', 'classDef', 'class', 'style', 'linkStyle'],
    erd: ['PK', 'FK', 'UK']
  },

  // Data types for ERD
  dataTypes: ['int', 'string', 'text', 'boolean', 'date', 'timestamp', 'decimal', 'uuid', 'varchar', 'char', 'float', 'double'],

  // Arrow types
  arrows: {
    sequence: ['->', '-->>', '-x', '--x', '-)', '--)', '->>', '-->>'],
    flowchart: ['-->', '---', '-.->','==>', '~~>', '--o', '--x'],
    erd: ['||--o{', '||--||', '}|..|{', '}o--o{', '||..|{', '}|--||']
  },

  // Shape templates for flowcharts
  shapes: [
    { name: 'Rectangle', syntax: 'A[Process]', description: 'Standard process' },
    { name: 'Rounded', syntax: 'A(Start/End)', description: 'Start or end point' },
    { name: 'Stadium', syntax: 'A([Pill Shape])', description: 'Alternative start/end' },
    { name: 'Subroutine', syntax: 'A[[Subroutine]]', description: 'Predefined process' },
    { name: 'Database', syntax: 'A[(Database)]', description: 'Database storage' },
    { name: 'Circle', syntax: 'A((Circle))', description: 'Connector point' },
    { name: 'Diamond', syntax: 'A{Decision?}', description: 'Decision point' },
    { name: 'Hexagon', syntax: 'A{{Preparation}}', description: 'Preparation step' },
    { name: 'Parallelogram', syntax: 'A[/Input-Output/]', description: 'Input or output' },
    { name: 'Trapezoid', syntax: 'A[/Manual Operation\\]', description: 'Manual process' }
  ]
};
import { MERMAID_TEMPLATES, MermaidTemplate } from './MermaidTemplates';

interface MermaidTemplateToolbarProps {
  onTemplateInsert: (template: MermaidTemplate) => void;
}

export function MermaidTemplateToolbar({ onTemplateInsert }: MermaidTemplateToolbarProps) {
  const quickTemplates = MERMAID_TEMPLATES.filter(t => 
    ['seq-basic', 'flow-basic', 'erd-basic'].includes(t.id)
  );

  const allTemplatesByCategory = MERMAID_TEMPLATES.reduce((acc, template) => {
    if (!acc[template.category]) {
      acc[template.category] = [];
    }
    acc[template.category].push(template);
    return acc;
  }, {} as Record<string, MermaidTemplate[]>);

  return (
    <div className="bg-muted/20 border-b p-2">
      <div className="flex items-center gap-2 flex-wrap">
        <span className="text-xs font-medium text-muted-foreground">Templates:</span>
        
        {/* Quick Templates */}
        {quickTemplates.map((template) => (
          <button
            key={template.id}
            onClick={() => onTemplateInsert(template)}
            className="px-2 py-1 text-xs bg-background border rounded hover:bg-accent hover:text-accent-foreground transition-colors"
            title={template.description}
          >
            {template.name}
          </button>
        ))}
        
        {/* Category Dropdowns */}
        <div className="flex gap-1 ml-2">
          {Object.entries(allTemplatesByCategory).map(([category, templates]) => (
            <div key={category} className="relative group">
              <button className="px-2 py-1 text-xs bg-background border rounded hover:bg-accent hover:text-accent-foreground transition-colors capitalize">
                {category} ▼
              </button>
              <div className="absolute top-full left-0 mt-1 w-64 bg-background border rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                <div className="p-2 max-h-80 overflow-y-auto">
                  {templates.map((template) => (
                    <button
                      key={template.id}
                      onClick={() => onTemplateInsert(template)}
                      className="w-full text-left p-2 text-xs hover:bg-accent hover:text-accent-foreground rounded transition-colors block"
                    >
                      <div className="font-medium">{template.name}</div>
                      <div className="text-muted-foreground text-xs mt-1">{template.description}</div>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
        
        {/* Quick Snippets */}
        <div className="flex gap-1 ml-4 border-l pl-4">
          <span className="text-xs font-medium text-muted-foreground">Quick:</span>
          <button
            onClick={() => onTemplateInsert({
              id: 'quick-seq',
              name: 'Quick Sequence',
              description: 'Basic sequence diagram structure',
              category: 'sequence',
              template: '',
              insertText: `\`\`\`mermaid
sequenceDiagram
    participant A
    participant B
    A->>B: Message
    B-->>A: Response
\`\`\``
            })}
            className="px-2 py-1 text-xs bg-blue-50 border border-blue-200 text-blue-700 rounded hover:bg-blue-100 transition-colors"
          >
            Sequence
          </button>
          <button
            onClick={() => onTemplateInsert({
              id: 'quick-flow',
              name: 'Quick Flow',
              description: 'Basic flowchart structure',
              category: 'flowchart',
              template: '',
              insertText: `\`\`\`mermaid
flowchart TD
    A[Start] --> B{Decision?}
    B -->|Yes| C[Action]
    B -->|No| D[End]
    C --> D
\`\`\``
            })}
            className="px-2 py-1 text-xs bg-green-50 border border-green-200 text-green-700 rounded hover:bg-green-100 transition-colors"
          >
            Flow
          </button>
          <button
            onClick={() => onTemplateInsert({
              id: 'quick-erd',
              name: 'Quick ERD',
              description: 'Basic ERD structure',
              category: 'erd',
              template: '',
              insertText: `\`\`\`mermaid
erDiagram
    USER {
        int id PK
        string name
        string email
    }
    ORDER {
        int id PK
        int user_id FK
        decimal total
    }
    USER ||--o{ ORDER : places
\`\`\``
            })}
            className="px-2 py-1 text-xs bg-purple-50 border border-purple-200 text-purple-700 rounded hover:bg-purple-100 transition-colors"
          >
            ERD
          </button>
        </div>
      </div>
    </div>
  );
}
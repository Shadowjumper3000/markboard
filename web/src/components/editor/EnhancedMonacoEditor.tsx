import Editor from '@monaco-editor/react';
import { useEffect, useRef } from 'react';
import { MermaidTemplate } from './MermaidTemplates';

interface EnhancedMonacoEditorProps {
  value: string;
  onChange: (value: string) => void;
  language?: string;
  theme?: string;
  readOnly?: boolean;
  onTemplateInsert?: (template: MermaidTemplate) => void;
}

export function EnhancedMonacoEditor({ 
  value, 
  onChange, 
  language = 'markdown', 
  theme = 'vs-dark',
  readOnly = false,
  onTemplateInsert
}: EnhancedMonacoEditorProps) {
  const editorRef = useRef<any>(null);
  const monacoRef = useRef<any>(null);

  const handleEditorDidMount = (editor: any, monaco: any) => {
    editorRef.current = editor;
    monacoRef.current = monaco;
    
    // Configure Monaco editor for markdown with Mermaid support
    monaco.languages.setMonarchTokensProvider('markdown', {
      tokenizer: {
        root: [
          [/^#+.*$/, 'markup.heading'],
          [/^```mermaid/, 'keyword', '@mermaid'],
          [/^\s*```.*$/, 'markup.code'],
          [/^\s*>.*$/, 'markup.quote'],
          [/^\s*-.*$/, 'markup.list'],
          [/\*\*.*?\*\*/, 'markup.bold'],
          [/\*.*?\*/, 'markup.italic'],
          [/`.*?`/, 'markup.code.inline'],
          [/\[.*?\]\(.*?\)/, 'markup.link'],
        ],
        mermaid: [
          [/```/, 'keyword', '@pop'],
          [/\b(sequenceDiagram|flowchart|erDiagram|classDiagram|stateDiagram|gantt|pie|journey|gitgraph|mindmap|timeline|sankey|xyChart|quadrantChart|requirement|C4Context|C4Container|C4Component|C4Dynamic|C4Deployment)\b/, 'type'],
          [/\b(participant|actor|note|loop|alt|else|opt|par|and|critical|break|rect|autonumber)\b/, 'keyword'],
          [/\b(TD|TB|BT|RL|LR|subgraph|end|click|classDef|linkStyle|style)\b/, 'keyword'],
          [/\b(PK|FK|UK|int|string|text|boolean|date|timestamp|decimal|uuid)\b/, 'type'],
          [/-->|->|-->>|->>|-x|--x|-\)|--\)|==>|~~>|--o|--x|\|\|--o\{|\|\|-\-\|\||}\|\.\.|\{|}\o--o\{|\|\|\.\.|\{|}\|--\|\|/, 'operator'],
          [/\[.*?\]|\(.*?\)|\{.*?\}|<.*?>/, 'string'],
          [/[A-Za-z_][A-Za-z0-9_]*/, 'variable'],
          [/[{}()\[\]]/, 'delimiter'],
          [/[;,.]/, 'delimiter'],
          [/".*?"/, 'string'],
          [/'.*?'/, 'string'],
          [/.*$/, 'comment']
        ]
      }
    });

    // Define Mermaid completion provider
    monaco.languages.registerCompletionItemProvider('markdown', {
      provideCompletionItems: (model: any, position: any) => {
        const word = model.getWordUntilPosition(position);
        const range = {
          startLineNumber: position.lineNumber,
          endLineNumber: position.lineNumber,
          startColumn: word.startColumn,
          endColumn: word.endColumn
        };

        const lineContent = model.getLineContent(position.lineNumber);
        const isInMermaidBlock = checkIfInMermaidBlock(model, position);

        let suggestions: any[] = [];

        if (isInMermaidBlock) {
          // Mermaid-specific completions
          suggestions = getMermaidCompletions(monaco, range, lineContent);
        } else {
          // Markdown completions including mermaid block starters
          suggestions = getMarkdownCompletions(monaco, range);
        }

        return { suggestions };
      }
    });

    // Add command for inserting templates
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyT, () => {
      if (onTemplateInsert) {
        // This would trigger template picker
        console.log('Template insertion triggered');
      }
    });

    // Set editor options
    editor.updateOptions({
      fontSize: 14,
      lineHeight: 22,
      minimap: { enabled: false },
      scrollBeyondLastLine: false,
      wordWrap: 'on',
      lineNumbers: 'on',
      folding: true,
      renderLineHighlight: 'line',
      selectOnLineNumbers: true,
      automaticLayout: true,
      suggestOnTriggerCharacters: true,
      quickSuggestions: {
        other: true,
        comments: false,
        strings: false
      }
    });
  };

  const checkIfInMermaidBlock = (model: any, position: any): boolean => {
    const lineCount = model.getLineCount();
    let inMermaidBlock = false;
    
    for (let i = 1; i <= position.lineNumber; i++) {
      const line = model.getLineContent(i);
      if (line.trim().startsWith('```mermaid')) {
        inMermaidBlock = true;
      } else if (line.trim() === '```' && inMermaidBlock) {
        inMermaidBlock = false;
      }
    }
    
    return inMermaidBlock;
  };

  const getMermaidCompletions = (monaco: any, range: any, lineContent: string) => {
    const suggestions = [];

    // Diagram type completions
    const diagramTypes = [
      { label: 'sequenceDiagram', detail: 'Sequence diagram', insertText: 'sequenceDiagram\n    participant A\n    participant B\n    A->>B: Message' },
      { label: 'flowchart TD', detail: 'Top-down flowchart', insertText: 'flowchart TD\n    A[Start] --> B[End]' },
      { label: 'flowchart LR', detail: 'Left-right flowchart', insertText: 'flowchart LR\n    A[Start] --> B[End]' },
      { label: 'erDiagram', detail: 'Entity relationship diagram', insertText: 'erDiagram\n    ENTITY {\n        int id PK\n        string name\n    }' },
      { label: 'classDiagram', detail: 'Class diagram', insertText: 'classDiagram\n    class Animal {\n        +name: string\n        +makeSound()\n    }' },
      { label: 'stateDiagram', detail: 'State diagram', insertText: 'stateDiagram-v2\n    [*] --> State1\n    State1 --> [*]' },
      { label: 'gantt', detail: 'Gantt chart', insertText: 'gantt\n    title Project Timeline\n    dateFormat YYYY-MM-DD\n    section Tasks\n    Task 1: 2024-01-01, 30d' },
      { label: 'pie', detail: 'Pie chart', insertText: 'pie title Sample Data\n    "Category A": 42.96\n    "Category B": 57.04' }
    ];

    // Sequence diagram keywords
    const sequenceKeywords = [
      { label: 'participant', detail: 'Define participant', insertText: 'participant ${1:A} as ${2:Alice}' },
      { label: 'actor', detail: 'Define actor', insertText: 'actor ${1:A} as ${2:Alice}' },
      { label: 'note', detail: 'Add note', insertText: 'note ${1|left of,right of,over|} ${2:A}: ${3:Note text}' },
      { label: 'activate', detail: 'Activate lifeline', insertText: 'activate ${1:A}' },
      { label: 'deactivate', detail: 'Deactivate lifeline', insertText: 'deactivate ${1:A}' },
      { label: 'loop', detail: 'Loop block', insertText: 'loop ${1:condition}\n    ${2:statements}\nend' },
      { label: 'alt', detail: 'Alternative block', insertText: 'alt ${1:condition}\n    ${2:statements}\nelse\n    ${3:alternative}\nend' },
      { label: 'opt', detail: 'Optional block', insertText: 'opt ${1:condition}\n    ${2:statements}\nend' }
    ];

    // Flowchart keywords
    const flowchartKeywords = [
      { label: 'subgraph', detail: 'Create subgraph', insertText: 'subgraph ${1:title}\n    ${2:content}\nend' },
      { label: 'click', detail: 'Add click event', insertText: 'click ${1:A} "${2:http://example.com}" "${3:tooltip}"' },
      { label: 'classDef', detail: 'Define CSS class', insertText: 'classDef ${1:className} ${2:fill:#f9f,stroke:#333}' },
      { label: 'class', detail: 'Apply CSS class', insertText: 'class ${1:A} ${2:className}' }
    ];

    // ERD keywords
    const erdKeywords = [
      { label: 'PK', detail: 'Primary key', insertText: 'PK' },
      { label: 'FK', detail: 'Foreign key', insertText: 'FK' },
      { label: 'UK', detail: 'Unique key', insertText: 'UK' },
      { label: 'int', detail: 'Integer type', insertText: 'int' },
      { label: 'string', detail: 'String type', insertText: 'string' },
      { label: 'text', detail: 'Text type', insertText: 'text' },
      { label: 'boolean', detail: 'Boolean type', insertText: 'boolean' },
      { label: 'date', detail: 'Date type', insertText: 'date' },
      { label: 'timestamp', detail: 'Timestamp type', insertText: 'timestamp' },
      { label: 'decimal', detail: 'Decimal type', insertText: 'decimal' },
      { label: 'uuid', detail: 'UUID type', insertText: 'uuid' }
    ];

    // Arrow types
    const arrowTypes = [
      { label: '->>', detail: 'Solid arrow with message', insertText: '->> ${1:B}: ${2:message}' },
      { label: '-->>', detail: 'Dotted arrow with message', insertText: '-->> ${1:B}: ${2:message}' },
      { label: '-x', detail: 'Solid arrow with cross', insertText: '-x ${1:B}: ${2:message}' },
      { label: '--x', detail: 'Dotted arrow with cross', insertText: '--x ${1:B}: ${2:message}' },
      { label: '-->', detail: 'Flowchart arrow', insertText: '--> ${1:B}' },
      { label: '===>', detail: 'Thick arrow', insertText: '===> ${1:B}' },
      { label: '-.->>', detail: 'Dotted arrow', insertText: '-.-> ${1:B}' }
    ];

    // Add all completions based on context
    suggestions.push(...diagramTypes.map(item => ({
      label: item.label,
      kind: monaco.languages.CompletionItemKind.Keyword,
      insertText: item.insertText,
      detail: item.detail,
      range: range,
      insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet
    })));

    suggestions.push(...[...sequenceKeywords, ...flowchartKeywords, ...erdKeywords, ...arrowTypes].map(item => ({
      label: item.label,
      kind: monaco.languages.CompletionItemKind.Keyword,
      insertText: item.insertText,
      detail: item.detail,
      range: range,
      insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet
    })));

    return suggestions;
  };

  const getMarkdownCompletions = (monaco: any, range: any) => {
    return [
      {
        label: 'mermaid-block',
        kind: monaco.languages.CompletionItemKind.Snippet,
        insertText: '```mermaid\n${1:flowchart TD\n    A[Start] --> B[End]}\n```',
        detail: 'Mermaid diagram block',
        range: range,
        insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet
      },
      {
        label: 'sequence-diagram',
        kind: monaco.languages.CompletionItemKind.Snippet,
        insertText: '```mermaid\nsequenceDiagram\n    participant ${1:A} as ${2:Alice}\n    participant ${3:B} as ${4:Bob}\n    ${1:A}->>${3:B}: ${5:Hello}\n    ${3:B}-->>${1:A}: ${6:Hi there!}\n```',
        detail: 'Sequence diagram template',
        range: range,
        insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet
      },
      {
        label: 'flowchart',
        kind: monaco.languages.CompletionItemKind.Snippet,
        insertText: '```mermaid\nflowchart ${1|TD,LR|}\n    ${2:A}[${3:Start}] --> ${4:B}{${5:Decision?}}\n    ${4:B} -->|${6:Yes}| ${7:C}[${8:Action 1}]\n    ${4:B} -->|${9:No}| ${10:D}[${11:Action 2}]\n    ${7:C} --> ${12:E}[${13:End}]\n    ${10:D} --> ${12:E}\n```',
        detail: 'Flowchart template',
        range: range,
        insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet
      },
      {
        label: 'erd',
        kind: monaco.languages.CompletionItemKind.Snippet,
        insertText: '```mermaid\nerDiagram\n    ${1:USER} {\n        ${2:int} ${3:id} PK\n        ${4:string} ${5:name}\n        ${6:string} ${7:email}\n    }\n    \n    ${8:ORDER} {\n        ${9:int} ${10:id} PK\n        ${11:int} ${12:user_id} FK\n        ${13:decimal} ${14:total}\n    }\n    \n    ${1:USER} ||--o{ ${8:ORDER} : ${15:places}\n```',
        detail: 'Entity Relationship Diagram template',
        range: range,
        insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet
      }
    ];
  };

  // Method to insert template at cursor
  const insertTemplate = (template: MermaidTemplate) => {
    if (editorRef.current) {
      const selection = editorRef.current.getSelection();
      const range = new monacoRef.current.Range(
        selection.startLineNumber,
        selection.startColumn,
        selection.endLineNumber,
        selection.endColumn
      );
      
      const op = {
        range: range,
        text: template.insertText,
        forceMoveMarkers: true
      };
      
      editorRef.current.executeEdits('insert-template', [op]);
      
      // Set cursor position if specified
      if (template.cursorPosition) {
        editorRef.current.setPosition({
          lineNumber: selection.startLineNumber + template.cursorPosition.line - 1,
          column: template.cursorPosition.column
        });
      }
      
      editorRef.current.focus();
    }
  };

  // Expose insertTemplate method
  useEffect(() => {
    if (onTemplateInsert) {
      // Store reference for external access
      (window as any).insertMermaidTemplate = insertTemplate;
    }
  }, [onTemplateInsert]);

  return (
    <div className="h-full w-full border rounded-lg overflow-hidden bg-card">
      <Editor
        height="100%"
        language={language}
        theme={theme}
        value={value}
        onChange={(newValue) => onChange(newValue || '')}
        onMount={handleEditorDidMount}
        options={{
          readOnly,
          automaticLayout: true,
          scrollBeyondLastLine: false,
          minimap: { enabled: false },
          wordWrap: 'on',
          lineNumbers: 'on',
          renderLineHighlight: 'line',
          fontSize: 14,
          fontFamily: "'Fira Code', 'Monaco', 'Cascadia Code', 'Roboto Mono', monospace",
          quickSuggestions: {
            other: true,
            comments: false,
            strings: false
          },
          suggestOnTriggerCharacters: true,
          acceptSuggestionOnCommitCharacter: true,
          acceptSuggestionOnEnter: 'on',
          tabCompletion: 'on'
        }}
      />
    </div>
  );
}
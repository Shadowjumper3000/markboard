import React, { useEffect, useRef } from 'react';
import Editor from '@monaco-editor/react';

interface MonacoEditorProps {
  value: string;
  onChange: (value: string) => void;
  language?: string;
  theme?: string;
  readOnly?: boolean;
}

export function MonacoEditor({ 
  value, 
  onChange, 
  language = 'markdown', 
  theme = 'vs-dark',
  readOnly = false 
}: MonacoEditorProps) {
  const editorRef = useRef(null);

  const handleEditorDidMount = (editor: any, monaco: any) => {
    editorRef.current = editor;
    
    // Configure Monaco editor for markdown
    monaco.languages.setMonarchTokensProvider('markdown', {
      tokenizer: {
        root: [
          [/^#+.*$/, 'markup.heading'],
          [/^\s*```.*$/, 'markup.code'],
          [/^\s*>.*$/, 'markup.quote'],
          [/^\s*-.*$/, 'markup.list'],
          [/\*\*.*?\*\*/, 'markup.bold'],
          [/\*.*?\*/, 'markup.italic'],
          [/`.*?`/, 'markup.code.inline'],
          [/\[.*?\]\(.*?\)/, 'markup.link'],
        ]
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
    });
  };

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
        }}
      />
    </div>
  );
}
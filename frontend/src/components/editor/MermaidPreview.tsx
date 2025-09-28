import mermaid from 'mermaid';
import { useEffect, useRef, useState } from 'react';

interface MermaidPreviewProps {
  content: string;
  className?: string;
}

export function MermaidPreview({ content, className = '' }: MermaidPreviewProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Configure Mermaid
    mermaid.initialize({
      startOnLoad: false,
      theme: 'default',
      securityLevel: 'loose',
      fontFamily: 'system-ui, -apple-system, sans-serif',
      fontSize: 14,
      flowchart: {
        useMaxWidth: true,
        htmlLabels: true,
      },
    });
  }, []);

  useEffect(() => {
    const renderDiagram = async () => {
      if (!containerRef.current || !content.trim()) {
        setIsLoading(false);
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        // Extract mermaid code blocks from markdown
        const mermaidBlocks = extractMermaidBlocks(content);
        
        if (mermaidBlocks.length === 0) {
          containerRef.current.innerHTML = `
            <div class="flex items-center justify-center h-full text-muted-foreground">
              <div class="text-center space-y-2">
                <div class="text-lg font-medium">No Mermaid diagrams found</div>
                <div class="text-sm">Add mermaid diagrams in code blocks to see live previews</div>
                <div class="text-xs mt-4 p-3 bg-muted rounded-lg font-mono space-y-2">
                  <div>Use code blocks with mermaid language:</div>
                  <div>
                    \`\`\`mermaid<br/>
                    flowchart LR<br/>
                    &nbsp;&nbsp;&nbsp;&nbsp;A[Start] --> B[End]<br/>
                    \`\`\`
                  </div>
                  <div class="mt-2">💡 This allows for comments and multiple diagrams</div>
                </div>
              </div>
            </div>
          `;
          setIsLoading(false);
          return;
        }

        // Render each mermaid block
        let htmlContent = '<div class="space-y-8">';
        
        for (let i = 0; i < mermaidBlocks.length; i++) {
          const block = mermaidBlocks[i];
          const elementId = `mermaid-${Date.now()}-${i}`;
          
          try {
            const { svg } = await mermaid.render(elementId, block);
            htmlContent += `
              <div class="mermaid-diagram bg-white rounded-lg p-6 shadow-sm border">
                ${svg}
              </div>
            `;
          } catch (renderError) {
            htmlContent += `
              <div class="p-4 bg-destructive/10 border border-destructive/20 rounded-lg">
                <div class="text-destructive font-medium mb-2">Diagram Error:</div>
                <pre class="text-xs text-destructive/80">${renderError instanceof Error ? renderError.message : 'Unknown error'}</pre>
              </div>
            `;
          }
        }
        
        htmlContent += '</div>';
        containerRef.current.innerHTML = htmlContent;
        
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to render diagram');
      } finally {
        setIsLoading(false);
      }
    };

    const debounceTimer = setTimeout(renderDiagram, 500);
    return () => clearTimeout(debounceTimer);
  }, [content]);

  const extractMermaidBlocks = (markdown: string): string[] => {
    const blocks: string[] = [];
    
    // Only extract mermaid code blocks - no fallback to raw syntax
    const codeBlockRegex = /```mermaid\s*([\s\S]*?)```/g;
    let match;
    
    while ((match = codeBlockRegex.exec(markdown)) !== null) {
      const blockContent = match[1].trim();
      if (blockContent) {
        blocks.push(blockContent);
      }
    }
    
    return blocks;
  };

  return (
    <div className={`h-full w-full overflow-auto bg-background border rounded-lg ${className}`}>
      <div className="h-full p-6">
        {isLoading && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center space-y-2">
              <div className="animate-pulse text-muted-foreground">Rendering diagrams...</div>
            </div>
          </div>
        )}
        
        {error && (
          <div className="p-4 bg-destructive/10 border border-destructive/20 rounded-lg">
            <div className="text-destructive font-medium mb-2">Error:</div>
            <pre className="text-xs text-destructive/80">{error}</pre>
          </div>
        )}
        
        <div ref={containerRef} className="mermaid-container" />
      </div>
    </div>
  );
}
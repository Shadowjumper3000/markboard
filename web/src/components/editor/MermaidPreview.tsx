import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogTitle } from '@/components/ui/dialog';
import { extractMermaidBlocks } from '@/lib/mermaidBlocks';
import { Move, RotateCcw, ZoomIn, ZoomOut } from 'lucide-react';
import mermaid from 'mermaid';
import { useEffect, useRef, useState } from 'react';

interface MermaidPreviewProps {
  content: string;
  className?: string;
}

interface RenderedDiagram {
  id: string;
  svg: string;
}

export function MermaidPreview({ content, className = '' }: MermaidPreviewProps) {
  const panStartRef = useRef<{ x: number; y: number } | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [renderedDiagrams, setRenderedDiagrams] = useState<RenderedDiagram[]>([]);
  const [renderErrors, setRenderErrors] = useState<string[]>([]);
  const [fullscreenDiagram, setFullscreenDiagram] = useState<RenderedDiagram | null>(null);
  const [zoom, setZoom] = useState(1);
  const [offset, setOffset] = useState({ x: 0, y: 0 });
  const [isPanning, setIsPanning] = useState(false);

  const clampZoom = (value: number) => {
    return Math.min(4, Math.max(0.3, value));
  };

  const resetView = () => {
    setZoom(1);
    setOffset({ x: 0, y: 0 });
    setIsPanning(false);
    panStartRef.current = null;
  };

  const openFullscreen = (diagram: RenderedDiagram) => {
    setFullscreenDiagram(diagram);
    resetView();
  };

  const closeFullscreen = () => {
    setFullscreenDiagram(null);
    resetView();
  };

  const adjustZoom = (multiplier: number) => {
    setZoom((prevZoom) => clampZoom(prevZoom * multiplier));
  };

  const handleWheelZoom = (event: React.WheelEvent<HTMLDivElement>) => {
    event.preventDefault();
    adjustZoom(event.deltaY < 0 ? 1.1 : 0.9);
  };

  const handlePointerDown = (event: React.PointerEvent<HTMLDivElement>) => {
    if (event.button !== 0) {
      return;
    }

    setIsPanning(true);
    panStartRef.current = {
      x: event.clientX - offset.x,
      y: event.clientY - offset.y,
    };
    event.currentTarget.setPointerCapture(event.pointerId);
  };

  const handlePointerMove = (event: React.PointerEvent<HTMLDivElement>) => {
    if (!isPanning || !panStartRef.current) {
      return;
    }

    setOffset({
      x: event.clientX - panStartRef.current.x,
      y: event.clientY - panStartRef.current.y,
    });
  };

  const handlePointerUp = (event: React.PointerEvent<HTMLDivElement>) => {
    if (event.currentTarget.hasPointerCapture(event.pointerId)) {
      event.currentTarget.releasePointerCapture(event.pointerId);
    }

    setIsPanning(false);
    panStartRef.current = null;
  };

  useEffect(() => {
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
    let isCancelled = false;

    const renderDiagrams = async () => {
      if (!content.trim()) {
        if (!isCancelled) {
          setRenderedDiagrams([]);
          setRenderErrors([]);
          setIsLoading(false);
        }
        return;
      }

      const mermaidBlocks = extractMermaidBlocks(content);

      if (mermaidBlocks.length === 0) {
        if (!isCancelled) {
          setRenderedDiagrams([]);
          setRenderErrors([]);
          setIsLoading(false);
        }
        return;
      }

      if (!isCancelled) {
        setIsLoading(true);
      }

      const diagrams: RenderedDiagram[] = [];
      const errors: string[] = [];

      try {
        for (let i = 0; i < mermaidBlocks.length; i++) {
          const block = mermaidBlocks[i];
          const elementId = `mermaid-${Date.now()}-${i}`;

          try {
            const { svg } = await mermaid.render(elementId, block);
            diagrams.push({ id: elementId, svg });
          } catch (renderError) {
            const errorMessage = renderError instanceof Error ? renderError.message : 'Failed to render diagram.';
            errors.push(`Diagram ${i + 1}: ${errorMessage}`);
          }
        }

        if (!isCancelled) {
          setRenderedDiagrams(diagrams);
          setRenderErrors(errors);
        }
      } finally {
        if (!isCancelled) {
          setIsLoading(false);
        }
      }
    };

    setIsLoading(true);
    const debounceTimer = setTimeout(renderDiagrams, 300);

    return () => {
      isCancelled = true;
      clearTimeout(debounceTimer);
    };
  }, [content]);

  useEffect(() => {
    if (!fullscreenDiagram) {
      return;
    }

    const stillExists = renderedDiagrams.some((diagram) => diagram.id === fullscreenDiagram.id);
    if (!stillExists) {
      closeFullscreen();
    }
  }, [fullscreenDiagram, renderedDiagrams]);

  return (
    <>
      <div className={`h-full w-full overflow-hidden bg-background border rounded-lg ${className}`}>
        <div className="h-full overflow-auto p-4">
          {isLoading && (
            <div className="flex items-center justify-center h-full">
              <div className="text-center space-y-2">
                <div className="animate-pulse text-muted-foreground">Rendering diagrams...</div>
              </div>
            </div>
          )}

          {!isLoading && renderedDiagrams.length === 0 && renderErrors.length === 0 && (
            <div className="flex items-center justify-center h-full text-muted-foreground">
              <div className="max-w-xl text-center space-y-2">
                <div className="text-lg font-medium">No diagrams detected</div>
                <div className="text-sm">Write Mermaid syntax directly in editor to see live preview.</div>
              </div>
            </div>
          )}

          {!isLoading && renderErrors.length > 0 && (
            <div className="mb-4 rounded-md border border-destructive/40 bg-destructive/5 p-3 text-sm text-destructive">
              <div className="font-medium mb-1">Diagram render issues</div>
              <ul className="list-disc pl-4 space-y-1">
                {renderErrors.slice(0, 4).map((error) => (
                  <li key={error}>{error}</li>
                ))}
              </ul>
              {renderErrors.length > 4 && (
                <div className="mt-1 text-xs text-destructive/80">+{renderErrors.length - 4} more errors</div>
              )}
            </div>
          )}

          {!isLoading && renderedDiagrams.length > 0 && (
            <div className="space-y-8">
              {renderedDiagrams.map((diagram, index) => (
                <button
                  key={diagram.id}
                  type="button"
                  onClick={() => openFullscreen(diagram)}
                  className="w-full text-left group"
                >
                  <div className="mb-2 flex items-center justify-between text-xs text-muted-foreground">
                    <span>Diagram {index + 1}</span>
                    <span className="opacity-70 group-hover:opacity-100">Click to expand</span>
                  </div>
                  <div
                    className="bg-white rounded-lg p-6 shadow-sm border transition-shadow group-hover:shadow-md [&>svg]:h-auto [&>svg]:max-w-full [&>svg]:mx-auto"
                    dangerouslySetInnerHTML={{ __html: diagram.svg }}
                  />
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      <Dialog open={Boolean(fullscreenDiagram)} onOpenChange={(open) => !open && closeFullscreen()}>
        <DialogContent className="max-w-[95vw] w-[95vw] h-[92vh] p-0 overflow-hidden">
          <DialogTitle className="sr-only">Fullscreen Mermaid Diagram</DialogTitle>

          <div className="flex h-full flex-col">
            <div className="flex items-center justify-between border-b px-4 py-2 bg-card">
              <div className="text-xs text-muted-foreground flex items-center gap-2">
                <Move className="h-3.5 w-3.5" />
                Drag to pan, scroll to zoom, double-click to reset.
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-muted-foreground w-16 text-center">{Math.round(zoom * 100)}%</span>
                <Button
                  size="icon"
                  variant="outline"
                  onClick={() => adjustZoom(0.9)}
                  className="h-8 w-8"
                >
                  <ZoomOut className="h-4 w-4" />
                </Button>
                <Button
                  size="icon"
                  variant="outline"
                  onClick={() => adjustZoom(1.1)}
                  className="h-8 w-8"
                >
                  <ZoomIn className="h-4 w-4" />
                </Button>
                <Button
                  size="icon"
                  variant="outline"
                  onClick={resetView}
                  className="h-8 w-8"
                >
                  <RotateCcw className="h-4 w-4" />
                </Button>
              </div>
            </div>

            <div
              className={`relative flex-1 overflow-hidden bg-muted/20 ${isPanning ? 'cursor-grabbing' : 'cursor-grab'}`}
              onWheel={handleWheelZoom}
              onPointerDown={handlePointerDown}
              onPointerMove={handlePointerMove}
              onPointerUp={handlePointerUp}
              onPointerCancel={handlePointerUp}
              onDoubleClick={resetView}
            >
              {fullscreenDiagram && (
                <div className="absolute inset-0 flex items-center justify-center">
                  <div
                    className="[&_svg]:pointer-events-none [&>svg]:h-auto [&>svg]:max-w-none"
                    style={{
                      transform: `translate(${offset.x}px, ${offset.y}px) scale(${zoom})`,
                      transformOrigin: 'center center',
                    }}
                    dangerouslySetInnerHTML={{ __html: fullscreenDiagram.svg }}
                  />
                </div>
              )}
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}

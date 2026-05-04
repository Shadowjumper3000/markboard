import { Button } from '@/components/ui/button';
import { stripMermaidFence } from '@/lib/mermaidBlocks';
import { Move, RotateCcw, ZoomIn, ZoomOut } from 'lucide-react';
import mermaid from 'mermaid';
import { useEffect, useMemo, useRef, useState } from 'react';

interface MermaidPreviewProps {
  content: string;
  className?: string;
  fullscreen?: boolean;
  showDotMatrix?: boolean;
  onRenderErrors?: (errors: string[]) => void;
}

interface RenderedDiagram {
  id: string;
  svg: string;
}


export function MermaidPreview({
  content,
  className = '',
  fullscreen = false,
  showDotMatrix = false,
  onRenderErrors,
}: MermaidPreviewProps) {
  const panStartRef = useRef<{ x: number; y: number } | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [renderedDiagrams, setRenderedDiagrams] = useState<RenderedDiagram[]>([]);
  const [renderErrors, setRenderErrors] = useState<string[]>([]);
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

  const resolvedDiagram = useMemo(() => {
    if (!content.trim()) {
      return '';
    }

    const stripped = stripMermaidFence(content);
    return stripped.trim();
  }, [content]);

  useEffect(() => {
    mermaid.initialize({
      startOnLoad: false,
      theme: 'default',
      securityLevel: 'loose',
      fontFamily: '"Space Grotesk", "Inter", system-ui, sans-serif',
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
      if (!resolvedDiagram.trim()) {
        if (!isCancelled) {
          setRenderedDiagrams([]);
          setRenderErrors([]);
          onRenderErrors?.([]);
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
        const elementId = `mermaid-${Date.now()}`;
        try {
          const { svg } = await mermaid.render(elementId, resolvedDiagram);
          diagrams.push({ id: elementId, svg });
        } catch (renderError) {
          const errorMessage = renderError instanceof Error ? renderError.message : 'Failed to render diagram.';
          errors.push(errorMessage);
        }

        if (!isCancelled) {
          setRenderedDiagrams(diagrams);
          setRenderErrors(errors);
          onRenderErrors?.(errors);
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
  }, [content, resolvedDiagram, onRenderErrors]);

  return (
    <>
      <div className={`h-full w-full overflow-hidden bg-background border rounded-lg ${className}`}>
        <div className="h-full overflow-hidden">
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

          {!isLoading && renderedDiagrams.length > 0 && (
            <div
              className={`relative h-full w-full ${isPanning ? 'cursor-grabbing' : 'cursor-grab'}`}
              onWheel={handleWheelZoom}
              onPointerDown={handlePointerDown}
              onPointerMove={handlePointerMove}
              onPointerUp={handlePointerUp}
              onPointerCancel={handlePointerUp}
              onDoubleClick={resetView}
              onKeyDown={(event) => {
                if (event.key === '0' || event.key.toLowerCase() === 'r') {
                  resetView();
                } else if (event.key === '+' || event.key === '=') {
                  adjustZoom(1.1);
                } else if (event.key === '-' || event.key === '_') {
                  adjustZoom(0.9);
                }
              }}
              onClick={(event) => {
                const target = event.currentTarget;
                if (target) {
                  target.focus();
                }
              }}
              tabIndex={0}
            >
              <div className="absolute inset-0 flex items-center justify-center">
                <div
                  className="relative pointer-events-none"
                  style={{
                    transform: `translate(${offset.x}px, ${offset.y}px) scale(${zoom})`,
                    transformOrigin: 'center center',
                  }}
                >
                  {showDotMatrix && (
                    <div className="absolute -inset-[140vh] bg-[radial-gradient(circle_at_1px_1px,rgba(148,163,184,0.35)_1px,transparent_0)] bg-[length:24px_24px]" />
                  )}
                  {renderedDiagrams.map((diagram) => (
                    <div key={diagram.id} className="relative flex items-center justify-center">
                      <div
                        className="relative [&_svg]:pointer-events-none [&>svg]:h-auto [&>svg]:max-w-none"
                        dangerouslySetInnerHTML={{ __html: diagram.svg }}
                      />
                    </div>
                  ))}
                </div>
              </div>
              <div className="absolute right-4 top-4 flex items-center gap-2 rounded-full border bg-card/90 px-3 py-1 text-[11px] text-muted-foreground shadow-sm">
                <Move className="h-3 w-3" />
                Drag to pan, scroll to zoom
              </div>
              <div className="absolute bottom-4 right-4 flex items-center gap-2 rounded-full border bg-card/90 p-1 shadow-sm pointer-events-auto">
                <Button size="icon" variant="ghost" onClick={() => adjustZoom(0.9)} className="h-7 w-7">
                  <ZoomOut className="h-3.5 w-3.5" />
                </Button>
                <span className="text-[11px] text-muted-foreground w-12 text-center">{Math.round(zoom * 100)}%</span>
                <Button size="icon" variant="ghost" onClick={() => adjustZoom(1.1)} className="h-7 w-7">
                  <ZoomIn className="h-3.5 w-3.5" />
                </Button>
                <Button size="icon" variant="ghost" onClick={resetView} className="h-7 w-7">
                  <RotateCcw className="h-3.5 w-3.5" />
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
      {fullscreen && null}
    </>
  );
}

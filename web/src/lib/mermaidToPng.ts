// Render all Mermaid diagrams in markdown as separate PNGs
export const renderAllMermaidToPngs = async (markdownContent: string): Promise<Blob[]> => {
  mermaid.initialize({
    startOnLoad: false,
    theme: 'default',
    securityLevel: 'loose',
    fontFamily: 'system-ui, -apple-system, sans-serif',
    flowchart: {
      useMaxWidth: false,
      htmlLabels: true,
      curve: 'basis',
    },
    themeVariables: {
      primaryColor: '#ffffff',
      primaryTextColor: '#000000',
      primaryBorderColor: '#000000',
      lineColor: '#000000',
      sectionBkgColor: '#ffffff',
      altSectionBkgColor: '#ffffff',
      gridColor: '#000000',
      secondaryColor: '#ffffff',
      tertiaryColor: '#ffffff',
    }
  });
  const mermaidBlocks = extractMermaidBlocks(markdownContent);
  const pngs: Blob[] = [];
  for (let i = 0; i < mermaidBlocks.length; i++) {
    const block = mermaidBlocks[i];
    const elementId = `mermaid-export-${Date.now()}-${i}`;
    try {
      const { svg } = await mermaid.render(elementId, block);
      // Parse SVG to get accurate dimensions
      const parser = new DOMParser();
      const svgDoc = parser.parseFromString(svg, 'image/svg+xml');
      const svgNode = svgDoc.querySelector('svg');
      if (svgNode) {
        let width = 400;
        let height = 300;
        const viewBox = svgNode.getAttribute('viewBox');
        if (viewBox) {
          const [, , vbWidth, vbHeight] = viewBox.split(' ').map(Number);
          width = vbWidth;
          height = vbHeight;
        } else {
          const svgWidth = svgNode.getAttribute('width');
          const svgHeight = svgNode.getAttribute('height');
          if (svgWidth && svgHeight) {
            width = parseInt(svgWidth.replace('px', ''));
            height = parseInt(svgHeight.replace('px', ''));
          }
        }
        width = Math.max(width, 200);
        height = Math.max(height, 100);
        // Render this SVG to PNG
        const scale = 2;
        const canvas = document.createElement('canvas');
        canvas.width = width * scale;
        canvas.height = height * scale;
        const ctx = canvas.getContext('2d');
        if (!ctx) continue;
        ctx.scale(scale, scale);
        ctx.fillStyle = 'white';
        ctx.fillRect(0, 0, width, height);
        const svgData = encodeURIComponent(svg);
        const dataUrl = `data:image/svg+xml;charset=utf-8,${svgData}`;
        await new Promise<void>((resolve) => {
          const img = new window.Image();
          img.onload = () => {
            ctx.drawImage(img, 0, 0, width, height);
            resolve();
          };
          img.onerror = () => resolve();
          img.src = dataUrl;
        });
        const blob = await new Promise<Blob | null>((resolve) => {
          canvas.toBlob((b) => resolve(b), 'image/png', 1.0);
        });
        if (blob) pngs.push(blob);
      }
    } catch (error) {
      // skip this block
    }
  }
  return pngs;
};
import mermaid from 'mermaid';

export const renderMermaidToPng = async (markdownContent: string): Promise<Blob | null> => {
  try {
    // Initialize Mermaid with better styling
    mermaid.initialize({
      startOnLoad: false,
      theme: 'default',
      securityLevel: 'loose',
      fontFamily: 'system-ui, -apple-system, sans-serif',
      flowchart: {
        useMaxWidth: false,
        htmlLabels: true,
        curve: 'basis',
      },
      themeVariables: {
        primaryColor: '#ffffff',
        primaryTextColor: '#000000',
        primaryBorderColor: '#000000',
        lineColor: '#000000',
        sectionBkgColor: '#ffffff',
        altSectionBkgColor: '#ffffff',
        gridColor: '#000000',
        secondaryColor: '#ffffff',
        tertiaryColor: '#ffffff',
      }
    });

    // Extract mermaid blocks from markdown
    const mermaidBlocks = extractMermaidBlocks(markdownContent);
    if (mermaidBlocks.length === 0) {
      return null;
    }

    // Render each block to SVG and measure
    const svgRenders: { svg: string; width: number; height: number }[] = [];
    let maxWidth = 0;
    let totalHeight = 0;
    for (let i = 0; i < mermaidBlocks.length; i++) {
      const block = mermaidBlocks[i];
      const elementId = `mermaid-export-${Date.now()}-${i}`;
      try {
        const { svg } = await mermaid.render(elementId, block);
        // Parse SVG to get accurate dimensions
        const parser = new DOMParser();
        const svgDoc = parser.parseFromString(svg, 'image/svg+xml');
        const svgNode = svgDoc.querySelector('svg');
        if (svgNode) {
          let width = 400;
          let height = 300;
          const viewBox = svgNode.getAttribute('viewBox');
          if (viewBox) {
            const [, , vbWidth, vbHeight] = viewBox.split(' ').map(Number);
            width = vbWidth;
            height = vbHeight;
          } else {
            const svgWidth = svgNode.getAttribute('width');
            const svgHeight = svgNode.getAttribute('height');
            if (svgWidth && svgHeight) {
              width = parseInt(svgWidth.replace('px', ''));
              height = parseInt(svgHeight.replace('px', ''));
            }
          }
          width = Math.max(width, 200);
          height = Math.max(height, 100);
          maxWidth = Math.max(maxWidth, width);
          totalHeight += height;
          svgRenders.push({ svg, width, height });
        }
      } catch (error) {
        console.warn(`Failed to render mermaid block ${i}:`, error);
      }
    }
    if (svgRenders.length === 0) {
      return null;
    }
    // Add padding between diagrams
    const padding = 20;
    totalHeight += (svgRenders.length + 1) * padding;
    const totalWidth = maxWidth + 2 * padding;

    // Create a canvas and draw each SVG as an image
    const scale = 2;
    const canvas = document.createElement('canvas');
    canvas.width = totalWidth * scale;
    canvas.height = totalHeight * scale;
    const ctx = canvas.getContext('2d');
    if (!ctx) throw new Error('Could not get canvas context');
    ctx.scale(scale, scale);
    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0, totalWidth, totalHeight);

    let yOffset = padding;
    for (const { svg, width, height } of svgRenders) {
      // Draw each SVG as an image
      // Use data URL for best compatibility
      const svgData = encodeURIComponent(svg);
      const dataUrl = `data:image/svg+xml;charset=utf-8,${svgData}`;
      // eslint-disable-next-line no-await-in-loop
      await new Promise<void>((resolve, reject) => {
        const img = new window.Image();
        img.onload = () => {
          // Center horizontally
          const x = (totalWidth - width) / 2;
          ctx.drawImage(img, x, yOffset, width, height);
          yOffset += height + padding;
          resolve();
        };
        img.onerror = (err) => {
          console.error('Error loading SVG image:', err);
          yOffset += height + padding;
          resolve(); // skip this one
        };
        img.src = dataUrl;
      });
    }

    return await new Promise<Blob>((resolve, reject) => {
      canvas.toBlob((blob) => {
        if (blob) resolve(blob);
        else reject(new Error('Failed to create PNG blob'));
      }, 'image/png', 1.0);
    });
  } catch (error) {
    console.error('Error rendering mermaid to PNG:', error);
    throw error;
  }
};

const extractMermaidBlocks = (markdown: string): string[] => {
  const blocks: string[] = [];
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

const svgToPng = (svgString: string, width: number, height: number): Promise<Blob> => {
  return new Promise((resolve, reject) => {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    if (!ctx) {
      reject(new Error('Could not get canvas context'));
      return;
    }

    // Set canvas size with higher resolution for better quality
    const scale = 2;
    canvas.width = width * scale;
    canvas.height = height * scale;
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
    
    ctx.scale(scale, scale);

    const img = new Image();
    
    // Create a data URL instead of blob for better browser support
    const svgData = encodeURIComponent(svgString);
    const dataUrl = `data:image/svg+xml;charset=utf-8,${svgData}`;

    img.onload = () => {
      // Fill with white background
      ctx.fillStyle = 'white';
      ctx.fillRect(0, 0, width, height);
      
      // Draw the SVG image
      ctx.drawImage(img, 0, 0, width, height);
      
      canvas.toBlob((blob) => {
        if (blob) {
          resolve(blob);
        } else {
          reject(new Error('Failed to create PNG blob'));
        }
      }, 'image/png', 1.0);
    };

    img.onerror = (error) => {
      console.error('Error loading SVG image:', error);
      reject(new Error('Failed to load SVG image'));
    };

    img.src = dataUrl;
  });
};
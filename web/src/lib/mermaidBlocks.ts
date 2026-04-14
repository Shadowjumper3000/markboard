const MERMAID_HEADER_REGEX =
  /^\s*(?:%%\{[\s\S]*?\}%%\s*)*(?:%%.*\n\s*)*(?:graph|flowchart|sequenceDiagram|classDiagram|stateDiagram(?:-v2)?|erDiagram|journey|gantt|pie|gitGraph|mindmap|timeline|sankey-beta|xychart-beta|quadrantChart|requirementDiagram|C4Context|C4Container|C4Component|C4Dynamic|C4Deployment)\b/i;

const dedupeBlocks = (blocks: string[]) => {
  const seen = new Set<string>();
  const uniqueBlocks: string[] = [];

  for (const block of blocks) {
    const normalized = block.trim();
    if (!normalized || seen.has(normalized)) {
      continue;
    }

    seen.add(normalized);
    uniqueBlocks.push(normalized);
  }

  return uniqueBlocks;
};

export const isLikelyMermaidDiagram = (content: string) => {
  return MERMAID_HEADER_REGEX.test(content.trim());
};

export const stripMermaidFence = (content: string) => {
  return content
    .trim()
    .replace(/^```mermaid\s*/i, '')
    .replace(/\s*```\s*$/i, '')
    .trim();
};

export const extractMermaidBlocks = (content: string): string[] => {
  const blocks: string[] = [];

  const mermaidFenceRegex = /```mermaid\s*([\s\S]*?)```/gi;
  let fenceMatch: RegExpExecArray | null;
  while ((fenceMatch = mermaidFenceRegex.exec(content)) !== null) {
    const block = stripMermaidFence(fenceMatch[0]);
    if (block) {
      blocks.push(block);
    }
  }

  const genericFenceRegex = /```([^\n`]*)\n([\s\S]*?)```/g;
  let genericMatch: RegExpExecArray | null;
  while ((genericMatch = genericFenceRegex.exec(content)) !== null) {
    const language = genericMatch[1].trim().toLowerCase();
    const block = genericMatch[2].trim();

    if (language === 'mermaid') {
      continue;
    }

    if (isLikelyMermaidDiagram(block)) {
      blocks.push(block);
    }
  }

  const withoutFences = content.replace(/```[\s\S]*?```/g, '\n');
  const paragraphCandidates = withoutFences
    .split(/\n{2,}/)
    .map((part) => part.trim())
    .filter(Boolean);

  for (const candidate of paragraphCandidates) {
    if (isLikelyMermaidDiagram(candidate)) {
      blocks.push(candidate);
    }
  }

  const uniqueBlocks = dedupeBlocks(blocks);

  if (uniqueBlocks.length === 0 && isLikelyMermaidDiagram(content)) {
    return [content.trim()];
  }

  return uniqueBlocks;
};

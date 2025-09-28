import { MERMAID_SNIPPETS, SIMPLE_MERMAID_TEMPLATES } from './SimpleMermaidTemplates';

interface SimpleMermaidToolbarProps {
  onTemplateInsert: (template: string) => void;
}

export function SimpleMermaidToolbar({ onTemplateInsert }: SimpleMermaidToolbarProps) {
  const insertTemplate = (template: string) => {
    onTemplateInsert(template);
  };

  return (
    <div style={{
      backgroundColor: '#f8f9fa',
      borderBottom: '1px solid #e5e7eb',
      padding: '8px 12px',
      fontSize: '12px',
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      flexWrap: 'wrap'
    }}>
      <span style={{ 
        fontWeight: '500', 
        color: '#6b7280',
        marginRight: '8px' 
      }}>
        Mermaid Templates:
      </span>
      
      {/* Quick Templates */}
      <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
        <button
          onClick={() => insertTemplate(SIMPLE_MERMAID_TEMPLATES.sequence.basic)}
          style={{
            padding: '4px 8px',
            backgroundColor: '#dbeafe',
            color: '#1d4ed8',
            border: '1px solid #bfdbfe',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '11px'
          }}
          title="Insert basic sequence diagram"
        >
          Sequence
        </button>
        
        <button
          onClick={() => insertTemplate(SIMPLE_MERMAID_TEMPLATES.flowchart.basic)}
          style={{
            padding: '4px 8px',
            backgroundColor: '#dcfce7',
            color: '#166534',
            border: '1px solid #bbf7d0',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '11px'
          }}
          title="Insert basic flowchart"
        >
          Flowchart
        </button>
        
        <button
          onClick={() => insertTemplate(SIMPLE_MERMAID_TEMPLATES.erd.basic)}
          style={{
            padding: '4px 8px',
            backgroundColor: '#f3e8ff',
            color: '#7c3aed',
            border: '1px solid #ddd6fe',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '11px'
          }}
          title="Insert basic ERD diagram"
        >
          ERD
        </button>
      </div>

      {/* Divider */}
      <div style={{
        width: '1px',
        height: '16px',
        backgroundColor: '#e5e7eb',
        margin: '0 4px'
      }}></div>

      {/* Advanced Templates Dropdown */}
      <div style={{ position: 'relative', display: 'inline-block' }}>
        <select
          onChange={(e) => {
            if (e.target.value) {
              insertTemplate(e.target.value);
              e.target.value = '';
            }
          }}
          style={{
            padding: '4px 8px',
            backgroundColor: 'white',
            border: '1px solid #d1d5db',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '11px'
          }}
          defaultValue=""
        >
          <option value="" disabled>More Templates...</option>
          
          <optgroup label="Sequence Diagrams">
            <option value={SIMPLE_MERMAID_TEMPLATES.sequence.auth}>Authentication Flow</option>
            <option value={SIMPLE_MERMAID_TEMPLATES.sequence.api}>API Call Sequence</option>
          </optgroup>
          
          <optgroup label="Flowcharts">
            <option value={SIMPLE_MERMAID_TEMPLATES.flowchart.process}>Process Flow</option>
            <option value={SIMPLE_MERMAID_TEMPLATES.flowchart.algorithm}>Algorithm Flow</option>
          </optgroup>
          
          <optgroup label="Entity Relationship">
            <option value={SIMPLE_MERMAID_TEMPLATES.erd.users}>User Management ERD</option>
            <option value={SIMPLE_MERMAID_TEMPLATES.erd.blog}>Blog System ERD</option>
          </optgroup>
        </select>
      </div>

      {/* Divider */}
      <div style={{
        width: '1px',
        height: '16px',
        backgroundColor: '#e5e7eb',
        margin: '0 4px'
      }}></div>

      {/* Quick Snippets */}
      <span style={{ 
        fontWeight: '500', 
        color: '#6b7280',
        fontSize: '11px'
      }}>
        Snippets:
      </span>
      
      <div style={{ position: 'relative', display: 'inline-block' }}>
        <select
          onChange={(e) => {
            if (e.target.value) {
              onTemplateInsert(e.target.value);
              e.target.value = '';
            }
          }}
          style={{
            padding: '3px 6px',
            backgroundColor: 'white',
            border: '1px solid #d1d5db',
            borderRadius: '3px',
            cursor: 'pointer',
            fontSize: '10px'
          }}
          defaultValue=""
        >
          <option value="" disabled>Insert Snippet...</option>
          
          <optgroup label="Sequence">
            <option value={MERMAID_SNIPPETS['seq-participants']}>Participants</option>
            <option value={MERMAID_SNIPPETS['seq-message']}>Message</option>
            <option value={MERMAID_SNIPPETS['seq-response']}>Response</option>
            <option value={MERMAID_SNIPPETS['seq-note']}>Note</option>
            <option value={MERMAID_SNIPPETS['seq-loop']}>Loop</option>
          </optgroup>
          
          <optgroup label="Flowchart">
            <option value={MERMAID_SNIPPETS['flow-rect']}>Rectangle</option>
            <option value={MERMAID_SNIPPETS['flow-diamond']}>Diamond</option>
            <option value={MERMAID_SNIPPETS['flow-rounded']}>Rounded</option>
            <option value={MERMAID_SNIPPETS['flow-database']}>Database</option>
            <option value={MERMAID_SNIPPETS['flow-arrow']}>Arrow</option>
            <option value={MERMAID_SNIPPETS['flow-label']}>Labeled Arrow</option>
          </optgroup>
          
          <optgroup label="ERD">
            <option value={MERMAID_SNIPPETS['erd-entity']}>Entity</option>
            <option value={MERMAID_SNIPPETS['erd-relationship']}>Relationship</option>
            <option value={MERMAID_SNIPPETS['erd-types']}>Common Types</option>
          </optgroup>
        </select>
      </div>

      {/* Help Text */}
      <div style={{ 
        marginLeft: 'auto',
        color: '#9ca3af',
        fontSize: '10px'
      }}>
        💡 Tip: Templates insert at cursor position
      </div>
    </div>
  );
}
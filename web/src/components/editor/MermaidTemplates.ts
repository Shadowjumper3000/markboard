// Mermaid diagram templates for autocomplete and quick insertion
export interface MermaidTemplate {
  id: string;
  name: string;
  description: string;
  category: 'sequence' | 'flowchart' | 'erd' | 'class' | 'state' | 'gantt' | 'pie' | 'journey';
  template: string;
  insertText: string;
  cursorPosition?: { line: number; column: number };
}

export const MERMAID_TEMPLATES: MermaidTemplate[] = [
  // Sequence Diagrams
  {
    id: 'seq-basic',
    name: 'Basic Sequence Diagram',
    description: 'Simple sequence diagram with two participants',
    category: 'sequence',
    template: `\`\`\`mermaid
sequenceDiagram
    participant A as Alice
    participant B as Bob

    A->>B: Hello Bob, how are you?
    B-->>A: Great!
\`\`\``,
    insertText: `\`\`\`mermaid
sequenceDiagram
    participant A as Alice
    participant B as Bob

    A->>B: Hello Bob, how are you?
    B-->>A: Great!
\`\`\``,
    cursorPosition: { line: 3, column: 30 }
  },
  {
    id: 'seq-auth-flow',
    name: 'Authentication Flow',
    description: 'User authentication sequence diagram',
    category: 'sequence',
    template: `\`\`\`mermaid
sequenceDiagram
    participant U as User
    participant C as Client
    participant S as Server
    participant DB as Database

    U->>C: Enter credentials
    C->>S: POST /login
    S->>DB: Verify user
    DB-->>S: User data
    S-->>C: JWT token
    C-->>U: Login success
\`\`\``,
    insertText: `\`\`\`mermaid
sequenceDiagram
    participant U as User
    participant C as Client
    participant S as Server
    participant DB as Database

    U->>C: Enter credentials
    C->>S: POST /login
    S->>DB: Verify user
    DB-->>S: User data
    S-->>C: JWT token
    C-->>U: Login success
\`\`\``,
    cursorPosition: { line: 2, column: 20 }
  },
  {
    id: 'seq-api-call',
    name: 'API Call Sequence',
    description: 'RESTful API interaction sequence',
    category: 'sequence',
    template: `\`\`\`mermaid
sequenceDiagram
    participant Client
    participant API as REST API
    participant Service
    participant DB as Database

    Client->>+API: GET /users
    API->>+Service: getUserList()
    Service->>+DB: SELECT * FROM users
    DB-->>-Service: User records
    Service-->>-API: User list
    API-->>-Client: JSON response
\`\`\``,
    insertText: `\`\`\`mermaid
sequenceDiagram
    participant Client
    participant API as REST API
    participant Service
    participant DB as Database

    Client->>+API: GET /users
    API->>+Service: getUserList()
    Service->>+DB: SELECT * FROM users
    DB-->>-Service: User records
    Service-->>-API: User list
    API-->>-Client: JSON response
\`\`\``,
    cursorPosition: { line: 6, column: 25 }
  },

  // Flowcharts
  {
    id: 'flow-basic',
    name: 'Basic Flowchart',
    description: 'Simple decision-making flowchart',
    category: 'flowchart',
    template: `\`\`\`mermaid
flowchart TD
    A[Start] --> B{Decision?}
    B -->|Yes| C[Action 1]
    B -->|No| D[Action 2]
    C --> E[End]
    D --> E
\`\`\``,
    insertText: `\`\`\`mermaid
flowchart TD
    A[Start] --> B{Decision?}
    B -->|Yes| C[Action 1]
    B -->|No| D[Action 2]
    C --> E[End]
    D --> E
\`\`\``,
    cursorPosition: { line: 2, column: 15 }
  },
  {
    id: 'flow-process',
    name: 'Process Flow',
    description: 'Business process flowchart with multiple steps',
    category: 'flowchart',
    template: `\`\`\`mermaid
flowchart LR
    Start([Start Process]) --> Input[/Input Data/]
    Input --> Validate{Valid?}
    Validate -->|No| Error[Show Error]
    Error --> Input
    Validate -->|Yes| Process[Process Data]
    Process --> Save[(Save to DB)]
    Save --> Success[/Success Message/]
    Success --> End([End])
\`\`\``,
    insertText: `\`\`\`mermaid
flowchart LR
    Start([Start Process]) --> Input[/Input Data/]
    Input --> Validate{Valid?}
    Validate -->|No| Error[Show Error]
    Error --> Input
    Validate -->|Yes| Process[Process Data]
    Process --> Save[(Save to DB)]
    Save --> Success[/Success Message/]
    Success --> End([End])
\`\`\``,
    cursorPosition: { line: 2, column: 30 }
  },
  {
    id: 'flow-algorithm',
    name: 'Algorithm Flow',
    description: 'Algorithm or function flow diagram',
    category: 'flowchart',
    template: `\`\`\`mermaid
flowchart TD
    A[Initialize Variables] --> B[Read Input]
    B --> C{Input Valid?}
    C -->|No| D[Display Error]
    D --> B
    C -->|Yes| E[Process Input]
    E --> F{More Data?}
    F -->|Yes| B
    F -->|No| G[Calculate Result]
    G --> H[Display Output]
    H --> I[End]
\`\`\``,
    insertText: `\`\`\`mermaid
flowchart TD
    A[Initialize Variables] --> B[Read Input]
    B --> C{Input Valid?}
    C -->|No| D[Display Error]
    D --> B
    C -->|Yes| E[Process Input]
    E --> F{More Data?}
    F -->|Yes| B
    F -->|No| G[Calculate Result]
    G --> H[Display Output]
    H --> I[End]
\`\`\``,
    cursorPosition: { line: 2, column: 30 }
  },

  // ERD Diagrams
  {
    id: 'erd-basic',
    name: 'Basic ERD',
    description: 'Simple entity relationship diagram',
    category: 'erd',
    template: `\`\`\`mermaid
erDiagram
    CUSTOMER {
        int customer_id PK
        string name
        string email
        date created_at
    }

    ORDER {
        int order_id PK
        int customer_id FK
        decimal total
        date order_date
    }

    PRODUCT {
        int product_id PK
        string name
        decimal price
        string description
    }

    ORDER_ITEM {
        int order_id FK
        int product_id FK
        int quantity
        decimal unit_price
    }

    CUSTOMER ||--o{ ORDER : places
    ORDER ||--o{ ORDER_ITEM : contains
    PRODUCT ||--o{ ORDER_ITEM : "ordered in"
\`\`\``,
    insertText: `\`\`\`mermaid
erDiagram
    CUSTOMER {
        int customer_id PK
        string name
        string email
        date created_at
    }

    ORDER {
        int order_id PK
        int customer_id FK
        decimal total
        date order_date
    }

    PRODUCT {
        int product_id PK
        string name
        decimal price
        string description
    }

    ORDER_ITEM {
        int order_id FK
        int product_id FK
        int quantity
        decimal unit_price
    }

    CUSTOMER ||--o{ ORDER : places
    ORDER ||--o{ ORDER_ITEM : contains
    PRODUCT ||--o{ ORDER_ITEM : "ordered in"
\`\`\``,
    cursorPosition: { line: 3, column: 15 }
  },
  {
    id: 'erd-user-system',
    name: 'User Management ERD',
    description: 'Entity relationship diagram for user management system',
    category: 'erd',
    template: `\`\`\`mermaid
erDiagram
    USER {
        uuid id PK
        string username UK
        string email UK
        string password_hash
        timestamp created_at
        timestamp updated_at
        boolean is_active
    }

    ROLE {
        int id PK
        string name UK
        string description
        timestamp created_at
    }

    PERMISSION {
        int id PK
        string name UK
        string resource
        string action
        string description
    }

    USER_ROLE {
        uuid user_id FK
        int role_id FK
        timestamp assigned_at
    }

    ROLE_PERMISSION {
        int role_id FK
        int permission_id FK
        timestamp granted_at
    }

    USER ||--o{ USER_ROLE : has
    ROLE ||--o{ USER_ROLE : assigned_to
    ROLE ||--o{ ROLE_PERMISSION : has
    PERMISSION ||--o{ ROLE_PERMISSION : granted_to
\`\`\``,
    insertText: `\`\`\`mermaid
erDiagram
    USER {
        uuid id PK
        string username UK
        string email UK
        string password_hash
        timestamp created_at
        timestamp updated_at
        boolean is_active
    }

    ROLE {
        int id PK
        string name UK
        string description
        timestamp created_at
    }

    PERMISSION {
        int id PK
        string name UK
        string resource
        string action
        string description
    }

    USER_ROLE {
        uuid user_id FK
        int role_id FK
        timestamp assigned_at
    }

    ROLE_PERMISSION {
        int role_id FK
        int permission_id FK
        timestamp granted_at
    }

    USER ||--o{ USER_ROLE : has
    ROLE ||--o{ USER_ROLE : assigned_to
    ROLE ||--o{ ROLE_PERMISSION : has
    PERMISSION ||--o{ ROLE_PERMISSION : granted_to
\`\`\``,
    cursorPosition: { line: 3, column: 15 }
  },
  {
    id: 'erd-blog',
    name: 'Blog System ERD',
    description: 'Blog/CMS entity relationship diagram',
    category: 'erd',
    template: `\`\`\`mermaid
erDiagram
    AUTHOR {
        int id PK
        string name
        string email UK
        string bio
        timestamp created_at
    }

    CATEGORY {
        int id PK
        string name UK
        string slug UK
        string description
    }

    POST {
        int id PK
        int author_id FK
        int category_id FK
        string title
        string slug UK
        text content
        string status
        timestamp published_at
        timestamp created_at
        timestamp updated_at
    }

    TAG {
        int id PK
        string name UK
        string slug UK
    }

    POST_TAG {
        int post_id FK
        int tag_id FK
    }

    COMMENT {
        int id PK
        int post_id FK
        string author_name
        string author_email
        text content
        string status
        timestamp created_at
    }

    AUTHOR ||--o{ POST : writes
    CATEGORY ||--o{ POST : contains
    POST ||--o{ POST_TAG : has
    TAG ||--o{ POST_TAG : tagged_in
    POST ||--o{ COMMENT : receives
\`\`\``,
    insertText: `\`\`\`mermaid
erDiagram
    AUTHOR {
        int id PK
        string name
        string email UK
        string bio
        timestamp created_at
    }

    CATEGORY {
        int id PK
        string name UK
        string slug UK
        string description
    }

    POST {
        int id PK
        int author_id FK
        int category_id FK
        string title
        string slug UK
        text content
        string status
        timestamp published_at
        timestamp created_at
        timestamp updated_at
    }

    TAG {
        int id PK
        string name UK
        string slug UK
    }

    POST_TAG {
        int post_id FK
        int tag_id FK
    }

    COMMENT {
        int id PK
        int post_id FK
        string author_name
        string author_email
        text content
        string status
        timestamp created_at
    }

    AUTHOR ||--o{ POST : writes
    CATEGORY ||--o{ POST : contains
    POST ||--o{ POST_TAG : has
    TAG ||--o{ POST_TAG : tagged_in
    POST ||--o{ COMMENT : receives
\`\`\``,
    cursorPosition: { line: 3, column: 15 }
  }
];

// Common Mermaid keywords for autocomplete
export const MERMAID_KEYWORDS = {
  sequence: [
    'sequenceDiagram',
    'participant',
    'actor',
    'activate',
    'deactivate',
    'note',
    'loop',
    'alt',
    'else',
    'opt',
    'par',
    'and',
    'critical',
    'break',
    'rect',
    'autonumber'
  ],
  flowchart: [
    'flowchart',
    'graph',
    'TD', 'TB', 'BT', 'RL', 'LR',
    'subgraph',
    'end',
    'click',
    'classDef',
    'linkStyle',
    'style'
  ],
  erd: [
    'erDiagram',
    'PK', 'FK', 'UK',
    'int', 'string', 'text', 'boolean', 'date', 'timestamp', 'decimal', 'uuid',
    'one', 'only one', 'zero or one', 'one or more', 'zero or more'
  ]
};

// Arrow types for different diagram types
export const ARROW_TYPES = {
  sequence: [
    '->', '-->>', '-x', '--x', '-)', '--)', '->>', '-->>',
    '+', '-'
  ],
  flowchart: [
    '-->', '---', '-.->', '==>', '~~>', '--o', '--x',
    '---|', '---|', 'o---o', 'x---x'
  ],
  erd: [
    '||--o{', '||--||', '}|..|{', '}o--o{', '||..|{', '}|--||'
  ]
};

// Shape types for flowcharts
export const FLOWCHART_SHAPES = [
  { name: 'Rectangle', syntax: '[text]', description: 'Process step' },
  { name: 'Rounded Rectangle', syntax: '(text)', description: 'Start/End' },
  { name: 'Stadium', syntax: '([text])', description: 'Start/End alternative' },
  { name: 'Subroutine', syntax: '[[text]]', description: 'Predefined process' },
  { name: 'Database', syntax: '[(text)]', description: 'Database' },
  { name: 'Circle', syntax: '((text))', description: 'Connector' },
  { name: 'Asymmetric', syntax: '>text]', description: 'Flag' },
  { name: 'Rhombus', syntax: '{text}', description: 'Decision' },
  { name: 'Hexagon', syntax: '{{text}}', description: 'Preparation' },
  { name: 'Parallelogram', syntax: '[/text/]', description: 'Input/Output' },
  { name: 'Parallelogram Alt', syntax: '[\\text\\]', description: 'Input/Output alternative' },
  { name: 'Trapezoid', syntax: '[/text\\]', description: 'Manual operation' },
  { name: 'Trapezoid Alt', syntax: '[\\text/]', description: 'Manual operation alternative' }
];
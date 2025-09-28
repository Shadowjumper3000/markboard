// Simple template data for direct insertion
export const SIMPLE_MERMAID_TEMPLATES = {
  sequence: {
    basic: `\`\`\`mermaid
sequenceDiagram
    participant A as Alice
    participant B as Bob
    A->>B: Hello Bob, how are you?
    B-->>A: Great!
\`\`\``,
    
    auth: `\`\`\`mermaid
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

    api: `\`\`\`mermaid
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
\`\`\``
  },

  flowchart: {
    basic: `\`\`\`mermaid
flowchart TD
    A[Start] --> B{Decision?}
    B -->|Yes| C[Action 1]
    B -->|No| D[Action 2]
    C --> E[End]
    D --> E
\`\`\``,

    process: `\`\`\`mermaid
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

    algorithm: `\`\`\`mermaid
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
\`\`\``
  },

  erd: {
    basic: `\`\`\`mermaid
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

    users: `\`\`\`mermaid
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

    blog: `\`\`\`mermaid
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
\`\`\``
  }
};

// Quick snippets for common patterns
export const MERMAID_SNIPPETS = {
  'seq-participants': `participant A as Alice
participant B as Bob`,

  'seq-message': `A->>B: Message text`,
  'seq-response': `B-->>A: Response text`,
  'seq-note': `note over A,B: Note text`,
  'seq-loop': `loop Condition
    A->>B: Message
end`,

  'flow-rect': `A[Process Step]`,
  'flow-diamond': `B{Decision?}`,
  'flow-rounded': `C(Start/End)`,
  'flow-database': `D[(Database)]`,
  'flow-arrow': `A --> B`,
  'flow-label': `A -->|Label| B`,

  'erd-entity': `ENTITY {
    int id PK
    string name
    timestamp created_at
}`,
  
  'erd-relationship': `ENTITY1 ||--o{ ENTITY2 : relationship_name`,
  'erd-types': `int id PK
string name
text description
boolean active
timestamp created_at
decimal price
uuid external_id FK`
};
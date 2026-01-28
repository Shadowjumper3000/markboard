# Markboard
Markboard is a web-based uml diagram editor. It uses Mermaid.js for rendering diagrams and provides a user-friendly interface for creating and managing your diagrams.

## Features
- Create and edit UML diagrams using Mermaid.js syntax.
- User authentication and role management (admin and user roles).
- Save and manage diagrams in a database.

## Technologies Used
- Frontend: React, TypeScript, TailwindCSS, Vite
- Backend: Flask, Python 3.11
- Database: MySQL 8.0
- Authentication: JWT with bcrypt
- Deployment: Docker, Azure Container Apps

## Project Structure

The project follows **Clean Architecture** principles with clear separation of concerns:

```
markboard/
├── app/                          # Backend application (Flask API)
│   ├── __init__.py
│   ├── main.py                  # Application entry point & factory
│   │
│   ├── api/                     # 📡 API/Presentation Layer
│   │   ├── middleware/          # Request/response middleware
│   │   │   └── auth_decorators.py  # Authentication & authorization
│   │   ├── routes/              # API endpoint blueprints
│   │   │   ├── auth.py         # Authentication endpoints
│   │   │   ├── admin.py        # Admin management endpoints
│   │   │   ├── files.py        # File CRUD endpoints
│   │   │   └── teams.py        # Team management endpoints
│   │   └── response_formatter.py  # Standardized API responses
│   │
│   ├── core/                    # 💼 Business Logic Layer
│   │   ├── services/            # Business logic services
│   │   │   ├── auth_service.py     # User registration & authentication
│   │   │   ├── admin_service.py    # Admin operations
│   │   │   ├── file_service.py     # File business logic
│   │   │   └── team_service.py     # Team operations
│   │   ├── repositories/        # Data access abstractions
│   │   │   └── file_repository.py  # File data access
│   │   ├── domain/              # Domain models (future)
│   │   └── permissions.py       # Access control logic
│   │
│   ├── infrastructure/          # 🔧 Infrastructure Layer
│   │   ├── database/            # Database concerns
│   │   │   ├── connection.py       # Connection pool manager
│   │   │   └── seed_data.py        # Initial data seeding
│   │   ├── security/            # Security infrastructure
│   │   │   ├── jwt_service.py      # JWT token operations
│   │   │   ├── password_service.py # Password hashing/verification
│   │   │   └── sanitizer.py        # Input sanitization
│   │   └── storage/             # File storage infrastructure
│   │       ├── interface.py        # Storage abstraction
│   │       └── file_storage.py     # Filesystem implementation
│   │
│   └── utils/                   # 🛠️ Shared Utilities
│       ├── activity_logger.py   # User activity logging
│       ├── formatters.py        # Data formatting utilities
│       └── validators.py        # Input validation rules
│
├── config/                      # ⚙️ Configuration Management
│   ├── __init__.py
│   └── settings.py             # Centralized configuration loader
│
├── web/                         # 🎨 Frontend Application (React + TypeScript)
│   ├── src/
│   │   ├── components/         # React components
│   │   │   ├── auth/          # Authentication components
│   │   │   ├── editor/        # Diagram editor components
│   │   │   ├── files/         # File management UI
│   │   │   ├── layout/        # Layout components
│   │   │   └── teams/         # Team management UI
│   │   ├── pages/             # Page components
│   │   ├── contexts/          # React contexts (Auth, etc.)
│   │   ├── hooks/             # Custom React hooks
│   │   ├── lib/               # API client & services
│   │   └── types/             # TypeScript type definitions
│   ├── public/
│   └── package.json
│
├── deployment/                  # 🚀 Deployment Configurations
│   ├── docker/                 # Dockerfiles by service
│   │   ├── backend/
│   │   │   ├── Dockerfile      # Production backend image
│   │   │   └── Dockerfile.dev  # Development backend image
│   │   ├── web/
│   │   │   ├── Dockerfile      # Production web image
│   │   │   └── Dockerfile.dev  # Development web image
│   │   └── database/
│   │       └── Dockerfile      # MySQL image
│   └── compose/                # Docker Compose configurations
│       ├── docker-compose.yml      # Production compose
│       └── docker-compose.dev.yml  # Development compose
│
├── tests/                       # 🧪 Test Suite
│   ├── test_*_api.py           # API endpoint tests
│   ├── test_*_service.py       # Service layer tests
│   └── conftest.py             # Pytest configuration
│
├── .dockerignore               # Docker ignore patterns
├── .pylintrc                   # Pylint configuration
├── pyproject.toml              # Python project metadata & tool configs
├── requirements.txt            # Production dependencies
├── requirements-dev.txt        # Development dependencies
└── README.md                   # This file
```

### Architecture Highlights

#### **Clean Architecture Layers**
- **API Layer**: Handles HTTP requests/responses, no business logic
- **Core Layer**: Contains all business logic, independent of frameworks
- **Infrastructure Layer**: External concerns (database, file system, security)
- **Utils Layer**: Shared utilities used across all layers

#### **SOLID Principles Applied**
- **Single Responsibility**: Each service/module has one clear purpose
  - `jwt_service.py` - Only JWT operations
  - `password_service.py` - Only password hashing
  - `auth_decorators.py` - Only Flask authentication decorators
- **Dependency Inversion**: Core logic depends on abstractions, not implementations
  - Storage interface allows swapping file storage backends
  - Repository pattern separates data access from business logic
- **Interface Segregation**: Services expose only what clients need
- **Open/Closed**: Easy to extend without modifying existing code

#### **Benefits**
✅ **Testability**: Easy to mock dependencies and test in isolation  
✅ **Maintainability**: Clear boundaries make code easier to understand and modify  
✅ **Scalability**: Can swap implementations (e.g., local storage → S3) without touching business logic  
✅ **Team Collaboration**: Clear structure helps multiple developers work without conflicts  
✅ **Code Quality**: Enforced through linting, formatting, and type hints

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/shadowjumper3000/markboard.git
   ```
2. Navigate to the project directory:
   ```bash
   cd markboard
   ```
3. **Install Docker and Docker Compose** (if not already installed):  
   Follow the official Docker installation guide for your OS:  
   [https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/)  
   Or, on Ubuntu:
   ```bash
   sudo apt update
   sudo apt install docker.io docker-compose
   sudo systemctl enable --now docker
   ```
   > **Note:** Make sure both `docker` and `docker-compose` are installed by running:
   > ```bash
   > docker --version
   > docker-compose --version
   > ```
4. Set up environment variables:
    ```bash
    cp .env-example .env
    # Edit .env file to set your environment variables
    ```
5. Use Docker Compose to set up the environment for local development:
   ```bash
   docker compose -f deployment/compose/docker-compose.dev.yml up -d --build
   ```
   or run the dev container directly
6. Access the application at
   [http://localhost:3000](http://localhost:3000) (Frontend) and [http://localhost:8000](http://localhost:8000) (Backend API)

## Testing

### Quick Test Run
```bash
# Use the provided test script (recommended)
./run_tests.sh
```

### Manual Testing
To run tests manually with coverage:
```bash
# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Set test environment variables
export FLASK_ENV=testing
export JWT_SECRET=test_jwt_secret

# Run tests with coverage
pytest --cov=app --cov-report=html --cov-fail-under=70
```

### Test Coverage
- **Target Coverage**: 70% minimum
- **Current Test Files**: 16 test modules with 140+ test functions
- **Coverage Report**: Generated in `htmlcov/index.html` after running tests
- **CI Integration**: Automated testing on all pull requests and deployments
- **Note**: Seed data tests are excluded from CI due to mocking complexity (non-critical functionality)

### Test Categories
- **Unit Tests**: Service layer testing (`test_*_service.py`)
- **API Tests**: Endpoint testing (`test_*_api.py`) 
- **Integration Tests**: Full application flow (`test_main.py`, `test_db.py`)
- **Validation Tests**: Input validation (`test_validation.py`)
- **Seed Data Tests**: Database seeding (excluded from CI, run manually if needed)

## CI/CD Pipeline

### GitHub Actions Workflow
The project uses a 3-stage GitHub Actions workflow for automated testing, building, and deployment to Azure:

#### **Stage 1: Test**
- Python backend tests with pytest (70% minimum coverage)
- Frontend build verification
- MySQL 8.0 integration testing

#### **Stage 2: Build and Push**
- Builds Docker images for backend, frontend, and database
- Pushes images to Azure Container Registry (markboard.azurecr.io)
- Tags images with commit SHA and 'latest'
- Uses GitHub Actions cache for faster builds

#### **Stage 3: Deploy**
- Deploys to Azure Container Apps in West Europe
- Creates or updates container apps automatically
- Configures secrets and environment variables
- Outputs application URLs

### Required GitHub Secrets
Add these secrets in your repository settings (Settings > Secrets and variables > Actions):

```
ACR_USERNAME              # Azure Container Registry username (usually 'markboard')
ACR_PASSWORD              # Azure Container Registry password
AZURE_CREDENTIALS         # Azure service principal JSON for authentication
MYSQL_ROOT_PASSWORD       # MySQL root password for production database
MYSQL_PASSWORD            # MySQL user password for application
JWT_SECRET                # JWT signing secret key
ADMIN_EMAIL               # Admin user email address
ADMIN_PASSWORD            # Admin user password
```

### Azure Prerequisites
Before running the pipeline, create the Container Apps environment:
```bash
az containerapp env create \
  --name markboard \
  --resource-group BCSAI2025-DEVOPS-STUDENTS-A \
  --location westeurope
```

### Get Azure Credentials
```bash
# Get ACR password
az acr credential show --name markboard --query passwords[0].value --output tsv

# Create service principal for GitHub Actions
az ad sp create-for-rbac \
  --name "markboard-github-actions" \
  --role contributor \
  --scopes /subscriptions/$(az account show --query id --output tsv)/resourceGroups/BCSAI2025-DEVOPS-STUDENTS-A \
  --json-auth
```

### Deployment Targets
- **Registry**: markboard.azurecr.io
- **Resource Group**: BCSAI2025-DEVOPS-STUDENTS-A
- **Container Apps Environment**: markboard
- **Location**: West Europe
- **Container Apps**: markboard-backend, markboard-frontend, markboard-db

## Contributing
Contributions are welcome! Please fork the repository and create a pull request with your changes.
Please ensure that your code adheres to the existing style and includes appropriate tests.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details



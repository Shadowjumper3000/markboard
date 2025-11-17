# Markboard
Markboard is a web-based uml diagram editor. It uses Mermaid.js for rendering diagrams and provides a user-friendly interface for creating and managing your diagrams.

## Features
- Create and edit UML diagrams using Mermaid.js syntax.
- User authentication and role management (admin and user roles).
- Save and manage diagrams in a database.

## Technologies Used
- Frontend: react, typescript, tailwindcss
- Backend: flask
- Database: MySQL
- Authentication: JWT

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
   docker compose -f 'docker-compose.dev.yml' up -d --build
   ```
   or run the dev container directly
6. Access the application at
   [http://localhost:80](http://localhost:80) or [http://localhost](http://localhost)

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

### Continuous Integration
The project includes automated CI/CD pipeline with the following stages:

1. **Testing Stage** (runs on all pushes and PRs):
   - Python dependency installation
   - Database setup (MySQL 8.0)
   - Test execution with coverage reporting
   - Coverage threshold enforcement (70% minimum)
   - Docker build verification
   - Frontend build verification

2. **Deployment Stage** (runs on `prod` branch only):
   - Automated deployment to Hetzner Cloud
   - Docker container orchestration
   - Health check verification
   - Rollback capability

### Pipeline Configuration
- **Test Database**: Ephemeral MySQL 8.0 instance
- **Coverage Reports**: Uploaded to Codecov
- **Build Verification**: Docker image build without container execution
- **Quality Gates**: Tests must pass and coverage ≥70% before deployment

### Branch Strategy
- **Main/Development**: All development work, triggers CI testing
- **Prod**: Production releases, triggers full CI/CD pipeline

## Contributing
Contributions are welcome! Please fork the repository and create a pull request with your changes.
Please ensure that your code adheres to the existing style and includes appropriate tests.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details



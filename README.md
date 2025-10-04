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
3. Set up environment variables:
    ```bash
    cp .env-example .env
    # Edit .env file to set your environment variables
    ```
4. Use Docker to set up the environment for local development:
   ```bash
   docker compose -f 'docker-compose.dev.yml' up -d --build
   ```
5. Access the application at
   [http://localhost:80](http://localhost:80) or [http://localhost](http://localhost)

## Contributing
Contributions are welcome! Please fork the repository and create a pull request with your changes.
Please ensure that your code adheres to the existing style and includes appropriate tests.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details



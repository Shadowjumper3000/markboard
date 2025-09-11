
# How to Run the Flask Server via VS Code

## Prerequisites
- Python 3.x installed
- VS Code installed
- (Recommended) Python extension for VS Code

## Steps

1. **Open the Project in VS Code**
   - Open the folder containing `server.py` in VS Code.

2. **Install Dependencies**
   - Open the integrated terminal (`Ctrl+``) in VS Code.
   - Run:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     pip install -r requirements.txt
     ```

3. **Run the Server**
   - Use the VS Code Task:
     - Press `Ctrl+Shift+P` and select `Run Task`, then choose `Run Backend (Flask)`.
   - Or, in the terminal (after activating the virtual environment):
     ```bash
     python server.py
     ```

4. **Access the Application**
   - Open [http://localhost:8080](http://localhost:8080) in your browser to view the frontend (index.html) and static files.

## Notes
- If you get an error about the port being in use, make sure no other process is running on port 8080.
- You can stop the server with `Ctrl+C` in the terminal.
- The server uses Flask only and serves static files (like index.html and style.css) from the project directory.

## AI Prompts used
> Generate a basic Flask backend serving a static html portfolio page with basic .css styling.

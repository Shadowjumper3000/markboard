<p><a target="_blank" href="https://app.eraser.io/workspace/kfgCuF5uvfbXwHaIkYch" id="edit-in-eraser-github-link"><img alt="Edit in Eraser" src="https://firebasestorage.googleapis.com/v0/b/second-petal-295822.appspot.com/o/images%2Fgithub%2FOpen%20in%20Eraser.svg?alt=media&amp;token=968381c8-a7e7-472a-8ed6-4a6626da5501"></a></p>

# Markboard
Markboard is a browser-based UML diagram maker. Users can create and edit `.md` files that define UML diagrams. The files are rendered live in the browser into sequence diagrams, flowcharts, ERDs, or cloud architecture diagrams using **Mermaid.js** for visualization. 

The project avoids heavy frameworks in critical areas to demonstrate manual implementation: 

- **Authentication and CRUD** (manual implementation with MySQL, no ORM) 
- **Database design and queries** written by hand 
- **AI-assisted frontend scaffolding**, but backend and data logic are hand-written
---

## Features
- **Authentication**: sign up, login, JWT-based sessions, password hashing (manual implementation in Python) 
- **File Management**: CRUD for `.md` UML files (metadata in DB, content on filesystem with version control) 
- **Live Preview**: Monaco editor + Mermaid.js renderer 
- **Upload**: Import existing `.md`  UML files 
- **Admin Dashboard** (post-MVP): manage users, track file counts, view activity logs
---

## Frontend
- **Generated via AI design scaffolding** (React + Tailwind + Monaco) 
- Handles UI, login forms, file browsing, editor, preview panel 
- Renders diagrams via **Mermaid.js**
---

## Backend
- Implemented in **Python** with the **simplest possible setup**: 
    - `http.server`  (for raw HTTP handling) or `Flask`  if minimal routing is needed 
    - `mysql.connector`  for direct SQL queries (no ORM) 
    - `bcrypt`  (via `passlib` ) for password hashing 
    - `PyJWT`  for JWT handling

- Responsibilities: 
    - Authentication (signup, login, JWT validation) 
    - File CRUD with `.md` metadata in DB and content on filesystem with checksums 
    - Admin endpoints (basic stats, activity logs)

---

## Database
- **MySQL** (Dockerized, volume-mounted for persistence) 
- Tables: 
    - `Users`  
    - `Teams`  
    - `Files`  
    - `FileVersions`  
    - `ActivityLogs` 

---

## Infrastructure
- Host: Hetzner server 
- Deployment: Docker containers (frontend, backend, MySQL, file storage) 
- CI/CD: GitHub Actions (build, test, deploy) 
- Volumes for DB and file storage portability
---

## Roadmap Beyond MVP
- Async job queue for heavy rendering (optional) 
- Extended diagram syntax features 
- Team collaboration features (real-time editing) 
- Admin dashboard with full monitoring



<!-- eraser-additional-content -->
## Diagrams
<!-- eraser-additional-files -->
<a href="/README-Database-1.eraserdiagram" data-element-id="QPf3Mtb0fC7U6seMayn-c"><img src="undefined" alt="" data-element-id="QPf3Mtb0fC7U6seMayn-c" /></a>
<a href="/README-CRUD-2.eraserdiagram" data-element-id="xMeEzWbIFAQq4dsKm8Lok"><img src="/.eraser/kfgCuF5uvfbXwHaIkYch___5kSoH9X6LrZJ6O4fyzbtABpyuCi2___---diagram----c2542370ecfdbdc8c73677f7d79d9d89-CRUD.png" alt="" data-element-id="xMeEzWbIFAQq4dsKm8Lok" /></a>
<a href="/README-Security-3.eraserdiagram" data-element-id="oXTHx5Uzyu7ElmYtgwYA2"><img src="undefined" alt="" data-element-id="oXTHx5Uzyu7ElmYtgwYA2" /></a>
<a href="/README-cloud-architecture-4.eraserdiagram" data-element-id="9g-6u7YBR_MSd3OKU0iRR"><img src="/.eraser/kfgCuF5uvfbXwHaIkYch___5kSoH9X6LrZJ6O4fyzbtABpyuCi2___---diagram----9435ccd805614e63cabfa4b1fe81095b.png" alt="" data-element-id="9g-6u7YBR_MSd3OKU0iRR" /></a>
<!-- end-eraser-additional-files -->
<!-- end-eraser-additional-content -->
<!--- Eraser file: https://app.eraser.io/workspace/kfgCuF5uvfbXwHaIkYch --->
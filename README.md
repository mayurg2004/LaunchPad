# LaunchPad – AI-Powered Campus Placement & Career Management Platform

Enterprise-level backend and frontend architecture for a campus placement and career management system.

## Project Structure

- `backend/`: Django project containing the REST API.
- `frontend/`: Directory reserved for the future Flutter application.

## Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Node.js / Flutter (for frontend, later)

## Getting Started

1. Set up the Database:
   ```bash
   docker-compose up -d
   ```

2. Configure Environment:
   ```bash
   cd backend
   cp .env.example .env
   ```
   *Edit `.env` to match your local setup.*

3. Setup Python Virtual Environment:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. Run Migrations:
   ```bash
   python manage.py migrate
   ```

5. Run Development Server:
   ```bash
   python manage.py runserver
   ```

# LaunchPad – AI-Powered Campus Placement & Career Management Platform

LaunchPad is a comprehensive, enterprise-level platform designed to streamline campus placements for universities. It features a robust Django backend API and a modern, responsive Flutter frontend.

## Features

- **Role-based Access Control**: Distinct dashboards and flows for Students, Placement Officers, and Recruiters.
- **AI-Powered Resume Analysis**: Students can upload their PDF resumes to get an instant AI-driven score and parsed skills list, highlighting gaps and strengths.
- **AI Career Recommendations**: Suggests roles (e.g., Backend Developer, Data Scientist) and missing skills based on the student's analyzed resume.
- **Smart Drive Matching**: Recommends active placement drives to students based on a match percentage calculated from their resume skills versus the drive requirements.
- **Comprehensive Lifecycle**: Manage drives, job applications, interview schedules, offers, and notifications seamlessly.
- **Beautiful UI/UX**: Dark-themed, highly responsive Flutter frontend with a focus on modern aesthetic design.

## Project Structure

- `backend/`: Django REST Framework API.
- `frontend/`: Flutter web/mobile application.

## Prerequisites

- **Python 3.11+**
- **Flutter SDK** (Channel stable)
- **Docker** (optional, for external database setups if used)

---

## 🚀 Getting Started

### 1. Backend Setup (Django)

1. **Setup Python Virtual Environment**:
   ```bash
   cd backend
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   ```bash
   cp .env.example .env
   # Ensure you configure any required API keys or DB credentials in .env
   ```

4. **Run Migrations & Start Server**:
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```
   *The backend API will run on `http://127.0.0.1:8000`.*

### 2. Frontend Setup (Flutter)

1. **Install Dependencies**:
   ```bash
   cd frontend
   flutter pub get
   ```

2. **Run the Application**:
   ```bash
   flutter run -d chrome
   ```
   *This launches the Flutter web app in your default browser.*

---

## 🔑 Demo Credentials

To test the role-based flows, create the users via Django Admin (`python manage.py createsuperuser` and then navigating to `http://127.0.0.1:8000/admin/`), or register them via the API. 

**Student Flow**:
- Sign in as a student to see the **Student Dashboard**.
- Upload a resume via the **Resume Center** to trigger the AI analysis.
- View AI role recommendations based on your parsed skills.
- Browse and apply to AI-recommended placement drives.

**Placement Officer Flow**:
- Sign in as a Placement Officer to see the **PO Dashboard**.
- View aggregate campus statistics (total students, drives, companies, offers).
- Manage placement drives, track students, and oversee applications.

## 🛠️ Testing

**Backend Tests**:
The backend comes with a comprehensive test suite covering all modules (Accounts, Students, AI, Resumes, Drives, Applications, etc.).

To run the tests:
```bash
cd backend
python manage.py test
```

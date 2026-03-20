# FinPlan — Financial Intelligence Platform

Cloud-native, multi-account financial analytics platform designed to track, analyze, and extract insights from financial data.

---

## Tech Stack

### Backend

* FastAPI
* SQLAlchemy
* PostgreSQL

### Frontend

* React (Vite)
* TailwindCSS
* React Query (server state)
* Zustand (client state)
* React Router

### Infrastructure

* Docker + Docker Compose
* AWS-ready architecture

---

## Architecture Overview

### Frontend (Clean Layered Architecture)

```
src/
  app/        # App entry, providers, routing
  core/       # API client, global state (auth, query)
  features/   # Business logic (auth, accounts, etc.)
  pages/      # Route-level UI
  shared/     # Reusable UI components/layout
  styles/     # Global styles (Tailwind)
```

**Flow:**

```
Page → Hook → API → apiClient → Backend
```

---

### Backend

```
backend/
  app/
    api/        # Routes
    db/         # DB init/session
    models/     # ORM models
    services/   # Business logic
    utils/      # Helpers
```

---

## Core Features (MVP)

* Multi-account tracking (banks, brokers, crypto)
* Transaction ingestion (manual + CSV)
* Financial dashboard (net worth, trends)
* Analytics engine (patterns, insights)
* Scalable data foundation for advanced modeling

---

## Local Development

### Option 1 — Docker (Recommended)

Run full stack:

```bash
docker compose up --build
```

Services:

* Frontend → [http://localhost:5173](http://localhost:5173)
* Backend → [http://localhost:8000](http://localhost:8000)
* Database → PostgreSQL (port 5432)

---

### Option 2 — Manual Setup

#### 1. Start Database

```bash
docker compose up -d db
```

#### 2. Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\Activate.ps1   # Windows

pip install -r requirements.txt
```

#### 3. Environment Variables

Create `.env` inside `/backend`:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/finplan
```

#### 4. Initialize Database

```bash
python app/db/init_db.py
```

#### 5. Run Backend

```bash
uvicorn main:app --reload
```

---

#### 6. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

---

## Environment Variables

### Backend

```
DATABASE_URL=postgresql://postgres:password@db:5432/finplan
```

### Frontend

```
VITE_API_URL=http://localhost:8000
```

---

## Current Status

* Backend API running
* Database connected
* Frontend migrated to Vite
* Clean architecture implemented
* Routing + base pages working

---

## Next Milestones

* Authentication (JWT + protected routes)
* Accounts integration
* Transactions UI + ingestion
* Dashboard analytics
* AI-driven insights layer

---

## Notes

* TailwindCSS used for rapid UI development
* Architecture designed for scalability and feature isolation
* Docker-first workflow ensures environment consistency

---

## License

Private project — internal use

# FinTech Platform

Cloud-native multi-tenant financial intelligence platform.

## Tech Stack

- FastAPI
- SQLAlchemy
- PostgreSQL
- Docker
- AWS-ready architecture

## Architecture

backend/
  app/
    api/
    db/
    models/
    services/
    utils/

## Features (MVP)

- Multi-tenant user model
- Account tracking
- Transaction storage
- Financial data warehouse foundation

## Local Development

### 1. Start Database

docker compose up -d

### 2. Activate Virtual Environment (Windows)

venv\Scripts\Activate.ps1

### 3. Install Dependencies

pip install -r backend/requirements.txt

### 4. Initialize Database

python backend/app/db/init_db.py

### 5. Run API

uvicorn backend.main:app --reload
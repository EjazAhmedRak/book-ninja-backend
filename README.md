# Book Ninja Monorepo

This repository contains the Book Ninja backend and frontend applications.

## Structure

- `apps/backend` - FastAPI + LangGraph backend
- `apps/frontend` - Frontend scaffold and development guide

## Local Development

### Backend

```bash
cd apps/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000
```

### Frontend

```bash
cd apps/frontend
npm install
npm run dev
```

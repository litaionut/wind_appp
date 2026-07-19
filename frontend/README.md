# Frontend

React + Vite + TypeScript SPA (UD-002 / AD-015).

## Dev

```powershell
# Terminal 1 — API
.\.venv\Scripts\python backend\manage.py runserver

# Terminal 2 — UI
cd frontend
npm install
npm run dev
```

Open http://127.0.0.1:5173 — Vite proxies `/api` to Django on port 8000.

Create a user with `createsuperuser` (or staff) before signing in.

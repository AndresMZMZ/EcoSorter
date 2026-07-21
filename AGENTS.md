# AGENTS.md — EcoSorter

## Project overview

Waste-classification visual agent: camera → YOLOv8 detection → waste-bin recommendation.
Two services in a monorepo: `backend/` (FastAPI, Python 3.12) and `frontend/` (Next.js 16, React 19, pnpm).

## Run everything with Docker

```bash
cp .env.example .env   # fill GEMINI_API_KEY, SUPABASE_URL, SUPABASE_KEY
docker-compose up --build
```

Backend: `localhost:8000` · API docs: `localhost:8000/docs` · Frontend: `localhost:3000`

## Backend (FastAPI + YOLOv8)

**Entry point:** `backend/app/main.py` — FastAPI app with CORS for `localhost:3000`.
**Router:** `backend/app/routers/detection.py` — all `/detect/*` endpoints.
**Key env vars:** `GEMINI_API_KEY`, `SUPABASE_URL`, `SUPABASE_KEY`, `CAMERA_INDEX` (default `0`), `YOLO_MODEL_PATH` (default `yolov8n.pt`), `YOLO_CONFIDENCE` (default `0.35`).

### Backend tests

The actual test files live in `backend/tests/` (not `backend/app/tests/` which is empty):

```bash
cd backend
pytest tests/ --cov=app --cov-report=term-missing
```

The README and CI reference `pytest app/tests/` which contains no tests — that path is incorrect.

### Run backend without Docker

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Frontend (Next.js 16)

**Entry point:** `frontend/app/page.tsx` (App Router, `"use client"`).
**Components:** `frontend/components/WasteClassifier.tsx` — camera capture + detection UI.
**API client:** `frontend/lib/api.ts` — calls backend `/detect/image` endpoint.
**Package manager:** pnpm (lockfile: `frontend/pnpm-lock.yaml`), though the Dockerfile uses npm.

### Frontend commands

```bash
cd frontend
pnpm install
pnpm run dev     # dev server on :3000
pnpm lint        # eslint (next/core-web-vitals + typescript)
pnpm run build   # production build
```

**Env var:** `NEXT_PUBLIC_API_URL` (default `http://localhost:8000`) — must be set at build time.

## CI (GitHub Actions)

`.github/workflows/ci.yml` runs on push/PR to `main` and `develop`:
1. **backend-tests** — pytest with coverage (currently has `|| echo` fallback since coverage threshold isn't met)
2. **frontend-build** — `npm install && npm run build`
3. **docker-build-check** — verifies both Dockerfiles build

## Architecture notes

- Backend detection flow: `DetectionService.detect()` runs YOLOv8 inference, then `waste_mapping.py` classifies each detection into 5 waste-bin categories (blanca/verde/negra/amarilla/roja) based on YOLO class names.
- Camera endpoints require a physical camera; camera-dependent tests use `monkeypatch` to mock `camera_service.read_frame`.
- The `POST /classify` endpoint in `main.py` is a mock stub; real detection goes through `/detect/*` routes.
- Frontend auto-scans every 1.8s when auto-scan is enabled (`SCAN_INTERVAL_MS`).

## Gotchas

- OpenCV requires system libs `libgl1` and `libglib2.0-0` (installed in the backend Dockerfile; may need manual install outside Docker on Linux).
- The frontend Dockerfile uses `npm install` but the repo has a `pnpm-lock.yaml` — inconsistency to be aware of.
- CI uses Python 3.11 for tests but the backend Dockerfile targets Python 3.12.
- `backend/app/tests/__init__.py` exists but is empty; don't confuse it with `backend/tests/` where real tests live.

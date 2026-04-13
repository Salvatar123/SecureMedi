# Render Backend Deployment (SecureMedi)

This guide deploys only the FastAPI backend to Render.

## 1. Prerequisites

- GitHub repo connected to Render
- Supabase project ready (URL + key)
- Frontend URL ready for CORS (for example: `https://your-frontend.onrender.com`)

## 2. Blueprint Deployment (recommended)

This repo includes a Render blueprint file: `render.yaml`.

1. Push your latest code to GitHub.
2. In Render, click **New +** -> **Blueprint**.
3. Select this repository.
4. Render will detect `render.yaml` and create `securemedi-backend`.
5. Set required secret env vars before first deploy:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `CORS_ALLOWED_ORIGINS` (example: `https://your-frontend.onrender.com`)
6. Click **Apply**.

## 3. Service Settings Used

- Build Command: `pip install -r backend/requirements.txt`
- Start Command: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
- Health Check Path: `/health/live`
- Python Version: `3.11.9`

## 4. Environment Variables

Configured in `render.yaml`:

- `ENABLE_BLOCKCHAIN=false`
- `ENABLE_SUPABASE=true`
- `ENABLE_LOCAL_LOGGING=true`
- `LOG_LEVEL=INFO`

Set as secrets in Render dashboard:

- `SUPABASE_URL`
- `SUPABASE_KEY`
- `CORS_ALLOWED_ORIGINS`
- `CORS_ALLOWED_ORIGIN_REGEX` (optional)

## 5. Verify Deployment

After deploy completes, check:

- `https://<your-backend>.onrender.com/health/live` returns `{ "status": "alive" }`
- `https://<your-backend>.onrender.com/docs` loads Swagger UI

## 6. Frontend API URL

Set frontend env to the Render backend URL:

- `NEXT_PUBLIC_API_URL=https://<your-backend>.onrender.com`

## 7. Notes

- Render filesystem is ephemeral. Local JSON state files are not durable between restarts.
- Blockchain is disabled by default in this Render config.
- If you later need blockchain in cloud, set `ENABLE_BLOCKCHAIN=true` and point `GANACHE_URL` to a reachable RPC endpoint.

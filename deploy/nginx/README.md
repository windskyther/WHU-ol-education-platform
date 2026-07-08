# Local Nginx Gateway

This config provides one local gateway for frontend integration:

- `/api/` is proxied to Django at `http://127.0.0.1:8000/api/`.
- `/media/` is served directly from `backend/media/`.
- Video files served through `/media/` support browser range requests through Nginx, so native HTML5 video seeking can work.

## Ports

| Service | URL |
|---|---|
| Django | `http://127.0.0.1:8000` |
| Nginx gateway | `http://127.0.0.1:8080` |
| Vite dev server | `http://127.0.0.1:5173` |

## Start Order

1. Start Django:

```powershell
cd backend
.\venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

2. Start Nginx with this config. Recommended on Windows: copy `nginx.dev.windows.conf` to your local Nginx `conf/nginx.conf`, then run:

```powershell
nginx -t
nginx
```

For running directly from this repository as the Nginx prefix, keep `deploy/nginx/logs/` and the temp subdirectories under `deploy/nginx/temp/` present. Windows Nginx uses them for pid, logs, and temporary request files.

If your project path contains spaces, Windows Nginx may split `-p` or `-c` arguments incorrectly. In that case, copy the config into the Nginx install directory or another path without spaces before starting Nginx.

3. Start frontend. The Vite dev proxy should point to the Nginx gateway:

```powershell
cd frontend
npm run dev
```

Default dev proxy target: `http://127.0.0.1:8080`.

## Verification

Open a video request in browser DevTools. A successful seek request should return:

```http
206 Partial Content
Accept-Ranges: bytes
Content-Range: bytes ...
```

If the request still returns `200 OK` from `WSGIServer`, the video is still going directly to Django instead of Nginx.

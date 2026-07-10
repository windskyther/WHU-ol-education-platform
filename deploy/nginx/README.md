# Campus LAN Nginx Gateway

This config provides one gateway for campus LAN frontend integration:

- `/api/` is proxied to Django at `http://127.0.0.1:8000/api/`.
- `/media/` is served directly from `backend/media/`.
- `/` serves the built frontend from `frontend/dist`.
- Video files served through `/media/` support browser range requests through Nginx, so native HTML5 video seeking can work.

## Ports

| Service | URL |
|---|---|
| Django | `http://127.0.0.1:8000` |
| Local Nginx gateway | `http://127.0.0.1:8080` |
| Campus LAN gateway, Ethernet | `http://10.138.78.52:8080` |
| Campus LAN gateway, Wi-Fi | `http://10.133.131.67:8080` |
| Vite dev server | `http://10.138.78.52:5173` or `http://10.133.131.67:5173` |

## Start Order

1. Start Django. Django can stay local-only because Nginx is the external LAN entry:

```powershell
cd backend
.\venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

2. Build frontend before serving it through Nginx:

```powershell
cd frontend
npm run build
```

3. Start Nginx with this config. Recommended on Windows: copy `nginx.dev.windows.conf` to your local Nginx `conf/nginx.conf`, then run:

```powershell
nginx -t
nginx
```

For running directly from this repository as the Nginx prefix, keep `deploy/nginx/logs/` and the temp subdirectories under `deploy/nginx/temp/` present. Windows Nginx uses them for pid, logs, and temporary request files.

If your project path contains spaces, Windows Nginx may split `-p` or `-c` arguments incorrectly. In that case, copy the config into the Nginx install directory or another path without spaces before starting Nginx.

4. If you use Vite dev server instead of `frontend/dist`, the Vite dev proxy should point to the LAN Nginx gateway:

```powershell
cd frontend
npm run dev
```

Default dev proxy target: `http://10.138.78.52:8080`. If the active campus network is Wi-Fi, change it to `http://10.133.131.67:8080`.

## Firewall

Allow inbound TCP `8080` in Windows Defender Firewall. If you also expose Vite dev server to teammates, allow inbound TCP `5173`.

Teammates on the same campus LAN should open:

```text
http://10.138.78.52:8080
```

If Ethernet is disconnected and Wi-Fi is the active campus network, use:

```text
http://10.133.131.67:8080
```

## Verification

Open these URLs from another device on the campus LAN:

```text
http://10.138.78.52:8080/
http://10.138.78.52:8080/api/health/
```

If the page cannot be opened but local `http://127.0.0.1:8080/` works, check Windows Firewall or campus network client isolation.

Open a video request in browser DevTools. A successful seek request should return:

```http
206 Partial Content
Accept-Ranges: bytes
Content-Range: bytes ...
```

If the request still returns `200 OK` from `WSGIServer`, the video is still going directly to Django instead of Nginx.

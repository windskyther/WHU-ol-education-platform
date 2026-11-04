# WHU 在线教育平台

面向学生、教师和管理员的在线教学平台，提供课程与章节管理、选课与进度、在线考试、课程问答、社区资源和证书查询。

前端使用 Vue 3、Vite、Pinia 和 Element Plus；后端使用 Django、Django REST Framework 和 Simple JWT。默认数据库为 MySQL，本地可切换 SQLite。

**在线访问（公网）：** [https://education.ccrate.cc](https://education.ccrate.cc)

校园网访问可使用已配置的 Nginx 网关，见下方部署说明。

## 本地开发

在 Windows PowerShell 中，从仓库根目录执行：

```powershell
cd backend
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
if (!(Test-Path .env)) { Copy-Item .env.example .env }
```

编辑 `backend/.env`：配置 MySQL 连接，或设置 `USE_SQLITE=True`。随后在 `backend/` 执行：

```powershell
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

另开终端，从仓库根目录启动前端：

```powershell
cd frontend
npm ci
$env:VITE_DEV_PROXY_TARGET = 'http://127.0.0.1:8000'
npm run dev
```

前端入口为 `http://localhost:5173/`，后端健康检查为 `http://127.0.0.1:8000/api/health/`。邮件验证码可通过配置 Django 的控制台邮件后端进行联调。

## 构建与文档

- 在 `frontend/` 执行 `npm run build`，产物位于 `frontend/dist/`。
- [API 接口文档](docs/API接口文档.md)：接口、认证与响应约定。
- [前端说明](frontend/README.md)与 [Nginx 部署说明](deploy/nginx/README.md)。

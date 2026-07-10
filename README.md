# WHU 在线教育平台

面向学生、教师和管理员的综合在线教学平台。项目提供课程发布与学习、在线考试、学习交流及证书管理等能力，前后端分离开发。

**在线访问：** [https://education.ccrate.cc](https://education.ccrate.cc)

## 功能概览

- 账号与权限：邮箱验证码注册、登录、JWT 身份认证，以及学生、教师、管理员角色路由控制。
- 课程教学：课程检索与详情、教师课程/章节管理、视频和资料上传、课程发布与下架。
- 学习与考核：选课学习、学习进度记录、在线答题、成绩查看，以及教师题库和答卷管理。
- 社区与成果：课程论坛、资料分享、收藏和个人发布管理，以及学习证书查看。

## 技术栈

| 层级 | 技术 |
| --- | --- |
| 前端 | Vue 3、Vite、Vue Router、Pinia、Element Plus、Axios |
| 后端 | Python 3.10+、Django、Django REST Framework、Simple JWT |
| 数据库 | MySQL 8.0（开发环境可切换 SQLite） |
| 部署 | Nginx、Gunicorn |

## 项目结构

```text
backend/        Django REST Framework 服务与业务应用
frontend/       Vue 3 前端应用
deploy/nginx/   Nginx 网关配置与部署说明
docs/           API 与阶段设计文档
demo/           演示相关资源
```

后端业务应用包括用户、课程、学习进度、考试、问答社区和证书等模块；接口统一以 `/api/` 为前缀。

## 本地运行

### 1. 启动后端

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py runserver
```

默认使用 MySQL。仅用于本地快速演示时，可在 `backend/.env` 中设置 `USE_SQLITE=True`。后端健康检查地址为 `http://127.0.0.1:8000/api/health/`。

### 2. 启动前端

```powershell
cd frontend
npm install
npm run dev
```

按终端提示访问前端；默认地址通常为 `http://localhost:5173`。前端通过 `VITE_API_BASE_URL` 配置接口网关，未配置时请求 `/api`。

### 3. 构建生产前端

```powershell
cd frontend
npm run build
```

构建产物输出至 `frontend/dist/`，由 Nginx 提供静态资源服务，并将 `/api/` 代理到 Django、`/media/` 用于媒体文件访问。更多网关配置见 [deploy/nginx/README.md](deploy/nginx/README.md)。

## 相关文档

- [API 接口文档](docs/API接口文档.md)
- [后端基础说明](docs/P0后端基础说明.md)
- [用户与权限说明](docs/P1用户权限后端说明.md)

## 安全提示

请勿提交 `.env`、数据库密码、SMTP 授权码、JWT Token、私钥、`node_modules`、虚拟环境、构建产物或大体积媒体文件。

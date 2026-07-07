# WHU Online Education Platform

三人协作的在线教育平台项目，按 `P0 -> P7` 阶段推进。当前仓库先完成成员 A 负责的 P0 后端基础：Django REST Framework 项目骨架、MySQL 配置、跨域、媒体目录、统一响应、统一异常和健康检查接口。

## 技术栈

- 后端：Python 3.10+、Django、Django REST Framework、Simple JWT、MySQL
- 前端：Vue 3、Vite、JavaScript、Element Plus、Pinia、Axios，由成员 B 按接口文档独立搭建
- 部署：Nginx、Gunicorn、云服务器、服务器本地 `media/`

## 目录

```text
backend/     成员 A 负责的 Django + DRF 后端
docs/        面向前端/部署/测试的接口与阶段说明
doc/         原始需求与设计文档
```

## 后端本地运行

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

健康检查：`GET http://127.0.0.1:8000/api/health/`

默认使用 MySQL。开发机暂时没有 MySQL 时，可在 `.env` 中设置 `USE_SQLITE=True` 快速启动本地演示库。

## 当前 P0 已提供接口

- `GET /api/health/`：后端健康检查，返回统一响应格式。

后续 P1-P4 的业务接口路径和字段见 [API接口文档](docs/API接口文档.md)。

## 阶段路线

- `v0.1` 项目初始化、前后端骨架、MySQL 连接、健康检查
- `v0.2` 用户、权限、邮箱验证码
- `v0.3` 课程、章节、上传、发布/下架
- `v0.4` 选课、视频学习、学习进度
- `v0.5` 在线考试、自动判分、成绩
- `v0.6` 论坛、报告、证书/推荐
- `v0.9` 部署、并发、安全测试
- `v1.0` 最终验收、演示数据、文档归档

## 协作约定

所有功能先进入个人 `feature/*` 分支，再 PR 到 `dev`。阶段测试通过后由成员 A 合并 `dev -> main` 并打版本标签。当前阶段只要求后端 P0 可启动、可迁移、健康检查可访问。

禁止提交 `.env`、数据库密码、SMTP 密码、Token、私钥、`node_modules`、虚拟环境、`dist` 和大型媒体文件。


## P0 前端启动

前端工程位于 `frontend/`，用于完成 P0 阶段成员 B 的前端骨架交付。

```bash
cd frontend
npm install
npm run dev
```

开发服务启动后，根据终端输出访问本地地址，默认通常为 `http://localhost:5173/`。

## 前端构建

```bash
cd frontend
npm run build
```

构建产物输出到 `frontend/dist/`，后续可交由 Nginx 部署。


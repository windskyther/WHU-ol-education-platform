# WHU 在线教育平台

三人暑期在线教育平台项目，技术栈为 Vue 3 + Vite + Element Plus、Django REST Framework、MySQL、Nginx + Gunicorn。

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

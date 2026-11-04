# 前端开发

本目录包含 Vue 3 单页应用。页面位于 `src/views/`，公共组件位于 `src/components/`，接口封装位于 `src/api/`；路由、用户状态和中英文文案分别位于 `src/router/`、`src/stores/` 和 `src/i18n/`。

```powershell
npm ci
$env:VITE_DEV_PROXY_TARGET = 'http://127.0.0.1:8000'
npm run dev
```

本地入口为 `http://localhost:5173/`。Axios 默认使用 `/api`；Vite 开发代理目标由 `VITE_DEV_PROXY_TARGET` 指定。上例连接本机 Django；使用 Nginx 联调时改为网关地址。生产构建使用 `npm run build`，产物在 `dist/`；`npm run preview` 用于预览构建产物。

见 [项目启动说明](../README.md)和 [API 接口文档](../docs/API接口文档.md)。

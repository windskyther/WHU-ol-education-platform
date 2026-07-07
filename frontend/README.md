# 在线教育平台前端

P0 阶段前端骨架，基于 Vue 3 + Vite + JavaScript + Element Plus。

## 安装依赖

```bash
npm install
```

## 本地开发

```bash
npm run dev
```

默认开发地址通常为 `http://localhost:5173/`。开发环境下 `/api` 会代理到 `http://127.0.0.1:8000`。

## 生产构建

```bash
npm run build
```

构建产物位于 `dist/`。

## 当前 P0 能力

- Vue Router 基础路由。
- Pinia 用户状态骨架。
- Axios 请求封装，默认 API 前缀为 `/api`。
- Element Plus 全局接入。
- 首页展示平台入口，并尝试请求 `/api/health/` 显示后端健康检查状态。

## P1 前端能力

- 登录页：`/login`。
- 注册页：`/register`，包含邮箱验证码、角色选择和 60 秒重发倒计时。
- 角色入口：`/student/dashboard`、`/teacher/dashboard`、`/admin/dashboard`。
- 路由权限：未登录访问角色入口会跳转登录页；已登录用户会按角色进入对应入口。
- 认证接口：`/api/auth/email-code/send/`、`/api/auth/register/`、`/api/auth/login/`、`/api/users/me/`、`/api/auth/logout/`。

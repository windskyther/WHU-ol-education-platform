# 项目信息记录

## 1. 项目概况

- 项目名称：WHU 在线教育平台。
- 项目类型：三人暑期协作开发的在线教育平台。
- 当前重点：成员 B 负责的前端部分。
- 当前前端技术栈：Vue 3、Vite、JavaScript、Element Plus、Pinia、Axios。
- 项目推进方式：按 P0 到 P7 阶段推进，先保证主流程可运行，再逐步完善课程、考试、论坛、报告、部署等模块。

## 2. 阶段路线

- P0：项目初始化、前后端骨架、MySQL 连接、健康检查。
- P1：用户注册登录、角色权限、邮箱验证码、当前用户信息。
- P2：课程、章节、视频/资料上传、发布/下架。
- P3：学生选课、视频学习、资料下载、学习进度。
- P4：在线考试、题目、提交、自动判分、成绩查看。
- P5：论坛、评论、学习报告、证书/推荐。
- P6：服务器部署、Nginx、Gunicorn、MySQL、并发与安全测试。
- P7：最终验收、演示数据、文档归档、main 发布。

## 3. 成员分工

- 成员 A：后端核心、数据库、权限、课程、考试、接口规范。
- 成员 B：前端负责人，负责 Vue 页面、路由、状态管理、Axios、前后端联调。
- 成员 C：论坛、报告、部署、测试、文档、演示数据。

## 4. 当前前端工程状态

前端工程位于 `frontend/`，当前已完成 P0 骨架和 P1 用户认证入口。

### P0 已完成

- 创建 Vite + Vue 3 前端工程。
- 接入 Element Plus。
- 接入 Vue Router。
- 接入 Pinia。
- 接入 Axios 请求封装。
- 首页可访问，并展示 `/api/health/` 健康检查状态。

### P1 已完成

- 登录页：`/login`。
- 注册页：`/register`。
- 学生入口页：`/student/dashboard`。
- 教师入口页：`/teacher/dashboard`。
- 管理员入口页：`/admin/dashboard`。
- 已实现路由权限：
  - 未登录访问角色入口会跳转到 `/login`。
  - 已登录访问 `/login` 或 `/register` 会跳转到对应角色首页。
  - 角色不匹配会跳回当前用户角色首页。
- 已实现退出登录并清理本地 token。

## 5. P1 登录与注册功能

### 登录页

- 输入项：
  - 账号：用户名或邮箱。
  - 密码。
- 登录成功后：
  - 保存 access token。
  - 保存 refresh token。
  - 获取或保存当前用户信息。
  - 按角色跳转：
    - `student` -> `/student/dashboard`
    - `teacher` -> `/teacher/dashboard`
    - `admin` -> `/admin/dashboard`

### 注册页

- 输入项：
  - 用户名。
  - 邮箱。
  - 邮箱验证码。
  - 角色：学生或教师。
  - 密码。
  - 确认密码。
- 验证码按钮：
  - 点击后调用发送验证码接口。
  - 成功后进入 60 秒倒计时。
- 注册成功后跳转到登录页。

## 6. 错误提示优化

登录页和注册页已经做过中文化与精确化处理，避免出现乱码或英文 Axios 错误。

### 通用错误处理

- 请求封装文件：`frontend/src/utils/request.js`。
- 场景化错误文件：`frontend/src/utils/errorMessage.js`。
- 请求错误对象会保留：
  - `rawData`：后端原始错误数据。
  - `status`：HTTP 状态码。
  - `businessCode`：后端业务错误码。
  - `userMessage`：通用中文错误提示。

### 登录错误提示

登录失败会尽量给出具体原因：

- 密码错误 -> `密码错误`
- 账号不存在 -> `账号不存在`
- 后端未启动 -> `无法连接后端服务，请确认服务已启动`
- 请求超时 -> `请求超时，请稍后重试`
- 其他情况 -> `登录失败，请检查账号和密码`

用户明确要求：密码错误时必须显示 `密码错误`。

### 注册错误提示

注册失败会按字段尽量提示：

- 用户名问题 -> `用户名已存在或格式不正确`
- 邮箱问题 -> `邮箱已被注册或格式不正确`
- 密码问题 -> `密码格式不正确`
- 确认密码问题 -> `两次输入的密码不一致`
- 验证码问题 -> `验证码错误或已过期`
- 角色问题 -> `请选择正确的用户角色`

### 验证码错误提示

- 邮箱格式错误 -> `请输入有效邮箱`
- 邮箱已注册 -> `该邮箱已被注册`
- 发送太频繁 -> `验证码发送太频繁，请稍后再试`
- 其他情况 -> `验证码发送失败，请稍后重试`

## 7. 当前主要前端文件

- `frontend/src/main.js`：创建 Vue 应用，注册 Pinia、Router、Element Plus。
- `frontend/src/App.vue`：应用根组件。
- `frontend/src/router/index.js`：路由表、页面标题、登录状态和角色权限守卫。
- `frontend/src/stores/user.js`：用户状态、token、当前用户信息、登录/注册/退出动作、角色跳转。
- `frontend/src/utils/request.js`：Axios 实例、Authorization 请求头、统一响应和错误上下文。
- `frontend/src/utils/errorMessage.js`：登录、注册、验证码错误提示精确化。
- `frontend/src/api/health.js`：健康检查接口。
- `frontend/src/api/auth.js`：P1 认证接口。
- `frontend/src/views/common/HomeView.vue`：首页。
- `frontend/src/views/auth/LoginView.vue`：登录页。
- `frontend/src/views/auth/RegisterView.vue`：注册页。
- `frontend/src/views/dashboard/RoleDashboard.vue`：角色入口占位页。
- `frontend/src/components/LearningPathPanel.vue`：登录/注册页左侧学习路径视觉组件。
- `frontend/src/styles/main.css`：全局样式、蓝白设计 token、认证页与角色页布局。

## 8. 当前接口约定

### 通用约定

- 所有业务接口以 `/api/` 开头。
- 登录后请求头携带：`Authorization: Bearer <access_token>`。
- 后端成功响应格式约定：

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

- 前端请求封装在 `code === 0` 时返回 `data`。
- 前端遇到认证失效时会清理 token，并触发重新登录流程。

### P1 认证接口

- 发送验证码：`POST /api/auth/email-code/send/`
  - 前端发送字段：`registerEmail`
- 注册：`POST /api/auth/register/`
  - 前端发送字段：`username`、`email`、`password`、`confirmPassword`、`role`、`email_code`
- 登录：`POST /api/auth/login/`
  - 前端发送字段：`account`、`password`
- 获取当前用户：`GET /api/users/me/`
- 退出登录：`POST /api/auth/logout/`
- 刷新 token 预留：`POST /api/auth/refresh/`

## 9. UI 设计方向

- 设计来源：使用过 `frontend-design` skill 的思路。
- 风格：蓝白色调、简约、清晰。
- 主色 token：
  - `--blue-700: #155eef`
  - `--blue-500: #2e90fa`
  - `--blue-050: #eff8ff`
  - `--ink-900: #102033`
  - `--slate-500: #667085`
  - `--white: #ffffff`
- 视觉签名：登录/注册页左侧的“学习路径线”，串联“注册 -> 登录 -> 进入学习”。
- 移动端：登录/注册页改为单列布局。

## 10. 运行与验证

### 前端开发

```bash
cd frontend
npm install
npm run dev
```

默认访问地址通常为：

```text
http://localhost:5173/
```

### 前端构建

```bash
cd frontend
npm run build
```

已验证：`npm.cmd run build` 可以成功通过。

构建时出现过 Element Plus 全量引入导致的 chunk size warning，不影响当前 P1 功能验收。

## 11. 工作区注意事项

- 当前 `git status` 曾显示 `backend/` 和 `docs/` 存在大量删除状态。
- 当前 `git status` 曾显示 `.gitignore` 有修改状态。
- 这些状态不是前端 P1 错误提示修改范围内的内容，后续不要随意恢复、删除或覆盖。
- 当前可见文件主要集中在 `frontend/`。

## 12. 后续建议

- P2 可继续实现课程列表、课程详情、教师课程管理、章节管理页面。
- 后端 P1 完成后，应使用真实接口联调：
  - 验证码发送。
  - 注册。
  - 登录。
  - 获取当前用户。
  - 退出登录。
  - 登录/注册错误提示是否能正确映射。
- 可考虑将 Element Plus 改为按需引入，减少构建体积 warning。

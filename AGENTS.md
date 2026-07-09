# 项目信息记录

## 项目概览

- 项目名称：WHU 在线教育平台。
- 项目类型：三人暑期在线教育平台项目。
- 当前前端阶段重点：P2 课程与章节管理。
- 当前实现范围：
  - P1：用户注册、邮箱验证码、登录、当前用户信息、角色路由守卫。
  - P2：课程列表、课程详情、教师课程管理、章节管理、视频上传、资料上传。
- 当前不属于 P2 的范围：
  - 选课。
  - 学习进度。
  - 资料下载权限。
  - 考试。
  - 论坛。
  - 报告和证书。

## 技术栈

- 前端：Vue 3 + Vite + JavaScript。
- UI 组件库：Element Plus。
- 状态管理：Pinia。
- 路由：Vue Router。
- HTTP 请求：Axios。
- 后端约定：Django REST Framework。
- 数据库约定：MySQL 8.0。
- 部署约定：Nginx + Gunicorn。

## 前端目录结构

- `frontend/src/main.js`：Vue 应用入口，挂载 Pinia、Router、Element Plus。
- `frontend/src/App.vue`：全局 `router-view`，当前已加入页面切换动画。
- `frontend/src/router/index.js`：路由表和全局路由守卫。
- `frontend/src/stores/user.js`：登录态、Token、用户信息和角色跳转逻辑。
- `frontend/src/utils/request.js`：Axios 实例，统一 baseURL、Token 请求头和错误处理。
- `frontend/src/utils/errorMessage.js`：登录、注册、验证码等错误提示转换。
- `frontend/src/api/auth.js`：P1 认证相关接口。
- `frontend/src/api/course.js`：P2 课程、章节、上传相关接口。
- `frontend/src/styles/main.css`：全局浅绿色视觉系统、共享布局、页面动画和响应式样式。
- `frontend/src/views/common/HomeView.vue`：公开首页。
- `frontend/src/views/auth/LoginView.vue`：登录页。
- `frontend/src/views/auth/RegisterView.vue`：注册页。
- `frontend/src/views/dashboard/RoleDashboard.vue`：学生、教师、管理员共用 Dashboard。
- `frontend/src/views/course/CourseListView.vue`：公开课程列表。
- `frontend/src/views/course/CourseDetailView.vue`：课程详情和章节目录。
- `frontend/src/views/teacher/TeacherCoursesView.vue`：教师课程管理。
- `frontend/src/views/teacher/TeacherChaptersView.vue`：教师章节管理和上传。

## P2 接口约定

- 本地后端 base URL 约定：`http://127.0.0.1:8000`。
- 前端请求 baseURL：
  - 优先读取 `VITE_API_BASE_URL`。
  - 未配置时使用 `/api`。
- 成功响应格式：

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

- 常见错误响应格式：

```json
{
  "code": 4000,
  "message": "error detail",
  "data": null
}
```

- 课程列表读取分页数据：
  - `data.count`
  - `data.page`
  - `data.page_size`
  - `data.results`
- 上传视频和资料时，表单字段名必须是 `file`。
- 发布和下架课程都调用：
  - `POST /api/courses/{course_id}/publish/`
  - 请求体：`{ "is_published": true | false }`

## P2 页面能力

- `/courses`
  - 课程列表。
  - 支持分页、关键词、分类、难度筛选。
  - 游客和学生只能看到后端允许可见的课程。

- `/courses/:id`
  - 课程详情。
  - 展示课程标题、简介、分类、难度、教师、章节数量和章节目录。
  - P2 不显示选课、学习进度入口。

- `/teacher/courses`
  - 教师课程管理。
  - 支持创建、编辑、发布、下架、软删除课程。
  - 支持封面上传。

- `/teacher/courses/:id/chapters`
  - 教师章节管理。
  - 支持创建、编辑、删除章节。
  - 支持上传章节视频和章节资料。

## 权限和导航规则

- 登录态保存在 Pinia 和 `localStorage` 中。
- 请求会自动携带：

```http
Authorization: Bearer <access_token>
```

- 角色跳转规则在 `userStore.redirectPathByRole()` 中：
  - `student` -> `/student/dashboard`
  - `teacher` -> `/teacher/dashboard`
  - `admin` -> `/admin/dashboard`
- 未登录访问需要认证的页面时，跳转到 `/login`，并带上 `redirect` 查询参数。
- 登录用户访问 `/login`、`/register` 时，会跳转到对应角色 Dashboard。
- 登录用户访问 `/` 或点击品牌/首页链接时，会跳转到对应角色 Dashboard。
- 未登录用户访问 `/` 时，仍然看到公开首页。
- `/teacher/courses` 和 `/teacher/courses/:id/chapters` 只允许 `teacher` 和 `admin` 访问。

## 视觉设计记录

- 当前前端统一为浅绿色简洁风格。
- 核心色板：
  - `--green-700: #2f6f4e`
  - `--green-500: #5ca982`
  - `--green-300: #a8d8bc`
  - `--green-100: #e8f6ee`
  - `--mint-050: #f6fbf8`
  - `--ink-900: #10251a`
- 设计记忆点：课程生长轨迹。
  - 首页、课程详情、章节相关页面使用轻量轨迹感元素表达“课程内容逐步生长”。
- UI 风格要求：
  - 保持统一、简洁、工作型界面。
  - 重视信息层级、留白、对齐、排版、卡片结构、配色细节和按钮层级。
  - 主按钮只用于关键动作，例如创建课程、管理课程、筛选、保存。
  - 次要导航和辅助动作使用普通链接、plain 或 text 按钮。
  - 卡片圆角保持在 8px 以内。
- 页面切换动画：
  - 全局在 `App.vue` 中包裹 `<Transition name="page" mode="out-in">`。
  - 动画为轻微淡入淡出和垂直位移。
  - `prefers-reduced-motion: reduce` 下禁用动画。

## 文件上传限制

- 课程封面：
  - 最大 5 MB。
  - 支持 `.jpg`、`.jpeg`、`.png`、`.webp`。
- 章节视频：
  - 最大 200 MB。
  - 支持 `.mp4`、`.webm`、`.mov`。
- 章节资料：
  - 最大 20 MB。
  - 支持 `.pdf`、`.doc`、`.docx`、`.ppt`、`.pptx`、`.xls`、`.xlsx`、`.txt`、`.zip`。
- 前端会做基础校验，后端仍是最终校验来源。

## 构建和运行

- 前端目录：`frontend`。
- 安装依赖：

```bash
npm install
```

- 启动开发服务器：

```bash
npm run dev
```

- 构建：

```bash
npm.cmd run build
```

- 最近一次构建结果：
  - `npm.cmd run build` 通过。
  - Vite 输出 Element Plus 相关大 chunk 提示，不影响运行。

## 协作注意事项

- 不要把 P3 的选课、学习进度、资料下载权限提前塞进 P2。
- 不要改动接口路径、请求字段、响应结构，除非同步更新前后端契约文档。
- 所有业务接口应该集中写在 `src/api/*.js`，页面不要散落硬编码请求逻辑。
- 前端按钮隐藏只改善体验，权限最终以后端校验为准。
- 现有工作区中可能存在非本轮产生的后端删除、`.gitignore` 或其他未提交变更；修改前应先查看 `git status`，不要回退他人改动。

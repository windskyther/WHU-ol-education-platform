# 在线教育平台 API 接口文档

当前阶段：P4 考试与成绩后端建设。本文档固定统一接口约定，并列出已实现的 P0-P4 接口契约。

## 统一约定

- 接口前缀：所有业务接口以 `/api/` 开头。
- 请求格式：普通请求使用 `application/json`；文件上传使用 `multipart/form-data`。
- 认证方式：登录后在请求头携带 `Authorization: Bearer <access_token>`。
- 成功响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

- 分页响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "count": 0,
    "page": 1,
    "page_size": 10,
    "results": []
  }
}
```

- 错误码：`4000` 参数错误，`4001` 未认证或 Token 失效，`4003` 权限不足，`4040` 资源不存在，`4090` 重复操作，`5000` 服务端错误。

## P0 已实现

### 健康检查

`GET /api/health/`

用途：供前端、部署人员和测试工具确认后端服务可访问。

响应示例：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "status": "ok",
    "time": "2026-07-07T11:45:00+08:00"
  }
}
```

## P1 已实现：用户与权限

| 方法 | 路径 | 权限 | 功能 |
|---|---|---|---|
| POST | `/api/auth/email-code/send/` | 公开 | 发送注册邮箱验证码 |
| POST | `/api/auth/register/` | 公开 | 用户注册 |
| POST | `/api/auth/login/` | 公开 | 用户登录 |
| POST | `/api/auth/refresh/` | 登录用户 | 刷新 Token |
| POST | `/api/auth/logout/` | 登录用户 | 退出登录 |
| GET | `/api/users/me/` | 登录用户 | 获取当前用户 |
| PUT | `/api/users/me/` | 登录用户 | 修改个人资料 |

### 发送邮箱验证码

`POST /api/auth/email-code/send/`

请求：

```json
{
  "email": "student@example.com",
  "purpose": "register"
}
```

响应：

```json
{
  "code": 0,
  "message": "验证码已发送",
  "data": {
    "email": "student@example.com",
    "expires_in": 300,
    "cooldown_seconds": 60
  }
}
```

说明：开发环境建议使用 console email backend，验证码会输出在后端控制台；生产环境配置真实 SMTP。

如果要真实发送到 QQ、163、Gmail 等邮箱，需要在 `backend/.env` 中启用 SMTP：

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.qq.com
EMAIL_PORT=465
EMAIL_USE_SSL=True
EMAIL_HOST_USER=your_email@qq.com
EMAIL_HOST_PASSWORD=your_smtp_auth_code
DEFAULT_FROM_EMAIL=your_email@qq.com
```

`EMAIL_HOST_PASSWORD` 必须填写邮箱服务商生成的 SMTP 授权码，不是邮箱登录密码。

前端请求体推荐使用 `email` 字段；后端也兼容 `mail`、`to`、`to_email`、`emailAddress`、`email_address`：

```json
{
  "email": "student@example.com",
  "purpose": "register"
}
```

### 用户注册

`POST /api/auth/register/`

请求：

```json
{
  "username": "student01",
  "email": "student@example.com",
  "password": "Pass123456",
  "role": "student",
  "email_code": "123456"
}
```

响应：

```json
{
  "code": 0,
  "message": "register success",
  "data": {
    "id": 1,
    "username": "student01",
    "email": "student@example.com",
    "role": "student",
    "avatar": null,
    "avatar_url": null,
    "bio": "",
    "date_joined": "2026-07-07T15:00:00+08:00"
  }
}
```

说明：`role` 只允许 `student` 或 `teacher`；管理员通过 Django Admin 或超级用户创建。

### 用户登录

`POST /api/auth/login/`

请求：

```json
{
  "account": "student@example.com",
  "password": "Pass123456"
}
```

响应：

```json
{
  "code": 0,
  "message": "login success",
  "data": {
    "access": "<jwt-access-token>",
    "refresh": "<jwt-refresh-token>",
    "user": {
      "id": 1,
      "username": "student01",
      "email": "student@example.com",
      "role": "student",
      "avatar": null,
      "avatar_url": null,
      "bio": "",
      "date_joined": "2026-07-07T15:00:00+08:00"
    }
  }
}
```

说明：`account` 支持用户名或邮箱。

### 刷新 Token

`POST /api/auth/refresh/`

请求：

```json
{
  "refresh": "<jwt-refresh-token>"
}
```

响应：Simple JWT 标准响应，返回新的 `access`。

### 退出登录

`POST /api/auth/logout/`

请求头：`Authorization: Bearer <access_token>`

响应：

```json
{
  "code": 0,
  "message": "logout success",
  "data": null
}
```

说明：当前采用无状态 JWT，退出时前端清理本地 token。

### 当前用户

`GET /api/users/me/`

请求头：`Authorization: Bearer <access_token>`

响应字段同登录响应中的 `user`。

### 修改个人资料

`PUT /api/users/me/`

请求头：`Authorization: Bearer <access_token>`

支持字段：

```json
{
  "username": "new_name",
  "bio": "个人简介"
}
```

头像上传可使用 `multipart/form-data` 字段 `avatar`。

## P2 计划接口：课程与章节

| 方法 | 路径 | 权限 | 功能 |
|---|---|---|---|
| GET | `/api/courses/` | 公开 | 课程分页列表 |
| POST | `/api/courses/` | 教师 | 创建课程 |
| GET | `/api/courses/{id}/` | 按状态判断 | 课程详情 |
| PUT | `/api/courses/{id}/` | 课程教师 | 编辑课程 |
| DELETE | `/api/courses/{id}/` | 课程教师 | 软删除课程 |
| POST | `/api/courses/{id}/publish/` | 课程教师 | 发布或下架课程 |
| GET | `/api/courses/{id}/chapters/` | 课程教师/已报名学生 | 章节列表 |
| POST | `/api/courses/{id}/chapters/` | 课程教师 | 创建章节 |
| PUT | `/api/chapters/{id}/` | 课程教师 | 修改章节 |
| DELETE | `/api/chapters/{id}/` | 课程教师 | 删除章节 |
| POST | `/api/chapters/{id}/upload-video/` | 课程教师 | 上传视频 |
| POST | `/api/chapters/{id}/upload-material/` | 课程教师 | 上传资料 |

## P3 计划接口：选课与学习进度

| 方法 | 路径 | 权限 | 功能 |
|---|---|---|---|
| POST | `/api/courses/{id}/enroll/` | 学生 | 加入课程 |
| GET | `/api/my/courses/` | 学生 | 我的课程 |
| POST | `/api/progress/update/` | 学生 | 更新学习进度 |
| GET | `/api/progress/course/{course_id}/` | 学生/课程教师 | 查看课程进度 |

## P4 已实现接口：考试与成绩

| 方法 | 路径 | 权限 | 功能 |
|---|---|---|---|
| GET | `/api/courses/{id}/exams/` | 课程教师/已报名学生 | 考试列表 |
| POST | `/api/courses/{id}/exams/` | 课程教师 | 创建考试 |
| GET | `/api/exams/{id}/` | 课程教师/已报名学生 | 考试详情，学生端不返回答案 |
| POST | `/api/exams/{id}/questions/` | 课程教师 | 添加题目 |
| PUT | `/api/questions/{id}/` | 课程教师 | 修改题目 |
| DELETE | `/api/questions/{id}/` | 课程教师 | 删除题目 |
| POST | `/api/exams/{id}/submit/` | 学生 | 提交考试 |
| GET | `/api/my/scores/` | 学生 | 我的成绩 |
| GET | `/api/exams/{id}/submissions/` | 课程教师 | 查看答卷 |

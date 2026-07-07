# 在线教育平台 API 接口文档

当前阶段：P0 后端基础建设。本文档先固定统一接口约定，并列出 P0 已实现接口和 P1-P4 将提供给前端的接口契约。

## 统一约定

- 接口前缀：所有业务接口以 `/api/` 开头。
- 请求格式：普通请求使用 `application/json`；文件上传使用 `multipart/form-data`。
- 认证方式：P1 起登录后在请求头携带 `Authorization: Bearer <access_token>`。
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

## P1 计划接口：用户与权限

| 方法 | 路径 | 权限 | 功能 |
|---|---|---|---|
| POST | `/api/auth/email-code/send/` | 公开 | 发送注册邮箱验证码 |
| POST | `/api/auth/register/` | 公开 | 用户注册 |
| POST | `/api/auth/login/` | 公开 | 用户登录 |
| POST | `/api/auth/refresh/` | 登录用户 | 刷新 Token |
| POST | `/api/auth/logout/` | 登录用户 | 退出登录 |
| GET | `/api/users/me/` | 登录用户 | 获取当前用户 |
| PUT | `/api/users/me/` | 登录用户 | 修改个人资料 |

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

## P4 计划接口：考试与成绩

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

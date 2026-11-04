# API 接口文档

下表路径统一以 `/api/` 为前缀，并保留末尾斜杠。需要登录的请求携带 `Authorization: Bearer <access_token>`。普通请求使用 JSON，上传使用 `multipart/form-data`。

业务 JSON 响应使用 `{"code":0,"message":"success","data":{}}`；分页的 `data` 含 `count`、`page`、`page_size`、`results`，默认每页 10 条，最多 100 条。JWT 刷新使用 Simple JWT 响应，资料下载返回文件。常见业务码：4000 参数错误、4001 未认证、4003 禁止访问、4040 资源不存在、4090 冲突、5000 服务端错误；仍应检查 HTTP 状态码。

## 账号与系统

| 方法 | 路径 | 用途 |
| --- | --- | --- |
| GET | `/health/` | 服务健康检查 |
| POST | `/auth/email-code/send/` | 提交 `email`，`purpose` 取 `register` |
| POST | `/auth/register/` | 提交 `username`、`email`、`password`、`role`、`email_code`；可注册学生或教师 |
| POST | `/auth/login/` | 提交 `account` 和 `password`，返回令牌与用户资料 |
| POST | `/auth/refresh/` | 提交 `refresh` 获取新访问令牌 |
| POST | `/auth/logout/` | 退出登录，客户端清除本地令牌 |
| GET、PUT | `/users/me/` | 读取、更新个人资料；上传头像使用 `avatar` |
| POST | `/users/me/password/` | 修改密码 |
| GET | `/users/{user_id}/` | 作者公开资料 |

## 课程、学习与考核

| 方法 | 路径 | 用途 |
| --- | --- | --- |
| GET、POST | `/courses/` | 查询课程、创建课程 |
| GET、PUT、PATCH、DELETE | `/courses/{course_id}/` | 查询、更新、删除课程 |
| POST | `/courses/{course_id}/publish/` | 更新发布状态 |
| GET、POST | `/courses/{course_id}/chapters/` | 查询、创建章节 |
| PUT、PATCH、DELETE | `/chapters/{chapter_id}/` | 更新、删除章节 |
| POST | `/chapters/{chapter_id}/upload-video/`、`/chapters/{chapter_id}/upload-material/` | 上传视频、资料 |
| GET | `/materials/{material_id}/download/` | 下载学习资料 |
| POST | `/courses/{course_id}/enroll/` | 学生选课 |
| GET | `/my/courses/` | 查询我的课程 |
| POST、GET（分别） | `/progress/update/`、`/progress/course/{course_id}/` | 写入章节进度、查询课程进度 |
| GET、POST | `/courses/{course_id}/exams/` | 查询、创建考试 |
| GET、PUT、PATCH、DELETE | `/exams/{exam_id}/` | 查询、更新、删除考试 |
| GET、POST | `/exams/{exam_id}/questions/` | 查询、创建题目 |
| PUT、PATCH、DELETE | `/questions/{question_id}/` | 更新、删除题目 |
| POST | `/exams/{exam_id}/submit/` | 提交答案 |
| GET | `/my/scores/`、`/exams/{exam_id}/submissions/` | 学生查成绩、教师查答卷 |
| GET | `/certificates/mine/`、`/certificates/{cert_no}/` | 查询证书列表与详情 |

教师管理课程时受课程归属校验；章节、资料和考试按各自接口校验角色及选课关系。学生端试题数据不返回标准答案。

## 课程问答

| 方法 | 路径 | 用途 |
| --- | --- | --- |
| GET、POST | `/courses/{course_id}/questions/` | 查询、提出课程问题 |
| GET | `/course-questions/{question_id}/` | 查询课程问题详情 |
| POST | `/course-questions/{question_id}/answer/`、`/course-questions/{question_id}/resolve/` | 回答、标记已解决 |

学生只查看自己的课程提问，任课教师和管理员可查看对应课程的问答。

## 公共社区

| 方法 | 路径 | 用途 |
| --- | --- | --- |
| GET | `/community/categories/` | 查询分类 |
| GET、POST | `/community/posts/`、`/community/resources/` | 查询、发布帖子或资源 |
| GET、PATCH、DELETE | `/community/posts/{post_id}/`、`/community/resources/{resource_id}/` | 查询、更新、删除帖子或资源 |
| POST | `/community/posts/{post_id}/attachments/` | 上传帖子附件 |
| GET、POST | `/community/{target_type}/{target_id}/comments/` | 查询、发表评论 |
| POST | `/community/{target_type}/{target_id}/like/`、`/community/{target_type}/{target_id}/favorite/` | 切换点赞、收藏状态 |
| GET | `/community/my/posts/`、`/community/my/resources/`、`/community/my/favorites/` | 查询个人发布与收藏 |

`target_type` 为 `post` 或 `resource`。完整字段及验证规则以 `backend/apps/*/serializers.py` 和视图为准；请求示例可查看 `frontend/src/api/`。

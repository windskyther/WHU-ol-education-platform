# 在线教育平台暑期项目分工需求文档

> 项目定位：大学生暑期三人团队项目。  
> 技术路线：后端 Python + Django + Django REST Framework，数据库 MySQL，前端 Vue 3 + Vite + JavaScript + Element Plus，部署采用云服务器 + Nginx + Gunicorn，支持通过公网 IP 或域名访问。  
> 项目目标：完成一个可演示、可访问、功能相对完整、具备基础并发能力的在线教育平台。

---

# 成员 A 需求文档：核心负责人 / 后端主程 / 架构负责人

## 1. 角色定位

成员 A 是项目核心负责人，负责系统主干架构、后端核心业务、数据库设计、权限控制、接口规范和最终集成。

成员 A 的工作重点不是“做所有后端”，而是负责最关键、最容易影响全局的部分，包括用户体系、课程体系、学习进度、在线考试、MySQL 数据库设计和后端部署运行基础。

---

## 2. 总体职责

成员 A 主要负责以下内容：

1. 搭建 Django + Django REST Framework 后端项目。
2. 设计 MySQL 数据库核心表结构。
3. 实现用户注册、登录、身份角色区分。
4. 实现学生、教师、管理员的基础权限控制。
5. 实现课程、章节、选课、学习进度等核心模块。
6. 实现在线考试、题目管理、答卷提交和自动判分。
7. 负责统一 API 返回格式和接口文档规范。
8. 负责后端关键接口的安全性和并发一致性。
9. 负责 Gunicorn 运行配置的后端部分。
10. 负责 GitHub 主分支管理、代码审核和最终集成。

---

## 3. 技术范围

| 分类 | 技术 |
|---|---|
| 后端语言 | Python 3.10+ |
| 后端框架 | Django |
| API 框架 | Django REST Framework |
| 数据库 | MySQL 8.0 |
| ORM | Django ORM |
| 登录认证 | JWT 或 Django Session，推荐 JWT |
| 后端运行 | Gunicorn |
| 接口测试 | Postman / Apifox |
| 代码管理 | Git + GitHub |

---

## 4. 功能需求

## 4.1 后端项目基础建设

### 4.1.1 Django 项目初始化

#### 功能要求

1. 创建后端项目目录。
2. 配置 Django 基础设置。
3. 配置 Django REST Framework。
4. 配置 MySQL 数据库连接。
5. 配置跨域访问，允许前端访问后端 API。
6. 配置媒体文件上传路径。
7. 配置统一异常处理。
8. 配置统一返回格式。

#### 推荐目录结构

```text
backend/
├── manage.py
├── requirements.txt
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── users/
│   ├── courses/
│   ├── exams/
│   ├── progress/
│   └── common/
├── media/
└── README.md
```

---

## 4.2 用户与权限模块

### 4.2.1 用户注册

#### 功能要求

1. 支持学生和教师注册。
2. 用户注册时需要填写用户名、邮箱、密码和角色。
3. 用户名和邮箱不能重复。
4. 密码必须加密存储。
5. 注册成功后返回用户基本信息。
6. 不向前端返回密码哈希字段。

#### 字段要求

| 字段 | 类型 | 是否必填 | 说明 |
|---|---|---|---|
| username | String | 是 | 用户名 |
| email | String | 是 | 邮箱 |
| password | String | 是 | 密码 |
| role | Enum | 是 | student / teacher |
| avatar | File | 否 | 头像 |
| bio | Text | 否 | 简介 |

---

### 4.2.2 用户登录

#### 功能要求

1. 支持用户名或邮箱登录。
2. 登录成功后返回 Token。
3. 登录失败时返回明确错误信息。
4. Token 过期后需要重新登录。
5. 前端可通过 `/api/users/me/` 获取当前登录用户信息。

---

### 4.2.3 角色权限控制

#### 角色说明

| 角色 | 权限说明 |
|---|---|
| student | 浏览课程、加入课程、观看视频、参加考试、发帖评论 |
| teacher | 创建课程、管理自己的课程、创建考试、查看学生成绩 |
| admin | 使用 Django Admin 管理用户、课程、考试、帖子等数据 |

#### 权限要求

1. 教师只能修改自己创建的课程。
2. 学生只能查看自己加入课程后的资料、视频和考试。
3. 学生只能查看自己的成绩。
4. 教师只能查看自己课程下学生的成绩。
5. 管理员通过 Django Admin 进行数据管理。
6. 所有权限判断以后端为准，不能依赖前端按钮隐藏。

---

## 4.3 课程管理模块

### 4.3.1 创建课程

教师可以创建课程。

#### 功能要求

1. 只有教师可以创建课程。
2. 课程创建后默认处于草稿状态。
3. 课程可以设置标题、简介、封面、分类、难度。
4. 教师可以发布或下架自己的课程。
5. 学生只能看到已发布课程。

#### Course 表建议

| 字段 | 类型 | 说明 |
|---|---|---|
| id | Integer | 主键 |
| title | String | 课程标题 |
| description | Text | 课程简介 |
| cover | File | 课程封面 |
| category | String | 课程分类 |
| level | Enum | beginner / intermediate / advanced |
| teacher | ForeignKey | 授课教师 |
| is_published | Boolean | 是否发布 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

---

### 4.3.2 课程编辑与删除

#### 功能要求

1. 教师只能编辑自己的课程。
2. 可修改课程标题、简介、封面、分类、难度、发布状态。
3. 删除课程建议采用软删除。
4. 删除或下架课程后，学生端不再展示。
5. 已有关联考试和学习记录的课程不建议物理删除。

---

### 4.3.3 章节管理

#### 功能要求

1. 教师可以为自己的课程创建章节。
2. 章节支持排序。
3. 每个章节可以绑定一个视频文件。
4. 每个章节可以绑定一个学习资料文件。
5. 教师可以编辑和删除章节。
6. 学生只能访问已加入课程的章节内容。

#### Chapter 表建议

| 字段 | 类型 | 说明 |
|---|---|---|
| id | Integer | 主键 |
| course | ForeignKey | 所属课程 |
| title | String | 章节标题 |
| description | Text | 章节简介 |
| order | Integer | 排序 |
| video | File | 视频文件 |
| material | File | 学习资料 |
| created_at | DateTime | 创建时间 |

---

## 4.4 选课模块

### 功能要求

1. 学生可以加入已发布课程。
2. 同一学生不能重复加入同一课程。
3. 学生加入课程后才能观看视频、下载资料、参加考试。
4. 学生可以查看自己的课程列表。
5. 教师可以查看自己课程的学生列表。

#### Enrollment 表建议

| 字段 | 类型 | 说明 |
|---|---|---|
| id | Integer | 主键 |
| student | ForeignKey | 学生 |
| course | ForeignKey | 课程 |
| progress | Float | 课程学习进度 |
| enrolled_at | DateTime | 加入时间 |
| last_learned_at | DateTime | 最近学习时间 |

#### 并发要求

1. 选课接口需要防止重复选课。
2. 可通过数据库唯一约束限制 `student + course`。
3. 后端接口需要判断课程是否已发布。

---

## 4.5 学习进度模块

### 功能要求

1. 学生观看视频时，前端定时提交当前观看秒数。
2. 后端保存每个学生、每门课程、每个章节的视频进度。
3. 视频接近播放完成时，标记该章节完成。
4. 根据完成章节数量计算课程总进度。
5. 学生可以查看自己的学习进度。
6. 教师可以查看自己课程下所有学生的学习进度。

#### LearningProgress 表建议

| 字段 | 类型 | 说明 |
|---|---|---|
| id | Integer | 主键 |
| student | ForeignKey | 学生 |
| course | ForeignKey | 课程 |
| chapter | ForeignKey | 章节 |
| watched_seconds | Integer | 已观看秒数 |
| is_completed | Boolean | 是否完成 |
| updated_at | DateTime | 更新时间 |

#### 进度计算规则

```text
课程完成率 = 已完成章节数 / 课程总章节数 × 100%
```

#### 接口要求

1. 更新学习进度时必须验证学生是否已加入课程。
2. 学生不能修改他人的学习进度。
3. watched_seconds 不能随意回退覆盖，可保留最大观看秒数。
4. 课程总进度需要同步更新到 Enrollment 表。

---

## 4.6 在线考试模块

## 4.6.1 教师创建考试

#### 功能要求

1. 只有课程教师可以创建考试。
2. 考试属于某一门课程。
3. 考试可以设置标题、说明、时长、开始时间、截止时间、是否发布。
4. 学生只能看到已发布考试。

#### Exam 表建议

| 字段 | 类型 | 说明 |
|---|---|---|
| id | Integer | 主键 |
| course | ForeignKey | 所属课程 |
| title | String | 考试标题 |
| description | Text | 考试说明 |
| duration | Integer | 考试时长，单位分钟 |
| start_time | DateTime | 开始时间 |
| end_time | DateTime | 结束时间 |
| is_published | Boolean | 是否发布 |
| created_at | DateTime | 创建时间 |

---

## 4.6.2 题目管理

#### 支持题型

| 题型 | 自动判分 | 说明 |
|---|---|---|
| 单选题 | 是 | 一个正确答案 |
| 多选题 | 是 | 多个正确答案 |
| 判断题 | 是 | 正确 / 错误 |
| 填空题 | 可选 | 简单答案可以自动判分 |
| 简答题 | 否 | 教师手动评分，可作为可选功能 |

#### Question 表建议

| 字段 | 类型 | 说明 |
|---|---|---|
| id | Integer | 主键 |
| exam | ForeignKey | 所属考试 |
| type | Enum | 题型 |
| content | Text | 题干 |
| options | JSON | 选项 |
| answer | JSON / Text | 标准答案 |
| score | Integer | 分值 |
| analysis | Text | 解析 |

---

## 4.6.3 学生提交考试

#### 功能要求

1. 学生必须加入课程后才能参加考试。
2. 学生只能提交一次，除非后期扩展允许重考。
3. 前端只提交学生答案，不提交最终分数。
4. 后端读取标准答案进行自动判分。
5. 客观题自动计算分数。
6. 提交后生成答卷记录。
7. 学生可以查看自己的考试结果。
8. 教师可以查看自己课程下所有学生答卷。

#### ExamSubmission 表建议

| 字段 | 类型 | 说明 |
|---|---|---|
| id | Integer | 主键 |
| exam | ForeignKey | 考试 |
| student | ForeignKey | 学生 |
| answers | JSON | 学生答案 |
| objective_score | Float | 客观题得分 |
| subjective_score | Float | 主观题得分 |
| total_score | Float | 总分 |
| submitted_at | DateTime | 提交时间 |
| status | Enum | submitted / graded |

#### 并发要求

1. 提交考试时使用数据库事务。
2. 同一学生同一考试只能有一条提交记录。
3. 通过唯一约束限制 `exam + student`。
4. 如果发生重复提交，后端返回错误。
5. 分数必须以后端计算结果为准。

---

## 5. API 需求

## 5.1 用户接口

| 方法 | 路径 | 功能 |
|---|---|---|
| POST | /api/auth/register/ | 用户注册 |
| POST | /api/auth/login/ | 用户登录 |
| POST | /api/auth/logout/ | 退出登录 |
| GET | /api/users/me/ | 获取当前用户信息 |
| PUT | /api/users/me/ | 修改个人资料 |

---

## 5.2 课程接口

| 方法 | 路径 | 功能 |
|---|---|---|
| GET | /api/courses/ | 获取课程列表 |
| POST | /api/courses/ | 教师创建课程 |
| GET | /api/courses/{id}/ | 获取课程详情 |
| PUT | /api/courses/{id}/ | 修改课程 |
| DELETE | /api/courses/{id}/ | 删除课程 |
| POST | /api/courses/{id}/publish/ | 发布或下架课程 |
| POST | /api/courses/{id}/enroll/ | 学生加入课程 |
| GET | /api/my/courses/ | 学生查看我的课程 |

---

## 5.3 章节接口

| 方法 | 路径 | 功能 |
|---|---|---|
| POST | /api/courses/{id}/chapters/ | 创建章节 |
| GET | /api/courses/{id}/chapters/ | 获取课程章节 |
| PUT | /api/chapters/{id}/ | 修改章节 |
| DELETE | /api/chapters/{id}/ | 删除章节 |
| POST | /api/chapters/{id}/upload-video/ | 上传视频 |
| POST | /api/chapters/{id}/upload-material/ | 上传资料 |

---

## 5.4 学习进度接口

| 方法 | 路径 | 功能 |
|---|---|---|
| POST | /api/progress/update/ | 更新视频学习进度 |
| GET | /api/progress/course/{course_id}/ | 查看某课程学习进度 |
| GET | /api/reports/student/ | 学生学习报告 |
| GET | /api/reports/teacher/course/{course_id}/ | 教师查看课程学习报告 |

---

## 5.5 考试接口

| 方法 | 路径 | 功能 |
|---|---|---|
| POST | /api/courses/{id}/exams/ | 创建考试 |
| GET | /api/courses/{id}/exams/ | 获取课程考试 |
| GET | /api/exams/{id}/ | 获取考试详情 |
| POST | /api/exams/{id}/questions/ | 添加题目 |
| PUT | /api/questions/{id}/ | 修改题目 |
| DELETE | /api/questions/{id}/ | 删除题目 |
| POST | /api/exams/{id}/submit/ | 学生提交考试 |
| GET | /api/my/scores/ | 学生查看成绩 |
| GET | /api/exams/{id}/submissions/ | 教师查看答卷 |

---

## 6. MySQL 设计要求

## 6.1 必须建立的唯一约束

| 表 | 约束 |
|---|---|
| User | username 唯一 |
| User | email 唯一 |
| Enrollment | student + course 唯一 |
| LearningProgress | student + course + chapter 唯一 |
| ExamSubmission | student + exam 唯一 |

---

## 6.2 建议索引

| 表 | 字段 |
|---|---|
| Course | teacher_id |
| Course | category |
| Course | is_published |
| Chapter | course_id |
| Enrollment | student_id |
| Enrollment | course_id |
| LearningProgress | student_id, course_id |
| Exam | course_id |
| Question | exam_id |
| ExamSubmission | exam_id, student_id |

---

## 7. 并发与安全要求

## 7.1 并发要求

1. 后端通过 Gunicorn 多进程运行。
2. 列表接口必须分页。
3. 选课、考试提交等关键接口要防重复请求。
4. 考试提交使用数据库事务。
5. 大文件不要通过 Django 直接读取返回。
6. 视频文件由 Nginx 处理访问。

---

## 7.2 安全要求

1. 密码加密存储。
2. 重要接口必须登录后访问。
3. 教师不能修改他人课程。
4. 学生不能查看他人成绩。
5. 学生不能访问未加入课程的资料。
6. 考试答案不能提前暴露给学生端。
7. 文件上传需要限制类型和大小。
8. 后端必须校验所有业务权限。

---

## 8. 与其他成员的接口约定

## 8.1 与成员 B 的协作

成员 A 需要向成员 B 提供：

1. API 路径。
2. 请求方法。
3. 请求参数。
4. 返回字段。
5. 错误码和错误信息。
6. 登录 Token 使用方式。
7. 文件上传接口说明。
8. 分页接口格式。

---

## 8.2 与成员 C 的协作

成员 A 需要向成员 C 提供：

1. 数据库表结构说明。
2. 后端运行方式。
3. MySQL 初始化步骤。
4. Gunicorn 启动方式。
5. 论坛模块与课程、用户的关联方式。
6. 报告模块所需的学习进度和成绩数据。
7. 测试账号和测试数据结构。

---

## 9. 交付物

成员 A 需要完成以下交付物：

1. Django 后端项目基础结构。
2. MySQL 数据库模型和迁移文件。
3. 用户认证模块。
4. 角色权限模块。
5. 课程管理接口。
6. 章节管理接口。
7. 选课接口。
8. 学习进度接口。
9. 在线考试接口。
10. 自动判分逻辑。
11. 核心接口文档。
12. 后端运行说明。
13. Gunicorn 后端运行配置说明。
14. 数据库初始化说明。

---

## 10. 验收标准

成员 A 的工作完成后，应满足以下标准：

1. 后端项目可以正常启动。
2. Django 能成功连接 MySQL。
3. 用户可以正常注册和登录。
4. 学生和教师权限区分正确。
5. 教师可以创建、编辑、发布课程。
6. 学生可以加入课程。
7. 学生可以观看已加入课程的章节内容。
8. 视频学习进度可以正常保存。
9. 教师可以创建考试和题目。
10. 学生可以提交考试。
11. 客观题可以自动判分。
12. 学生无法重复提交同一场考试。
13. 教师可以查看自己课程下的成绩。
14. 未授权访问会被后端拦截。
15. 核心接口能被前端成功调用。
16. 主要列表接口支持分页。
17. 后端可以通过 Gunicorn 运行。
18. 项目文档中包含数据库和接口说明。

---

## 11. 开发优先级

### 第一优先级

1. 后端项目搭建。
2. MySQL 连接。
3. 用户注册登录。
4. 权限控制。
5. 课程管理。
6. 章节管理。
7. 学生选课。

### 第二优先级

1. 学习进度。
2. 在线考试。
3. 自动判分。
4. 成绩查询。
5. 教师成绩管理。

### 第三优先级

1. 接口性能优化。
2. 事务处理。
3. Gunicorn 配置。
4. API 文档完善。
5. 协助部署联调。

---

## 12. 风险与解决方案

| 风险 | 解决方案 |
|---|---|
| 后端模块过多，开发压力大 | 优先完成课程、考试、进度，论坛和报告由成员 C 分担 |
| 接口频繁变化影响前端 | 先制定接口文档，变更时及时通知 |
| MySQL 表关系复杂 | 先完成核心表，不提前设计过度复杂字段 |
| 考试重复提交 | 使用唯一约束和事务 |
| 权限漏洞 | 所有敏感接口后端判断权限 |
| 视频文件过大影响服务 | 限制大小，Nginx 提供媒体文件访问 |

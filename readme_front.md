# Frontend Integration README - P1/P2/P3/P4

This file is the frontend/backend contract for the P1 user-auth, P2 course/chapter, P3 enrollment/progress, and P4 exam/score stages.

Whenever the backend request fields, response fields, URL paths, auth rules, or error messages change, this file must be updated in the same commit.

## Base Rules

- Unified local gateway URL: `http://127.0.0.1:8080`
- Django local upstream URL: `http://127.0.0.1:8000` (frontend should not call this directly)
- All P1 business APIs are under `/api/`
- JSON requests must use `Content-Type: application/json`
- Authenticated requests must include:

```http
Authorization: Bearer <access_token>
```

## Local Nginx Gateway

Frontend integration should use Nginx as the single local entry:

```text
Frontend -> Nginx 8080 -> Django 8000 for /api/
Frontend -> Nginx 8080 -> backend/media for /media/
```

Repository config:

```text
deploy/nginx/nginx.dev.windows.conf
```

Frontend dev proxy target:

```text
VITE_DEV_PROXY_TARGET=http://127.0.0.1:8080
```

Video and material URLs returned by backend should therefore use the Nginx gateway host, for example:

```text
http://127.0.0.1:8080/media/materials/demo.mp4
```

Do not use `http://127.0.0.1:8000/media/...` for video playback during frontend integration, because Django development static serving does not return video range responses required for seeking.

- Successful backend response format:

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

- Common error response format:

```json
{
  "code": 4000,
  "message": "error detail",
  "data": null
}
```

## Error Codes

| code | Meaning |
|---|---|
| `4000` | Bad request, validation error, invalid verification code |
| `4001` | Not authenticated or token invalid |
| `4003` | Permission denied |
| `4040` | Resource not found |
| `4090` | Conflict, duplicate data, cooldown |
| `5000` | Server error, email SMTP error |

## P0 Health Check

### GET `/api/health/`

Use this before frontend/backend integration to confirm the backend is running.

Response:

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "status": "ok",
    "time": "2026-07-07T18:00:00+08:00"
  }
}
```

## P1 APIs

| Method | Path | Auth | Purpose |
|---|---|---|---|
| `POST` | `/api/auth/email-code/send/` | No | Send registration email code |
| `POST` | `/api/auth/register/` | No | Register user |
| `POST` | `/api/auth/login/` | No | Login |
| `POST` | `/api/auth/refresh/` | No | Refresh JWT access token |
| `POST` | `/api/auth/logout/` | Yes | Logout |
| `GET` | `/api/users/me/` | Yes | Get current user |
| `PUT` | `/api/users/me/` | Yes | Update current user profile |

## 1. Send Registration Email Code

### POST `/api/auth/email-code/send/`

Do not call this API with `GET`. Opening this URL directly in the browser address bar sends `GET` and will return `405 Method Not Allowed`.

Recommended request body:

```json
{
  "email": "student@example.com",
  "purpose": "register"
}
```

Frontend-compatible request body:

```json
{
  "registerEmail": "student@example.com",
  "purpose": "register"
}
```

Accepted email field names:

| Field | Status |
|---|---|
| `email` | Recommended |
| `registerEmail` | Supported for current frontend |
| `register_email` | Supported |
| `mail` | Supported |
| `to` | Supported |
| `to_email` | Supported |
| `emailAddress` | Supported |
| `email_address` | Supported |

`purpose` is optional. If sent, it must be:

```json
{
  "purpose": "register"
}
```

Success response:

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

Important frontend behavior:

- Start a 60-second countdown after success.
- The verification code is valid for 5 minutes.
- Do not repeatedly call this API during the cooldown.

Common errors:

```json
{
  "code": 4090,
  "message": "CODE_COOLDOWN",
  "data": null
}
```

```json
{
  "code": 4090,
  "message": "EMAIL_EXISTS",
  "data": null
}
```

```json
{
  "code": 5000,
  "message": "EMAIL_SEND_FAILED",
  "data": null
}
```

## 2. Register

### POST `/api/auth/register/`

Password rule:

- Minimum length: 6 characters
- Frontend should send a confirm password field.
- Backend supports both `confirmPassword` and `password_confirm`.
- If confirm password is sent and does not match `password`, backend rejects the request.

Recommended frontend request body:

```json
{
  "username": "student01",
  "email": "student@example.com",
  "password": "123456",
  "confirmPassword": "123456",
  "role": "student",
  "email_code": "123456"
}
```

Also supported:

```json
{
  "username": "student01",
  "email": "student@example.com",
  "password": "123456",
  "password_confirm": "123456",
  "role": "student",
  "email_code": "123456"
}
```

Fields:

| Field | Required | Type | Notes |
|---|---|---|---|
| `username` | Yes | string | Max length 64, must be unique |
| `email` | Yes | string | Must be valid email, must be unique |
| `password` | Yes | string | Minimum length 6 |
| `confirmPassword` | Recommended | string | Frontend camelCase confirm password |
| `password_confirm` | Supported | string | Backend snake_case confirm password |
| `role` | Yes | string | `student` or `teacher` |
| `email_code` | Yes | string | 6-digit code from email |

Success response:

```json
{
  "code": 0,
  "message": "register success",
  "data": {
    "id": 1,
    "username": "student01",
    "email": "student@example.com",
    "role": "student",
    "avatar_url": null,
    "date_joined": "2026-07-07T18:00:00+08:00",
    "avatar": null,
    "bio": ""
  }
}
```

Confirm password mismatch response:

```json
{
  "code": 4000,
  "message": {
    "password_confirm": [
      "PASSWORD_CONFIRM_MISMATCH"
    ]
  },
  "data": null
}
```

Common errors:

| message | Meaning |
|---|---|
| `USERNAME_EXISTS` | Username already exists |
| `EMAIL_EXISTS` | Email already exists |
| `CODE_NOT_FOUND` | No active verification code |
| `CODE_EXPIRED` | Verification code expired |
| `CODE_INVALID` | Verification code is wrong |
| `CODE_TOO_MANY_ATTEMPTS` | Too many wrong attempts |
| `PASSWORD_CONFIRM_MISMATCH` | Confirm password does not match password |

## 3. Login

### POST `/api/auth/login/`

Request body:

```json
{
  "account": "student01",
  "password": "123456"
}
```

`account` supports username or email.

Success response:

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
      "avatar_url": null,
      "date_joined": "2026-07-07T18:00:00+08:00",
      "avatar": null,
      "bio": ""
    }
  }
}
```

Frontend storage suggestion:

- Store `access` for API requests.
- Store `refresh` only if the frontend implements token refresh.
- Add `Authorization: Bearer <access>` to authenticated requests.

Common error:

```json
{
  "code": 4000,
  "message": {
    "non_field_errors": [
      "INVALID_CREDENTIALS"
    ]
  },
  "data": null
}
```

## 4. Refresh Token

### POST `/api/auth/refresh/`

Request body:

```json
{
  "refresh": "<jwt-refresh-token>"
}
```

Response:

```json
{
  "access": "<new-jwt-access-token>"
}
```

Note: this endpoint currently uses Simple JWT's default response format, so it is not wrapped with `{ "code": 0, "message": "success", "data": ... }`.

## 5. Logout

### POST `/api/auth/logout/`

Headers:

```http
Authorization: Bearer <access_token>
```

Request body: none.

Response:

```json
{
  "code": 0,
  "message": "logout success",
  "data": null
}
```

Current backend logout is stateless JWT logout. Frontend should clear local tokens after success.

## 6. Current User

### GET `/api/users/me/`

Headers:

```http
Authorization: Bearer <access_token>
```

Response:

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "username": "student01",
    "email": "student@example.com",
    "role": "student",
    "avatar_url": null,
    "date_joined": "2026-07-07T18:00:00+08:00",
    "avatar": null,
    "bio": ""
  }
}
```

## 7. Update Current User

### PUT `/api/users/me/`

Headers:

```http
Authorization: Bearer <access_token>
```

JSON request body:

```json
{
  "username": "new_student_name",
  "bio": "My profile"
}
```

Avatar upload should use `multipart/form-data`:

| Field | Type | Notes |
|---|---|---|
| `avatar` | file | Optional avatar image |
| `username` | string | Optional |
| `bio` | string | Optional |

Response fields are the same as `GET /api/users/me/`.

## Frontend Integration Checklist

1. Use `POST`, not `GET`, for `/api/auth/email-code/send/`.
2. For sending email code, prefer `email`; current frontend may use `registerEmail`, which is supported.
3. For register, password minimum length is 6.
4. For register, send `confirmPassword` or `password_confirm`; backend validates mismatch.
5. For login, send `account`, not `username`.
6. For authenticated APIs, include `Authorization: Bearer <access_token>`.
7. Handle `/api/auth/refresh/` separately because its response is Simple JWT default format.
8. If the browser reports CORS errors, check backend `.env` `CORS_ALLOWED_ORIGINS`.

## Local CORS Example

Backend `.env` should include the frontend dev origin:

```env
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

## P2 Course And Chapter APIs

P2 scope:

- Teacher creates, edits, publishes, unpublishes, and soft-deletes own courses.
- Teacher creates, edits, deletes chapters for own courses.
- Teacher uploads one video file and one material file for each chapter.
- Public and student users can only see published courses.
- P3 will add enrollment and learning-progress restrictions. Do not assume P2 includes enroll/progress APIs.

### P2 API Summary

| Method | Path | Auth | Purpose |
|---|---|---|---|
| `GET` | `/api/courses/` | No | Published course list; teacher sees own courses after login |
| `POST` | `/api/courses/` | Teacher/Admin | Create course |
| `GET` | `/api/courses/{course_id}/` | No | Course detail if published; owner teacher can view draft |
| `PUT/PATCH` | `/api/courses/{course_id}/` | Course teacher/Admin | Update course |
| `DELETE` | `/api/courses/{course_id}/` | Course teacher/Admin | Soft-delete course |
| `POST` | `/api/courses/{course_id}/publish/` | Course teacher/Admin | Publish or unpublish course |
| `GET` | `/api/courses/{course_id}/chapters/` | No | Chapter list for visible course |
| `POST` | `/api/courses/{course_id}/chapters/` | Course teacher/Admin | Create chapter |
| `PUT/PATCH` | `/api/chapters/{chapter_id}/` | Course teacher/Admin | Update chapter |
| `DELETE` | `/api/chapters/{chapter_id}/` | Course teacher/Admin | Delete chapter |
| `POST` | `/api/chapters/{chapter_id}/upload-video/` | Course teacher/Admin | Upload chapter video |
| `POST` | `/api/chapters/{chapter_id}/upload-material/` | Course teacher/Admin | Upload chapter material |

### Course Object

```json
{
  "id": 1,
  "title": "Python Basics",
  "description": "Intro course",
  "cover_url": "http://127.0.0.1:8000/media/covers/demo.png",
  "category": "programming",
  "level": "beginner",
  "teacher": {
    "id": 2,
    "username": "teacher01",
    "email": "teacher@example.com"
  },
  "teacher_role": "teacher",
  "is_published": false,
  "published_at": null,
  "chapter_count": 0,
  "created_at": "2026-07-08T10:00:00+08:00",
  "updated_at": "2026-07-08T10:00:00+08:00"
}
```

`level` must be one of `beginner`, `intermediate`, `advanced`.

### 8. Course List

#### GET `/api/courses/`

Query params:

| Param | Required | Notes |
|---|---|---|
| `page` | No | Page number, default `1` |
| `page_size` | No | Default `10`, max `100` |
| `category` | No | Exact category filter |
| `level` | No | `beginner`, `intermediate`, `advanced` |
| `keyword` | No | Search by course title |
| `search` | No | Alias of `keyword` |
| `is_published` | No | Only effective for teacher/admin; `true` or `false` |

Response is paginated. Course items are in `data.results`:

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "count": 1,
    "page": 1,
    "page_size": 10,
    "results": [
      {
        "id": 1,
        "title": "Python Basics",
        "description": "Intro course",
        "cover_url": null,
        "category": "programming",
        "level": "beginner",
        "teacher": {
          "id": 2,
          "username": "teacher01",
          "email": "teacher@example.com"
        },
        "teacher_role": "teacher",
        "is_published": true,
        "published_at": "2026-07-08T10:00:00+08:00",
        "chapter_count": 2,
        "created_at": "2026-07-08T10:00:00+08:00",
        "updated_at": "2026-07-08T10:00:00+08:00"
      }
    ]
  }
}
```

Visibility rule:

- No token/student token: only published and not deleted courses.
- Teacher token: teacher's own not deleted courses, including drafts.
- Admin token: all not deleted courses.

### 9. Create Course

#### POST `/api/courses/`

Headers:

```http
Authorization: Bearer <teacher_access_token>
```

JSON request body:

```json
{
  "title": "Python Basics",
  "description": "Intro course",
  "category": "programming",
  "level": "beginner"
}
```

If uploading a cover at creation/update time, use `multipart/form-data`.

Cover limits:

- Max size: 5 MB
- Extensions: `.jpg`, `.jpeg`, `.png`, `.webp`

Common errors:

| message | Meaning |
|---|---|
| `ONLY_TEACHER_CAN_MANAGE_COURSE` | Student cannot create/manage courses |
| `COURSE_OWNER_REQUIRED` | Teacher is not the owner of this course |
| `COVER_TYPE_NOT_ALLOWED` | Cover extension not allowed |
| `COVER_SIZE_EXCEEDED` | Cover is larger than 5 MB |

### 10. Course Detail

#### GET `/api/courses/{course_id}/`

Visible course returns the same `Course Object` shape.

Draft visibility:

- Owner teacher/admin can view draft courses.
- Students/public users receive `COURSE_NOT_FOUND` for draft or deleted courses.

### 11. Update Course

#### PUT/PATCH `/api/courses/{course_id}/`

Headers:

```http
Authorization: Bearer <teacher_access_token>
```

Request body supports the same fields as create.

### 12. Delete Course

#### DELETE `/api/courses/{course_id}/`

Headers:

```http
Authorization: Bearer <teacher_access_token>
```

This is a soft delete. The course will not appear in course lists after deletion.

### 13. Publish Or Unpublish Course

#### POST `/api/courses/{course_id}/publish/`

Headers:

```http
Authorization: Bearer <teacher_access_token>
```

Publish:

```json
{
  "is_published": true
}
```

Unpublish:

```json
{
  "is_published": false
}
```

If request body is empty, backend treats it as publish.

### Chapter Object

```json
{
  "id": 1,
  "course": 1,
  "title": "Chapter 1",
  "description": "Introduction",
  "order": 1,
  "video": null,
  "material": null,
  "created_at": "2026-07-08T10:00:00+08:00",
  "updated_at": "2026-07-08T10:00:00+08:00"
}
```

When files are uploaded, `video` and `material` contain:

```json
{
  "id": 1,
  "kind": "video",
  "url": "http://127.0.0.1:8000/media/materials/demo.mp4",
  "original_name": "demo.mp4",
  "content_type": "video/mp4",
  "size": 123456,
  "created_at": "2026-07-08T10:00:00+08:00"
}
```

### 14. Chapter List

#### GET `/api/courses/{course_id}/chapters/`

Response `data` is an array of chapter objects.

### 15. Create Chapter

#### POST `/api/courses/{course_id}/chapters/`

Headers:

```http
Authorization: Bearer <teacher_access_token>
```

Request body:

```json
{
  "title": "Chapter 1",
  "description": "Introduction",
  "order": 1
}
```

`order` must be unique inside one course. Duplicate order returns `CHAPTER_ORDER_EXISTS`.

### 16. Update Chapter

#### PUT/PATCH `/api/chapters/{chapter_id}/`

Headers:

```http
Authorization: Bearer <teacher_access_token>
```

Request body:

```json
{
  "title": "Chapter 1 Updated",
  "description": "Updated introduction",
  "order": 2
}
```

### 17. Delete Chapter

#### DELETE `/api/chapters/{chapter_id}/`

Headers:

```http
Authorization: Bearer <teacher_access_token>
```

### 18. Upload Chapter Video

#### POST `/api/chapters/{chapter_id}/upload-video/`

Headers:

```http
Authorization: Bearer <teacher_access_token>
Content-Type: multipart/form-data
```

Form field:

| Field | Required | Notes |
|---|---|---|
| `file` | Yes | Video file |

Video limits:

- Max size: 200 MB
- Extensions: `.mp4`, `.webm`, `.mov`

Common errors:

| message | Meaning |
|---|---|
| `VIDEO_TYPE_NOT_ALLOWED` | Video extension not allowed |
| `VIDEO_SIZE_EXCEEDED` | Video larger than 200 MB |

### 19. Upload Chapter Material

#### POST `/api/chapters/{chapter_id}/upload-material/`

Headers:

```http
Authorization: Bearer <teacher_access_token>
Content-Type: multipart/form-data
```

Form field:

| Field | Required | Notes |
|---|---|---|
| `file` | Yes | Material file |

Material limits:

- Max size: 20 MB
- Extensions: `.pdf`, `.doc`, `.docx`, `.ppt`, `.pptx`, `.xls`, `.xlsx`, `.txt`, `.zip`

Common errors:

| message | Meaning |
|---|---|
| `MATERIAL_TYPE_NOT_ALLOWED` | Material extension not allowed |
| `MATERIAL_SIZE_EXCEEDED` | Material larger than 20 MB |

## P2 Frontend Integration Checklist

1. Course create/update/upload APIs require teacher token.
2. Student token cannot create courses or chapters.
3. Use `multipart/form-data` for `cover`, chapter video, and chapter material.
4. Upload file field name must be exactly `file` for video/material endpoints.
5. Publish and unpublish both use `/api/courses/{course_id}/publish/` with `is_published`.
6. Course list is paginated; read list items from `data.results`.
7. Chapter resource access now follows P3 enrollment rules.

## P3 Enrollment And Learning Progress APIs

P3 scope:

- Student enrolls in published courses.
- Student cannot enroll in the same course twice.
- Student can view own enrolled courses.
- Student can update learning progress only after enrollment.
- `watched_seconds` and `percent` only increase; smaller submitted values will not roll progress back.
- Course total progress is calculated by averaging chapter `percent`; completed chapters count as `100`.
- Teacher can view progress summary for own courses.

### P3 API Summary

| Method | Path | Auth | Purpose |
|---|---|---|---|
| `POST` | `/api/courses/{course_id}/enroll/` | Student | Enroll in published course |
| `GET` | `/api/my/courses/` | Student | List current student's enrolled courses |
| `POST` | `/api/progress/update/` | Student | Update chapter learning progress |
| `GET` | `/api/progress/course/{course_id}/` | Student/Teacher/Admin | Student own progress or teacher course progress summary |
| `GET` | `/api/materials/{material_id}/download/` | Student/Teacher/Admin | Download chapter material file |

### Enrollment Object

```json
{
  "id": 1,
  "course": {
    "id": 1,
    "title": "Python Basics",
    "description": "Intro course",
    "cover_url": null,
    "category": "programming",
    "level": "beginner",
    "teacher": {
      "id": 2,
      "username": "teacher01",
      "email": "teacher@example.com"
    },
    "teacher_role": "teacher",
    "is_published": true,
    "published_at": "2026-07-08T10:00:00+08:00",
    "chapter_count": 2,
    "created_at": "2026-07-08T10:00:00+08:00",
    "updated_at": "2026-07-08T10:00:00+08:00"
  },
  "progress": 0,
  "enrolled_at": "2026-07-08T10:10:00+08:00",
  "last_learned_at": null
}
```

### 20. Enroll Course

#### POST `/api/courses/{course_id}/enroll/`

Headers:

```http
Authorization: Bearer <student_access_token>
```

Request body: none.

Success response:

```json
{
  "code": 0,
  "message": "enrolled",
  "data": {
    "id": 1,
    "course": {},
    "progress": 0,
    "enrolled_at": "2026-07-08T10:10:00+08:00",
    "last_learned_at": null
  }
}
```

Common errors:

| message | Meaning |
|---|---|
| `ONLY_STUDENT_CAN_ENROLL` | Teacher/admin cannot use student enrollment endpoint |
| `COURSE_NOT_FOUND` | Course does not exist, is deleted, or is not published |
| `ALREADY_ENROLLED` | Student already enrolled in this course |

### 21. My Courses

#### GET `/api/my/courses/`

Headers:

```http
Authorization: Bearer <student_access_token>
```

Query params:

| Param | Required | Notes |
|---|---|---|
| `page` | No | Page number, default `1` |
| `page_size` | No | Default `10`, max `100` |

Response is paginated. Enrollment items are in `data.results`.

### 22. Update Learning Progress

#### POST `/api/progress/update/`

Headers:

```http
Authorization: Bearer <student_access_token>
```

Request body:

```json
{
  "course_id": 1,
  "chapter_id": 1,
  "watched_seconds": 120,
  "percent": 35,
  "is_completed": false
}
```

Fields:

| Field | Required | Notes |
|---|---|---|
| `course_id` | No | If sent, must match the chapter's course |
| `chapter_id` | Yes | Chapter being watched |
| `watched_seconds` | Yes | Non-negative integer; backend keeps max value |
| `percent` | No | Number from `0` to `100`; backend keeps max value |
| `is_completed` | No | If `true`, marks this chapter completed |

Success response:

```json
{
  "code": 0,
  "message": "progress updated",
  "data": {
    "progress": 35,
    "enrollment": {},
    "progress_item": {
      "id": 1,
      "course": 1,
      "chapter": {
        "id": 1,
        "course": 1,
        "title": "Chapter 1",
        "description": "Introduction",
        "order": 1
      },
      "watched_seconds": 120,
      "percent": 35,
      "is_completed": false,
      "updated_at": "2026-07-08T10:20:00+08:00"
    },
    "chapter_progress": []
  }
}
```

Important behavior:

- If frontend first submits `watched_seconds: 120`, then later submits `60`, backend keeps `120`.
- If frontend first submits `percent: 35`, then later submits `20`, backend keeps `35`.
- If frontend submits `is_completed: true`, the chapter stays completed and its `percent` becomes `100`.
- Backend recalculates enrollment `progress` after every update by averaging all chapter percentages.

Common errors:

| message | Meaning |
|---|---|
| `ENROLLMENT_REQUIRED` | Student has not enrolled in this course |
| `CHAPTER_NOT_FOUND` | Chapter does not exist or course is unavailable |
| `CHAPTER_NOT_IN_COURSE` | Submitted `course_id` does not match chapter |

### 23. Course Progress

#### GET `/api/progress/course/{course_id}/`

Student response:

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "course_id": 1,
    "student_id": 3,
    "progress": 50.0,
    "enrollment": {},
    "progress_items": [
      {
        "id": 1,
        "course": 1,
        "chapter": {},
        "chapter_id": 1,
        "watched_seconds": 120,
        "percent": 50,
        "is_completed": false,
        "updated_at": "2026-07-08T10:20:00+08:00"
      }
    ],
    "chapter_progress": [
      {
        "id": 1,
        "course": 1,
        "chapter": {},
        "chapter_id": 1,
        "watched_seconds": 120,
        "percent": 50,
        "is_completed": false,
        "updated_at": "2026-07-08T10:20:00+08:00"
      }
    ]
  }
}
```

`chapter_progress` is an alias of `progress_items` for frontend compatibility.

Teacher/Admin response:

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "course_id": 1,
    "course_title": "Python Basics",
    "student_count": 1,
    "students": [
      {
        "student": {
          "id": 3,
          "username": "student01",
          "email": "student@example.com"
        },
        "progress": 50.0,
        "enrolled_at": "2026-07-08T10:10:00+08:00",
        "last_learned_at": "2026-07-08T10:20:00+08:00"
      }
    ]
  }
}
```

### 24. Download Chapter Material

#### GET `/api/materials/{material_id}/download/`

Headers:

```http
Authorization: Bearer <access_token>
```

Frontend request:

```js
request.get(`/materials/${materialId}/download/`, {
  responseType: 'blob'
})
```

Response:

- This endpoint returns the raw file stream, not the unified JSON wrapper.
- Browser response headers include `Content-Disposition: attachment`.
- The frontend should create a Blob URL and trigger download.

Permission rule:

- Student can download only after enrolling in the material's course.
- Course teacher/admin can download materials for accessible courses.
- Only chapter material files are downloadable through this endpoint; videos still use the returned `/media/` URL for playback.

Common errors:

| message | Meaning |
|---|---|
| `MATERIAL_NOT_FOUND` | Material does not exist, is not a document material, or belongs to an unavailable course |
| `MATERIAL_FILE_NOT_FOUND` | Database record exists but local file is missing |
| `ENROLLMENT_REQUIRED` | Student has not enrolled in this course |
| `PERMISSION_DENIED` | Current role cannot access this material |

### P3 Resource Access Rule

`GET /api/courses/{course_id}/chapters/` now requires:

- course teacher/admin, or
- student already enrolled in the course.

Unauthenticated users or unenrolled students cannot obtain chapter video/material URLs.

## P3 Frontend Integration Checklist

1. Show enroll button only for student users, but still rely on backend permission.
2. After enrollment succeeds, call `/api/courses/{course_id}/chapters/` to load learning resources.
3. Submit progress periodically with `chapter_id` and `watched_seconds`.
4. Send `is_completed: true` when the chapter is completed.
5. Render course progress from enrollment `progress`.
6. Treat `ENROLLMENT_REQUIRED` as "please enroll first".
7. Load video URLs through the Nginx gateway `/media/` address, not Django `8000`, so browser seeking receives `206 Partial Content`.

## P4 Exam And Score APIs

P4 scope:

- Teacher/admin creates exams for own accessible courses.
- Teacher/admin manages questions and can view submissions.
- Student can list and take exams only after enrolling in the course.
- Student exam detail never returns `answer`.
- Student submits answers only; backend calculates score transactionally.
- Each student can submit the same exam only once.

### P4 API Summary

| Method | Path | Auth | Purpose |
|---|---|---|---|
| `GET` | `/api/courses/{course_id}/exams/` | Student/Teacher/Admin | List course exams |
| `POST` | `/api/courses/{course_id}/exams/` | Course teacher/Admin | Create exam |
| `GET` | `/api/exams/{exam_id}/` | Student/Teacher/Admin | Exam detail and questions |
| `PUT/PATCH` | `/api/exams/{exam_id}/` | Course teacher/Admin | Update exam |
| `DELETE` | `/api/exams/{exam_id}/` | Course teacher/Admin | Delete exam |
| `POST` | `/api/exams/{exam_id}/questions/` | Course teacher/Admin | Create question |
| `PUT/PATCH` | `/api/questions/{question_id}/` | Course teacher/Admin | Update question |
| `DELETE` | `/api/questions/{question_id}/` | Course teacher/Admin | Delete question |
| `POST` | `/api/exams/{exam_id}/submit/` | Student | Submit exam answers |
| `GET` | `/api/my/scores/` | Student | List my scores |
| `GET` | `/api/exams/{exam_id}/submissions/` | Course teacher/Admin | List exam submissions |

### Exam Object

```json
{
  "id": 1,
  "course": 1,
  "title": "Chapter Quiz",
  "description": "Basic quiz",
  "total_score": 100,
  "duration_minutes": 60,
  "is_published": true,
  "start_time": null,
  "end_time": null,
  "question_count": 2,
  "submitted": false,
  "score": null,
  "created_at": "2026-07-08T10:00:00+08:00",
  "updated_at": "2026-07-08T10:00:00+08:00"
}
```

For teacher/admin, `submitted` is always `false` and `score` is `null`. For students, these fields show the current student's exam state.

### Question Object

Teacher/admin response includes `answer`:

```json
{
  "id": 1,
  "exam": 1,
  "question_type": "single",
  "content": "Which option is correct?",
  "options": ["A", "B", "C", "D"],
  "answer": ["A"],
  "score": 10,
  "order": 1,
  "created_at": "2026-07-08T10:00:00+08:00",
  "updated_at": "2026-07-08T10:00:00+08:00"
}
```

Student response removes `answer`:

```json
{
  "id": 1,
  "exam": 1,
  "question_type": "single",
  "content": "Which option is correct?",
  "options": ["A", "B", "C", "D"],
  "score": 10,
  "order": 1,
  "created_at": "2026-07-08T10:00:00+08:00",
  "updated_at": "2026-07-08T10:00:00+08:00"
}
```

Supported `question_type` values:

| Value | Meaning | Answer example |
|---|---|---|
| `single` | Single choice | `["A"]` |
| `multiple` | Multiple choice | `["A", "C"]` |
| `true_false` | True or false | `["true"]` |
| `fill` | Fill in the blank | `["Django"]` |

### 25. Course Exam List

#### GET `/api/courses/{course_id}/exams/`

Headers:

```http
Authorization: Bearer <access_token>
```

Response is paginated. Exam items are in `data.results`.

Permission rule:

- Student must be enrolled and only sees published exams.
- Course teacher/admin can see all exams in the course.

### 26. Create Exam

#### POST `/api/courses/{course_id}/exams/`

Headers:

```http
Authorization: Bearer <teacher_access_token>
```

Request body:

```json
{
  "title": "Chapter Quiz",
  "description": "Basic quiz",
  "total_score": 100,
  "duration_minutes": 60,
  "is_published": false,
  "start_time": null,
  "end_time": null
}
```

### 27. Exam Detail

#### GET `/api/exams/{exam_id}/`

Student response includes `questions`, but every question hides `answer`.

Teacher/admin response includes `questions` with `answer`.

### 28. Create Question

#### POST `/api/exams/{exam_id}/questions/`

Headers:

```http
Authorization: Bearer <teacher_access_token>
```

Request body:

```json
{
  "question_type": "single",
  "content": "Which option is correct?",
  "options": ["A", "B", "C", "D"],
  "answer": ["A"],
  "score": 10,
  "order": 1
}
```

`order` must be unique inside one exam. Duplicate order returns `QUESTION_ORDER_EXISTS`.

### 29. Submit Exam

#### POST `/api/exams/{exam_id}/submit/`

Headers:

```http
Authorization: Bearer <student_access_token>
```

Request body:

```json
{
  "answers": {
    "1": ["A"],
    "2": ["A", "C"],
    "3": ["true"]
  }
}
```

The keys inside `answers` are `question_id` strings. A single answer may be sent as a scalar or list; backend normalizes it to a list.

Success response:

```json
{
  "code": 0,
  "message": "exam submitted",
  "data": {
    "id": 1,
    "exam": 1,
    "exam_title": "Chapter Quiz",
    "course_id": 1,
    "course_title": "Python Basics",
    "student": {
      "id": 3,
      "username": "student01",
      "email": "student@example.com"
    },
    "answers": {
      "1": {
        "answer": ["A"],
        "is_correct": true,
        "score": 10.0
      }
    },
    "score": 10.0,
    "submitted_at": "2026-07-08T10:30:00+08:00"
  }
}
```

Important behavior:

- Backend does not trust frontend score.
- Backend compares normalized answer arrays.
- Same student can submit the same exam only once.
- If `start_time` is in the future, backend returns `EXAM_NOT_STARTED`.
- If `end_time` has passed, backend returns `EXAM_ENDED`.

Common errors:

| message | Meaning |
|---|---|
| `ENROLLMENT_REQUIRED` | Student has not enrolled in the course |
| `EXAM_NOT_FOUND` | Exam does not exist or is not visible |
| `EXAM_NOT_STARTED` | Exam has not started |
| `EXAM_ENDED` | Exam has ended |
| `EXAM_ALREADY_SUBMITTED` | Student already submitted this exam |
| `QUESTION_ORDER_EXISTS` | Question order already exists in the exam |

### 30. My Scores

#### GET `/api/my/scores/`

Headers:

```http
Authorization: Bearer <student_access_token>
```

Response is paginated. Score items are in `data.results`.

### 31. Exam Submissions

#### GET `/api/exams/{exam_id}/submissions/`

Headers:

```http
Authorization: Bearer <teacher_access_token>
```

Only the course teacher/admin can view submissions.

### P4 Frontend Integration Checklist

1. Use `GET /api/courses/{course_id}/exams/` after enrollment to show exams.
2. Student exam page must render questions from `GET /api/exams/{exam_id}/`; do not expect `answer`.
3. Submit only `answers`; never calculate or send final score as trusted data.
4. Treat `EXAM_ALREADY_SUBMITTED` as "already submitted"; then load `/api/my/scores/`.
5. Teacher/admin question management should keep `order` unique inside each exam.

## Maintenance Rule

When backend auth/user/course/chapter/enrollment/progress/exam APIs change, update this file in the same commit. This includes:

- URL path changes
- Request field changes
- Accepted alias field changes
- Response field changes
- Error code or message changes
- Authentication or permission changes
- Validation rule changes, especially password and verification-code rules

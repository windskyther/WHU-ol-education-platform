# Frontend Integration README - P1

This file is the frontend/backend contract for the P1 user-auth stage.

Whenever the backend request fields, response fields, URL paths, auth rules, or error messages change, this file must be updated in the same commit.

## Base Rules

- Backend base URL in local development: `http://127.0.0.1:8000`
- All P1 business APIs are under `/api/`
- JSON requests must use `Content-Type: application/json`
- Authenticated requests must include:

```http
Authorization: Bearer <access_token>
```

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

## Maintenance Rule

When backend P1 auth/user APIs change, update this file in the same commit. This includes:

- URL path changes
- Request field changes
- Accepted alias field changes
- Response field changes
- Error code or message changes
- Authentication or permission changes
- Validation rule changes, especially password and verification-code rules

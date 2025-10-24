# User API Routes Documentation

## Overview
The user management API provides endpoints for authenticated users to manage their own profiles, including viewing, updating, and deleting their accounts. All endpoints require authentication via JWT tokens.

## Base URL
All user endpoints are prefixed with `/api/users`

## Authentication
All user endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### 1. Get Current User Profile
**GET** `/api/users/me`

Retrieves the current authenticated user's profile information.

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-09-04T10:00:00Z",
  "updated_at": "2025-09-04T10:30:00Z"
}
```

### 2. Update Current User Profile
**PUT** `/api/users/me`

Updates the current authenticated user's profile information.

**Request Body:**
```json
{
  "email": "newemail@example.com",
  "username": "newusername",
  "full_name": "New Full Name",
  "is_active": true
}
```

**Response (200 OK):**
Returns the updated user profile object.

**Validation Rules:**
- Email must be unique across all users
- Username must be unique across all users
- All fields are optional - only provided fields will be updated

### 3. Change Password
**POST** `/api/users/me/change-password`

Changes the current user's password.

**Request Body:**
```json
{
  "current_password": "oldpassword123",
  "new_password": "newpassword123"
}
```

**Response (200 OK):**
```json
{
  "detail": "Password changed successfully"
}
```

**Validation Rules:**
- Current password must be correct
- New password must be at least 8 characters long

### 4. Delete Current User Account
**DELETE** `/api/users/me`

Deletes the current authenticated user's account permanently.

**Response (200 OK):**
```json
{
  "detail": "User account deleted successfully"
}
```

**Important Notes:**
- This action is irreversible
- All associated data (notes, reminders) will be affected
- Consider implementing a soft delete or confirmation step in production

## Error Responses

All endpoints may return the following error responses:

**400 Bad Request:**
```json
{
  "detail": "Email already registered"
}
```
```json
{
  "detail": "Username already taken"
}
```
```json
{
  "detail": "Current password is incorrect"
}
```
```json
{
  "detail": "New password must be at least 8 characters long"
}
```

**401 Unauthorized:**
```json
{
  "detail": "Invalid authentication credentials"
}
```

**404 Not Found:**
```json
{
  "detail": "User not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Failed to delete user account"
}
```

## Security Features

- **Authentication Required**: All endpoints require valid JWT authentication
- **Self-Service Only**: Users can only manage their own profiles
- **Input Validation**: Comprehensive validation of all input data
- **Password Security**: Secure password hashing and verification
- **Uniqueness Validation**: Email and username uniqueness enforcement
- **SQL Injection Protection**: Uses parameterized queries

## Business Rules

- Users can only modify their own profile information
- Email and username must be unique across the system
- Password changes require verification of the current password
- Account deletion is permanent and should be used with caution
- All profile updates are tracked with timestamps

## Integration Notes

- All datetime fields use ISO 8601 format with timezone information
- Password changes invalidate existing sessions (consider implementing token refresh)
- Consider implementing email verification for email changes in production
- Profile updates should trigger appropriate notifications or audit logs
- Account deletion should cascade to related data or implement soft deletion

## Related Endpoints

- **POST** `/api/auth/register` - User registration
- **POST** `/api/auth/login` - User authentication
- **POST** `/api/auth/refresh` - Token refresh
- **GET** `/api/auth/me` - Get current user info (from auth routes)

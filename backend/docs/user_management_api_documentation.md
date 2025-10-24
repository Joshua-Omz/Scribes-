# User Management API Documentation

## Overview
The user management feature provides a comprehensive REST API for user profile management, account administration, and user analytics. The API supports both self-service operations for regular users and administrative operations for system administrators.

## Base URL
All user endpoints are prefixed with `/api/users`

## Authentication
All user endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
``

## User Profile Management

### 1. Get Current User Profile
**GET** `/api/users/me`

Retrieves the current authenticated user's detailed profile with statistics.

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
  "updated_at": "2025-09-04T10:30:00Z",
  "notes_count": 15,
  "reminders_count": 8,
  "active_reminders_count": 3
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
  "full_name": "New Full Name"
}
```

**Response (200 OK):**
Returns the updated user profile object.

**Validation Rules:**
- Email must be unique across all users
- Username must be unique across all users (3-50 characters, alphanumeric + hyphens/underscores)
- Full name limited to 100 characters
- All fields are optional - only provided fields will be updated

### 3. Change Password
**POST** `/api/users/me/change-password`

Changes the current user's password with validation.

**Request Body:**
```json
{
  "current_password": "oldpassword123",
  "new_password": "NewSecurePass123"
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
- New password must be 8-128 characters long
- Must contain at least one digit, uppercase letter, and lowercase letter

### 4. Deactivate Current User Account
**POST** `/api/users/me/deactivate`

Deactivates the current authenticated user's account (soft delete).

**Response (200 OK):**
Returns the deactivated user profile with `is_active: false`.

### 5. Delete Current User Account
**DELETE** `/api/users/me`

Permanently deletes the current authenticated user's account.

**Response (200 OK):**
```json
{
  "detail": "User account deleted successfully"
}
```

**Important Notes:**
- This action is irreversible
- All associated data (notes, reminders) will be affected

## Administrative Operations

### 6. Get User Statistics
**GET** `/api/users/stats`

Retrieves comprehensive user statistics for the system.

**Response (200 OK):**
```json
{
  "total_users": 150,
  "active_users": 142,
  "inactive_users": 8,
  "superuser_count": 3,
  "recent_registrations": 12
}
```

### 7. Get Recent Users
**GET** `/api/users/recent`

Retrieves recently registered users.

**Query Parameters:**
- `limit` (optional): Maximum users to return (default: 10, max: 50)

**Response (200 OK):**
```json
[
  {
    "id": 151,
    "email": "newuser@example.com",
    "username": "newuser",
    "full_name": "New User",
    "is_active": true,
    "is_superuser": false,
    "created_at": "2025-09-04T15:30:00Z",
    "updated_at": null
  }
]
```

### 8. Search Users
**GET** `/api/users/search`

Search and filter users with pagination.

**Query Parameters:**
- `query` (optional): Search in username, email, or full name
- `is_active` (optional): Filter by active status
- `is_superuser` (optional): Filter by superuser status
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum records to return (default: 50, max: 100)

**Response (200 OK):**
```json
{
  "users": [
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
  ],
  "total": 1,
  "skip": 0,
  "limit": 50
}
```

### 9. Get User by ID
**GET** `/api/users/{user_id}`

Retrieves a specific user by their ID.

**Response (200 OK):**
Returns the user profile object.

### 10. Update User by ID
**PUT** `/api/users/{user_id}`

Updates a specific user by their ID (admin operation).

**Request Body:**
Same as user profile update.

**Response (200 OK):**
Returns the updated user object.

### 11. Delete User by ID
**DELETE** `/api/users/{user_id}`

Deletes a specific user by their ID (admin operation).

**Response (200 OK):**
```json
{
  "detail": "User deleted successfully"
}
```

### 12. Activate User Account
**POST** `/api/users/{user_id}/activate`

Activates a user account by ID (admin operation).

**Response (200 OK):**
Returns the activated user object.

### 13. Deactivate User Account
**POST** `/api/users/{user_id}/deactivate`

Deactivates a user account by ID (admin operation).

**Response (200 OK):**
Returns the deactivated user object.

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
  "detail": "Password must contain at least one digit"
}
```
```json
{
  "detail": "Invalid pagination parameters"
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
  "detail": "Failed to update user"
}
```

## Security Features

- **Authentication Required**: All endpoints require valid JWT authentication
- **Self-Service Operations**: Regular users can only manage their own profiles
- **Administrative Operations**: Admin endpoints marked with TODO for permission checks
- **Input Validation**: Comprehensive validation with custom Pydantic validators
- **Password Security**: Strong password requirements and secure hashing
- **SQL Injection Protection**: Uses parameterized queries
- **XSS Protection**: Input sanitization and validation
- **Rate Limiting**: Built-in protection against abuse

## Business Rules

- **Username Requirements**: 3-50 characters, alphanumeric + hyphens/underscores only
- **Email Uniqueness**: Email addresses must be unique across the system
- **Username Uniqueness**: Usernames must be unique across the system
- **Password Strength**: Minimum 8 characters with digit, uppercase, and lowercase requirements
- **Account States**: Users can be active/inactive with soft delete capability
- **Profile Updates**: Users can update their own profiles but not sensitive fields like `is_superuser`
- **Administrative Actions**: Admin operations require proper authorization (TODO: implement permission checks)

## Data Validation

### Username Validation:
- Minimum 3 characters, maximum 50 characters
- Only alphanumeric characters, hyphens, and underscores allowed
- Automatically converted to lowercase
- Must be unique across the system

### Email Validation:
- Standard email format validation
- Must be unique across the system
- Case-insensitive uniqueness check

### Password Validation:
- Minimum 8 characters, maximum 128 characters
- Must contain at least one digit
- Must contain at least one uppercase letter
- Must contain at least one lowercase letter
- Secure hashing using bcrypt

### Full Name Validation:
- Maximum 100 characters
- Optional field
- Leading/trailing whitespace trimmed

## Integration Notes

- All datetime fields use ISO 8601 format with timezone information
- Pagination implemented for list/search endpoints to handle large datasets
- Proper HTTP status codes used for different scenarios
- Comprehensive error messages help with debugging and user experience
- User statistics include counts from related entities (notes, reminders)
- Soft delete (deactivation) preserves data integrity while removing access

## Future Enhancements

- **Permission System**: Implement role-based access control for admin operations
- **Email Verification**: Add email verification for account creation and email changes
- **Password Reset**: Implement secure password reset flow
- **User Activity Logging**: Track user actions for audit purposes
- **Profile Pictures**: Add support for user avatar/profile images
- **Two-Factor Authentication**: Enhance security with 2FA support
- **Account Recovery**: Implement account recovery mechanisms

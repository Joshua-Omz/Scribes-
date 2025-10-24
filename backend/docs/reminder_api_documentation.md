# Reminder API Routes Documentation

## Overview
The reminder feature provides a complete REST API for managing user reminders associated with notes. All endpoints require authentication via JWT tokens.

## Base URL
All reminder endpoints are prefixed with `/api/reminders`

## Authentication
All reminder endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### 1. Create Reminder
**POST** `/api/reminders/`

Creates a new reminder for a note.

**Request Body:**
```json
{
  "scheduled_at": "2025-09-10T15:30:00Z",
  "note_id": 1
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "user_id": 123,
  "note_id": 1,
  "scheduled_at": "2025-09-10T15:30:00Z",
  "status": "pending",
  "created_at": "2025-09-04T10:00:00Z",
  "updated_at": null
}
```

**Validation Rules:**
- `scheduled_at` must be in the future
- `note_id` must exist and belong to the authenticated user
- Cannot create duplicate reminders for the same note at the same time

### 2. Get Reminder by ID
**GET** `/api/reminders/{reminder_id}`

Retrieves a specific reminder by its ID.

**Response (200 OK):**
```json
{
  "id": 1,
  "user_id": 123,
  "note_id": 1,
  "scheduled_at": "2025-09-10T15:30:00Z",
  "status": "pending",
  "created_at": "2025-09-04T10:00:00Z",
  "updated_at": null
}
```

### 3. Get User Reminders
**GET** `/api/reminders/`

Retrieves paginated list of user's reminders with optional filtering.

**Query Parameters:**
- `status_filter` (optional): Filter by status (`pending`, `sent`, `cancelled`)
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum records to return (default: 50, max: 100)

**Response (200 OK):**
```json
{
  "reminders": [
    {
      "id": 1,
      "user_id": 123,
      "note_id": 1,
      "scheduled_at": "2025-09-10T15:30:00Z",
      "status": "pending",
      "created_at": "2025-09-04T10:00:00Z",
      "updated_at": null
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 50,
  "status_filter": null
}
```

### 4. Update Reminder
**PUT** `/api/reminders/{reminder_id}`

Updates an existing reminder.

**Request Body:**
```json
{
  "scheduled_at": "2025-09-11T16:00:00Z",
  "status": "pending"
}
```

**Response (200 OK):**
Returns the updated reminder object.

**Validation Rules:**
- Cannot update `scheduled_at` for sent reminders
- Status must be one of: `pending`, `sent`, `cancelled`
- If `scheduled_at` is provided, it must be in the future

### 5. Delete Reminder
**DELETE** `/api/reminders/{reminder_id}`

Deletes a reminder.

**Response (204 No Content):**
```json
{
  "detail": "Reminder deleted successfully"
}
```

**Business Rules:**
- Cannot delete sent reminders

### 6. Cancel Reminder
**POST** `/api/reminders/{reminder_id}/cancel`

Cancels a pending reminder by changing its status to "cancelled".

**Response (200 OK):**
Returns the updated reminder with status "cancelled".

**Business Rules:**
- Only pending reminders can be cancelled

### 7. Get Upcoming Reminders
**GET** `/api/reminders/upcoming/list`

Retrieves upcoming pending reminders for the user.

**Query Parameters:**
- `limit` (optional): Maximum reminders to return (default: 10, max: 50)

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "user_id": 123,
    "note_id": 1,
    "scheduled_at": "2025-09-10T15:30:00Z",
    "status": "pending",
    "created_at": "2025-09-04T10:00:00Z",
    "updated_at": null
  }
]
```

## Error Responses

All endpoints may return the following error responses:

**400 Bad Request:**
```json
{
  "detail": "Invalid reminder ID"
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
  "detail": "Reminder not found or access denied"
}
```

**409 Conflict:**
```json
{
  "detail": "A reminder for this note at this time already exists"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Failed to create reminder"
}
```

## Security Features

- **Authentication Required**: All endpoints require valid JWT authentication
- **Authorization**: Users can only access their own reminders
- **Input Validation**: Comprehensive validation of all input data
- **SQL Injection Protection**: Uses parameterized queries
- **XSS Protection**: Input sanitization and validation
- **Rate Limiting**: Built-in protection against abuse

## Business Rules

- Reminders must be scheduled for future dates
- Reminders cannot be scheduled more than 365 days in the future
- Users can only create reminders for notes they own
- Duplicate reminders for the same note at the same time are not allowed
- Sent reminders cannot be modified or deleted
- Only pending reminders can be cancelled

## Integration Notes

- All datetime fields use ISO 8601 format with timezone information
- The API uses pagination for list endpoints to handle large datasets efficiently
- Proper HTTP status codes are used for different scenarios
- Comprehensive error messages help with debugging and user experience

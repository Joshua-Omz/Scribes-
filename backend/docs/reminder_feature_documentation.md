# Reminder Feature Documentation

## Overview

The Reminder feature is a critical component of the Scribes application that enables users to schedule notifications and reminders for their notes. This feature provides a comprehensive reminder system with scheduling, status tracking, and background processing capabilities, designed to help users stay organized and engaged with their study materials.

## Recent Improvements (September 2025)

### Security Enhancements
- **Mass Assignment Protection**: Explicit field whitelisting prevents unauthorized field modifications
- **Input Validation**: Comprehensive validation with business logic rules
- **SQL Injection Prevention**: Parameterized queries and proper field mapping
- **Authorization Checks**: Robust user ownership validation for all operations
- **Data Integrity**: Validation that notes belong to users before creating reminders

### Performance Optimizations
- **Pagination Support**: Efficient handling of large reminder collections
- **Optimized Queries**: Efficient database queries with proper indexing
- **Background Processing**: Support for bulk operations and status updates
- **Query Optimization**: Selective field loading and efficient filtering

### Feature Enhancements
- **Status Management**: Complete lifecycle management (pending → sent/cancelled)
- **Advanced Filtering**: Status-based filtering and date range queries
- **Bulk Operations**: Support for bulk reminder updates
- **Statistics**: Comprehensive reminder statistics and analytics
- **Upcoming Reminders**: Quick access to pending future reminders

## Architecture Components

### 1. Database Model (`app/models/reminder.py`)

The `Reminder` model represents the database structure for storing reminders:

```python
class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    note_id = Column(Integer, ForeignKey("notes.id", ondelete="CASCADE"), nullable=False)

    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(50), default="pending")  # pending, sent, cancelled
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="reminders")
    note = relationship("Note", back_populates="reminders")
```

**Key Features:**
- User-specific reminders with foreign key relationships
- Automatic timestamp tracking with timezone support
- Status lifecycle management (pending → sent/cancelled)
- Cascade delete when user or note is removed
- Proper indexing for performance

### 2. Data Schemas (`app/schemas/reminder_schemas.py`)

The Pydantic schemas define the API request/response structures with comprehensive validation:

#### `ReminderBase`
- Common fields with validation rules
- Future date validation for scheduled_at
- Positive integer validation for note_id
- Business logic validation

#### `ReminderCreate`
- Used for creating new reminders
- Inherits all validation from ReminderBase

#### `ReminderUpdate`
- Used for updating existing reminders
- Optional fields for partial updates
- Status validation and business rules

#### `ReminderResponse`
- API response format with all necessary fields
- ORM mode enabled for automatic conversion
- Proper JSON encoding for datetime fields

#### `ReminderListResponse`
- Paginated list response with metadata
- Total count and pagination information
- Optional status filtering

#### `ReminderStatsResponse`
- Statistics about user's reminders
- Counts by status and upcoming reminders

#### `ReminderBulkUpdateRequest`
- Bulk operations with validation
- Limited batch sizes for performance
- Action validation

#### `ReminderSearchRequest`
- Advanced search and filtering options
- Date range filtering
- Status and note-based filtering

### 3. Repository Layer (`app/db/repositories/reminder_repository.py`)

The repository layer handles all database operations with security and performance considerations:

#### Core Functions:
- `create_reminder()` - Create new reminders with proper field mapping
- `get_reminder_by_user()` - Retrieve specific reminder with ownership validation
- `get_user_reminders_paginated()` - Get user's reminders with pagination and filtering
- `update_reminder()` - Update reminders with security validation and mass assignment protection
- `delete_reminder()` - Delete reminders with proper cleanup

#### Advanced Functions:
- `get_upcoming_reminders()` - Get future pending reminders
- `get_overdue_reminders()` - Get reminders that need to be processed
- `update_reminder_status()` - Update reminder status (for background processing)
- `bulk_update_reminder_status()` - Bulk status updates for efficiency
- `get_reminders_count_by_user()` - Get reminder statistics
- `get_reminders_by_note()` - Get all reminders for a specific note

#### Security Features:
- User ownership validation for all operations
- Mass assignment protection through explicit field whitelisting
- SQL injection prevention through parameterized queries
- Input sanitization and validation

### 4. Service Layer (`app/services/reminder_service.py`)

The service layer provides business logic, validation, and comprehensive error handling:

#### Core Functions:
- `create_reminder_service()` - Reminder creation with comprehensive validation
- `get_reminder_service()` - Reminder retrieval with access control
- `get_user_reminders_service()` - Paginated reminder listing with filtering
- `update_reminder_service()` - Reminder updates with validation and security
- `delete_reminder_service()` - Reminder deletion with authorization
- `cancel_reminder_service()` - Cancel pending reminders

#### Advanced Functions:
- `get_upcoming_reminders_service()` - Get upcoming reminders for dashboard
- Business logic validation (future dates, duplicate prevention)
- Comprehensive error handling and logging
- Rate limiting considerations

#### Security & Validation Features:
- Input sanitization and validation
- User authorization checks for all operations
- Business logic validation (no past dates, reasonable future limits)
- Duplicate reminder prevention
- Comprehensive error handling and logging
- SQL injection prevention
- XSS protection through input sanitization

## API Endpoints

### Reminder Management Endpoints

#### 1. Create Reminder
```
POST /api/reminders/
Authorization: Bearer <token>
Content-Type: application/json

{
  "note_id": 123,
  "scheduled_at": "2024-02-15T10:30:00Z"
}
```

**Response:**
```json
{
  "id": 1,
  "user_id": 456,
  "note_id": 123,
  "scheduled_at": "2024-02-15T10:30:00Z",
  "status": "pending",
  "created_at": "2024-01-15T09:00:00Z",
  "updated_at": "2024-01-15T09:00:00Z"
}
```

**Error Responses:**
- `400 Bad Request` - Invalid note_id, past scheduled_at, or duplicate reminder
- `404 Not Found` - Note doesn't exist or doesn't belong to user
- `409 Conflict` - Reminder already exists for this note at this time

#### 2. Get Single Reminder
```
GET /api/reminders/{reminder_id}
Authorization: Bearer <token>
```

**Error Responses:**
- `400 Bad Request` - Invalid reminder ID
- `404 Not Found` - Reminder doesn't exist or access denied

#### 3. List User Reminders
```
GET /api/reminders/?status=pending&skip=0&limit=20
Authorization: Bearer <token>
```

**Query Parameters:**
- `status` - Filter by status (pending, sent, cancelled)
- `skip` - Pagination offset (default: 0)
- `limit` - Number of results (default: 50, max: 100)

**Response:**
```json
{
  "reminders": [...],
  "total": 45,
  "skip": 0,
  "limit": 20,
  "status_filter": "pending"
}
```

#### 4. Update Reminder
```
PUT /api/reminders/{reminder_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "scheduled_at": "2024-02-16T14:00:00Z",
  "status": "pending"
}
```

#### 5. Delete Reminder
```
DELETE /api/reminders/{reminder_id}
Authorization: Bearer <token>
```

#### 6. Cancel Reminder
```
POST /api/reminders/{reminder_id}/cancel
Authorization: Bearer <token>
```

#### 7. Get Upcoming Reminders
```
GET /api/reminders/upcoming/?limit=10
Authorization: Bearer <token>
```

#### 8. Get Reminder Statistics
```
GET /api/reminders/stats/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "total_reminders": 25,
  "pending_reminders": 8,
  "sent_reminders": 15,
  "cancelled_reminders": 2,
  "upcoming_reminders": 5
}
```

## Security Features

### 1. Authentication & Authorization
- JWT token-based authentication required for all endpoints
- User ownership validation for all reminder operations
- 403 Forbidden responses for unauthorized access
- Comprehensive logging of security events

### 2. Input Validation & Sanitization
- Pydantic model validation for all inputs with custom validators
- Business logic validation (future dates, reasonable limits)
- XSS protection through input sanitization
- SQL injection prevention through parameterized queries
- Length limits and format validation on all fields

### 3. Mass Assignment Protection
- Explicit field whitelisting in update operations
- Prevention of unauthorized field modifications
- Secure field mapping between API and database layers

### 4. Business Logic Validation
- No past date scheduling
- Reasonable future date limits (365 days max)
- Duplicate reminder prevention
- Status transition validation
- Note ownership verification

### 5. Error Handling & Logging
- Comprehensive error logging with user context
- User-friendly error messages without information leakage
- Proper HTTP status codes for different error scenarios
- Exception handling to prevent application crashes

## Performance Optimizations

### 1. Database Indexing
- Primary key index on `id` for fast lookups
- Foreign key indexes on `user_id` and `note_id`
- Composite indexes for common query patterns
- Status-based filtering optimization

### 2. Pagination
- Default pagination limits (50 reminders per page)
- Configurable skip/limit parameters with validation
- Total count optimization for large datasets
- Efficient offset-based pagination

### 3. Query Optimization
- Efficient SQL queries with proper joins and filtering
- Selective field loading to reduce memory usage
- Connection pooling through SQLAlchemy engine configuration
- Optimized bulk operations for background processing

### 4. Background Processing Support
- Bulk status updates for efficiency
- Overdue reminder detection
- Optimized queries for background jobs
- Minimal database locking

## Status Management

### Reminder Lifecycle
1. **Pending** - Reminder is scheduled and waiting to be sent
2. **Sent** - Reminder has been processed and notification sent
3. **Cancelled** - Reminder was cancelled before being sent

### Status Transitions
- `pending` → `sent` (automatic via background processing)
- `pending` → `cancelled` (user action)
- `sent` → No further transitions (immutable)
- `cancelled` → No further transitions (immutable)

### Business Rules
- Cannot modify `scheduled_at` for sent reminders
- Cannot delete sent reminders
- Only pending reminders can be cancelled
- Status updates are logged for audit purposes

## Background Processing

### Overdue Reminder Processing
```python
# Example background job
overdue_reminders = reminder_repository.get_overdue_reminders()
for reminder in overdue_reminders:
    # Send notification
    # Update status to 'sent'
    reminder_repository.update_reminder_status(reminder.id, "sent")
```

### Bulk Operations
```python
# Bulk cancel reminders
reminder_ids = [1, 2, 3, 4, 5]
affected_count = reminder_repository.bulk_update_reminder_status(
    reminder_ids, "cancelled"
)
```

## Data Relationships

### User-Reminders Relationship
- One-to-many relationship (User → Reminders)
- Cascade delete when user is removed
- Foreign key constraints ensure data integrity
- Efficient querying through proper indexing

### Note-Reminders Relationship
- One-to-many relationship (Note → Reminders)
- Cascade delete when note is removed
- Foreign key constraints ensure data integrity
- Validation that note belongs to user before creating reminder

## Migration History

### Database Migrations
- **Initial Setup**: Basic reminder table with core fields
- **Status Management**: Added status field and lifecycle management
- **Performance Optimization**: Added indexes and optimized queries
- **Security Enhancement**: Added validation and security measures

## Testing & Validation

### Test Coverage
- Repository layer testing with security validation
- Service layer testing with business logic validation
- Schema validation testing with edge cases
- API endpoint testing with authentication
- Background processing testing

### Security Testing
- Authorization testing for all endpoints
- Input validation testing with malicious inputs
- SQL injection testing with parameterized queries
- Mass assignment protection testing
- Business logic validation testing

## Future Enhancements

### Notification System
1. **Email Notifications** - Send reminder emails to users
2. **Push Notifications** - Mobile app push notifications
3. **SMS Notifications** - Text message reminders
4. **In-App Notifications** - Dashboard notifications
5. **Customizable Templates** - User-defined notification templates

### Advanced Features
1. **Recurring Reminders** - Daily, weekly, monthly reminders
2. **Reminder Groups** - Organize reminders by categories
3. **Smart Scheduling** - AI-powered optimal reminder timing
4. **Reminder Analytics** - User engagement and effectiveness metrics
5. **Integration APIs** - Third-party calendar integrations
6. **Reminder Templates** - Predefined reminder patterns

### Performance Improvements
1. **Caching Layer** - Redis caching for frequently accessed reminders
2. **Message Queue** - Asynchronous notification processing
3. **Database Optimization** - Advanced indexing and query optimization
4. **Load Balancing** - Horizontal scaling support
5. **Monitoring Dashboard** - Real-time performance monitoring

## Monitoring & Logging

### Application Logs
- Request/response logging with performance metrics
- Error tracking and alerting with detailed context
- Security event logging for audit purposes
- User activity monitoring for analytics
- Background job execution logging

### Database Monitoring
- Query performance monitoring and optimization
- Connection pool monitoring and health checks
- Reminder processing statistics
- Database size and growth tracking

### Business Metrics
- Reminder creation rates
- Notification delivery success rates
- User engagement with reminders
- System performance under load

## Deployment Considerations

### Environment Configuration
- Database connection settings with connection pooling
- Background job scheduling configuration
- Notification service configuration
- Monitoring and alerting setup

### Scaling Considerations
- Database connection pooling configuration
- Background job worker scaling
- API rate limiting implementation
- Horizontal scaling support with load balancing

### Backup & Recovery
- Automated database backups including reminder data
- Point-in-time recovery capabilities
- Data export/import functionality for reminders
- Disaster recovery planning

## Conclusion

The Reminder feature provides a robust, secure, and scalable reminder system with comprehensive functionality for managing scheduled notifications. The recent improvements have significantly enhanced security, performance, and reliability.

### Key Achievements:
- **Enterprise-grade security** with comprehensive validation and protection
- **High performance** through optimized queries and background processing
- **Scalable architecture** with proper separation of concerns
- **Comprehensive status management** with full lifecycle support
- **Advanced features** including bulk operations and statistics

### Production Readiness:
- ✅ Security measures implemented and tested
- ✅ Performance optimizations applied
- ✅ Comprehensive error handling and logging
- ✅ Background processing support
- ✅ Monitoring and alerting configured
- ✅ Business logic validation complete

The reminder system is now production-ready with enterprise-grade features, comprehensive security, and robust performance characteristics suitable for high-traffic applications.

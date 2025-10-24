from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, Field, validator

class ReminderBase(BaseModel):
    """Base schema for reminders with common attributes."""
    scheduled_at: datetime = Field(..., description="When the reminder should trigger")
    note_id: int = Field(..., gt=0, description="ID of the associated note")

    @validator('scheduled_at')
    def scheduled_at_must_be_future(cls, v):
        if v <= datetime.now(timezone.utc):
            raise ValueError('Reminder must be scheduled for a future time')
        return v

    @validator('note_id')
    def note_id_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Note ID must be a positive integer')
        return v

class ReminderCreate(ReminderBase):
    """Schema for creating a new reminder."""
    pass

class ReminderUpdate(BaseModel):
    """Schema for updating an existing reminder."""
    scheduled_at: Optional[datetime] = Field(None, description="Updated scheduled time")
    status: Optional[str] = Field(None, description="Reminder status")

    @validator('scheduled_at')
    def scheduled_at_must_be_future_if_provided(cls, v):
        if v is not None and v <= datetime.now(timezone.utc):
            raise ValueError('Reminder must be scheduled for a future time')
        return v

    @validator('status')
    def status_must_be_valid(cls, v):
        if v is not None:
            valid_statuses = ["pending", "sent", "cancelled"]
            if v not in valid_statuses:
                raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v

class ReminderResponse(BaseModel):
    """Schema for reminder response data."""
    id: int
    user_id: int
    note_id: int
    scheduled_at: datetime
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class ReminderListResponse(BaseModel):
    """Schema for paginated reminder list response."""
    reminders: List[ReminderResponse]
    total: int
    skip: int
    limit: int
    status_filter: Optional[str] = None

class ReminderStatsResponse(BaseModel):
    """Schema for reminder statistics."""
    total_reminders: int
    pending_reminders: int
    sent_reminders: int
    cancelled_reminders: int
    upcoming_reminders: int

class ReminderBulkUpdateRequest(BaseModel):
    """Schema for bulk reminder operations."""
    reminder_ids: List[int] = Field(..., min_items=1, max_items=100)
    action: str = Field(..., description="Action to perform")

    @validator('reminder_ids', each_item=True)
    def reminder_ids_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Reminder ID must be a positive integer')
        return v

    @validator('action')
    def action_must_be_valid(cls, v):
        valid_actions = ["cancel", "mark_sent"]
        if v not in valid_actions:
            raise ValueError(f'Action must be one of: {", ".join(valid_actions)}')
        return v

class ReminderSearchRequest(BaseModel):
    """Schema for reminder search and filtering."""
    status: Optional[str] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    note_id: Optional[int] = Field(None, gt=0)
    skip: int = Field(0, ge=0)
    limit: int = Field(50, ge=1, le=100)

    @validator('status')
    def status_must_be_valid(cls, v):
        if v is not None:
            valid_statuses = ["pending", "sent", "cancelled"]
            if v not in valid_statuses:
                raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v

    @validator('from_date', 'to_date')
    def dates_must_be_valid(cls, v):
        if v is not None and v > datetime.now(timezone.utc):
            raise ValueError('Date cannot be in the future')
        return v

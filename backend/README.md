# Backend Setup and Development

## Local Development Setup

1. **Install Python 3.12+**
2. **Install PostgreSQL and Redis**
3. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
4. **Install dependencies**: `pip install -r requirements.txt`
5. **Set up environment**: `cp .env.example .env` and edit values
6. **Create database**: `createdb scribes_db`
7. **Run server**: `uvicorn main:app --reload`

## Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head
```

## Running Tests

```bash
pytest tests/ -v --cov=app
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
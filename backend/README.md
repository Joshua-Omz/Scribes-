# Scribes Backend

This is the backend API server for the Scribes application, a note-taking app with scripture tagging, cross-references, and reminder features.

## Features

- User authentication with JWT tokens
- Notes management with tagging
- Scripture reference detection and linking
- Cross-reference generation
- Reminder scheduling and notifications
- Export functionality

## Technology Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT with refresh tokens
- **Task Queue**: Celery with Redis
- **Caching**: Redis
- **Testing**: pytest

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis

### Local Development

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and configure:
   ```bash
   cp .env.example .env
   # Edit .env file with your settings
   ```
5. Run database migrations:
   ```bash
   alembic upgrade head
   ```
6. Start the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

### Using Docker

You can also use Docker Compose to run the entire stack:

```bash
docker-compose up -d
```

This will start PostgreSQL, Redis, the API server, and a Celery worker.

## Project Structure

```
backend/
├── app/
│   ├── db/                # Database connection and models
│   │   ├── repositories/  # Database access layer
│   │   └── models/        # SQLAlchemy models
│   ├── middleware/        # Request/response middleware
│   ├── models/            # SQLAlchemy ORM models
│   ├── routes/            # API route handlers
│   ├── schemas/           # Pydantic models for validation
│   ├── security/          # Authentication and security utilities
│   ├── services/          # Business logic
│   ├── tests/             # Test modules
│   ├── utils/             # Utility functions
│   ├── workers/           # Celery tasks
│   ├── config.py          # Application configuration
│   └── main.py            # FastAPI application initialization
├── alembic/               # Database migration scripts
├── docs/                  # Documentation files
├── Dockerfile             # Docker configuration
└── docker-compose.yml     # Docker Compose configuration
```

## API Documentation

When the server is running, you can access the API documentation at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Testing

Run tests with pytest:

```bash
pytest
```

For coverage report:

```bash
pytest --cov=app
```

## Deployment

For production deployment, consider:

1. Using environment variables for all sensitive configuration
2. Setting up proper database backups
3. Configuring proper logging
4. Setting up monitoring and alerting
5. Using a production-ready ASGI server like Gunicorn with Uvicorn workers

## License

This project is licensed under the MIT License - see the LICENSE file for details.

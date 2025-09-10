# Scribes - Spiritually Intelligent Note-Taking App

<div align="center">
  <img src="https://img.shields.io/badge/Flutter-3.16.0-blue?logo=flutter" alt="Flutter">
  <img src="https://img.shields.io/badge/FastAPI-0.104.1-green?logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/Python-3.12-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Redis-7-red?logo=redis" alt="Redis">
  <img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="License">
</div>

## 🙏 Overview

**Scribes** is a spiritually intelligent note-taking application designed to help believers capture, organize, and live their sermon notes with powerful AI assistance. Built with Flutter for mobile and FastAPI for the backend, Scribes combines modern technology with spiritual growth tools.

### ✨ Key Features

- **📝 Intelligent Note-Taking**: Capture sermon notes, spiritual insights, and personal reflections
- **🤖 AI-Assisted Paraphrasing**: Transform your notes into clear, actionable insights using AI
- **📖 Scripture Tagging**: Automatically tag and cross-reference Bible verses in your notes  
- **🔔 Smart Reminders**: Set reminders to review and apply your spiritual insights
- **🤝 Private Sharing**: Securely share notes with prayer partners and small groups
- **📊 Growth Tracking**: Monitor your spiritual journey with analytics and insights
- **🙏 Prayer Journal**: Integrated prayer tracking and answered prayer celebration
- **🎯 Action Items**: Convert sermon insights into actionable spiritual practices

## 🏗️ Architecture

This is a **monorepo** containing both the mobile app and backend API:

```
Scribes/
├── mobile/          # Flutter mobile application
├── backend/         # FastAPI backend server
├── .github/         # CI/CD workflows
└── docs/            # Documentation
```

### Mobile App (Flutter)
- **State Management**: BLoC pattern with flutter_bloc
- **Local Storage**: SQLite with sqflite
- **Navigation**: go_router for declarative routing
- **UI**: Material 3 design system
- **Architecture**: Clean architecture with repository pattern

### Backend API (FastAPI)
- **Framework**: FastAPI with async/await support
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens with secure storage
- **Caching**: Redis for session management and caching
- **Background Tasks**: Celery for AI processing and notifications
- **API Documentation**: Auto-generated OpenAPI/Swagger docs

## 🚀 Getting Started

### Prerequisites

- **Flutter SDK** 3.16.0 or higher
- **Python** 3.12 or higher
- **PostgreSQL** 15 or higher
- **Redis** 7 or higher
- **Git**

### 📱 Mobile App Setup

1. **Navigate to mobile directory**:
   ```bash
   cd mobile
   ```

2. **Install Flutter dependencies**:
   ```bash
   flutter pub get
   ```

3. **Generate code** (if needed):
   ```bash
   flutter packages pub run build_runner build
   ```

4. **Run the app**:
   ```bash
   # For debugging
   flutter run
   
   # For release build
   flutter build apk --release
   ```

### 🔧 Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your database and API keys
   ```

5. **Set up database**:
   ```bash
   # Make sure PostgreSQL is running
   createdb scribes_db
   ```

6. **Run the server**:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Start background workers** (optional):
   ```bash
   celery -A app.celery_app worker --loglevel=info
   ```

### 🛠️ Development Workflow

#### Running Tests

**Mobile Tests**:
```bash
cd mobile
flutter test
```

**Backend Tests**:
```bash
cd backend
pytest tests/ -v
```

#### Code Quality

**Mobile Linting**:
```bash
cd mobile
flutter analyze
dart format lib/ test/
```

**Backend Linting**:
```bash
cd backend
black .
isort .
flake8 .
```

## 🔐 Environment Configuration

### Backend Environment Variables

Create a `.env` file in the `backend` directory:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/scribes_db
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External APIs
OPENAI_API_KEY=your-openai-api-key-here
BIBLE_API_KEY=your-bible-api-key-here

# Email (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

## 📚 API Documentation

When running the backend server, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key API Endpoints

- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User authentication  
- `GET /api/v1/notes/` - Get user notes
- `POST /api/v1/notes/` - Create new note
- `POST /api/v1/notes/{id}/ai-paraphrase` - Generate AI summary

## 🗃️ Database Schema

### Key Tables

- **users**: User accounts and profiles
- **notes**: Sermon notes and spiritual content
- **tags**: Categorization tags
- **scripture_references**: Bible verse references
- **note_tags**: Many-to-many relationship between notes and tags

## 🤖 AI Features

### Planned AI Integrations

1. **Sermon Summarization**: AI-powered note summarization
2. **Scripture Discovery**: Automatic Bible verse suggestions
3. **Action Item Extraction**: Convert insights to actionable items
4. **Prayer Request Tracking**: Smart prayer journal features
5. **Growth Analytics**: Spiritual growth pattern recognition

## 🚀 Deployment

### Mobile App Deployment

**Android (Google Play Store)**:
```bash
cd mobile
flutter build appbundle --release
```

**iOS (App Store)**:
```bash
cd mobile
flutter build ios --release
```

### Backend Deployment

**Docker** (recommended):
```bash
cd backend
docker build -t scribes-api .
docker run -p 8000:8000 scribes-api
```

**Traditional hosting** with gunicorn:
```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and write tests
4. Ensure all tests pass: `flutter test && pytest`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Submit a Pull Request

## 📊 Project Status

- ✅ **Backend API**: Core authentication and notes CRUD
- ✅ **Mobile App**: Basic note-taking functionality
- ⏳ **AI Integration**: OpenAI paraphrasing (in progress)
- ⏳ **Scripture API**: Bible verse integration (planned)
- ⏳ **Push Notifications**: Reminder system (planned)
- ⏳ **Sharing Features**: Private note sharing (planned)

## 🛣️ Roadmap

### Phase 1 (MVP) ✅
- [x] User authentication
- [x] Basic note CRUD operations
- [x] Mobile app scaffold
- [x] Backend API foundation

### Phase 2 (Core Features)
- [ ] AI-powered note summarization
- [ ] Scripture tagging and cross-references
- [ ] Reminder notifications
- [ ] Note search and filtering

### Phase 3 (Advanced Features)
- [ ] Private sharing with contacts
- [ ] Prayer journal integration
- [ ] Spiritual growth analytics
- [ ] Offline synchronization

### Phase 4 (Community Features)
- [ ] Small group collaboration
- [ ] Public note sharing (optional)
- [ ] Community prayer requests
- [ ] Devotional content integration

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

- 📧 **Email**: support@scribes-app.com
- 🐛 **Issues**: [GitHub Issues](https://github.com/Joshua-Omz/Scribes-/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/Joshua-Omz/Scribes-/discussions)

## 🙏 Acknowledgments

- The global Christian development community
- Open source contributors
- Beta testers and early adopters
- Churches and ministries providing feedback

---

<div align="center">
  <p><strong>Built with ❤️ for the Kingdom</strong></p>
  <p><em>"Let the word of Christ dwell in you richly" - Colossians 3:16</em></p>
</div>

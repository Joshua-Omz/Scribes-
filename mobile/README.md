# Flutter Mobile App

## Development Setup

1. **Install Flutter 3.16.0+**
2. **Get dependencies**: `flutter pub get`
3. **Run app**: `flutter run`

## Architecture

- **State Management**: BLoC pattern
- **Database**: SQLite with sqflite
- **Navigation**: go_router
- **HTTP**: dio for API calls

## Key Features

- Offline-first note storage
- BLoC state management
- Material 3 design
- JWT authentication
- Real-time synchronization

## Testing

```bash
flutter test
flutter test --coverage
```

## Building

```bash
# Android APK
flutter build apk --release

# iOS
flutter build ios --release
```
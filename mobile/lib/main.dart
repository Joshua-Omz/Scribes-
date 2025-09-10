import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';

import 'src/blocs/auth/auth_bloc.dart';
import 'src/blocs/notes/notes_bloc.dart';
import 'src/repositories/auth_repository.dart';
import 'src/repositories/notes_repository.dart';
import 'src/services/database_service.dart';
import 'src/screens/home_screen.dart';
import 'src/screens/login_screen.dart';
import 'src/screens/note_detail_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize database
  final databaseService = DatabaseService();
  await databaseService.initialize();
  
  runApp(ScribesApp(databaseService: databaseService));
}

class ScribesApp extends StatelessWidget {
  final DatabaseService databaseService;
  
  const ScribesApp({super.key, required this.databaseService});

  @override
  Widget build(BuildContext context) {
    return MultiRepositoryProvider(
      providers: [
        RepositoryProvider<AuthRepository>(
          create: (context) => AuthRepository(),
        ),
        RepositoryProvider<NotesRepository>(
          create: (context) => NotesRepository(databaseService),
        ),
      ],
      child: MultiBlocProvider(
        providers: [
          BlocProvider<AuthBloc>(
            create: (context) => AuthBloc(
              authRepository: context.read<AuthRepository>(),
            ),
          ),
          BlocProvider<NotesBloc>(
            create: (context) => NotesBloc(
              notesRepository: context.read<NotesRepository>(),
            ),
          ),
        ],
        child: MaterialApp.router(
          title: 'Scribes - Spiritual Note Taking',
          theme: ThemeData(
            primarySwatch: Colors.deepPurple,
            useMaterial3: true,
            colorScheme: ColorScheme.fromSeed(
              seedColor: Colors.deepPurple,
            ),
          ),
          routerConfig: _router,
        ),
      ),
    );
  }
}

final GoRouter _router = GoRouter(
  routes: [
    GoRoute(
      path: '/',
      builder: (context, state) => const LoginScreen(),
    ),
    GoRoute(
      path: '/home',
      builder: (context, state) => const HomeScreen(),
    ),
    GoRoute(
      path: '/note/:id',
      builder: (context, state) {
        final id = state.pathParameters['id']!;
        return NoteDetailScreen(noteId: id);
      },
    ),
  ],
);
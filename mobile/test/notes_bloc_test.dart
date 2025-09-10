import 'package:flutter_test/flutter_test.dart';
import 'package:bloc_test/bloc_test.dart';
import 'package:mocktail/mocktail.dart';

import 'package:scribes/src/blocs/notes/notes_bloc.dart';
import 'package:scribes/src/models/note.dart';
import 'package:scribes/src/repositories/notes_repository.dart';

class MockNotesRepository extends Mock implements NotesRepository {}

void main() {
  group('NotesBloc', () {
    late MockNotesRepository mockNotesRepository;
    late NotesBloc notesBloc;

    setUp(() {
      mockNotesRepository = MockNotesRepository();
      notesBloc = NotesBloc(notesRepository: mockNotesRepository);
    });

    tearDown(() {
      notesBloc.close();
    });

    test('initial state is NotesInitial', () {
      expect(notesBloc.state, equals(NotesInitial()));
    });

    blocTest<NotesBloc, NotesState>(
      'emits [NotesLoading, NotesLoaded] when LoadNotes is added',
      build: () {
        when(() => mockNotesRepository.getAllNotes())
            .thenAnswer((_) async => <Note>[]);
        return notesBloc;
      },
      act: (bloc) => bloc.add(LoadNotes()),
      expect: () => [
        NotesLoading(),
        const NotesLoaded(notes: <Note>[]),
      ],
    );

    blocTest<NotesBloc, NotesState>(
      'emits [NotesError] when LoadNotes fails',
      build: () {
        when(() => mockNotesRepository.getAllNotes())
            .thenThrow(Exception('Failed to load notes'));
        return notesBloc;
      },
      act: (bloc) => bloc.add(LoadNotes()),
      expect: () => [
        NotesLoading(),
        const NotesError('Exception: Failed to load notes'),
      ],
    );

    blocTest<NotesBloc, NotesState>(
      'emits [NotesLoaded] when AddNote is successful',
      build: () {
        final note = Note(
          id: '1',
          title: 'Test Note',
          content: 'Test Content',
          createdAt: DateTime.now(),
          updatedAt: DateTime.now(),
        );
        when(() => mockNotesRepository.createNote(note))
            .thenAnswer((_) async {});
        when(() => mockNotesRepository.getAllNotes())
            .thenAnswer((_) async => [note]);
        return notesBloc;
      },
      act: (bloc) {
        final note = Note(
          id: '1',
          title: 'Test Note',
          content: 'Test Content',
          createdAt: DateTime.now(),
          updatedAt: DateTime.now(),
        );
        bloc.add(AddNote(note));
      },
      expect: () => [
        isA<NotesLoaded>(),
      ],
    );
  });
}
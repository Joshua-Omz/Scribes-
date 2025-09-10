import 'package:equatable/equatable.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../models/note.dart';
import '../../repositories/notes_repository.dart';

part 'notes_event.dart';
part 'notes_state.dart';

class NotesBloc extends Bloc<NotesEvent, NotesState> {
  final NotesRepository notesRepository;

  NotesBloc({required this.notesRepository}) : super(NotesInitial()) {
    on<LoadNotes>(_onLoadNotes);
    on<AddNote>(_onAddNote);
    on<UpdateNote>(_onUpdateNote);
    on<DeleteNote>(_onDeleteNote);
    on<SearchNotes>(_onSearchNotes);
    on<FilterNotesByTag>(_onFilterNotesByTag);
  }

  Future<void> _onLoadNotes(
    LoadNotes event,
    Emitter<NotesState> emit,
  ) async {
    emit(NotesLoading());
    try {
      final notes = await notesRepository.getAllNotes();
      emit(NotesLoaded(notes: notes));
    } catch (e) {
      emit(NotesError(e.toString()));
    }
  }

  Future<void> _onAddNote(
    AddNote event,
    Emitter<NotesState> emit,
  ) async {
    try {
      await notesRepository.createNote(event.note);
      final notes = await notesRepository.getAllNotes();
      emit(NotesLoaded(notes: notes));
    } catch (e) {
      emit(NotesError(e.toString()));
    }
  }

  Future<void> _onUpdateNote(
    UpdateNote event,
    Emitter<NotesState> emit,
  ) async {
    try {
      await notesRepository.updateNote(event.note);
      final notes = await notesRepository.getAllNotes();
      emit(NotesLoaded(notes: notes));
    } catch (e) {
      emit(NotesError(e.toString()));
    }
  }

  Future<void> _onDeleteNote(
    DeleteNote event,
    Emitter<NotesState> emit,
  ) async {
    try {
      await notesRepository.deleteNote(event.noteId);
      final notes = await notesRepository.getAllNotes();
      emit(NotesLoaded(notes: notes));
    } catch (e) {
      emit(NotesError(e.toString()));
    }
  }

  Future<void> _onSearchNotes(
    SearchNotes event,
    Emitter<NotesState> emit,
  ) async {
    try {
      final notes = await notesRepository.searchNotes(event.query);
      emit(NotesLoaded(notes: notes, searchQuery: event.query));
    } catch (e) {
      emit(NotesError(e.toString()));
    }
  }

  Future<void> _onFilterNotesByTag(
    FilterNotesByTag event,
    Emitter<NotesState> emit,
  ) async {
    try {
      final notes = await notesRepository.getNotesByTag(event.tag);
      emit(NotesLoaded(notes: notes, filterTag: event.tag));
    } catch (e) {
      emit(NotesError(e.toString()));
    }
  }
}
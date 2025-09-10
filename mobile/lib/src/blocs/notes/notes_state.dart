part of 'notes_bloc.dart';

abstract class NotesState extends Equatable {
  const NotesState();
  
  @override
  List<Object?> get props => [];
}

class NotesInitial extends NotesState {}

class NotesLoading extends NotesState {}

class NotesLoaded extends NotesState {
  final List<Note> notes;
  final String? searchQuery;
  final String? filterTag;
  
  const NotesLoaded({
    required this.notes,
    this.searchQuery,
    this.filterTag,
  });
  
  @override
  List<Object?> get props => [notes, searchQuery, filterTag];
}

class NotesError extends NotesState {
  final String message;
  
  const NotesError(this.message);
  
  @override
  List<Object> get props => [message];
}
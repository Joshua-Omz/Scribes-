part of 'notes_bloc.dart';

abstract class NotesEvent extends Equatable {
  const NotesEvent();

  @override
  List<Object?> get props => [];
}

class LoadNotes extends NotesEvent {}

class AddNote extends NotesEvent {
  final Note note;
  
  const AddNote(this.note);
  
  @override
  List<Object> get props => [note];
}

class UpdateNote extends NotesEvent {
  final Note note;
  
  const UpdateNote(this.note);
  
  @override
  List<Object> get props => [note];
}

class DeleteNote extends NotesEvent {
  final String noteId;
  
  const DeleteNote(this.noteId);
  
  @override
  List<Object> get props => [noteId];
}

class SearchNotes extends NotesEvent {
  final String query;
  
  const SearchNotes(this.query);
  
  @override
  List<Object> get props => [query];
}

class FilterNotesByTag extends NotesEvent {
  final String tag;
  
  const FilterNotesByTag(this.tag);
  
  @override
  List<Object> get props => [tag];
}
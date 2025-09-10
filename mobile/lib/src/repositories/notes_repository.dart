import '../models/note.dart';
import '../services/database_service.dart';

class NotesRepository {
  final DatabaseService databaseService;

  NotesRepository(this.databaseService);

  Future<List<Note>> getAllNotes() async {
    final db = await databaseService.database;
    final List<Map<String, dynamic>> maps = await db.query(
      'notes',
      orderBy: 'updated_at DESC',
    );

    return List.generate(maps.length, (i) {
      return Note.fromMap(maps[i]);
    });
  }

  Future<Note?> getNoteById(String id) async {
    final db = await databaseService.database;
    final List<Map<String, dynamic>> maps = await db.query(
      'notes',
      where: 'id = ?',
      whereArgs: [id],
    );

    if (maps.isNotEmpty) {
      return Note.fromMap(maps.first);
    }
    return null;
  }

  Future<void> createNote(Note note) async {
    final db = await databaseService.database;
    await db.insert('notes', note.toMap());
  }

  Future<void> updateNote(Note note) async {
    final db = await databaseService.database;
    await db.update(
      'notes',
      note.toMap(),
      where: 'id = ?',
      whereArgs: [note.id],
    );
  }

  Future<void> deleteNote(String id) async {
    final db = await databaseService.database;
    await db.delete(
      'notes',
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  Future<List<Note>> searchNotes(String query) async {
    final db = await databaseService.database;
    final List<Map<String, dynamic>> maps = await db.query(
      'notes',
      where: 'title LIKE ? OR content LIKE ?',
      whereArgs: ['%$query%', '%$query%'],
      orderBy: 'updated_at DESC',
    );

    return List.generate(maps.length, (i) {
      return Note.fromMap(maps[i]);
    });
  }

  Future<List<Note>> getNotesByTag(String tag) async {
    final db = await databaseService.database;
    final List<Map<String, dynamic>> maps = await db.query(
      'notes',
      where: 'tags LIKE ?',
      whereArgs: ['%$tag%'],
      orderBy: 'updated_at DESC',
    );

    return List.generate(maps.length, (i) {
      return Note.fromMap(maps[i]);
    });
  }

  Future<List<Note>> getNotesWithReminders() async {
    final db = await databaseService.database;
    final List<Map<String, dynamic>> maps = await db.query(
      'notes',
      where: 'reminder_date IS NOT NULL AND reminder_date > ?',
      whereArgs: [DateTime.now().millisecondsSinceEpoch],
      orderBy: 'reminder_date ASC',
    );

    return List.generate(maps.length, (i) {
      return Note.fromMap(maps[i]);
    });
  }
}
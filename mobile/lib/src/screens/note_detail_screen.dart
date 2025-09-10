import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';

import '../blocs/notes/notes_bloc.dart';
import '../models/note.dart';

class NoteDetailScreen extends StatefulWidget {
  final String noteId;
  
  const NoteDetailScreen({super.key, required this.noteId});

  @override
  State<NoteDetailScreen> createState() => _NoteDetailScreenState();
}

class _NoteDetailScreenState extends State<NoteDetailScreen> {
  final _titleController = TextEditingController();
  final _contentController = TextEditingController();
  final _tagsController = TextEditingController();
  Note? _currentNote;

  @override
  void initState() {
    super.initState();
    _loadNote();
  }

  void _loadNote() {
    // In a real app, you'd fetch the note from the repository
    // For this scaffold, we'll create a basic note structure
    _currentNote = Note(
      id: widget.noteId,
      title: 'Sermon Notes',
      content: '',
      createdAt: DateTime.now(),
      updatedAt: DateTime.now(),
    );
    
    _titleController.text = _currentNote!.title;
    _contentController.text = _currentNote!.content;
    _tagsController.text = _currentNote!.tags.join(', ');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Note Details'),
        backgroundColor: Colors.deepPurple,
        foregroundColor: Colors.white,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () {
            _saveNote();
            context.go('/home');
          },
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.share),
            onPressed: _shareNote,
          ),
          IconButton(
            icon: const Icon(Icons.more_vert),
            onPressed: _showMoreOptions,
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            TextField(
              controller: _titleController,
              style: const TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
              decoration: const InputDecoration(
                hintText: 'Note Title',
                border: InputBorder.none,
              ),
            ),
            const Divider(),
            TextField(
              controller: _tagsController,
              decoration: InputDecoration(
                hintText: 'Tags (separated by commas)',
                prefixIcon: const Icon(Icons.tag),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _addScriptureReference,
                    icon: const Icon(Icons.book),
                    label: const Text('Add Scripture'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.blue,
                      foregroundColor: Colors.white,
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _setReminder,
                    icon: const Icon(Icons.alarm),
                    label: const Text('Reminder'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.orange,
                      foregroundColor: Colors.white,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: _aiParaphrase,
              icon: const Icon(Icons.psychology),
              label: const Text('AI Paraphrase'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.purple,
                foregroundColor: Colors.white,
              ),
            ),
            const SizedBox(height: 16),
            Expanded(
              child: TextField(
                controller: _contentController,
                maxLines: null,
                expands: true,
                decoration: const InputDecoration(
                  hintText: 'Start writing your note...\n\nTip: Use @ to tag scriptures, # for themes',
                  border: OutlineInputBorder(),
                  alignLabelWithHint: true,
                ),
                textAlignVertical: TextAlignVertical.top,
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _saveNote() {
    if (_currentNote != null) {
      final updatedNote = _currentNote!.copyWith(
        title: _titleController.text.isNotEmpty ? _titleController.text : 'Untitled',
        content: _contentController.text,
        tags: _tagsController.text.split(',').map((tag) => tag.trim()).where((tag) => tag.isNotEmpty).toList(),
        updatedAt: DateTime.now(),
      );
      
      context.read<NotesBloc>().add(UpdateNote(updatedNote));
    }
  }

  void _shareNote() {
    // Implement sharing functionality
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Share feature coming soon!')),
    );
  }

  void _showMoreOptions() {
    showModalBottomSheet(
      context: context,
      builder: (BuildContext context) {
        return SafeArea(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              ListTile(
                leading: const Icon(Icons.delete),
                title: const Text('Delete Note'),
                onTap: () {
                  Navigator.pop(context);
                  _deleteNote();
                },
              ),
              ListTile(
                leading: const Icon(Icons.copy),
                title: const Text('Duplicate Note'),
                onTap: () {
                  Navigator.pop(context);
                  _duplicateNote();
                },
              ),
              ListTile(
                leading: const Icon(Icons.lock),
                title: const Text('Make Private'),
                onTap: () {
                  Navigator.pop(context);
                  _togglePrivacy();
                },
              ),
            ],
          ),
        );
      },
    );
  }

  void _addScriptureReference() {
    // Implement scripture reference picker
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Scripture reference picker coming soon!')),
    );
  }

  void _setReminder() {
    // Implement reminder setting
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Reminder feature coming soon!')),
    );
  }

  void _aiParaphrase() {
    // Implement AI paraphrasing
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('AI paraphrasing coming soon!')),
    );
  }

  void _deleteNote() {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Delete Note'),
          content: const Text('Are you sure you want to delete this note? This action cannot be undone.'),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel'),
            ),
            TextButton(
              onPressed: () {
                context.read<NotesBloc>().add(DeleteNote(widget.noteId));
                Navigator.pop(context);
                context.go('/home');
              },
              child: const Text('Delete', style: TextStyle(color: Colors.red)),
            ),
          ],
        );
      },
    );
  }

  void _duplicateNote() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Duplicate feature coming soon!')),
    );
  }

  void _togglePrivacy() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Privacy toggle coming soon!')),
    );
  }

  @override
  void dispose() {
    _titleController.dispose();
    _contentController.dispose();
    _tagsController.dispose();
    super.dispose();
  }
}
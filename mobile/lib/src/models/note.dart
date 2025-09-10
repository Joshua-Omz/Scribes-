import 'package:equatable/equatable.dart';

class Note extends Equatable {
  final String id;
  final String title;
  final String content;
  final List<String> scriptureReferences;
  final List<String> tags;
  final String? aiSummary;
  final DateTime createdAt;
  final DateTime updatedAt;
  final DateTime? reminderDate;
  final bool isPrivate;

  const Note({
    required this.id,
    required this.title,
    required this.content,
    this.scriptureReferences = const [],
    this.tags = const [],
    this.aiSummary,
    required this.createdAt,
    required this.updatedAt,
    this.reminderDate,
    this.isPrivate = false,
  });

  factory Note.fromMap(Map<String, dynamic> map) {
    return Note(
      id: map['id'],
      title: map['title'],
      content: map['content'],
      scriptureReferences: map['scripture_references']?.split(',') ?? [],
      tags: map['tags']?.split(',') ?? [],
      aiSummary: map['ai_summary'],
      createdAt: DateTime.fromMillisecondsSinceEpoch(map['created_at']),
      updatedAt: DateTime.fromMillisecondsSinceEpoch(map['updated_at']),
      reminderDate: map['reminder_date'] != null 
          ? DateTime.fromMillisecondsSinceEpoch(map['reminder_date'])
          : null,
      isPrivate: map['is_private'] == 1,
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'title': title,
      'content': content,
      'scripture_references': scriptureReferences.join(','),
      'tags': tags.join(','),
      'ai_summary': aiSummary,
      'created_at': createdAt.millisecondsSinceEpoch,
      'updated_at': updatedAt.millisecondsSinceEpoch,
      'reminder_date': reminderDate?.millisecondsSinceEpoch,
      'is_private': isPrivate ? 1 : 0,
    };
  }

  Note copyWith({
    String? id,
    String? title,
    String? content,
    List<String>? scriptureReferences,
    List<String>? tags,
    String? aiSummary,
    DateTime? createdAt,
    DateTime? updatedAt,
    DateTime? reminderDate,
    bool? isPrivate,
  }) {
    return Note(
      id: id ?? this.id,
      title: title ?? this.title,
      content: content ?? this.content,
      scriptureReferences: scriptureReferences ?? this.scriptureReferences,
      tags: tags ?? this.tags,
      aiSummary: aiSummary ?? this.aiSummary,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      reminderDate: reminderDate ?? this.reminderDate,
      isPrivate: isPrivate ?? this.isPrivate,
    );
  }

  @override
  List<Object?> get props => [
    id,
    title,
    content,
    scriptureReferences,
    tags,
    aiSummary,
    createdAt,
    updatedAt,
    reminderDate,
    isPrivate,
  ];
}
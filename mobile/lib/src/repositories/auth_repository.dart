import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import '../models/user.dart';

class AuthResult {
  final User user;
  final String token;
  
  AuthResult({required this.user, required this.token});
}

class AuthRepository {
  static const String _baseUrl = 'http://localhost:8000/api/v1';
  static const FlutterSecureStorage _storage = FlutterSecureStorage();
  static const String _tokenKey = 'auth_token';

  Future<AuthResult> login(String email, String password) async {
    final response = await http.post(
      Uri.parse('$_baseUrl/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'email': email,
        'password': password,
      }),
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      final token = data['access_token'];
      final user = User.fromJson(data['user']);
      
      await _storage.write(key: _tokenKey, value: token);
      
      return AuthResult(user: user, token: token);
    } else {
      final error = json.decode(response.body);
      throw Exception(error['detail'] ?? 'Login failed');
    }
  }

  Future<AuthResult> register(String email, String password, String name) async {
    final response = await http.post(
      Uri.parse('$_baseUrl/auth/register'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'email': email,
        'password': password,
        'name': name,
      }),
    );

    if (response.statusCode == 201) {
      final data = json.decode(response.body);
      final token = data['access_token'];
      final user = User.fromJson(data['user']);
      
      await _storage.write(key: _tokenKey, value: token);
      
      return AuthResult(user: user, token: token);
    } else {
      final error = json.decode(response.body);
      throw Exception(error['detail'] ?? 'Registration failed');
    }
  }

  Future<void> logout() async {
    await _storage.delete(key: _tokenKey);
  }

  Future<String?> getStoredToken() async {
    return await _storage.read(key: _tokenKey);
  }

  Future<User> getCurrentUser(String token) async {
    final response = await http.get(
      Uri.parse('$_baseUrl/auth/me'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return User.fromJson(data);
    } else {
      throw Exception('Failed to get current user');
    }
  }

  Future<String> refreshToken(String token) async {
    final response = await http.post(
      Uri.parse('$_baseUrl/auth/refresh'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      final newToken = data['access_token'];
      
      await _storage.write(key: _tokenKey, value: newToken);
      
      return newToken;
    } else {
      throw Exception('Failed to refresh token');
    }
  }
}
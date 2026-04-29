import 'dart:convert';
import 'dart:typed_data';

import 'package:http/http.dart' as http;

import '../models/session_state.dart';

class ApiException implements Exception {
  ApiException(this.message);

  final String message;

  @override
  String toString() => message;
}

class ApiService {
  Future<void> register({
    required String baseUrl,
    required String fullName,
    required String email,
    required String password,
    required String role,
    String? bootstrapCode,
  }) async {
    final response = await http.post(
      Uri.parse('${_normalizeBaseUrl(baseUrl)}/api/v1/auth/register'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'full_name': fullName,
        'email': email,
        'password': password,
        'role': role,
        if ((bootstrapCode ?? '').trim().isNotEmpty)
          'bootstrap_code': bootstrapCode!.trim(),
      }),
    );

    _ensureSuccess(response);
  }

  Future<SessionState> login({
    required String baseUrl,
    required String email,
    required String password,
  }) async {
    final normalizedBaseUrl = _normalizeBaseUrl(baseUrl);
    final response = await http.post(
      Uri.parse('$normalizedBaseUrl/api/v1/auth/token'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email, 'password': password}),
    );

    final body = _decodeBody(response);
    if (response.statusCode >= 400) {
      throw ApiException(body['error']?.toString() ?? 'Giris basarisiz oldu');
    }

    final user = body['user'] as Map<String, dynamic>? ?? const {};
    return SessionState(
      userId: user['id'] as int? ?? 0,
      baseUrl: normalizedBaseUrl,
      accessToken: body['access_token']?.toString() ?? '',
      refreshToken: body['refresh_token']?.toString() ?? '',
      role: user['role']?.toString() ?? 'candidate',
      email: user['email']?.toString() ?? email,
    );
  }

  Future<Map<String, dynamic>> fetchOverview(SessionState session) async {
    final response = await http.get(
      Uri.parse('${session.baseUrl}/api/v1/reports/overview'),
      headers: _authHeaders(session),
    );
    return _parseProtectedJson(response);
  }

  Future<Map<String, dynamic>> fetchAuditLogs(SessionState session) async {
    final response = await http.get(
      Uri.parse('${session.baseUrl}/api/v1/audit-logs?limit=10'),
      headers: _authHeaders(session),
    );
    return _parseProtectedJson(response);
  }

  Future<Map<String, dynamic>> fetchMyApplications(SessionState session) async {
    final response = await http.get(
      Uri.parse('${session.baseUrl}/api/v1/applications/me'),
      headers: _authHeaders(session),
    );
    return _parseProtectedJson(response);
  }

  Future<Map<String, dynamic>> fetchJobs(SessionState session) async {
    final response = await http.get(
      Uri.parse('${session.baseUrl}/api/v1/jobs'),
      headers: _authHeaders(session),
    );
    return _parseProtectedJson(response);
  }

  Future<Map<String, dynamic>> createJob({
    required SessionState session,
    required String title,
    required String description,
    required int minYearsExperience,
    required List<String> requiredSkills,
  }) async {
    final response = await http.post(
      Uri.parse('${session.baseUrl}/api/v1/jobs'),
      headers: _authHeaders(session),
      body: jsonEncode({
        'title': title,
        'description': description,
        'min_years_experience': minYearsExperience,
        'required_skills': requiredSkills,
      }),
    );
    return _parseProtectedJson(response);
  }

  Future<Map<String, dynamic>> fetchJobCandidates({
    required SessionState session,
    required int jobPostingId,
  }) async {
    final response = await http.get(
      Uri.parse('${session.baseUrl}/api/v1/jobs/$jobPostingId/candidates'),
      headers: _authHeaders(session),
    );
    return _parseProtectedJson(response);
  }

  Future<Map<String, dynamic>> fetchShortlisted({
    required SessionState session,
    required int jobPostingId,
    double threshold = 70,
  }) async {
    final url = Uri.parse(
      '${session.baseUrl}/api/v1/jobs/$jobPostingId/shortlisted?threshold=$threshold',
    );
    final response = await http.get(url, headers: _authHeaders(session));
    return _parseProtectedJson(response);
  }

  Future<Map<String, dynamic>> fetchInvitations({
    required SessionState session,
    required int jobPostingId,
  }) async {
    final url = Uri.parse(
      '${session.baseUrl}/api/v1/invitations?job_posting_id=$jobPostingId',
    );
    final response = await http.get(url, headers: _authHeaders(session));
    return _parseProtectedJson(response);
  }

  Future<Map<String, dynamic>> uploadApplicationCv({
    required SessionState session,
    required int jobPostingId,
    required String fileName,
    required Uint8List fileBytes,
  }) async {
    final request = http.MultipartRequest(
      'POST',
      Uri.parse('${session.baseUrl}/api/v1/applications/upload'),
    );
    request.headers['Authorization'] = 'Bearer ${session.accessToken}';
    request.fields['candidate_id'] = '${session.userId}';
    request.fields['job_posting_id'] = '$jobPostingId';
    request.files.add(
      http.MultipartFile.fromBytes('cv_file', fileBytes, filename: fileName),
    );

    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);
    return _parseProtectedJson(response);
  }

  Map<String, String> _authHeaders(SessionState session) {
    return {
      'Authorization': 'Bearer ${session.accessToken}',
      'Content-Type': 'application/json',
    };
  }

  Map<String, dynamic> _parseProtectedJson(http.Response response) {
    final body = _decodeBody(response);
    if (response.statusCode >= 400) {
      throw ApiException(body['error']?.toString() ?? 'Istek basarisiz oldu');
    }
    return body;
  }

  void _ensureSuccess(http.Response response) {
    if (response.statusCode < 400) {
      return;
    }

    final body = _decodeBody(response);
    throw ApiException(body['error']?.toString() ?? 'Istek basarisiz oldu');
  }

  Map<String, dynamic> _decodeBody(http.Response response) {
    if (response.body.isEmpty) {
      return <String, dynamic>{};
    }
    final decoded = jsonDecode(response.body);
    if (decoded is Map<String, dynamic>) {
      return decoded;
    }
    return <String, dynamic>{};
  }

  String _normalizeBaseUrl(String value) {
    return value.trim().replaceAll(RegExp(r'/+$'), '');
  }
}

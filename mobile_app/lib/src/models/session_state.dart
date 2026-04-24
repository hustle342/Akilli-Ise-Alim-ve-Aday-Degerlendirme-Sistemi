class SessionState {
  const SessionState({
    required this.userId,
    required this.baseUrl,
    required this.accessToken,
    required this.refreshToken,
    required this.role,
    required this.email,
  });

  final int userId;
  final String baseUrl;
  final String accessToken;
  final String refreshToken;
  final String role;
  final String email;

  bool get isPrivileged => role == 'admin' || role == 'hr';
}

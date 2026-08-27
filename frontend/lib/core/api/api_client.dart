import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../router/app_router.dart';

class ApiClient {
  static const String baseUrl = 'http://127.0.0.1:8000/api';
  
  static String? _accessToken;
  static String? _refreshToken;

  static void setTokens(String access, String refresh) {
    _accessToken = access;
    _refreshToken = refresh;
  }

  static String? get accessToken => _accessToken;
  static String? get refreshToken => _refreshToken;
  static bool get isAuthenticated => _accessToken != null;

  static Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        if (_accessToken != null) 'Authorization': 'Token $_accessToken',
      };
      
  static void clearSession() {
    _accessToken = null;
    _refreshToken = null;
    // Clear relevant in-memory authentication state and navigate to Login
    appRouter.go('/login');
  }

  static void logout() {
    clearSession();
  }

  static Future<void> _handleResponse(http.Response response) async {
    if (response.statusCode == 401) {
      // Attempt to use refresh-token mechanism if already implemented
      // Since it's not implemented, clear the session and return to Login
      clearSession();
    }
  }

  static Future<http.Response> get(String endpoint) async {
    final url = Uri.parse('$baseUrl$endpoint');
    final response = await http.get(url, headers: _headers);
    await _handleResponse(response);
    return response;
  }

  static Future<http.Response> post(String endpoint, {Map<String, dynamic>? body}) async {
    final url = Uri.parse('$baseUrl$endpoint');
    final response = await http.post(
      url,
      headers: _headers,
      body: body != null ? jsonEncode(body) : null,
    );
    await _handleResponse(response);
    return response;
  }

  static Future<http.Response> patch(String endpoint, {Map<String, dynamic>? body}) async {
    final url = Uri.parse('$baseUrl$endpoint');
    final response = await http.patch(
      url,
      headers: _headers,
      body: body != null ? jsonEncode(body) : null,
    );
    await _handleResponse(response);
    return response;
  }
}

import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/api/api_client.dart';

final dashboardRefreshProvider = StateProvider<int>((ref) => 0);

final dashboardSummaryProvider = FutureProvider.autoDispose<Map<String, dynamic>>((ref) async {
  ref.watch(dashboardRefreshProvider);
  try {
    // Reuse existing API client to fetch dashboard summary
    final response = await ApiClient.get('/analytics/summary/');
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
  } catch (e) {
    // Handle network errors gracefully without crashing
  }
  return {};
});

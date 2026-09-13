import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/api/api_client.dart';

final dashboardRefreshProvider = StateProvider<int>((ref) => 0);

final dashboardSummaryProvider = FutureProvider.autoDispose<Map<String, dynamic>>((ref) async {
  ref.watch(dashboardRefreshProvider);
  try {
    final response = await ApiClient.get('/dashboard/summary/');
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
  } catch (e) {
    // Handle network errors gracefully
  }
  return {};
});

final studentDashboardSummaryProvider = FutureProvider.autoDispose<Map<String, dynamic>>((ref) async {
  ref.watch(dashboardRefreshProvider);
  try {
    final response = await ApiClient.get('/dashboard/student-summary/');
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
  } catch (e) {
    // Handle network errors gracefully
  }
  return {};
});

final recommendedDrivesProvider = FutureProvider.autoDispose<List<dynamic>>((ref) async {
  try {
    final response = await ApiClient.get('/ai/recommended-drives/');
    if (response.statusCode == 200) {
      return jsonDecode(response.body)['data'] ?? [];
    }
  } catch (e) {
    // Handle error
  }
  return [];
});

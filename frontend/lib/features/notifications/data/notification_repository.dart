import 'dart:convert';
import '../../../core/api/api_client.dart';
import 'notification_model.dart';

class NotificationRepository {
  Future<List<NotificationModel>> fetchNotifications() async {
    final response = await ApiClient.get('/notifications/');
    
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      // The API uses pagination, so results are under 'results'
      final results = data['results'] as List;
      return results.map((json) => NotificationModel.fromJson(json)).toList();
    } else {
      throw Exception('Failed to load notifications: ${response.statusCode}');
    }
  }

  Future<void> markAsRead(int id) async {
    final response = await ApiClient.patch('/notifications/$id/read/');
    
    if (response.statusCode != 200) {
      throw Exception('Failed to mark notification as read: ${response.statusCode}');
    }
  }

  Future<void> markAllAsRead() async {
    final response = await ApiClient.patch('/notifications/read-all/');
    
    if (response.statusCode != 200) {
      throw Exception('Failed to mark all notifications as read: ${response.statusCode}');
    }
  }
}

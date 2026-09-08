import 'dart:convert';
import '../../../../core/api/api_client.dart';
import '../../../../core/api/endpoints.dart';
import '../models/interview.dart';

class InterviewRepository {
  Future<List<Interview>> getInterviews() async {
    try {
      final response = await ApiClient.get(Endpoints.interviews);
      
      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(response.body);
        return data.map((json) => Interview.fromJson(json)).toList();
      } else {
        throw Exception('Failed to load interviews');
      }
    } catch (e) {
      throw Exception('Error fetching interviews: $e');
    }
  }

  Future<List<Interview>> getUpcomingInterviews() async {
    try {
      final response = await ApiClient.get(Endpoints.upcomingInterviews);
      
      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(response.body);
        return data.map((json) => Interview.fromJson(json)).toList();
      } else {
        throw Exception('Failed to load upcoming interviews');
      }
    } catch (e) {
      throw Exception('Error fetching upcoming interviews: $e');
    }
  }

  Future<Interview> getInterviewDetails(int id) async {
    try {
      final response = await ApiClient.get('${Endpoints.interviews}$id/');
      
      if (response.statusCode == 200) {
        return Interview.fromJson(jsonDecode(response.body));
      } else {
        throw Exception('Failed to load interview details');
      }
    } catch (e) {
      throw Exception('Error fetching interview details: $e');
    }
  }
}

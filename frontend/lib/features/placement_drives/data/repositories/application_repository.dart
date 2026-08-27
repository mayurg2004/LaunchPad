import 'dart:convert';
import 'package:launchpad/core/api/api_client.dart';
import 'package:launchpad/core/api/endpoints.dart';
import '../models/application.dart';

class ApplicationRepository {
  Future<Application> apply(int placementDriveId) async {
    final response = await ApiClient.post(
      Endpoints.applications,
      body: {'placement_drive': placementDriveId},
    );

    if (response.statusCode == 201) {
      return Application.fromJson(jsonDecode(response.body));
    } else {
      try {
        final error = jsonDecode(response.body);
        if (error is List && error.isNotEmpty) {
          throw Exception(error[0]);
        }
        if (error['error'] != null) {
          throw Exception(error['error']);
        }
        if (error['non_field_errors'] != null && error['non_field_errors'].isNotEmpty) {
          throw Exception(error['non_field_errors'][0]);
        }
      } catch (e) {
        if (e is Exception) rethrow;
      }
      throw Exception('Failed to apply. Please try again.');
    }
  }

  Future<List<Application>> getMyApplications() async {
    final response = await ApiClient.get(Endpoints.myApplications);

    if (response.statusCode == 200) {
      final decoded = jsonDecode(response.body);
      // It might be paginated or a direct list depending on the DRF implementation.
      // In the view it says: "page = self.paginate_queryset(queryset)..."
      // Let's handle both.
      List<dynamic> results;
      if (decoded is Map<String, dynamic> && decoded.containsKey('results')) {
        results = decoded['results'];
      } else if (decoded is List) {
        results = decoded;
      } else {
        results = [];
      }
      
      return results.map((e) => Application.fromJson(e)).toList();
    } else {
      throw Exception('Failed to load your applications.');
    }
  }
}

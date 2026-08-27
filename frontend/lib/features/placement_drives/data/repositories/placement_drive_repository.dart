import 'dart:convert';
import 'package:launchpad/core/api/api_client.dart';
import 'package:launchpad/core/api/endpoints.dart';
import '../models/placement_drive.dart';

class PaginatedDrives {
  final int count;
  final String? next;
  final String? previous;
  final List<PlacementDrive> results;

  PaginatedDrives({
    required this.count,
    this.next,
    this.previous,
    required this.results,
  });
}

class PlacementDriveRepository {
  Future<PaginatedDrives> getDrives({
    int page = 1,
    String? search,
    String? status,
    String? companyId,
    String? minimumCgpa,
  }) async {
    final queryParams = <String, String>{
      'page': page.toString(),
    };
    if (search != null && search.isNotEmpty) queryParams['search'] = search;
    if (status != null && status.isNotEmpty) queryParams['status'] = status;
    if (companyId != null && companyId.isNotEmpty) queryParams['company'] = companyId;
    if (minimumCgpa != null && minimumCgpa.isNotEmpty) queryParams['minimum_cgpa'] = minimumCgpa;

    final uri = Uri(queryParameters: queryParams);
    final endpoint = '${Endpoints.placementDrives}?${uri.query}';
    
    final response = await ApiClient.get(endpoint);

    if (response.statusCode == 200) {
      final decoded = jsonDecode(response.body);
      final List<dynamic> results = decoded['results'] ?? [];
      
      return PaginatedDrives(
        count: decoded['count'] as int? ?? 0,
        next: decoded['next'] as String?,
        previous: decoded['previous'] as String?,
        results: results.map((e) => PlacementDrive.fromJson(e)).toList(),
      );
    } else {
      throw Exception('Failed to load placement drives: ${response.statusCode}');
    }
  }

  Future<PlacementDrive> getDriveDetails(int id) async {
    final response = await ApiClient.get('${Endpoints.placementDrives}$id/');
    
    if (response.statusCode == 200) {
      return PlacementDrive.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Failed to load drive details: ${response.statusCode}');
    }
  }
}

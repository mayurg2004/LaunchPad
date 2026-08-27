import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/models/placement_drive.dart';
import '../data/repositories/placement_drive_repository.dart';

final placementDriveRepositoryProvider = Provider((ref) {
  return PlacementDriveRepository();
});

class PlacementDriveFilter {
  final String? search;
  final String? status;
  final String? companyId;
  final String? minimumCgpa;

  PlacementDriveFilter({
    this.search,
    this.status,
    this.companyId,
    this.minimumCgpa,
  });

  PlacementDriveFilter copyWith({
    String? search,
    String? status,
    String? companyId,
    String? minimumCgpa,
    bool clearStatus = false,
    bool clearCompanyId = false,
    bool clearMinimumCgpa = false,
  }) {
    return PlacementDriveFilter(
      search: search ?? this.search,
      status: clearStatus ? null : (status ?? this.status),
      companyId: clearCompanyId ? null : (companyId ?? this.companyId),
      minimumCgpa: clearMinimumCgpa ? null : (minimumCgpa ?? this.minimumCgpa),
    );
  }
}

final placementDriveFilterProvider = StateProvider<PlacementDriveFilter>((ref) {
  return PlacementDriveFilter(status: 'OPEN'); // Default filter to OPEN drives
});

final placementDrivesProvider = FutureProvider<PaginatedDrives>((ref) async {
  final filter = ref.watch(placementDriveFilterProvider);
  final repo = ref.watch(placementDriveRepositoryProvider);
  
  return await repo.getDrives(
    page: 1, // Add pagination support later if needed for infinite scroll
    search: filter.search,
    status: filter.status,
    companyId: filter.companyId,
    minimumCgpa: filter.minimumCgpa,
  );
});

final placementDriveDetailsProvider = FutureProvider.family<PlacementDrive, int>((ref, id) async {
  final repo = ref.watch(placementDriveRepositoryProvider);
  return await repo.getDriveDetails(id);
});

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:launchpad/features/placement_drives/data/models/placement_drive.dart';
import 'package:launchpad/features/placement_drives/presentation/placement_drives_screen.dart';
import 'package:launchpad/features/placement_drives/providers/placement_drive_provider.dart';
import 'package:launchpad/features/placement_drives/data/repositories/placement_drive_repository.dart';

// Mock Repository
class MockPlacementDriveRepository extends PlacementDriveRepository {
  @override
  Future<PaginatedDrives> getDrives({
    int page = 1,
    String? search,
    String? status,
    String? companyId,
    String? minimumCgpa,
  }) async {
    return PaginatedDrives(
      count: 1,
      results: [
        PlacementDrive(
          id: 1,
          companyId: 1,
          companyName: 'Test Company',
          title: 'Software Engineer',
          jobRole: 'Software Engineer',
          jobDescription: 'Test Description',
          packageLpa: 10.0,
          location: 'Remote',
          minimumCgpa: 7.0,
          eligibleBranch: 'All',
          status: 'OPEN',
          requiredSkills: ['Flutter'],
          createdAt: DateTime.now(),
          updatedAt: DateTime.now(),
        )
      ],
    );
  }
}

void main() {
  testWidgets('PlacementDrivesScreen renders correctly and shows mock data', (WidgetTester tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          placementDriveRepositoryProvider.overrideWithValue(MockPlacementDriveRepository()),
        ],
        child: const MaterialApp(
          home: Scaffold(
            body: PlacementDrivesScreen(),
          ),
        ),
      ),
    );

    // Initial loading state
    expect(find.byType(CircularProgressIndicator), findsOneWidget);

    // Wait for the mock future to resolve
    await tester.pumpAndSettle();

    // Verify Title is displayed
    expect(find.text('Find your next opportunity'), findsOneWidget);

    // Verify Search Bar is present
    expect(find.byType(TextField), findsOneWidget);

    // Verify Mock Data is displayed
    expect(find.text('Test Company'), findsOneWidget);
    expect(find.text('Software Engineer'), findsNWidgets(2));
    expect(find.text('10.0 LPA'), findsOneWidget);
  });
}

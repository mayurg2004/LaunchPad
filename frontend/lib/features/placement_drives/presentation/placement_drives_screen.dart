import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';
import 'package:go_router/go_router.dart';
import 'dart:async';

import 'package:launchpad/core/theme/app_colors.dart';
import 'package:launchpad/core/theme/app_spacing.dart';
import '../providers/placement_drive_provider.dart';
import 'widgets/placement_drive_card.dart';
import 'widgets/filter_sheet.dart';

class PlacementDrivesScreen extends ConsumerStatefulWidget {
  const PlacementDrivesScreen({super.key});

  @override
  ConsumerState<PlacementDrivesScreen> createState() => _PlacementDrivesScreenState();
}

class _PlacementDrivesScreenState extends ConsumerState<PlacementDrivesScreen> {
  final TextEditingController _searchController = TextEditingController();
  Timer? _debounce;

  @override
  void dispose() {
    _searchController.dispose();
    _debounce?.cancel();
    super.dispose();
  }

  void _onSearchChanged(String query) {
    if (_debounce?.isActive ?? false) _debounce!.cancel();
    _debounce = Timer(const Duration(milliseconds: 500), () {
      final currentFilter = ref.read(placementDriveFilterProvider);
      ref.read(placementDriveFilterProvider.notifier).state = currentFilter.copyWith(search: query);
    });
  }

  void _showFilterSheet() {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (context) => const FilterSheet(),
    );
  }

  @override
  Widget build(BuildContext context) {
    final drivesAsyncValue = ref.watch(placementDrivesProvider);
    final currentFilter = ref.watch(placementDriveFilterProvider);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.all(AppSpacing.xl),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Find your next opportunity',
                style: Theme.of(context).textTheme.displaySmall,
              ),
              const SizedBox(height: AppSpacing.xs),
              Text(
                'Explore placement opportunities matched to your profile.',
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                  color: AppColors.textSecondary,
                ),
              ),
              const SizedBox(height: AppSpacing.xl),
              Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _searchController,
                      onChanged: _onSearchChanged,
                      decoration: InputDecoration(
                        hintText: 'Search companies, roles...',
                        prefixIcon: const Icon(LucideIcons.search, color: AppColors.textSecondary),
                        filled: true,
                        fillColor: AppColors.surface,
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(AppSpacing.buttonRadius),
                          borderSide: BorderSide.none,
                        ),
                        contentPadding: const EdgeInsets.symmetric(vertical: 0),
                      ),
                    ),
                  ),
                  const SizedBox(width: AppSpacing.md),
                  Container(
                    decoration: BoxDecoration(
                      color: currentFilter.status != null || currentFilter.minimumCgpa != null 
                          ? AppColors.primary.withValues(alpha: 0.1) 
                          : AppColors.surface,
                      borderRadius: BorderRadius.circular(AppSpacing.buttonRadius),
                      border: Border.all(
                        color: currentFilter.status != null || currentFilter.minimumCgpa != null 
                            ? AppColors.primary.withValues(alpha: 0.3) 
                            : Colors.transparent,
                      )
                    ),
                    child: IconButton(
                      icon: Icon(
                        LucideIcons.slidersHorizontal,
                        color: currentFilter.status != null || currentFilter.minimumCgpa != null 
                            ? AppColors.primary 
                            : AppColors.textSecondary,
                      ),
                      onPressed: _showFilterSheet,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
        Expanded(
          child: drivesAsyncValue.when(
            data: (paginatedData) {
              if (paginatedData.results.isEmpty) {
                return _buildEmptyState();
              }
              return RefreshIndicator(
                onRefresh: () async {
                  try {
                    final _ = await ref.refresh(placementDrivesProvider.future);
                  } catch (e) {
                    if (context.mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('Failed to refresh placement drives.'),
                          backgroundColor: AppColors.error,
                        ),
                      );
                    }
                  }
                },
                color: AppColors.primary,
                backgroundColor: AppColors.surfaceElevated,
                child: ListView.separated(
                  padding: const EdgeInsets.symmetric(horizontal: AppSpacing.xl, vertical: AppSpacing.md),
                  itemCount: paginatedData.results.length,
                  separatorBuilder: (context, index) => const SizedBox(height: AppSpacing.md),
                  itemBuilder: (context, index) {
                    final drive = paginatedData.results[index];
                    return PlacementDriveCard(
                      drive: drive,
                      onTap: () {
                        context.push('/placement-drives/${drive.id}');
                      },
                    );
                  },
                ),
              );
            },
            loading: () => const Center(child: CircularProgressIndicator(color: AppColors.primary)),
            error: (error, stack) => Center(
              child: Text(
                'Failed to load drives.',
                style: TextStyle(color: AppColors.error),
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(LucideIcons.searchX, size: 64, color: AppColors.textSecondary.withValues(alpha: 0.5)),
          const SizedBox(height: AppSpacing.lg),
          Text(
            'No opportunities found',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: AppSpacing.sm),
          Text(
            'Try adjusting your filters or search query.',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: AppColors.textSecondary,
            ),
          ),
          const SizedBox(height: AppSpacing.xl),
          TextButton.icon(
            onPressed: () {
              _searchController.clear();
              ref.read(placementDriveFilterProvider.notifier).state = PlacementDriveFilter();
            },
            icon: const Icon(LucideIcons.refreshCw, size: 16),
            label: const Text('Clear Filters'),
          ),
        ],
      ),
    );
  }
}

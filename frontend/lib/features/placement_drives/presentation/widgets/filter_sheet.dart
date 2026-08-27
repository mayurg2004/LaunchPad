import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:launchpad/core/theme/app_colors.dart';
import 'package:launchpad/core/theme/app_spacing.dart';
import '../../providers/placement_drive_provider.dart';

class FilterSheet extends ConsumerWidget {
  const FilterSheet({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final currentFilter = ref.watch(placementDriveFilterProvider);

    return Container(
      padding: const EdgeInsets.all(AppSpacing.lg),
      decoration: const BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.vertical(top: Radius.circular(AppSpacing.borderRadius * 2)),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Filter Drives',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              TextButton(
                onPressed: () {
                  ref.read(placementDriveFilterProvider.notifier).state = PlacementDriveFilter(search: currentFilter.search);
                  Navigator.pop(context);
                },
                child: const Text('Clear All'),
              ),
            ],
          ),
          const SizedBox(height: AppSpacing.md),
          const Divider(color: AppColors.border),
          const SizedBox(height: AppSpacing.md),
          Text(
            'Status',
            style: Theme.of(context).textTheme.labelLarge,
          ),
          const SizedBox(height: AppSpacing.sm),
          Wrap(
            spacing: AppSpacing.sm,
            children: [
              _buildStatusChip(context, ref, currentFilter, 'OPEN', 'Open'),
              _buildStatusChip(context, ref, currentFilter, 'CLOSED', 'Closed'),
              _buildStatusChip(context, ref, currentFilter, 'COMPLETED', 'Completed'),
            ],
          ),
          const SizedBox(height: AppSpacing.xl),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.primary,
                foregroundColor: AppColors.textPrimary,
                padding: const EdgeInsets.symmetric(vertical: AppSpacing.md),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(AppSpacing.buttonRadius),
                ),
              ),
              onPressed: () {
                Navigator.pop(context);
              },
              child: const Text('Apply Filters'),
            ),
          ),
          const SizedBox(height: AppSpacing.lg),
        ],
      ),
    );
  }

  Widget _buildStatusChip(BuildContext context, WidgetRef ref, PlacementDriveFilter filter, String value, String label) {
    final isSelected = filter.status == value;
    return ChoiceChip(
      label: Text(label),
      selected: isSelected,
      onSelected: (selected) {
        ref.read(placementDriveFilterProvider.notifier).state = filter.copyWith(
          status: selected ? value : null,
          clearStatus: !selected,
        );
      },
      selectedColor: AppColors.primary.withValues(alpha: 0.2),
      backgroundColor: AppColors.surfaceElevated,
      side: BorderSide(
        color: isSelected ? AppColors.primary : AppColors.border,
      ),
      labelStyle: TextStyle(
        color: isSelected ? AppColors.primary : AppColors.textSecondary,
      ),
    );
  }
}

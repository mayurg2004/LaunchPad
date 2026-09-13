import 'package:flutter/material.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:responsive_builder/responsive_builder.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../widgets/common/stat_card.dart';
import '../../../widgets/common/surface_card.dart';
import '../../../widgets/common/section_header.dart';
import '../providers/dashboard_provider.dart';

class PODashboardScreen extends ConsumerWidget {
  const PODashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppSpacing.xxl),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHero(context),
          const SizedBox(height: AppSpacing.xxl),
          _buildStatsGrid(ref),
          const SizedBox(height: AppSpacing.xxl),
          _buildRecentActivity(context, ref),
        ],
      ),
    );
  }

  Widget _buildHero(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Expanded(
              child: Text(
                'Placement Officer Dashboard',
                style: Theme.of(context).textTheme.displaySmall,
              ),
            ),
          ],
        ),
        const SizedBox(height: AppSpacing.xs),
        Text(
          'Overview of campus placements.',
          style: Theme.of(context).textTheme.bodyLarge?.copyWith(
            color: AppColors.textSecondary,
          ),
        ),
      ],
    );
  }

  Widget _buildStatsGrid(WidgetRef ref) {
    return ResponsiveBuilder(
      builder: (context, sizingInfo) {
        int crossAxisCount = 4;
        if (sizingInfo.deviceScreenType == DeviceScreenType.mobile) {
          crossAxisCount = 1;
        } else if (sizingInfo.deviceScreenType == DeviceScreenType.tablet) {
          crossAxisCount = 2;
        }

        final summaryAsync = ref.watch(dashboardSummaryProvider);

        return summaryAsync.when(
          data: (data) {
            final studentsCount = data['total_students'] ?? 0;
            final companiesCount = data['total_companies'] ?? 0;
            final drivesCount = data['active_drives'] ?? 0;
            final offersCount = data['total_offers'] ?? 0;

            return GridView.count(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              crossAxisCount: crossAxisCount,
              crossAxisSpacing: AppSpacing.lg,
              mainAxisSpacing: AppSpacing.lg,
              childAspectRatio: 1.5,
              children: [
                StatCard(
                  title: 'Total Students',
                  value: studentsCount.toString(),
                  icon: LucideIcons.users,
                ),
                StatCard(
                  title: 'Companies',
                  value: companiesCount.toString(),
                  icon: LucideIcons.building2,
                ),
                StatCard(
                  title: 'Active Drives',
                  value: drivesCount.toString(),
                  icon: LucideIcons.briefcase,
                ),
                StatCard(
                  title: 'Total Offers',
                  value: offersCount.toString(),
                  icon: LucideIcons.award,
                ),
              ],
            );
          },
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (error, _) => const Center(child: Text('Failed to load stats')),
        );
      },
    );
  }

  Widget _buildRecentActivity(BuildContext context, WidgetRef ref) {
    // We don't have a provider for recent activity yet, but we can add one or use a placeholder for now
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SectionHeader(
          title: 'Recent Activity',
          trailing: TextButton(
            onPressed: () {},
            child: const Text('View All'),
          ),
        ),
        const SizedBox(height: AppSpacing.lg),
        SurfaceCard(
          child: const Center(
            child: Padding(
              padding: EdgeInsets.all(AppSpacing.xl),
              child: Text('Recent activity feed coming soon', style: TextStyle(color: AppColors.textSecondary)),
            ),
          ),
        ),
      ],
    );
  }
}

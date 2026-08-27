import 'package:flutter/material.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../widgets/common/stat_card.dart';
import '../../../widgets/common/surface_card.dart';
import '../../../widgets/common/status_badge.dart';
import '../../../widgets/common/section_header.dart';
import 'package:responsive_builder/responsive_builder.dart';

class DashboardScreen extends StatelessWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppSpacing.xxl),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHero(context),
          const SizedBox(height: AppSpacing.xxl),
          _buildStatsGrid(),
          const SizedBox(height: AppSpacing.xxl),
          _buildRecommendedOpportunities(context),
          const SizedBox(height: AppSpacing.xxl),
          ResponsiveBuilder(
            builder: (context, sizingInfo) {
              if (sizingInfo.deviceScreenType == DeviceScreenType.desktop) {
                return Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(flex: 2, child: _buildUpcomingInterviews(context)),
                    const SizedBox(width: AppSpacing.xl),
                    Expanded(flex: 1, child: _buildResumeAndAI(context)),
                  ],
                );
              }
              return Column(
                children: [
                  _buildUpcomingInterviews(context),
                  const SizedBox(height: AppSpacing.xxl),
                  _buildResumeAndAI(context),
                ],
              );
            },
          ),
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
                'Good morning, Student',
                style: Theme.of(context).textTheme.displaySmall,
              ),
            ),
            Padding(
              padding: const EdgeInsets.only(left: AppSpacing.md),
              child: Text(
                'Last updated just now',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: AppColors.textSecondary,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: AppSpacing.xs),
        Text(
          'Here\'s what\'s happening with your placement journey.',
          style: Theme.of(context).textTheme.bodyLarge?.copyWith(
            color: AppColors.textSecondary,
          ),
        ),
      ],
    );
  }

  Widget _buildStatsGrid() {
    return ResponsiveBuilder(
      builder: (context, sizingInfo) {
        int crossAxisCount = 4;
        if (sizingInfo.deviceScreenType == DeviceScreenType.mobile) {
          crossAxisCount = 1;
        } else if (sizingInfo.deviceScreenType == DeviceScreenType.tablet) {
          crossAxisCount = 2;
        }

        return GridView.count(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          crossAxisCount: crossAxisCount,
          crossAxisSpacing: AppSpacing.lg,
          mainAxisSpacing: AppSpacing.lg,
          childAspectRatio: 1.5,
          children: const [
            StatCard(
              title: 'Applications',
              value: '12',
              icon: LucideIcons.send,
              trend: '+2 this week',
            ),
            StatCard(
              title: 'Interviews',
              value: '3',
              icon: LucideIcons.calendar,
              trend: '1 upcoming',
              isTrendPositive: true,
            ),
            StatCard(
              title: 'Offers',
              value: '1',
              icon: LucideIcons.award,
            ),
            StatCard(
              title: 'Placement Status',
              value: 'Placed',
              icon: LucideIcons.checkCircle,
            ),
          ],
        );
      },
    );
  }

  Widget _buildRecommendedOpportunities(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SectionHeader(
          title: 'Recommended Opportunities',
          trailing: TextButton(
            onPressed: () {},
            child: const Text('View All'),
          ),
        ),
        const SizedBox(height: AppSpacing.lg),
        SizedBox(
          height: 180,
          child: ListView.builder(
            scrollDirection: Axis.horizontal,
            itemCount: 3,
            itemBuilder: (context, index) {
              return Padding(
                padding: const EdgeInsets.only(right: AppSpacing.lg),
                child: SizedBox(
                  width: 300,
                  child: SurfaceCard(
                    onTap: () {},
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              index == 0 ? 'TCS' : index == 1 ? 'Infosys' : 'Wipro',
                              style: Theme.of(context).textTheme.labelLarge,
                            ),
                            const StatusBadge(
                              text: '82% Match',
                              status: BadgeStatus.success,
                            ),
                          ],
                        ),
                        const SizedBox(height: AppSpacing.sm),
                        Text(
                          'Backend Developer',
                          style: Theme.of(context).textTheme.titleLarge,
                        ),
                        const Spacer(),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              '₹8.5 LPA',
                              style: Theme.of(context).textTheme.labelLarge?.copyWith(
                                color: AppColors.primary,
                              ),
                            ),
                            Row(
                              children: [
                                const Icon(LucideIcons.mapPin, size: 14, color: AppColors.textSecondary),
                                const SizedBox(width: AppSpacing.xs),
                                Text('Mumbai', style: Theme.of(context).textTheme.bodySmall),
                              ],
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildUpcomingInterviews(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const SectionHeader(title: 'Upcoming Interviews'),
        const SizedBox(height: AppSpacing.lg),
        SurfaceCard(
          padding: EdgeInsets.zero,
          child: ListView.separated(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: 3,
            separatorBuilder: (context, index) => const Divider(height: 1, color: AppColors.border),
            itemBuilder: (context, index) {
              return ListTile(
                contentPadding: const EdgeInsets.all(AppSpacing.md),
                leading: Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    color: AppColors.primary.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(AppSpacing.borderRadius),
                  ),
                  child: const Center(
                    child: Icon(LucideIcons.calendar, color: AppColors.primary),
                  ),
                ),
                title: Text(
                  'Technical Round - TCS',
                  style: Theme.of(context).textTheme.labelLarge,
                ),
                subtitle: Padding(
                  padding: const EdgeInsets.only(top: AppSpacing.xs),
                  child: Row(
                    children: [
                      const Icon(LucideIcons.clock, size: 14, color: AppColors.textSecondary),
                      const SizedBox(width: AppSpacing.xs),
                      Text('Tomorrow, 10:00 AM', style: Theme.of(context).textTheme.bodySmall),
                      const SizedBox(width: AppSpacing.md),
                      const Icon(LucideIcons.video, size: 14, color: AppColors.textSecondary),
                      const SizedBox(width: AppSpacing.xs),
                      Text('Online', style: Theme.of(context).textTheme.bodySmall),
                    ],
                  ),
                ),
                trailing: const StatusBadge(text: 'Scheduled', status: BadgeStatus.info),
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildResumeAndAI(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const SectionHeader(title: 'Resume Score'),
        const SizedBox(height: AppSpacing.lg),
        SurfaceCard(
          child: Column(
            children: [
              Stack(
                alignment: Alignment.center,
                children: [
                  SizedBox(
                    width: 120,
                    height: 120,
                    child: CircularProgressIndicator(
                      value: 0.78,
                      strokeWidth: 8,
                      backgroundColor: AppColors.surfaceElevated,
                      valueColor: const AlwaysStoppedAnimation<Color>(AppColors.primary),
                    ),
                  ),
                  Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        '78',
                        style: Theme.of(context).textTheme.displaySmall?.copyWith(
                          color: AppColors.primary,
                        ),
                      ),
                      Text(
                        'Score',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    ],
                  ),
                ],
              ),
              const SizedBox(height: AppSpacing.lg),
              const Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  _ResumeStat(label: 'Skills', value: '14'),
                  _ResumeStat(label: 'Suggestions', value: '3'),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: AppSpacing.xxl),
        const SectionHeader(
          title: 'LaunchPad AI',
          subtitle: 'Your personal career assistant',
        ),
        const SizedBox(height: AppSpacing.lg),
        Container(
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(AppSpacing.borderRadius),
            gradient: LinearGradient(
              colors: [
                AppColors.primary.withValues(alpha: 0.2),
                AppColors.secondary.withValues(alpha: 0.2),
              ],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            border: Border.all(color: AppColors.primary.withValues(alpha: 0.3)),
          ),
          child: ListTile(
            contentPadding: const EdgeInsets.all(AppSpacing.lg),
            leading: const Icon(LucideIcons.sparkles, color: AppColors.primary, size: 32),
            title: Text('Resume Analysis', style: Theme.of(context).textTheme.titleLarge),
            subtitle: const Text('Get AI feedback on your latest resume update.'),
            trailing: const Icon(LucideIcons.chevronRight, color: AppColors.textSecondary),
            onTap: () {},
          ),
        ),
      ],
    );
  }
}

class _ResumeStat extends StatelessWidget {
  final String label;
  final String value;

  const _ResumeStat({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(value, style: Theme.of(context).textTheme.titleLarge),
        Text(label, style: Theme.of(context).textTheme.bodySmall),
      ],
    );
  }
}

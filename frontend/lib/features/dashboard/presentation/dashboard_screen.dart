import 'package:flutter/material.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../widgets/common/stat_card.dart';
import '../../../widgets/common/surface_card.dart';
import '../../../widgets/common/status_badge.dart';
import '../../../widgets/common/section_header.dart';
import 'package:responsive_builder/responsive_builder.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import '../../interviews/providers/interview_provider.dart';
import '../../interviews/presentation/widgets/interview_status_badge.dart';
import '../providers/dashboard_provider.dart';
import '../../resumes/providers/resume_provider.dart';

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

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
          _buildRecommendedOpportunities(context, ref),
          const SizedBox(height: AppSpacing.xxl),
          ResponsiveBuilder(
            builder: (context, sizingInfo) {
              if (sizingInfo.deviceScreenType == DeviceScreenType.desktop) {
                return Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(flex: 2, child: _buildUpcomingInterviews(context)),
                    const SizedBox(width: AppSpacing.xl),
                    Expanded(flex: 1, child: _buildResumeAndAI(context, ref)),
                  ],
                );
              }
              return Column(
                children: [
                  _buildUpcomingInterviews(context),
                  const SizedBox(height: AppSpacing.xxl),
                  _buildResumeAndAI(context, ref),
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

  Widget _buildStatsGrid(WidgetRef ref) {
    return ResponsiveBuilder(
      builder: (context, sizingInfo) {
        int crossAxisCount = 4;
        if (sizingInfo.deviceScreenType == DeviceScreenType.mobile) {
          crossAxisCount = 1;
        } else if (sizingInfo.deviceScreenType == DeviceScreenType.tablet) {
          crossAxisCount = 2;
        }

        final summaryAsync = ref.watch(studentDashboardSummaryProvider);

        return summaryAsync.when(
          data: (data) {
            final applicationsCount = data['applications_count'] ?? 0;
            final interviewsCount = data['interviews_count'] ?? 0;
            final offersCount = data['offers_count'] ?? 0;
            final isPlaced = data['is_placed'] ?? false;

            return GridView.count(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              crossAxisCount: crossAxisCount,
              crossAxisSpacing: AppSpacing.lg,
              mainAxisSpacing: AppSpacing.lg,
              childAspectRatio: 1.5,
              children: [
                StatCard(
                  title: 'Applications',
                  value: applicationsCount.toString(),
                  icon: LucideIcons.send,
                ),
                StatCard(
                  title: 'Interviews',
                  value: interviewsCount.toString(),
                  icon: LucideIcons.calendar,
                ),
                StatCard(
                  title: 'Offers',
                  value: offersCount.toString(),
                  icon: LucideIcons.award,
                ),
                StatCard(
                  title: 'Placement Status',
                  value: isPlaced ? 'Placed' : 'Not Placed',
                  icon: isPlaced ? LucideIcons.checkCircle : LucideIcons.clock,
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

  Widget _buildRecommendedOpportunities(BuildContext context, WidgetRef ref) {
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
          child: Consumer(
            builder: (context, ref, child) {
              final drivesAsync = ref.watch(recommendedDrivesProvider);
              
              return drivesAsync.when(
                data: (drives) {
                  if (drives.isEmpty) {
                    return const Center(child: Text('No recommendations available yet. Update your resume!'));
                  }
                  return ListView.builder(
                    scrollDirection: Axis.horizontal,
                    itemCount: drives.length,
                    itemBuilder: (context, index) {
                      final drive = drives[index];
                      return Padding(
                        padding: const EdgeInsets.only(right: AppSpacing.lg),
                        child: SizedBox(
                          width: 300,
                          child: SurfaceCard(
                            onTap: () {
                              context.push('/placement-drives/${drive['placement_drive_id']}');
                            },
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                  children: [
                                    Expanded(
                                      child: Text(
                                        drive['company_name'],
                                        style: Theme.of(context).textTheme.labelLarge,
                                        overflow: TextOverflow.ellipsis,
                                      ),
                                    ),
                                    StatusBadge(
                                      text: '${drive['match_percentage']}% Match',
                                      status: BadgeStatus.success,
                                    ),
                                  ],
                                ),
                                const SizedBox(height: AppSpacing.sm),
                                Text(
                                  drive['job_role'],
                                  style: Theme.of(context).textTheme.titleLarge,
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                ),
                                const Spacer(),
                                Row(
                                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                  children: [
                                    Text(
                                      drive['package_lpa'] != null ? '₹${drive['package_lpa']} LPA' : 'Not Specified',
                                      style: Theme.of(context).textTheme.labelLarge?.copyWith(
                                        color: AppColors.primary,
                                      ),
                                    ),
                                  ],
                                ),
                              ],
                            ),
                          ),
                        ),
                      );
                    },
                  );
                },
                loading: () => const Center(child: CircularProgressIndicator()),
                error: (e, st) => const Center(child: Text('Failed to load recommendations.')),
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
        SectionHeader(
          title: 'Upcoming Interviews',
          trailing: TextButton(
            onPressed: () {
              // The dashboard layout handles tab switching to index 3 for interviews
              // But we can also just use GoRouter if we configured it. 
              // For consistency with Applications, we should ideally use a callback, 
              // but GoRouter is easier here since we didn't pass a callback for interviews.
              // Let's assume the user will navigate via the sidebar.
            },
            child: const Text('View All'),
          ),
        ),
        const SizedBox(height: AppSpacing.lg),
        SurfaceCard(
          padding: EdgeInsets.zero,
          child: Consumer(
            builder: (context, ref, child) {
              final upcomingAsync = ref.watch(upcomingInterviewsProvider);
              
              return upcomingAsync.when(
                data: (interviews) {
                  if (interviews.isEmpty) {
                    return const Padding(
                      padding: EdgeInsets.all(AppSpacing.xl),
                      child: Center(
                        child: Text('No upcoming interviews', style: TextStyle(color: AppColors.textSecondary)),
                      ),
                    );
                  }
                  
                  final displayInterviews = interviews.take(3).toList();
                  
                  return ListView.separated(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    itemCount: displayInterviews.length,
                    separatorBuilder: (context, index) => const Divider(height: 1, color: AppColors.border),
                    itemBuilder: (context, index) {
                      final interview = displayInterviews[index];
                      final dateStr = DateFormat('MMM d, y').format(interview.scheduledAt);
                      final timeStr = DateFormat('h:mm a').format(interview.scheduledAt);
                      final isOnline = interview.meetingLink != null && interview.meetingLink!.isNotEmpty;
                      
                      return ListTile(
                        onTap: () => context.push('/interviews/${interview.id}'),
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
                          '${interview.roundName} - ${interview.companyName ?? 'Company'}',
                          style: Theme.of(context).textTheme.labelLarge,
                        ),
                        subtitle: Padding(
                          padding: const EdgeInsets.only(top: AppSpacing.xs),
                          child: Row(
                            children: [
                              const Icon(LucideIcons.clock, size: 14, color: AppColors.textSecondary),
                              const SizedBox(width: AppSpacing.xs),
                              Text('$dateStr, $timeStr', style: Theme.of(context).textTheme.bodySmall),
                              const SizedBox(width: AppSpacing.md),
                              Icon(isOnline ? LucideIcons.video : LucideIcons.mapPin, size: 14, color: AppColors.textSecondary),
                              const SizedBox(width: AppSpacing.xs),
                              Text(isOnline ? 'Online' : 'In Person', style: Theme.of(context).textTheme.bodySmall),
                            ],
                          ),
                        ),
                        trailing: InterviewStatusBadge(status: interview.status, result: interview.result),
                      );
                    },
                  );
                },
                loading: () => const Padding(
                  padding: EdgeInsets.all(AppSpacing.xl),
                  child: Center(child: CircularProgressIndicator()),
                ),
                error: (error, _) => Padding(
                  padding: const EdgeInsets.all(AppSpacing.xl),
                  child: Center(child: Text('Error loading interviews', style: TextStyle(color: AppColors.error))),
                ),
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildResumeAndAI(BuildContext context, WidgetRef ref) {
    final activeResumeAsync = ref.watch(activeResumeProvider);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const SectionHeader(title: 'Resume Score'),
        const SizedBox(height: AppSpacing.lg),
        activeResumeAsync.when(
          data: (resume) {
            if (resume == null) {
              return SurfaceCard(
                child: const Center(
                  child: Text('No active resume. Please upload one.'),
                ),
              );
            }

            final analysisAsync = ref.watch(resumeAnalysisProvider(resume.id));
            
            return analysisAsync.when(
              data: (analysis) {
                if (analysis == null) {
                  return SurfaceCard(
                    child: const Center(
                      child: Text('Resume not analyzed yet.'),
                    ),
                  );
                }

                return SurfaceCard(
                  child: Column(
                    children: [
                      Stack(
                        alignment: Alignment.center,
                        children: [
                          SizedBox(
                            width: 120,
                            height: 120,
                            child: CircularProgressIndicator(
                              value: analysis.score / 100,
                              strokeWidth: 8,
                              backgroundColor: AppColors.surfaceElevated,
                              valueColor: const AlwaysStoppedAnimation<Color>(AppColors.primary),
                            ),
                          ),
                          Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Text(
                                analysis.score.toStringAsFixed(0),
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
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceAround,
                        children: [
                          _ResumeStat(label: 'Skills', value: analysis.skillsFound.length.toString()),
                          _ResumeStat(label: 'Suggestions', value: analysis.suggestions.length.toString()),
                        ],
                      ),
                    ],
                  ),
                );
              },
              loading: () => const SurfaceCard(child: Center(child: CircularProgressIndicator())),
              error: (_, __) => const SurfaceCard(child: Center(child: Text('Error loading analysis'))),
            );
          },
          loading: () => const SurfaceCard(child: Center(child: CircularProgressIndicator())),
          error: (_, __) => const SurfaceCard(child: Center(child: Text('Error loading resume'))),
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

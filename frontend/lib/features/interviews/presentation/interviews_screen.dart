import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../widgets/common/primary_button.dart';
import '../providers/interview_provider.dart';
import 'widgets/interview_card.dart';
import '../data/models/interview.dart';

class InterviewsScreen extends ConsumerStatefulWidget {
  final VoidCallback onBrowseOpportunities;

  const InterviewsScreen({
    super.key,
    required this.onBrowseOpportunities,
  });

  @override
  ConsumerState<InterviewsScreen> createState() => _InterviewsScreenState();
}

class _InterviewsScreenState extends ConsumerState<InterviewsScreen> {
  String _filter = 'All';

  @override
  Widget build(BuildContext context) {
    final interviewsAsync = ref.watch(allInterviewsProvider);

    return Scaffold(
      backgroundColor: AppColors.background,
      body: interviewsAsync.when(
        data: (interviews) {
          if (interviews.isEmpty) {
            return _buildEmptyState();
          }
          return _buildContent(interviews);
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(LucideIcons.alertCircle, color: AppColors.error, size: 48),
              const SizedBox(height: AppSpacing.md),
              Text('Failed to load interviews', style: Theme.of(context).textTheme.titleLarge),
              const SizedBox(height: AppSpacing.sm),
              Text(error.toString(), style: const TextStyle(color: AppColors.textSecondary)),
              const SizedBox(height: AppSpacing.lg),
              PrimaryButton(
                text: 'Retry',
                onPressed: () => ref.invalidate(allInterviewsProvider),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            LucideIcons.calendarX,
            size: 64,
            color: AppColors.textSecondary.withValues(alpha: 0.5),
          ),
          const SizedBox(height: AppSpacing.lg),
          Text(
            'No interviews scheduled',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: AppSpacing.sm),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: AppSpacing.xxl * 2),
            child: Text(
              'Your scheduled placement interviews will appear here.',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: AppColors.textSecondary,
              ),
            ),
          ),
          const SizedBox(height: AppSpacing.xl),
          PrimaryButton(
            text: 'Browse Opportunities',
            onPressed: widget.onBrowseOpportunities,
            icon: LucideIcons.search,
          ),
        ],
      ),
    );
  }

  Widget _buildContent(List<Interview> allInterviews) {
    final now = DateTime.now();
    
    // Groupings
    final upcoming = allInterviews.where((i) => i.scheduledAt.isAfter(now) && i.status == 'SCHEDULED').toList();
    final completed = allInterviews.where((i) => i.status == 'COMPLETED').toList();
    final cancelled = allInterviews.where((i) => i.status == 'CANCELLED').toList();

    // Filtering
    List<Interview> filtered = allInterviews;
    if (_filter == 'Upcoming') filtered = upcoming;
    if (_filter == 'Completed') filtered = completed;
    if (_filter == 'Cancelled') filtered = cancelled;

    // Sorting
    filtered.sort((a, b) => a.scheduledAt.compareTo(b.scheduledAt));

    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppSpacing.xxl),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildOverviewCards(upcoming.length, completed.length, upcoming.isNotEmpty ? upcoming.first : null),
          const SizedBox(height: AppSpacing.xxl),
          _buildFilters(),
          const SizedBox(height: AppSpacing.xl),
          if (filtered.isEmpty)
            Padding(
              padding: const EdgeInsets.only(top: AppSpacing.xxl),
              child: Center(
                child: Text('No interviews found for this filter.', style: Theme.of(context).textTheme.bodyLarge?.copyWith(color: AppColors.textSecondary)),
              ),
            )
          else
            ListView.separated(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: filtered.length,
              separatorBuilder: (_, _) => const SizedBox(height: AppSpacing.md),
              itemBuilder: (context, index) {
                final interview = filtered[index];
                return InterviewCard(
                  interview: interview,
                  onTap: () => context.push('/interviews/${interview.id}'),
                );
              },
            ),
        ],
      ),
    );
  }

  Widget _buildOverviewCards(int upcomingCount, int completedCount, Interview? nextInterview) {
    String nextStr = 'None';
    if (nextInterview != null) {
      final diff = nextInterview.scheduledAt.difference(DateTime.now());
      if (diff.inDays == 0) {
        nextStr = 'Today';
      } else if (diff.inDays == 1) {
        nextStr = 'Tomorrow';
      } else {
        nextStr = 'In ${diff.inDays} days';
      }
    }

    return Row(
      children: [
        Expanded(child: _OverviewStatCard(title: 'Upcoming', value: '$upcomingCount', icon: LucideIcons.calendarClock)),
        const SizedBox(width: AppSpacing.lg),
        Expanded(child: _OverviewStatCard(title: 'Completed', value: '$completedCount', icon: LucideIcons.calendarCheck)),
        const SizedBox(width: AppSpacing.lg),
        Expanded(child: _OverviewStatCard(title: 'Next Interview', value: nextStr, icon: LucideIcons.forward)),
      ],
    );
  }

  Widget _buildFilters() {
    final filters = ['All', 'Upcoming', 'Completed', 'Cancelled'];
    return Wrap(
      spacing: AppSpacing.sm,
      children: filters.map((f) {
        final isSelected = _filter == f;
        return FilterChip(
          label: Text(f),
          selected: isSelected,
          onSelected: (selected) {
            setState(() => _filter = f);
          },
          backgroundColor: AppColors.surface,
          selectedColor: AppColors.primary.withValues(alpha: 0.1),
          checkmarkColor: AppColors.primary,
          labelStyle: TextStyle(
            color: isSelected ? AppColors.primary : AppColors.textSecondary,
            fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
          ),
          side: BorderSide(
            color: isSelected ? AppColors.primary : AppColors.border,
          ),
        );
      }).toList(),
    );
  }
}

class _OverviewStatCard extends StatelessWidget {
  final String title;
  final String value;
  final IconData icon;

  const _OverviewStatCard({
    required this.title,
    required this.value,
    required this.icon,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(AppSpacing.lg),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(AppSpacing.borderRadius),
        border: Border.all(color: AppColors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(title, style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: AppColors.textSecondary)),
              Icon(icon, size: 20, color: AppColors.primary),
            ],
          ),
          const SizedBox(height: AppSpacing.md),
          Text(value, style: Theme.of(context).textTheme.headlineMedium),
        ],
      ),
    );
  }
}

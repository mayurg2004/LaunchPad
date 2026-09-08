import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';
import 'package:intl/intl.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../widgets/common/primary_button.dart';
import '../../../widgets/common/surface_card.dart';
import '../../../widgets/common/section_header.dart';
import '../providers/interview_provider.dart';
import 'widgets/interview_status_badge.dart';

class InterviewDetailsScreen extends ConsumerWidget {
  final int interviewId;

  const InterviewDetailsScreen({
    super.key,
    required this.interviewId,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final interviewAsync = ref.watch(interviewDetailsProvider(interviewId));

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Interview Details'),
      ),
      body: interviewAsync.when(
        data: (interview) {
          return SingleChildScrollView(
            padding: const EdgeInsets.all(AppSpacing.xxl),
            child: Center(
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 800),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildHeader(context, interview),
                    const SizedBox(height: AppSpacing.xxl),
                    _buildTimeline(context, interview),
                    const SizedBox(height: AppSpacing.xxl),
                    _buildDetailsCard(context, interview),
                  ],
                ),
              ),
            ),
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => Center(child: Text('Error: $error')),
      ),
    );
  }

  Widget _buildHeader(BuildContext context, interview) {
    return SurfaceCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      interview.companyName ?? 'Company',
                      style: Theme.of(context).textTheme.headlineMedium,
                    ),
                    const SizedBox(height: AppSpacing.xs),
                    Text(
                      interview.jobRole ?? 'Role',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            color: AppColors.textSecondary,
                          ),
                    ),
                  ],
                ),
              ),
              InterviewStatusBadge(
                status: interview.status,
                result: interview.result,
              ),
            ],
          ),
          const SizedBox(height: AppSpacing.xl),
          if (interview.meetingLink != null && interview.meetingLink!.isNotEmpty)
            PrimaryButton(
              text: 'Join Interview',
              icon: LucideIcons.video,
              onPressed: () async {
                final url = Uri.parse(interview.meetingLink!);
                if (await canLaunchUrl(url)) {
                  await launchUrl(url);
                } else {
                  if (context.mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Could not open meeting link')),
                    );
                  }
                }
              },
            ),
        ],
      ),
    );
  }

  Widget _buildTimeline(BuildContext context, interview) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const SectionHeader(title: 'Recruitment Process'),
        const SizedBox(height: AppSpacing.lg),
        SurfaceCard(
          child: Column(
            children: [
              _buildTimelineStep(context, 'Application', true, true, false),
              _buildTimelineStep(context, 'Shortlisted', true, true, false),
              _buildTimelineStep(
                context, 
                '${interview.roundName} (${interview.roundType})', 
                true, 
                interview.status == 'COMPLETED',
                interview.status == 'COMPLETED' && interview.result == 'FAILED',
              ),
              _buildTimelineStep(context, 'Offer', false, false, false, isLast: true),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildTimelineStep(BuildContext context, String title, bool isCurrentOrPast, bool isCompleted, bool isFailed, {bool isLast = false}) {
    final color = isFailed 
        ? AppColors.error 
        : (isCompleted ? AppColors.success : (isCurrentOrPast ? AppColors.primary : AppColors.border));
        
    final icon = isFailed 
        ? LucideIcons.xCircle
        : (isCompleted ? LucideIcons.checkCircle2 : LucideIcons.circle);

    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Column(
          children: [
            Icon(icon, color: color, size: 24),
            if (!isLast)
              Container(
                width: 2,
                height: 40,
                color: isCompleted ? AppColors.success : AppColors.border,
              ),
          ],
        ),
        const SizedBox(width: AppSpacing.md),
        Expanded(
          child: Padding(
            padding: const EdgeInsets.only(top: 2),
            child: Text(
              title,
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    color: isCurrentOrPast ? AppColors.textPrimary : AppColors.textSecondary,
                    fontWeight: isCurrentOrPast ? FontWeight.bold : FontWeight.normal,
                  ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildDetailsCard(BuildContext context, interview) {
    final dateFormatter = DateFormat('EEEE, MMMM d, y');
    final timeFormatter = DateFormat('h:mm a');

    return SurfaceCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SectionHeader(title: 'Details'),
          const SizedBox(height: AppSpacing.lg),
          _buildDetailRow(context, LucideIcons.calendar, 'Date', dateFormatter.format(interview.scheduledAt)),
          const SizedBox(height: AppSpacing.md),
          _buildDetailRow(context, LucideIcons.clock, 'Time', '${timeFormatter.format(interview.scheduledAt)} (${interview.durationMinutes} mins)'),
          const SizedBox(height: AppSpacing.md),
          _buildDetailRow(
            context, 
            LucideIcons.mapPin, 
            'Location', 
            interview.location?.isNotEmpty == true ? interview.location! : (interview.meetingLink?.isNotEmpty == true ? 'Online' : 'TBD'),
          ),
          if (interview.interviewerName != null && interview.interviewerName!.isNotEmpty) ...[
            const SizedBox(height: AppSpacing.md),
            _buildDetailRow(context, LucideIcons.user, 'Interviewer', '${interview.interviewerName}'),
          ],
          if (interview.feedback != null && interview.feedback!.isNotEmpty) ...[
            const SizedBox(height: AppSpacing.lg),
            const Divider(color: AppColors.border),
            const SizedBox(height: AppSpacing.lg),
            const SectionHeader(title: 'Feedback / Result Notes'),
            const SizedBox(height: AppSpacing.sm),
            Text(interview.feedback!, style: Theme.of(context).textTheme.bodyMedium),
          ]
        ],
      ),
    );
  }

  Widget _buildDetailRow(BuildContext context, IconData icon, String label, String value) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, size: 20, color: AppColors.textSecondary),
        const SizedBox(width: AppSpacing.md),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(label, style: Theme.of(context).textTheme.bodySmall?.copyWith(color: AppColors.textSecondary)),
              const SizedBox(height: 2),
              Text(value, style: Theme.of(context).textTheme.bodyMedium),
            ],
          ),
        ),
      ],
    );
  }
}

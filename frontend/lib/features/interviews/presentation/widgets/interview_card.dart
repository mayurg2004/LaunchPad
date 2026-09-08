import 'package:flutter/material.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';
import 'package:intl/intl.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_spacing.dart';
import '../../../../widgets/common/surface_card.dart';
import '../../data/models/interview.dart';
import 'interview_status_badge.dart';

class InterviewCard extends StatelessWidget {
  final Interview interview;
  final VoidCallback onTap;

  const InterviewCard({
    super.key,
    required this.interview,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final dateFormatter = DateFormat('MMM d, y');
    final timeFormatter = DateFormat('h:mm a');

    final dateString = dateFormatter.format(interview.scheduledAt);
    final timeString = timeFormatter.format(interview.scheduledAt);
    final isOnline = interview.meetingLink != null && interview.meetingLink!.isNotEmpty;
    final locationText = isOnline ? 'Online' : (interview.location?.isNotEmpty == true ? 'In Person' : 'TBD');

    return SurfaceCard(
      onTap: onTap,
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
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                    const SizedBox(height: AppSpacing.xs),
                    Text(
                      interview.jobRole ?? 'Role',
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
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
          const SizedBox(height: AppSpacing.lg),
          const Divider(height: 1, color: AppColors.border),
          const SizedBox(height: AppSpacing.lg),
          Row(
            children: [
              Expanded(
                child: _buildInfoRow(
                  context,
                  LucideIcons.list,
                  '${interview.roundName} (${interview.roundType})',
                ),
              ),
            ],
          ),
          const SizedBox(height: AppSpacing.sm),
          Row(
            children: [
              Expanded(
                flex: 3,
                child: _buildInfoRow(
                  context,
                  LucideIcons.calendar,
                  '$dateString \u00B7 $timeString',
                ),
              ),
              Expanded(
                flex: 2,
                child: _buildInfoRow(
                  context,
                  isOnline ? LucideIcons.video : LucideIcons.mapPin,
                  locationText,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildInfoRow(BuildContext context, IconData icon, String text) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 16, color: AppColors.textSecondary),
        const SizedBox(width: AppSpacing.sm),
        Flexible(
          child: Text(
            text,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: AppColors.textSecondary,
                ),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ),
      ],
    );
  }
}

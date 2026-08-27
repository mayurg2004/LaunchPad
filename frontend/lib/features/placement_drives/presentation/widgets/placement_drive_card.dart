import 'package:flutter/material.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';
import 'package:launchpad/core/theme/app_colors.dart';
import 'package:launchpad/core/theme/app_spacing.dart';
import 'package:launchpad/widgets/common/surface_card.dart';
import 'package:launchpad/widgets/common/status_badge.dart';
import '../../data/models/placement_drive.dart';
import 'package:intl/intl.dart';

class PlacementDriveCard extends StatelessWidget {
  final PlacementDrive drive;
  final VoidCallback onTap;

  const PlacementDriveCard({
    super.key,
    required this.drive,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return SurfaceCard(
      onTap: onTap,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              _buildCompanyLogo(context),
              const SizedBox(width: AppSpacing.md),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      drive.companyName,
                      style: Theme.of(context).textTheme.labelLarge?.copyWith(
                            color: AppColors.textSecondary,
                          ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      drive.title,
                      style: Theme.of(context).textTheme.titleLarge,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ),
              ),
              _buildStatusBadge(),
            ],
          ),
          const SizedBox(height: AppSpacing.md),
          const Divider(color: AppColors.border),
          const SizedBox(height: AppSpacing.md),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _buildInfoItem(
                context,
                icon: LucideIcons.indianRupee,
                text: drive.packageLpa != null
                    ? '${drive.packageLpa} LPA'
                    : 'Not Disclosed',
                isHighlight: true,
              ),
              _buildInfoItem(
                context,
                icon: LucideIcons.mapPin,
                text: drive.location.isNotEmpty ? drive.location : 'Remote',
              ),
            ],
          ),
          const SizedBox(height: AppSpacing.sm),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _buildInfoItem(
                context,
                icon: LucideIcons.briefcase,
                text: drive.jobRole,
              ),
              if (drive.applicationDeadline != null)
                _buildInfoItem(
                  context,
                  icon: LucideIcons.calendar,
                  text: DateFormat('MMM dd, yyyy').format(drive.applicationDeadline!),
                  isWarning: drive.applicationDeadline!.isBefore(DateTime.now()),
                ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildCompanyLogo(BuildContext context) {
    return Container(
      width: 48,
      height: 48,
      decoration: BoxDecoration(
        color: AppColors.primary.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(AppSpacing.borderRadius),
        border: Border.all(color: AppColors.primary.withValues(alpha: 0.2)),
      ),
      child: Center(
        child: Text(
          drive.companyName.isNotEmpty ? drive.companyName[0].toUpperCase() : 'C',
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
                color: AppColors.primary,
                fontWeight: FontWeight.bold,
              ),
        ),
      ),
    );
  }

  Widget _buildStatusBadge() {
    BadgeStatus status;
    switch (drive.status) {
      case 'OPEN':
        status = BadgeStatus.success;
        break;
      case 'CLOSED':
        status = BadgeStatus.error;
        break;
      case 'COMPLETED':
        status = BadgeStatus.info;
        break;
      case 'DRAFT':
        status = BadgeStatus.warning;
        break;
      default:
        status = BadgeStatus.neutral;
    }
    return StatusBadge(text: drive.status, status: status);
  }

  Widget _buildInfoItem(
    BuildContext context, {
    required IconData icon,
    required String text,
    bool isHighlight = false,
    bool isWarning = false,
  }) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(
          icon,
          size: 16,
          color: isHighlight
              ? AppColors.primary
              : (isWarning ? AppColors.warning : AppColors.textSecondary),
        ),
        const SizedBox(width: AppSpacing.xs),
        Text(
          text,
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: isHighlight
                    ? AppColors.primary
                    : (isWarning ? AppColors.warning : AppColors.textSecondary),
                fontWeight: isHighlight ? FontWeight.bold : FontWeight.normal,
              ),
        ),
      ],
    );
  }
}

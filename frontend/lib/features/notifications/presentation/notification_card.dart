import 'package:flutter/material.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_spacing.dart';
import '../data/notification_model.dart';
import 'package:timeago/timeago.dart' as timeago;

class NotificationCard extends StatelessWidget {
  final NotificationModel notification;
  final VoidCallback onTap;

  const NotificationCard({
    super.key,
    required this.notification,
    required this.onTap,
  });

  IconData _getIcon() {
    switch (notification.notificationType) {
      case 'PLACEMENT_DRIVE':
        return LucideIcons.briefcase;
      case 'APPLICATION':
        return LucideIcons.fileText;
      case 'INTERVIEW':
        return LucideIcons.calendarDays;
      case 'OFFER':
        return LucideIcons.award;
      case 'SYSTEM':
      default:
        return LucideIcons.bell;
    }
  }

  Color _getIconBackgroundColor() {
    switch (notification.notificationType) {
      case 'OFFER':
        return AppColors.successBackground;
      case 'INTERVIEW':
        return AppColors.infoBackground;
      default:
        return AppColors.surfaceElevated;
    }
  }

  Color _getIconColor() {
    switch (notification.notificationType) {
      case 'OFFER':
        return AppColors.success;
      case 'INTERVIEW':
        return AppColors.info;
      default:
        return AppColors.primary;
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isUnread = !notification.isRead;

    return InkWell(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(AppSpacing.md),
        decoration: BoxDecoration(
          color: isUnread ? AppColors.primary.withValues(alpha: 0.05) : Colors.transparent,
          border: Border(
            left: BorderSide(
              color: isUnread ? AppColors.primary : Colors.transparent,
              width: 3,
            ),
            bottom: const BorderSide(
              color: AppColors.border,
              width: 1,
            ),
          ),
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              padding: const EdgeInsets.all(AppSpacing.sm),
              decoration: BoxDecoration(
                color: _getIconBackgroundColor(),
                borderRadius: BorderRadius.circular(AppSpacing.buttonRadius),
              ),
              child: Icon(
                _getIcon(),
                color: _getIconColor(),
                size: 20,
              ),
            ),
            const SizedBox(width: AppSpacing.md),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(
                        child: Text(
                          notification.title,
                          style: theme.textTheme.labelLarge?.copyWith(
                            fontWeight: isUnread ? FontWeight.w700 : FontWeight.w600,
                            color: isUnread ? AppColors.textPrimary : AppColors.textSecondary,
                          ),
                        ),
                      ),
                      const SizedBox(width: AppSpacing.xs),
                      Text(
                        timeago.format(notification.createdAt),
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: isUnread ? AppColors.primary : AppColors.textHint,
                          fontWeight: isUnread ? FontWeight.w600 : FontWeight.w400,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: AppSpacing.xs),
                  Text(
                    notification.message,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: isUnread ? AppColors.textSecondary : AppColors.textHint,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

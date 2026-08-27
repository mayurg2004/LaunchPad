import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_spacing.dart';

enum BadgeStatus { success, warning, error, info, neutral }

class StatusBadge extends StatelessWidget {
  final String text;
  final BadgeStatus status;

  const StatusBadge({
    super.key,
    required this.text,
    this.status = BadgeStatus.neutral,
  });

  @override
  Widget build(BuildContext context) {
    Color backgroundColor;
    Color textColor;

    switch (status) {
      case BadgeStatus.success:
        backgroundColor = AppColors.successBackground;
        textColor = AppColors.success;
        break;
      case BadgeStatus.warning:
        backgroundColor = AppColors.warningBackground;
        textColor = AppColors.warning;
        break;
      case BadgeStatus.error:
        backgroundColor = AppColors.errorBackground;
        textColor = AppColors.error;
        break;
      case BadgeStatus.info:
        backgroundColor = AppColors.infoBackground;
        textColor = AppColors.info;
        break;
      case BadgeStatus.neutral:
        backgroundColor = AppColors.surfaceElevated;
        textColor = AppColors.textSecondary;
        break;
    }

    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: AppSpacing.sm,
        vertical: AppSpacing.xs,
      ),
      decoration: BoxDecoration(
        color: backgroundColor,
        borderRadius: BorderRadius.circular(AppSpacing.buttonRadius),
      ),
      child: Text(
        text,
        style: Theme.of(context).textTheme.bodySmall?.copyWith(
          color: textColor,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
}

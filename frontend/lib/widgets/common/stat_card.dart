import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_spacing.dart';
import 'surface_card.dart';

class StatCard extends StatelessWidget {
  final String title;
  final String value;
  final IconData icon;
  final String? trend;
  final bool isTrendPositive;

  const StatCard({
    super.key,
    required this.title,
    required this.value,
    required this.icon,
    this.trend,
    this.isTrendPositive = true,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return SurfaceCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                title,
                style: theme.textTheme.labelLarge?.copyWith(
                  color: AppColors.textSecondary,
                ),
              ),
              Container(
                padding: const EdgeInsets.all(AppSpacing.sm),
                decoration: BoxDecoration(
                  color: AppColors.surfaceElevated,
                  borderRadius: BorderRadius.circular(AppSpacing.buttonRadius),
                ),
                child: Icon(
                  icon,
                  size: 20,
                  color: AppColors.primary,
                ),
              ),
            ],
          ),
          const SizedBox(height: AppSpacing.md),
          Text(
            value,
            style: theme.textTheme.displayMedium,
          ),
          if (trend != null) ...[
            const SizedBox(height: AppSpacing.sm),
            Row(
              children: [
                Icon(
                  isTrendPositive ? Icons.arrow_upward : Icons.arrow_downward,
                  size: 14,
                  color: isTrendPositive ? AppColors.success : AppColors.error,
                ),
                const SizedBox(width: AppSpacing.xs),
                Text(
                  trend!,
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: isTrendPositive ? AppColors.success : AppColors.error,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ]
        ],
      ),
    );
  }
}

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';
import 'package:intl/intl.dart';
import 'package:launchpad/core/theme/app_colors.dart';
import 'package:launchpad/core/theme/app_spacing.dart';
import 'package:launchpad/widgets/common/primary_button.dart';
import 'package:launchpad/widgets/common/status_badge.dart';
import '../providers/placement_drive_provider.dart';
import '../providers/application_provider.dart';
import '../data/models/placement_drive.dart';
import '../data/models/application.dart';

class PlacementDriveDetailsScreen extends ConsumerWidget {
  final int driveId;

  const PlacementDriveDetailsScreen({super.key, required this.driveId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final driveAsync = ref.watch(placementDriveDetailsProvider(driveId));
    final myApplicationsAsync = ref.watch(myApplicationsProvider);
    final applicationState = ref.watch(applicationNotifierProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Drive Details'),
        backgroundColor: AppColors.background,
        elevation: 0,
      ),
      body: driveAsync.when(
        data: (drive) {
          final isDeadlinePassed = drive.applicationDeadline != null &&
              drive.applicationDeadline!.isBefore(DateTime.now());

          // Find if user already applied
          Application? myApp;
          if (myApplicationsAsync is AsyncData) {
            final apps = myApplicationsAsync.value!;
            try {
              myApp = apps.firstWhere((app) => app.placementDriveId == driveId);
            } catch (e) {
              myApp = null;
            }
          }

          return SingleChildScrollView(
            padding: const EdgeInsets.all(AppSpacing.xl),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildHeader(context, drive),
                const SizedBox(height: AppSpacing.xxl),
                _buildDetailsGrid(context, drive),
                const SizedBox(height: AppSpacing.xxl),
                _buildJobDescription(context, drive.jobDescription),
                const SizedBox(height: AppSpacing.xxl),
                _buildEligibilitySection(context, drive),
                const SizedBox(height: AppSpacing.xxl),
                if (myApp != null)
                  _buildApplicationStatus(context, myApp)
                else
                  _buildApplySection(context, ref, drive, isDeadlinePassed, applicationState),
                const SizedBox(height: AppSpacing.xxl),
              ],
            ),
          );
        },
        loading: () => const Center(child: CircularProgressIndicator(color: AppColors.primary)),
        error: (err, stack) => Center(
          child: Text('Error loading details.', style: TextStyle(color: AppColors.error)),
        ),
      ),
    );
  }

  Widget _buildHeader(BuildContext context, PlacementDrive drive) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: 80,
          height: 80,
          decoration: BoxDecoration(
            color: AppColors.primary.withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(AppSpacing.borderRadius),
            border: Border.all(color: AppColors.primary.withValues(alpha: 0.3)),
          ),
          child: Center(
            child: Text(
              drive.companyName.isNotEmpty ? drive.companyName[0].toUpperCase() : 'C',
              style: Theme.of(context).textTheme.displaySmall?.copyWith(
                    color: AppColors.primary,
                  ),
            ),
          ),
        ),
        const SizedBox(width: AppSpacing.xl),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                drive.companyName,
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      color: AppColors.textSecondary,
                    ),
              ),
              const SizedBox(height: AppSpacing.xs),
              Text(
                drive.title,
                style: Theme.of(context).textTheme.displaySmall,
              ),
              const SizedBox(height: AppSpacing.md),
              Row(
                children: [
                  StatusBadge(
                    text: drive.status,
                    status: drive.status == 'OPEN' ? BadgeStatus.success : BadgeStatus.warning,
                  ),
                ],
              )
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildDetailsGrid(BuildContext context, PlacementDrive drive) {
    return Container(
      padding: const EdgeInsets.all(AppSpacing.lg),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(AppSpacing.borderRadius),
        border: Border.all(color: AppColors.border),
      ),
      child: Wrap(
        spacing: AppSpacing.xl,
        runSpacing: AppSpacing.xl,
        children: [
          _buildDetailItem(context, LucideIcons.briefcase, 'Job Role', drive.jobRole),
          _buildDetailItem(context, LucideIcons.indianRupee, 'Package', 
              drive.packageLpa != null ? '${drive.packageLpa} LPA' : 'Not Disclosed'),
          _buildDetailItem(context, LucideIcons.mapPin, 'Location', 
              drive.location.isNotEmpty ? drive.location : 'Remote'),
          if (drive.driveDate != null)
            _buildDetailItem(context, LucideIcons.calendarClock, 'Drive Date', 
                DateFormat('MMM dd, yyyy - hh:mm a').format(drive.driveDate!)),
        ],
      ),
    );
  }

  Widget _buildDetailItem(BuildContext context, IconData icon, String label, String value) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, color: AppColors.primary, size: 24),
        const SizedBox(width: AppSpacing.md),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(label, style: Theme.of(context).textTheme.bodySmall?.copyWith(color: AppColors.textSecondary)),
            Text(value, style: Theme.of(context).textTheme.titleMedium),
          ],
        ),
      ],
    );
  }

  Widget _buildJobDescription(BuildContext context, String description) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Job Description', style: Theme.of(context).textTheme.titleLarge),
        const SizedBox(height: AppSpacing.md),
        Text(
          description.isNotEmpty ? description : 'No description provided.',
          style: Theme.of(context).textTheme.bodyLarge?.copyWith(height: 1.6),
        ),
      ],
    );
  }

  Widget _buildEligibilitySection(BuildContext context, PlacementDrive drive) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Eligibility & Requirements', style: Theme.of(context).textTheme.titleLarge),
        const SizedBox(height: AppSpacing.md),
        Container(
          padding: const EdgeInsets.all(AppSpacing.lg),
          decoration: BoxDecoration(
            color: AppColors.surface,
            borderRadius: BorderRadius.circular(AppSpacing.borderRadius),
            border: Border.all(color: AppColors.border),
          ),
          child: Column(
            children: [
              _buildRequirementRow(context, 'Minimum CGPA', drive.minimumCgpa?.toString() ?? 'No minimum'),
              const Divider(color: AppColors.border),
              _buildRequirementRow(context, 'Eligible Branches', drive.eligibleBranch.isNotEmpty ? drive.eligibleBranch : 'All Branches'),
              const Divider(color: AppColors.border),
              _buildRequirementRow(context, 'Application Deadline', 
                  drive.applicationDeadline != null ? DateFormat('MMM dd, yyyy - hh:mm a').format(drive.applicationDeadline!) : 'None',
                  isWarning: drive.applicationDeadline != null && drive.applicationDeadline!.isBefore(DateTime.now())),
              if (drive.requiredSkills.isNotEmpty) ...[
                const Divider(color: AppColors.border),
                _buildRequirementRow(context, 'Required Skills', drive.requiredSkills.join(', ')),
              ]
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildRequirementRow(BuildContext context, String label, String value, {bool isWarning = false}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: AppSpacing.sm),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(
            flex: 2,
            child: Text(label, style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: AppColors.textSecondary)),
          ),
          Expanded(
            flex: 3,
            child: Text(
              value,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    fontWeight: FontWeight.w500,
                    color: isWarning ? AppColors.error : AppColors.textPrimary,
                  ),
              textAlign: TextAlign.right,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildApplicationStatus(BuildContext context, Application app) {
    BadgeStatus badgeStatus;
    switch (app.status) {
      case 'APPLIED': badgeStatus = BadgeStatus.info; break;
      case 'SHORTLISTED': badgeStatus = BadgeStatus.success; break;
      case 'SELECTED': badgeStatus = BadgeStatus.success; break;
      case 'REJECTED': badgeStatus = BadgeStatus.error; break;
      default: badgeStatus = BadgeStatus.neutral;
    }

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(AppSpacing.xl),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(AppSpacing.borderRadius),
        border: Border.all(color: AppColors.primary.withValues(alpha: 0.5)),
      ),
      child: Column(
        children: [
          const Icon(LucideIcons.checkCircle, color: AppColors.success, size: 48),
          const SizedBox(height: AppSpacing.md),
          Text('Application Submitted', style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: AppSpacing.sm),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text('Current Status: ', style: Theme.of(context).textTheme.bodyMedium),
              StatusBadge(text: app.status, status: badgeStatus),
            ],
          ),
          const SizedBox(height: AppSpacing.md),
          Text(
            'Applied on ${DateFormat('MMM dd, yyyy').format(app.appliedAt)}',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(color: AppColors.textSecondary),
          ),
        ],
      ),
    );
  }

  Widget _buildApplySection(BuildContext context, WidgetRef ref, PlacementDrive drive, bool isDeadlinePassed, AsyncValue<Application?> applyState) {
    if (drive.status != 'OPEN') {
      return _buildAlertBox(context, 'This drive is not currently open for applications.', LucideIcons.lock);
    }
    
    if (isDeadlinePassed) {
      return _buildAlertBox(context, 'The application deadline has passed.', LucideIcons.clock);
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (applyState.hasError)
          Padding(
            padding: const EdgeInsets.only(bottom: AppSpacing.md),
            child: _buildAlertBox(context, applyState.error.toString(), LucideIcons.alertCircle, isError: true),
          ),
        SizedBox(
          width: double.infinity,
          height: 56,
          child: PrimaryButton(
            text: 'Apply Now',
            isLoading: applyState.isLoading,
            onPressed: () => _showApplyConfirmation(context, ref, drive),
          ),
        ),
      ],
    );
  }

  Widget _buildAlertBox(BuildContext context, String message, IconData icon, {bool isError = false}) {
    final color = isError ? AppColors.error : AppColors.warning;
    final bgColor = isError ? AppColors.errorBackground : AppColors.warningBackground;

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(AppSpacing.md),
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(AppSpacing.borderRadius),
        border: Border.all(color: color.withValues(alpha: 0.5)),
      ),
      child: Row(
        children: [
          Icon(icon, color: color),
          const SizedBox(width: AppSpacing.md),
          Expanded(child: Text(message, style: TextStyle(color: color))),
        ],
      ),
    );
  }

  void _showApplyConfirmation(BuildContext context, WidgetRef ref, PlacementDrive drive) {
    showDialog(
      context: context,
      builder: (dialogContext) {
        return AlertDialog(
          backgroundColor: AppColors.surface,
          title: const Text('Confirm Application'),
          content: Text(
            'Are you sure you want to apply for ${drive.jobRole} at ${drive.companyName}?',
            style: Theme.of(context).textTheme.bodyLarge,
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(dialogContext),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.primary,
                foregroundColor: AppColors.textPrimary,
              ),
              onPressed: () async {
                Navigator.pop(dialogContext); // Close dialog
                final success = await ref.read(applicationNotifierProvider.notifier).apply(drive.id);
                if (success && context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: const Text('Application submitted successfully!'),
                      backgroundColor: AppColors.success,
                      behavior: SnackBarBehavior.floating,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                    ),
                  );
                }
              },
              child: const Text('Confirm Apply'),
            ),
          ],
        );
      },
    );
  }
}

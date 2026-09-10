import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_spacing.dart';
import '../providers/resume_provider.dart';
import '../../placement_drives/providers/placement_drive_provider.dart';

class SkillGapScreen extends ConsumerStatefulWidget {
  final int resumeId;

  const SkillGapScreen({super.key, required this.resumeId});

  @override
  ConsumerState<SkillGapScreen> createState() => _SkillGapScreenState();
}

class _SkillGapScreenState extends ConsumerState<SkillGapScreen> {
  int? _selectedDriveId;

  @override
  Widget build(BuildContext context) {
    final drivesAsync = ref.watch(placementDrivesProvider);

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Skill Gap Analysis'),
        backgroundColor: AppColors.surface,
        leading: IconButton(
          icon: const Icon(LucideIcons.arrowLeft),
          onPressed: () => context.pop(),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(AppSpacing.screenPadding),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Compare Your Skills',
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                fontWeight: FontWeight.bold,
                color: AppColors.textPrimary,
              ),
            ),
            const SizedBox(height: AppSpacing.xs),
            Text(
              'Select a placement drive to see how well your resume matches the requirements.',
              style: Theme.of(context).textTheme.bodyLarge?.copyWith(color: AppColors.textSecondary),
            ),
            const SizedBox(height: AppSpacing.xl),
            drivesAsync.when(
              data: (paginatedDrives) {
                final drives = paginatedDrives.results;
                if (drives.isEmpty) {
                  return const Text('No active placement drives available.', style: TextStyle(color: AppColors.textSecondary));
                }

                return Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: AppSpacing.md),
                      decoration: BoxDecoration(
                        color: AppColors.surface,
                        borderRadius: BorderRadius.circular(AppSpacing.borderRadius),
                        border: Border.all(color: AppColors.border),
                      ),
                      child: DropdownButtonHideUnderline(
                        child: DropdownButton<int>(
                          value: _selectedDriveId,
                          hint: const Text('Select a Placement Drive', style: TextStyle(color: AppColors.textSecondary)),
                          isExpanded: true,
                          dropdownColor: AppColors.surfaceElevated,
                          icon: const Icon(LucideIcons.chevronDown, color: AppColors.textSecondary),
                          items: drives.map((drive) {
                            return DropdownMenuItem<int>(
                              value: drive.id,
                              child: Text(
                                '${drive.jobRole} at ${drive.companyName}',
                                style: const TextStyle(color: AppColors.textPrimary),
                              ),
                            );
                          }).toList(),
                          onChanged: (value) {
                            setState(() {
                              _selectedDriveId = value;
                            });
                          },
                        ),
                      ),
                    ),
                    const SizedBox(height: AppSpacing.xxl),
                    if (_selectedDriveId != null)
                      _buildSkillGapResults(),
                  ],
                );
              },
              loading: () => const Center(child: CircularProgressIndicator(color: AppColors.primary)),
              error: (error, _) => Text('Error loading drives: $error', style: const TextStyle(color: AppColors.error)),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSkillGapResults() {
    final skillGapAsync = ref.watch(skillGapProvider({'resumeId': widget.resumeId, 'driveId': _selectedDriveId!}));

    return skillGapAsync.when(
      data: (result) {
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Container(
                    padding: const EdgeInsets.all(AppSpacing.cardPadding),
                    decoration: BoxDecoration(
                      color: AppColors.surface,
                      borderRadius: BorderRadius.circular(AppSpacing.borderRadius),
                      border: Border.all(color: AppColors.primary),
                    ),
                    child: Column(
                      children: [
                        const Text('Match Score', style: TextStyle(color: AppColors.textSecondary, fontWeight: FontWeight.bold)),
                        const SizedBox(height: AppSpacing.sm),
                        Text(
                          '${result.matchPercentage.round()}%',
                          style: Theme.of(context).textTheme.headlineLarge?.copyWith(
                            fontWeight: FontWeight.bold,
                            color: result.matchPercentage >= 70 ? AppColors.success : (result.matchPercentage >= 40 ? AppColors.warning : AppColors.error),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: AppSpacing.xl),
            _buildSkillList('Matched Skills', result.matchedSkills, AppColors.success, LucideIcons.checkCircle),
            const SizedBox(height: AppSpacing.lg),
            _buildSkillList('Missing Skills', result.missingSkills, AppColors.error, LucideIcons.xCircle),
          ],
        );
      },
      loading: () => const Center(child: CircularProgressIndicator(color: AppColors.primary)),
      error: (error, _) => Container(
        padding: const EdgeInsets.all(AppSpacing.lg),
        decoration: BoxDecoration(
          color: AppColors.error.withValues(alpha: 0.1),
          borderRadius: BorderRadius.circular(AppSpacing.borderRadius),
          border: Border.all(color: AppColors.error.withValues(alpha: 0.3)),
        ),
        child: Row(
          children: [
            const Icon(LucideIcons.alertCircle, color: AppColors.error),
            const SizedBox(width: AppSpacing.md),
            Expanded(
              child: Text(
                'Could not load skill gap. Please make sure you have analyzed this resume first.',
                style: const TextStyle(color: AppColors.error),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSkillList(String title, List<String> skills, Color color, IconData icon) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(AppSpacing.cardPadding),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(AppSpacing.borderRadius),
        border: Border.all(color: AppColors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, color: color),
              const SizedBox(width: AppSpacing.sm),
              Text(
                title,
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: AppColors.textPrimary,
                ),
              ),
              const Spacer(),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: color.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text('${skills.length}', style: TextStyle(color: color, fontWeight: FontWeight.bold)),
              ),
            ],
          ),
          const SizedBox(height: AppSpacing.md),
          if (skills.isEmpty)
            const Text('None', style: TextStyle(color: AppColors.textSecondary))
          else
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: skills.map((skill) => Chip(
                label: Text(skill),
                backgroundColor: color.withValues(alpha: 0.1),
                labelStyle: TextStyle(color: color, fontSize: 13),
                side: BorderSide(color: color.withValues(alpha: 0.3)),
              )).toList(),
            ),
        ],
      ),
    );
  }
}

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_spacing.dart';
import '../providers/profile_provider.dart';
import '../data/models/student_profile_model.dart';
import 'package:responsive_builder/responsive_builder.dart';

class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final profileState = ref.watch(profileProvider);

    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: profileState.when(
          data: (profile) {
            if (profile == null) {
              return _buildEmptyState(context);
            }
            return _buildProfileContent(context, ref, profile);
          },
          loading: () => const Center(child: CircularProgressIndicator(color: AppColors.primary)),
          error: (error, _) => Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(LucideIcons.alertCircle, color: AppColors.error, size: 48),
                const SizedBox(height: AppSpacing.md),
                Text('Failed to load profile', style: Theme.of(context).textTheme.titleLarge),
                const SizedBox(height: AppSpacing.sm),
                ElevatedButton(
                  onPressed: () => ref.read(profileProvider.notifier).fetchProfile(),
                  child: const Text('Retry'),
                )
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildEmptyState(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            padding: const EdgeInsets.all(AppSpacing.xl),
            decoration: BoxDecoration(
              color: AppColors.surfaceElevated,
              shape: BoxShape.circle,
            ),
            child: const Icon(LucideIcons.userX, size: 64, color: AppColors.textSecondary),
          ),
          const SizedBox(height: AppSpacing.xl),
          Text(
            'Profile Not Found',
            style: Theme.of(context).textTheme.headlineMedium?.copyWith(
              color: AppColors.textPrimary,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: AppSpacing.md),
          Text(
            'Create your student profile to access LaunchPad features.',
            style: Theme.of(context).textTheme.bodyLarge?.copyWith(color: AppColors.textSecondary),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: AppSpacing.xl),
          ElevatedButton.icon(
            icon: const Icon(LucideIcons.plus),
            label: const Text('Create Profile'),
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.primary,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(horizontal: AppSpacing.xl, vertical: AppSpacing.md),
            ),
            onPressed: () => context.go('/profile/edit'),
          ),
        ],
      ),
    );
  }

  Widget _buildProfileContent(BuildContext context, WidgetRef ref, StudentProfileModel profile) {
    return ResponsiveBuilder(
      builder: (context, sizingInformation) {
        final isMobile = sizingInformation.deviceScreenType == DeviceScreenType.mobile;
        
        return RefreshIndicator(
          onRefresh: () => ref.read(profileProvider.notifier).fetchProfile(),
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(AppSpacing.screenPadding),
            physics: const AlwaysScrollableScrollPhysics(),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildHeader(context, profile, isMobile),
                const SizedBox(height: AppSpacing.xl),
                if (isMobile) ...[
                  _buildCompletionCard(context, profile),
                  const SizedBox(height: AppSpacing.lg),
                ],
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      flex: 2,
                      child: Column(
                        children: [
                          _buildAcademicCard(context, profile),
                          const SizedBox(height: AppSpacing.lg),
                          _buildContactCard(context, profile),
                        ],
                      ),
                    ),
                    if (!isMobile) ...[
                      const SizedBox(width: AppSpacing.xl),
                      Expanded(
                        flex: 1,
                        child: Column(
                          children: [
                            _buildCompletionCard(context, profile),
                            const SizedBox(height: AppSpacing.lg),
                            _buildSkillsCard(context, profile),
                            const SizedBox(height: AppSpacing.lg),
                            _buildResumeCard(context, profile),
                          ],
                        ),
                      ),
                    ]
                  ],
                ),
                if (isMobile) ...[
                  _buildSkillsCard(context, profile),
                  const SizedBox(height: AppSpacing.lg),
                  _buildResumeCard(context, profile),
                ],
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildHeader(BuildContext context, StudentProfileModel profile, bool isMobile) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        Expanded(
          child: Row(
            children: [
              CircleAvatar(
                radius: 40,
                backgroundColor: AppColors.surfaceElevated,
                backgroundImage: profile.profilePhoto != null ? NetworkImage(profile.profilePhoto!) : null,
                child: profile.profilePhoto == null 
                    ? Text(
                        profile.firstName.isNotEmpty ? profile.firstName[0].toUpperCase() : 'S',
                        style: Theme.of(context).textTheme.headlineMedium?.copyWith(color: AppColors.primary),
                      )
                    : null,
              ),
              const SizedBox(width: AppSpacing.lg),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '${profile.firstName} ${profile.lastName}',
                      style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                        color: AppColors.textPrimary,
                        fontWeight: FontWeight.bold,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: AppSpacing.xs),
                    Text(
                      profile.email,
                      style: Theme.of(context).textTheme.bodyLarge?.copyWith(color: AppColors.textSecondary),
                    ),
                    if (profile.isPlaced)
                      Container(
                        margin: const EdgeInsets.only(top: AppSpacing.sm),
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: AppColors.successBackground,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: AppColors.success.withValues(alpha: 0.3)),
                        ),
                        child: Text(
                          'Placed',
                          style: TextStyle(color: AppColors.success, fontSize: 12, fontWeight: FontWeight.bold),
                        ),
                      ),
                  ],
                ),
              ),
            ],
          ),
        ),
        ElevatedButton.icon(
          icon: const Icon(LucideIcons.edit3, size: 18),
          label: isMobile ? const SizedBox.shrink() : const Text('Edit Profile'),
          style: ElevatedButton.styleFrom(
            backgroundColor: AppColors.surfaceElevated,
            foregroundColor: AppColors.textPrimary,
            padding: EdgeInsets.symmetric(
              horizontal: isMobile ? AppSpacing.md : AppSpacing.lg,
              vertical: AppSpacing.md,
            ),
          ),
          onPressed: () => context.go('/profile/edit'),
        )
      ],
    );
  }

  Widget _buildCompletionCard(BuildContext context, StudentProfileModel profile) {
    final completion = profile.completionPercentage;
    final isComplete = completion == 100;

    return Container(
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
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Profile Completion',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w600,
                  color: AppColors.textPrimary,
                ),
              ),
              Text(
                '$completion%',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: isComplete ? AppColors.success : AppColors.primary,
                ),
              ),
            ],
          ),
          const SizedBox(height: AppSpacing.md),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: completion / 100,
              minHeight: 8,
              backgroundColor: AppColors.surfaceElevated,
              valueColor: AlwaysStoppedAnimation<Color>(
                isComplete ? AppColors.success : AppColors.primary,
              ),
            ),
          ),
          if (!isComplete) ...[
            const SizedBox(height: AppSpacing.md),
            Text(
              'Complete your profile to increase your chances of being shortlisted by recruiters.',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(color: AppColors.textSecondary),
            ),
          ]
        ],
      ),
    );
  }

  Widget _buildAcademicCard(BuildContext context, StudentProfileModel profile) {
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
              const Icon(LucideIcons.graduationCap, color: AppColors.primary),
              const SizedBox(width: AppSpacing.sm),
              Text(
                'Academic Information',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: AppColors.textPrimary,
                ),
              ),
            ],
          ),
          const SizedBox(height: AppSpacing.lg),
          Wrap(
            spacing: AppSpacing.xxl,
            runSpacing: AppSpacing.lg,
            children: [
              _buildInfoItem(context, 'Enrollment Number', profile.enrollmentNumber),
              _buildInfoItem(context, 'Branch', profile.branch),
              _buildInfoItem(context, 'Year', '${profile.year}'),
              _buildInfoItem(context, 'Semester', '${profile.semester}'),
              _buildInfoItem(context, 'CGPA', profile.cgpa.toStringAsFixed(2)),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildContactCard(BuildContext context, StudentProfileModel profile) {
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
              const Icon(LucideIcons.contact, color: AppColors.primary),
              const SizedBox(width: AppSpacing.sm),
              Text(
                'Contact & Social Links',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: AppColors.textPrimary,
                ),
              ),
            ],
          ),
          const SizedBox(height: AppSpacing.lg),
          Wrap(
            spacing: AppSpacing.xxl,
            runSpacing: AppSpacing.lg,
            children: [
              _buildInfoItem(context, 'Phone Number', profile.phoneNumber),
              _buildInfoItem(context, 'Gender', profile.gender),
              _buildInfoItem(context, 'Date of Birth', profile.dateOfBirth ?? 'Not provided'),
            ],
          ),
          const SizedBox(height: AppSpacing.lg),
          const Divider(color: AppColors.border),
          const SizedBox(height: AppSpacing.lg),
          _buildLinkItem(context, 'GitHub', profile.githubUrl, LucideIcons.code2),
          const SizedBox(height: AppSpacing.sm),
          _buildLinkItem(context, 'LinkedIn', profile.linkedinUrl, LucideIcons.briefcase),
          const SizedBox(height: AppSpacing.sm),
          _buildLinkItem(context, 'Portfolio', profile.portfolioUrl, LucideIcons.globe),
        ],
      ),
    );
  }

  Widget _buildSkillsCard(BuildContext context, StudentProfileModel profile) {
    final skills = profile.skills.split(',').map((s) => s.trim()).where((s) => s.isNotEmpty).toList();

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
              const Icon(LucideIcons.code, color: AppColors.primary),
              const SizedBox(width: AppSpacing.sm),
              Text(
                'Skills',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: AppColors.textPrimary,
                ),
              ),
            ],
          ),
          const SizedBox(height: AppSpacing.md),
          if (skills.isEmpty)
            Text(
              'No skills added yet.',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: AppColors.textSecondary),
            )
          else
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: skills.map((skill) => Chip(
                label: Text(skill),
                backgroundColor: AppColors.surfaceElevated,
                labelStyle: const TextStyle(color: AppColors.textPrimary, fontSize: 12),
                side: const BorderSide(color: AppColors.border),
                padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 0),
              )).toList(),
            ),
        ],
      ),
    );
  }

  Widget _buildResumeCard(BuildContext context, StudentProfileModel profile) {
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
              const Icon(LucideIcons.fileText, color: AppColors.primary),
              const SizedBox(width: AppSpacing.sm),
              Text(
                'Resume',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: AppColors.textPrimary,
                ),
              ),
            ],
          ),
          const SizedBox(height: AppSpacing.md),
          if (profile.resume != null && profile.resume!.isNotEmpty)
            Container(
              padding: const EdgeInsets.all(AppSpacing.md),
              decoration: BoxDecoration(
                color: AppColors.surfaceElevated,
                borderRadius: BorderRadius.circular(AppSpacing.borderRadius),
              ),
              child: Row(
                children: [
                  const Icon(LucideIcons.fileText, color: AppColors.textPrimary, size: 32),
                  const SizedBox(width: AppSpacing.md),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Resume Uploaded',
                          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                            color: AppColors.textPrimary,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        Text(
                          'View or update in Resume section',
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(color: AppColors.textSecondary),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            )
          else
            Text(
              'No resume uploaded.',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: AppColors.textSecondary),
            ),
          const SizedBox(height: AppSpacing.md),
          SizedBox(
            width: double.infinity,
            child: OutlinedButton(
              onPressed: () {
                // Navigate to resume management
                // Assuming it's implemented or will be at /resume
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Navigate to Resume Management')),
                );
              },
              child: const Text('Manage Resumes'),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInfoItem(BuildContext context, String label, String value) {
    return SizedBox(
      width: 150,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: AppColors.textSecondary,
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            value.isEmpty ? '-' : value,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: AppColors.textPrimary,
              fontWeight: FontWeight.w600,
            ),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }

  Widget _buildLinkItem(BuildContext context, String label, String url, IconData icon) {
    if (url.isEmpty) return const SizedBox.shrink();
    
    return Row(
      children: [
        Icon(icon, size: 16, color: AppColors.textSecondary),
        const SizedBox(width: AppSpacing.sm),
        Text(
          label,
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: AppColors.textSecondary),
        ),
        const SizedBox(width: AppSpacing.sm),
        Expanded(
          child: Text(
            url,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: AppColors.primary,
              decoration: TextDecoration.underline,
            ),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ),
      ],
    );
  }
}

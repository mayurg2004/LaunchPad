import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:file_picker/file_picker.dart';
import 'package:go_router/go_router.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';
import 'package:timeago/timeago.dart' as timeago;

import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_spacing.dart';
import '../providers/resume_provider.dart';
import '../data/models/resume_model.dart';

class ResumeCenterScreen extends ConsumerStatefulWidget {
  const ResumeCenterScreen({super.key});

  @override
  ConsumerState<ResumeCenterScreen> createState() => _ResumeCenterScreenState();
}

class _ResumeCenterScreenState extends ConsumerState<ResumeCenterScreen> {
  bool _isUploading = false;

  Future<void> _uploadResume() async {
    try {
      // ignore: undefined_getter, argument_type_not_assignable
      final result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['pdf'],
        withData: true,
      );

      if (result != null && result.files.isNotEmpty) {
        final file = result.files.first;
        if (file.bytes == null) {
          _showError('Could not read file data. Please try again.');
          return;
        }

        if (file.size > 5 * 1024 * 1024) {
          _showError('File is too large. Maximum size is 5MB.');
          return;
        }

        setState(() => _isUploading = true);

        // Upload resume
        final success = await ref.read(resumeActionsProvider).uploadResume(
          file.name,
          file.bytes!,
          file.name,
          true, // Set active by default
        );

        if (success) {
          _showSuccess('Resume uploaded successfully!');
        } else {
          _showError('Failed to upload resume. Please try again.');
        }
      }
    } catch (e) {
      _showError('An error occurred while uploading.');
    } finally {
      if (mounted) {
        setState(() => _isUploading = false);
      }
    }
  }

  void _showError(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message), backgroundColor: AppColors.error));
  }

  void _showSuccess(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message), backgroundColor: AppColors.success));
  }

  @override
  Widget build(BuildContext context) {
    final activeResumeAsync = ref.watch(activeResumeProvider);
    final versionsAsync = ref.watch(resumeVersionsProvider);

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Resume Center'),
        backgroundColor: AppColors.surface,
        elevation: 0,
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(activeResumeProvider);
          ref.invalidate(resumeVersionsProvider);
        },
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(AppSpacing.screenPadding),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildHeader(),
              const SizedBox(height: AppSpacing.xl),
              activeResumeAsync.when(
                data: (resume) {
                  if (resume == null) {
                    return _buildEmptyState();
                  }
                  return _buildActiveResumeCard(resume);
                },
                loading: () => const Center(child: CircularProgressIndicator(color: AppColors.primary)),
                error: (error, _) => Text('Error loading active resume: $error', style: const TextStyle(color: AppColors.error)),
              ),
              const SizedBox(height: AppSpacing.xxl),
              Text(
                'Version History',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: AppColors.textPrimary,
                ),
              ),
              const SizedBox(height: AppSpacing.md),
              versionsAsync.when(
                data: (versions) {
                  if (versions.isEmpty) {
                    return const Text('No resume versions found.', style: TextStyle(color: AppColors.textSecondary));
                  }
                  return _buildVersionList(versions);
                },
                loading: () => const CircularProgressIndicator(color: AppColors.primary),
                error: (error, _) => Text('Error loading versions: $error', style: const TextStyle(color: AppColors.error)),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Manage Resumes',
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                fontWeight: FontWeight.bold,
                color: AppColors.textPrimary,
              ),
            ),
            const SizedBox(height: AppSpacing.xs),
            Text(
              'Upload, analyze, and track your resumes.',
              style: Theme.of(context).textTheme.bodyLarge?.copyWith(color: AppColors.textSecondary),
            ),
          ],
        ),
        ElevatedButton.icon(
          onPressed: _isUploading ? null : _uploadResume,
          icon: _isUploading
              ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
              : const Icon(LucideIcons.uploadCloud),
          label: Text(_isUploading ? 'Uploading...' : 'Upload PDF'),
          style: ElevatedButton.styleFrom(
            backgroundColor: AppColors.primary,
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(horizontal: AppSpacing.lg, vertical: AppSpacing.md),
          ),
        ),
      ],
    );
  }

  Widget _buildEmptyState() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(AppSpacing.xxl),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(AppSpacing.borderRadius),
        border: Border.all(color: AppColors.border, style: BorderStyle.solid),
      ),
      child: Column(
        children: [
          const Icon(LucideIcons.fileQuestion, size: 64, color: AppColors.textSecondary),
          const SizedBox(height: AppSpacing.lg),
          Text(
            'No Active Resume',
            style: Theme.of(context).textTheme.titleLarge?.copyWith(color: AppColors.textPrimary),
          ),
          const SizedBox(height: AppSpacing.sm),
          Text(
            'Upload a PDF resume to get started with AI analysis.',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: AppColors.textSecondary),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildActiveResumeCard(ResumeModel resume) {
    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            AppColors.surfaceElevated,
            AppColors.surface,
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(AppSpacing.borderRadius),
        border: Border.all(color: AppColors.primary.withValues(alpha: 0.5), width: 2),
      ),
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.cardPadding),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(AppSpacing.sm),
                  decoration: BoxDecoration(
                    color: AppColors.primary.withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Icon(LucideIcons.fileText, color: AppColors.primary, size: 28),
                ),
                const SizedBox(width: AppSpacing.md),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Expanded(
                            child: Text(
                              resume.title,
                              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                                fontWeight: FontWeight.bold,
                                color: AppColors.textPrimary,
                              ),
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                            decoration: BoxDecoration(
                              color: AppColors.successBackground,
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: const Text('Active', style: TextStyle(color: AppColors.success, fontSize: 12, fontWeight: FontWeight.bold)),
                          ),
                        ],
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Version ${resume.versionNumber} • Uploaded ${timeago.format(DateTime.parse(resume.uploadedAt))}',
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: AppColors.textSecondary),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: AppSpacing.xl),
            const Divider(color: AppColors.border),
            const SizedBox(height: AppSpacing.md),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () {
                      context.push('/resumes/${resume.id}/analysis');
                    },
                    icon: const Icon(LucideIcons.barChart2),
                    label: const Text('View Analysis'),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: AppColors.primary,
                      side: const BorderSide(color: AppColors.primary),
                      padding: const EdgeInsets.symmetric(vertical: AppSpacing.md),
                    ),
                  ),
                ),
                const SizedBox(width: AppSpacing.md),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () {
                      context.push('/resumes/${resume.id}/skill-gap');
                    },
                    icon: const Icon(LucideIcons.target),
                    label: const Text('Skill Gap Analysis'),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: AppColors.textPrimary,
                      side: const BorderSide(color: AppColors.border),
                      padding: const EdgeInsets.symmetric(vertical: AppSpacing.md),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildVersionList(List<ResumeVersionModel> versions) {
    return ListView.separated(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: versions.length,
      separatorBuilder: (context, index) => const SizedBox(height: AppSpacing.sm),
      itemBuilder: (context, index) {
        final version = versions[index];
        return Card(
          color: AppColors.surface,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppSpacing.borderRadius),
            side: BorderSide(color: version.isActive ? AppColors.primary : AppColors.border),
          ),
          child: ListTile(
            contentPadding: const EdgeInsets.all(AppSpacing.md),
            leading: CircleAvatar(
              backgroundColor: AppColors.surfaceElevated,
              child: Text(
                'v${version.versionNumber}',
                style: const TextStyle(color: AppColors.primary, fontWeight: FontWeight.bold),
              ),
            ),
            title: Text(
              version.title,
              style: TextStyle(
                color: AppColors.textPrimary,
                fontWeight: version.isActive ? FontWeight.bold : FontWeight.normal,
              ),
            ),
            subtitle: Text(
              'Uploaded ${timeago.format(DateTime.parse(version.uploadedAt))}',
              style: const TextStyle(color: AppColors.textSecondary),
            ),
            trailing: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                if (!version.isActive)
                  TextButton(
                    onPressed: () async {
                      final success = await ref.read(resumeActionsProvider).setActiveResume(version.id);
                      if (success) {
                        _showSuccess('Version ${version.versionNumber} set as active.');
                      } else {
                        _showError('Failed to set active resume.');
                      }
                    },
                    child: const Text('Set Active'),
                  ),
                IconButton(
                  icon: const Icon(LucideIcons.trash2, color: AppColors.error),
                  onPressed: () async {
                    final confirm = await showDialog<bool>(
                      context: context,
                      builder: (context) => AlertDialog(
                        backgroundColor: AppColors.surfaceElevated,
                        title: const Text('Delete Resume?', style: TextStyle(color: AppColors.textPrimary)),
                        content: const Text('This action cannot be undone.', style: TextStyle(color: AppColors.textSecondary)),
                        actions: [
                          TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancel')),
                          TextButton(
                            onPressed: () => Navigator.pop(context, true),
                            child: const Text('Delete', style: TextStyle(color: AppColors.error)),
                          ),
                        ],
                      ),
                    );

                    if (confirm == true) {
                      final success = await ref.read(resumeActionsProvider).deleteResume(version.id);
                      if (success) {
                        _showSuccess('Resume deleted.');
                      } else {
                        _showError('Failed to delete resume.');
                      }
                    }
                  },
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}

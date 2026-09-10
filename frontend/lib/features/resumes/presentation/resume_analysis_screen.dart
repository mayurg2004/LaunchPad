import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';
import 'package:timeago/timeago.dart' as timeago;

import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_spacing.dart';
import '../providers/resume_provider.dart';
import '../data/models/resume_analysis_model.dart';

class ResumeAnalysisScreen extends ConsumerStatefulWidget {
  final int resumeId;

  const ResumeAnalysisScreen({super.key, required this.resumeId});

  @override
  ConsumerState<ResumeAnalysisScreen> createState() => _ResumeAnalysisScreenState();
}

class _ResumeAnalysisScreenState extends ConsumerState<ResumeAnalysisScreen> {
  bool _isAnalyzing = false;
  bool _isAiAnalyzing = false;

  Future<void> _triggerAnalysis({required bool useAi}) async {
    setState(() {
      if (useAi) {
        _isAiAnalyzing = true;
      } else {
        _isAnalyzing = true;
      }
    });

    try {
      await ref.read(resumeActionsProvider).analyzeResume(widget.resumeId, useAi: useAi);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Analysis complete!'), backgroundColor: AppColors.success),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Analysis failed: $e'), backgroundColor: AppColors.error),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isAiAnalyzing = false;
          _isAnalyzing = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final analysisAsync = ref.watch(resumeAnalysisProvider(widget.resumeId));

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Resume Analysis'),
        backgroundColor: AppColors.surface,
        leading: IconButton(
          icon: const Icon(LucideIcons.arrowLeft),
          onPressed: () => context.pop(),
        ),
      ),
      body: analysisAsync.when(
        data: (analysis) {
          if (analysis == null) {
            return _buildEmptyState();
          }
          return _buildAnalysisContent(analysis);
        },
        loading: () => const Center(child: CircularProgressIndicator(color: AppColors.primary)),
        error: (error, _) => Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(LucideIcons.alertCircle, color: AppColors.error, size: 48),
              const SizedBox(height: AppSpacing.md),
              Text('Error loading analysis', style: Theme.of(context).textTheme.titleLarge?.copyWith(color: AppColors.textPrimary)),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.xxl),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(LucideIcons.barChart, size: 64, color: AppColors.textSecondary),
            const SizedBox(height: AppSpacing.lg),
            Text(
              'No Analysis Found',
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(color: AppColors.textPrimary),
            ),
            const SizedBox(height: AppSpacing.md),
            Text(
              'Analyze your resume to get a score, detect skills, and receive improvement suggestions.',
              style: Theme.of(context).textTheme.bodyLarge?.copyWith(color: AppColors.textSecondary),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: AppSpacing.xl),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                ElevatedButton.icon(
                  onPressed: _isAnalyzing || _isAiAnalyzing ? null : () => _triggerAnalysis(useAi: false),
                  icon: _isAnalyzing
                      ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                      : const Icon(LucideIcons.checkSquare),
                  label: const Text('Standard Analysis'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.surfaceElevated,
                    foregroundColor: AppColors.textPrimary,
                  ),
                ),
                const SizedBox(width: AppSpacing.md),
                ElevatedButton.icon(
                  onPressed: _isAnalyzing || _isAiAnalyzing ? null : () => _triggerAnalysis(useAi: true),
                  icon: _isAiAnalyzing
                      ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                      : const Icon(LucideIcons.sparkles),
                  label: const Text('AI Analysis'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.primary,
                    foregroundColor: Colors.white,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAnalysisContent(ResumeAnalysisModel analysis) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppSpacing.screenPadding),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Analysis Results',
                style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: AppColors.textPrimary,
                ),
              ),
              Row(
                children: [
                  OutlinedButton.icon(
                    onPressed: _isAnalyzing || _isAiAnalyzing ? null : () => _triggerAnalysis(useAi: false),
                    icon: _isAnalyzing
                      ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(color: AppColors.primary, strokeWidth: 2))
                      : const Icon(LucideIcons.refreshCw, size: 16),
                    label: const Text('Re-Analyze'),
                    style: OutlinedButton.styleFrom(foregroundColor: AppColors.primary),
                  ),
                  const SizedBox(width: AppSpacing.sm),
                  ElevatedButton.icon(
                    onPressed: _isAnalyzing || _isAiAnalyzing ? null : () => _triggerAnalysis(useAi: true),
                    icon: _isAiAnalyzing
                      ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                      : const Icon(LucideIcons.sparkles, size: 16),
                    label: const Text('AI Analyze'),
                    style: ElevatedButton.styleFrom(backgroundColor: AppColors.primary, foregroundColor: Colors.white),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: AppSpacing.xs),
          Text(
            'Analyzed ${timeago.format(DateTime.parse(analysis.analyzedAt))}',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: AppColors.textSecondary),
          ),
          const SizedBox(height: AppSpacing.xl),
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                flex: 1,
                child: _buildScoreCard(analysis.score),
              ),
              const SizedBox(width: AppSpacing.lg),
              Expanded(
                flex: 2,
                child: _buildSkillsCard(analysis.skillsFound),
              ),
            ],
          ),
          const SizedBox(height: AppSpacing.lg),
          _buildFeedbackCard('Strengths', analysis.strengths, LucideIcons.trendingUp, AppColors.success),
          const SizedBox(height: AppSpacing.lg),
          _buildFeedbackCard('Areas for Improvement', analysis.weaknesses.isEmpty ? analysis.suggestions : analysis.weaknesses, LucideIcons.trendingDown, AppColors.warning),
          if (analysis.suggestions.isNotEmpty && analysis.weaknesses.isNotEmpty) ...[
            const SizedBox(height: AppSpacing.lg),
            _buildFeedbackCard('Suggestions', analysis.suggestions, LucideIcons.lightbulb, AppColors.info),
          ]
        ],
      ),
    );
  }

  Widget _buildScoreCard(double score) {
    Color scoreColor;
    if (score >= 80) {
      scoreColor = AppColors.success;
    } else if (score >= 50) {
      scoreColor = AppColors.warning;
    } else {
      scoreColor = AppColors.error;
    }

    return Container(
      padding: const EdgeInsets.all(AppSpacing.xl),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(AppSpacing.borderRadius),
        border: Border.all(color: AppColors.border),
      ),
      child: Column(
        children: [
          const Text(
            'Overall Score',
            style: TextStyle(color: AppColors.textSecondary, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: AppSpacing.lg),
          Stack(
            alignment: Alignment.center,
            children: [
              SizedBox(
                width: 120,
                height: 120,
                child: CircularProgressIndicator(
                  value: score / 100,
                  strokeWidth: 12,
                  backgroundColor: AppColors.surfaceElevated,
                  color: scoreColor,
                ),
              ),
              Text(
                '${score.round()}',
                style: Theme.of(context).textTheme.headlineLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: scoreColor,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSkillsCard(List<String> skills) {
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
            children: [
              const Icon(LucideIcons.code2, color: AppColors.primary),
              const SizedBox(width: AppSpacing.sm),
              Text(
                'Detected Skills',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: AppColors.textPrimary,
                ),
              ),
            ],
          ),
          const SizedBox(height: AppSpacing.md),
          if (skills.isEmpty)
            const Text('No skills detected.', style: TextStyle(color: AppColors.textSecondary))
          else
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: skills.map((skill) => Chip(
                label: Text(skill),
                backgroundColor: AppColors.surfaceElevated,
                labelStyle: const TextStyle(color: AppColors.textPrimary, fontSize: 13),
                side: const BorderSide(color: AppColors.border),
              )).toList(),
            ),
        ],
      ),
    );
  }

  Widget _buildFeedbackCard(String title, List<String> items, IconData icon, Color color) {
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
            ],
          ),
          const SizedBox(height: AppSpacing.md),
          if (items.isEmpty)
            const Text('No data available.', style: TextStyle(color: AppColors.textSecondary))
          else
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: items.map((item) => Padding(
                padding: const EdgeInsets.only(bottom: AppSpacing.sm),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      margin: const EdgeInsets.only(top: 6, right: 12),
                      width: 6,
                      height: 6,
                      decoration: BoxDecoration(color: color, shape: BoxShape.circle),
                    ),
                    Expanded(
                      child: Text(
                        item,
                        style: const TextStyle(color: AppColors.textPrimary, height: 1.5),
                      ),
                    ),
                  ],
                ),
              )).toList(),
            ),
        ],
      ),
    );
  }
}

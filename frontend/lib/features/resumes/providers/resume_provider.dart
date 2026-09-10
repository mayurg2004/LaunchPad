import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/api/api_client.dart';
import '../../../core/api/endpoints.dart';
import '../data/models/resume_model.dart';
import '../data/models/resume_analysis_model.dart';
import '../data/models/skill_gap_model.dart';

final resumeVersionsProvider = FutureProvider.autoDispose<List<ResumeVersionModel>>((ref) async {
  final response = await ApiClient.get(Endpoints.resumeVersions);
  if (response.statusCode == 200) {
    final List<dynamic> data = jsonDecode(response.body);
    return data.map((e) => ResumeVersionModel.fromJson(e)).toList();
  }
  throw Exception('Failed to load resume versions');
});

final activeResumeProvider = FutureProvider.autoDispose<ResumeModel?>((ref) async {
  final response = await ApiClient.get(Endpoints.resumeActive);
  if (response.statusCode == 200) {
    return ResumeModel.fromJson(jsonDecode(response.body));
  } else if (response.statusCode == 404) {
    return null;
  }
  throw Exception('Failed to load active resume');
});

final resumeAnalysisProvider = FutureProvider.family.autoDispose<ResumeAnalysisModel?, int>((ref, resumeId) async {
  final response = await ApiClient.get('${Endpoints.resumes}$resumeId/analysis/');
  if (response.statusCode == 200) {
    return ResumeAnalysisModel.fromJson(jsonDecode(response.body));
  } else if (response.statusCode == 404) {
    return null;
  }
  throw Exception('Failed to load resume analysis');
});

final skillGapProvider = FutureProvider.family.autoDispose<SkillGapModel, Map<String, int>>((ref, params) async {
  final resumeId = params['resumeId']!;
  final driveId = params['driveId']!;
  final response = await ApiClient.get('${Endpoints.resumes}$resumeId/skill-gap/$driveId/');
  if (response.statusCode == 200) {
    return SkillGapModel.fromJson(jsonDecode(response.body));
  }
  throw Exception(jsonDecode(response.body)['detail'] ?? 'Failed to calculate skill gap');
});

final resumeActionsProvider = Provider((ref) => ResumeActions(ref));

class ResumeActions {
  final Ref ref;
  ResumeActions(this.ref);

  Future<bool> uploadResume(String title, List<int> fileBytes, String filename, bool isActive) async {
    final response = await ApiClient.multipartPost(
      Endpoints.resumes,
      fileField: 'file',
      fileBytes: fileBytes,
      filename: filename,
      fields: {
        'title': title,
        'is_active': isActive.toString(),
      },
    );
    if (response.statusCode == 201) {
      ref.invalidate(resumeVersionsProvider);
      if (isActive) ref.invalidate(activeResumeProvider);
      return true;
    }
    return false;
  }

  Future<bool> setActiveResume(int resumeId) async {
    final response = await ApiClient.patch(
      '${Endpoints.resumes}$resumeId/',
      body: {'is_active': true},
    );
    if (response.statusCode == 200) {
      ref.invalidate(resumeVersionsProvider);
      ref.invalidate(activeResumeProvider);
      return true;
    }
    return false;
  }

  Future<bool> deleteResume(int resumeId) async {
    final response = await ApiClient.delete('${Endpoints.resumes}$resumeId/');
    if (response.statusCode == 204) {
      ref.invalidate(resumeVersionsProvider);
      ref.invalidate(activeResumeProvider);
      return true;
    }
    return false;
  }

  Future<ResumeAnalysisModel?> analyzeResume(int resumeId, {bool useAi = false}) async {
    final endpoint = useAi ? '${Endpoints.resumes}$resumeId/ai-analyze/' : '${Endpoints.resumes}$resumeId/analyze/';
    final response = await ApiClient.post(endpoint);
    
    if (response.statusCode == 200) {
      ref.invalidate(resumeAnalysisProvider(resumeId));
      return ResumeAnalysisModel.fromJson(jsonDecode(response.body));
    }
    throw Exception(jsonDecode(response.body)['detail'] ?? 'Failed to analyze resume');
  }
}

class ResumeAnalysisModel {
  final int resumeId;
  final double score;
  final List<String> skillsFound;
  final List<String> strengths;
  final List<String> weaknesses;
  final List<String> suggestions;
  final String analyzedAt;

  ResumeAnalysisModel({
    required this.resumeId,
    required this.score,
    required this.skillsFound,
    required this.strengths,
    required this.weaknesses,
    required this.suggestions,
    required this.analyzedAt,
  });

  factory ResumeAnalysisModel.fromJson(Map<String, dynamic> json) {
    return ResumeAnalysisModel(
      resumeId: json['resume_id'] ?? json['resume'] ?? 0,
      score: double.tryParse(json['score']?.toString() ?? '0') ?? 0.0,
      skillsFound: List<String>.from(json['skills_found'] ?? []),
      strengths: List<String>.from(json['strengths'] ?? []),
      weaknesses: List<String>.from(json['weaknesses'] ?? []),
      suggestions: List<String>.from(json['suggestions'] ?? []),
      analyzedAt: json['analyzed_at'] ?? '',
    );
  }
}

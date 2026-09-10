class SkillGapModel {
  final int resumeId;
  final int placementDriveId;
  final List<String> requiredSkills;
  final List<String> matchedSkills;
  final List<String> missingSkills;
  final double matchPercentage;

  SkillGapModel({
    required this.resumeId,
    required this.placementDriveId,
    required this.requiredSkills,
    required this.matchedSkills,
    required this.missingSkills,
    required this.matchPercentage,
  });

  factory SkillGapModel.fromJson(Map<String, dynamic> json) {
    return SkillGapModel(
      resumeId: json['resume_id'] ?? 0,
      placementDriveId: json['placement_drive_id'] ?? 0,
      requiredSkills: List<String>.from(json['required_skills'] ?? []),
      matchedSkills: List<String>.from(json['matched_skills'] ?? []),
      missingSkills: List<String>.from(json['missing_skills'] ?? []),
      matchPercentage: double.tryParse(json['match_percentage']?.toString() ?? '0') ?? 0.0,
    );
  }
}

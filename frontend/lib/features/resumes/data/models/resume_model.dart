class ResumeModel {
  final int id;
  final String title;
  final String fileUrl;
  final bool isActive;
  final int versionNumber;
  final String uploadedAt;
  final String updatedAt;

  ResumeModel({
    required this.id,
    required this.title,
    required this.fileUrl,
    required this.isActive,
    required this.versionNumber,
    required this.uploadedAt,
    required this.updatedAt,
  });

  factory ResumeModel.fromJson(Map<String, dynamic> json) {
    return ResumeModel(
      id: json['id'],
      title: json['title'] ?? '',
      fileUrl: json['file'] ?? '',
      isActive: json['is_active'] ?? false,
      versionNumber: json['version_number'] ?? 1,
      uploadedAt: json['uploaded_at'] ?? '',
      updatedAt: json['updated_at'] ?? '',
    );
  }
}

class ResumeVersionModel {
  final int id;
  final String title;
  final int versionNumber;
  final bool isActive;
  final String uploadedAt;

  ResumeVersionModel({
    required this.id,
    required this.title,
    required this.versionNumber,
    required this.isActive,
    required this.uploadedAt,
  });

  factory ResumeVersionModel.fromJson(Map<String, dynamic> json) {
    return ResumeVersionModel(
      id: json['id'],
      title: json['title'] ?? '',
      versionNumber: json['version_number'] ?? 1,
      isActive: json['is_active'] ?? false,
      uploadedAt: json['uploaded_at'] ?? '',
    );
  }
}

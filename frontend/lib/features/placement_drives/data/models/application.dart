class Application {
  final int id;
  final int studentId;
  final int placementDriveId;
  final String status;
  final DateTime appliedAt;
  final DateTime updatedAt;
  final String? studentName;
  final String? studentEnrollmentNumber;
  final String? companyName;
  final String? placementDriveTitle;
  final String? jobRole;
  final double? package;

  Application({
    required this.id,
    required this.studentId,
    required this.placementDriveId,
    required this.status,
    required this.appliedAt,
    required this.updatedAt,
    this.studentName,
    this.studentEnrollmentNumber,
    this.companyName,
    this.placementDriveTitle,
    this.jobRole,
    this.package,
  });

  factory Application.fromJson(Map<String, dynamic> json) {
    return Application(
      id: json['id'] as int,
      studentId: json['student'] as int,
      placementDriveId: json['placement_drive'] as int,
      status: json['status'] as String? ?? 'APPLIED',
      appliedAt: DateTime.parse(json['applied_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
      studentName: json['student_name'] as String?,
      studentEnrollmentNumber: json['student_enrollment_number'] as String?,
      companyName: json['company_name'] as String?,
      placementDriveTitle: json['placement_drive_title'] as String?,
      jobRole: json['job_role'] as String?,
      package: json['package'] != null
          ? double.tryParse(json['package'].toString())
          : null,
    );
  }
}

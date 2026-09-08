class Interview {
  final int id;
  final int application;
  final String roundName;
  final String roundType;
  final DateTime scheduledAt;
  final int durationMinutes;
  final String? location;
  final String? meetingLink;
  final String? interviewerName;
  final String? interviewerEmail;
  final String status;
  final String? feedback;
  final String result;
  final DateTime createdAt;
  final DateTime updatedAt;

  // Derived fields from serializer
  final String? companyName;
  final String? jobRole;
  final String? placementDriveTitle;
  final String? studentName;
  final String? studentEnrollmentNumber;

  Interview({
    required this.id,
    required this.application,
    required this.roundName,
    required this.roundType,
    required this.scheduledAt,
    required this.durationMinutes,
    this.location,
    this.meetingLink,
    this.interviewerName,
    this.interviewerEmail,
    required this.status,
    this.feedback,
    required this.result,
    required this.createdAt,
    required this.updatedAt,
    this.companyName,
    this.jobRole,
    this.placementDriveTitle,
    this.studentName,
    this.studentEnrollmentNumber,
  });

  factory Interview.fromJson(Map<String, dynamic> json) {
    return Interview(
      id: json['id'] as int,
      application: json['application'] as int,
      roundName: json['round_name'] as String,
      roundType: json['round_type'] as String,
      scheduledAt: DateTime.parse(json['scheduled_at'] as String),
      durationMinutes: json['duration_minutes'] as int,
      location: json['location'] as String?,
      meetingLink: json['meeting_link'] as String?,
      interviewerName: json['interviewer_name'] as String?,
      interviewerEmail: json['interviewer_email'] as String?,
      status: json['status'] as String,
      feedback: json['feedback'] as String?,
      result: json['result'] as String,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
      companyName: json['company_name'] as String?,
      jobRole: json['job_role'] as String?,
      placementDriveTitle: json['placement_drive_title'] as String?,
      studentName: json['student_name'] as String?,
      studentEnrollmentNumber: json['student_enrollment_number'] as String?,
    );
  }
}

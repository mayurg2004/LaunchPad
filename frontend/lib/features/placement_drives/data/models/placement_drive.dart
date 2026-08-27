class PlacementDrive {
  final int id;
  final int companyId;
  final String companyName;
  final String title;
  final String jobRole;
  final String jobDescription;
  final double? packageLpa;
  final String location;
  final double? minimumCgpa;
  final String eligibleBranch;
  final DateTime? applicationDeadline;
  final DateTime? driveDate;
  final String status;
  final List<String> requiredSkills;
  final DateTime createdAt;
  final DateTime updatedAt;

  PlacementDrive({
    required this.id,
    required this.companyId,
    required this.companyName,
    required this.title,
    required this.jobRole,
    required this.jobDescription,
    this.packageLpa,
    required this.location,
    this.minimumCgpa,
    required this.eligibleBranch,
    this.applicationDeadline,
    this.driveDate,
    required this.status,
    required this.requiredSkills,
    required this.createdAt,
    required this.updatedAt,
  });

  factory PlacementDrive.fromJson(Map<String, dynamic> json) {
    return PlacementDrive(
      id: json['id'] as int,
      companyId: json['company'] as int,
      companyName: json['company_name'] as String? ?? 'Unknown Company',
      title: json['title'] as String? ?? '',
      jobRole: json['job_role'] as String? ?? '',
      jobDescription: json['job_description'] as String? ?? '',
      packageLpa: json['package_lpa'] != null
          ? double.tryParse(json['package_lpa'].toString())
          : null,
      location: json['location'] as String? ?? '',
      minimumCgpa: json['minimum_cgpa'] != null
          ? double.tryParse(json['minimum_cgpa'].toString())
          : null,
      eligibleBranch: json['eligible_branch'] as String? ?? '',
      applicationDeadline: json['application_deadline'] != null
          ? DateTime.tryParse(json['application_deadline'] as String)
          : null,
      driveDate: json['drive_date'] != null
          ? DateTime.tryParse(json['drive_date'] as String)
          : null,
      status: json['status'] as String? ?? 'DRAFT',
      requiredSkills: (json['required_skills'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
  }
}

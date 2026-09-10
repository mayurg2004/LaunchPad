class StudentProfileModel {
  final int id;
  final String email;
  final String firstName;
  final String lastName;
  final String enrollmentNumber;
  final String branch;
  final int year;
  final int semester;
  final double cgpa;
  final String phoneNumber;
  final String gender;
  final String? dateOfBirth;
  final String skills;
  final String githubUrl;
  final String linkedinUrl;
  final String portfolioUrl;
  final String? resume;
  final String? profilePhoto;
  final bool isPlaced;

  StudentProfileModel({
    required this.id,
    required this.email,
    required this.firstName,
    required this.lastName,
    required this.enrollmentNumber,
    required this.branch,
    required this.year,
    required this.semester,
    required this.cgpa,
    required this.phoneNumber,
    required this.gender,
    this.dateOfBirth,
    required this.skills,
    required this.githubUrl,
    required this.linkedinUrl,
    required this.portfolioUrl,
    this.resume,
    this.profilePhoto,
    required this.isPlaced,
  });

  factory StudentProfileModel.fromJson(Map<String, dynamic> json) {
    return StudentProfileModel(
      id: json['id'],
      email: json['email'] ?? '',
      firstName: json['first_name'] ?? '',
      lastName: json['last_name'] ?? '',
      enrollmentNumber: json['enrollment_number'] ?? '',
      branch: json['branch'] ?? '',
      year: json['year'] ?? 1,
      semester: json['semester'] ?? 1,
      cgpa: double.tryParse(json['cgpa']?.toString() ?? '0') ?? 0.0,
      phoneNumber: json['phone_number'] ?? '',
      gender: json['gender'] ?? '',
      dateOfBirth: json['date_of_birth'],
      skills: json['skills'] ?? '',
      githubUrl: json['github_url'] ?? '',
      linkedinUrl: json['linkedin_url'] ?? '',
      portfolioUrl: json['portfolio_url'] ?? '',
      resume: json['resume'],
      profilePhoto: json['profile_photo'],
      isPlaced: json['is_placed'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'enrollment_number': enrollmentNumber,
      'branch': branch,
      'year': year,
      'semester': semester,
      'cgpa': cgpa,
      'phone_number': phoneNumber,
      'gender': gender,
      'date_of_birth': dateOfBirth,
      'skills': skills,
      'github_url': githubUrl,
      'linkedin_url': linkedinUrl,
      'portfolio_url': portfolioUrl,
    };
  }

  int get completionPercentage {
    int totalFields = 12; // Including major fields
    int filledFields = 0;

    if (firstName.isNotEmpty || lastName.isNotEmpty) filledFields++;
    if (enrollmentNumber.isNotEmpty) filledFields++;
    if (branch.isNotEmpty) filledFields++;
    if (year > 0) filledFields++;
    if (semester > 0) filledFields++;
    if (cgpa > 0) filledFields++;
    if (phoneNumber.isNotEmpty) filledFields++;
    if (gender.isNotEmpty) filledFields++;
    if (skills.isNotEmpty) filledFields++;
    if (githubUrl.isNotEmpty || linkedinUrl.isNotEmpty || portfolioUrl.isNotEmpty) filledFields++;
    if (resume != null) filledFields++;
    if (profilePhoto != null) filledFields++;

    return ((filledFields / totalFields) * 100).round();
  }
}

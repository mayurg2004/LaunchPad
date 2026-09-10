import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_spacing.dart';
import '../providers/profile_provider.dart';
import '../data/models/student_profile_model.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';

class EditProfileScreen extends ConsumerStatefulWidget {
  const EditProfileScreen({super.key});

  @override
  ConsumerState<EditProfileScreen> createState() => _EditProfileScreenState();
}

class _EditProfileScreenState extends ConsumerState<EditProfileScreen> {
  final _formKey = GlobalKey<FormState>();
  
  late TextEditingController _enrollmentController;
  late TextEditingController _branchController;
  late TextEditingController _yearController;
  late TextEditingController _semesterController;
  late TextEditingController _cgpaController;
  late TextEditingController _phoneController;
  late TextEditingController _githubController;
  late TextEditingController _linkedinController;
  late TextEditingController _portfolioController;
  late TextEditingController _skillsController;
  
  String _gender = 'M';
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    final profile = ref.read(profileProvider).value;
    
    _enrollmentController = TextEditingController(text: profile?.enrollmentNumber ?? '');
    _branchController = TextEditingController(text: profile?.branch ?? '');
    _yearController = TextEditingController(text: profile?.year.toString() ?? '');
    _semesterController = TextEditingController(text: profile?.semester.toString() ?? '');
    _cgpaController = TextEditingController(text: profile?.cgpa.toString() ?? '');
    _phoneController = TextEditingController(text: profile?.phoneNumber ?? '');
    _githubController = TextEditingController(text: profile?.githubUrl ?? '');
    _linkedinController = TextEditingController(text: profile?.linkedinUrl ?? '');
    _portfolioController = TextEditingController(text: profile?.portfolioUrl ?? '');
    _skillsController = TextEditingController(text: profile?.skills ?? '');
    
    if (profile?.gender != null && profile!.gender.isNotEmpty) {
      _gender = profile.gender;
    }
  }

  @override
  void dispose() {
    _enrollmentController.dispose();
    _branchController.dispose();
    _yearController.dispose();
    _semesterController.dispose();
    _cgpaController.dispose();
    _phoneController.dispose();
    _githubController.dispose();
    _linkedinController.dispose();
    _portfolioController.dispose();
    _skillsController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    
    setState(() => _isLoading = true);
    
    final currentProfile = ref.read(profileProvider).value;

    final updatedProfile = StudentProfileModel(
      id: currentProfile?.id ?? 0,
      email: currentProfile?.email ?? '',
      firstName: currentProfile?.firstName ?? '',
      lastName: currentProfile?.lastName ?? '',
      enrollmentNumber: _enrollmentController.text,
      branch: _branchController.text,
      year: int.tryParse(_yearController.text) ?? 1,
      semester: int.tryParse(_semesterController.text) ?? 1,
      cgpa: double.tryParse(_cgpaController.text) ?? 0.0,
      phoneNumber: _phoneController.text,
      gender: _gender,
      skills: _skillsController.text,
      githubUrl: _githubController.text,
      linkedinUrl: _linkedinController.text,
      portfolioUrl: _portfolioController.text,
      isPlaced: currentProfile?.isPlaced ?? false,
    );

    final success = await ref.read(profileProvider.notifier).updateProfile(updatedProfile);
    
    if (mounted) {
      setState(() => _isLoading = false);
      if (success) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Profile updated successfully'), backgroundColor: AppColors.success),
        );
        context.pop();
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Failed to update profile'), backgroundColor: AppColors.error),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Edit Profile'),
        backgroundColor: AppColors.surface,
        leading: IconButton(
          icon: const Icon(LucideIcons.arrowLeft),
          onPressed: () => context.pop(),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(AppSpacing.screenPadding),
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 800),
            child: Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildSectionTitle('Academic Details', LucideIcons.graduationCap),
                  _buildCard(
                    child: Column(
                      children: [
                        Row(
                          children: [
                            Expanded(child: _buildTextField(_enrollmentController, 'Enrollment Number', required: true)),
                            const SizedBox(width: AppSpacing.md),
                            Expanded(child: _buildTextField(_branchController, 'Branch', required: true)),
                          ],
                        ),
                        const SizedBox(height: AppSpacing.md),
                        Row(
                          children: [
                            Expanded(
                              child: _buildTextField(
                                _yearController, 'Year (1-5)', 
                                required: true,
                                keyboardType: TextInputType.number,
                                validator: (v) {
                                  if (v == null || v.isEmpty) return 'Required';
                                  final n = int.tryParse(v);
                                  if (n == null || n < 1 || n > 5) return '1-5 only';
                                  return null;
                                }
                              )
                            ),
                            const SizedBox(width: AppSpacing.md),
                            Expanded(
                              child: _buildTextField(
                                _semesterController, 'Semester (1-10)', 
                                required: true,
                                keyboardType: TextInputType.number,
                                validator: (v) {
                                  if (v == null || v.isEmpty) return 'Required';
                                  final n = int.tryParse(v);
                                  if (n == null || n < 1 || n > 10) return '1-10 only';
                                  return null;
                                }
                              )
                            ),
                            const SizedBox(width: AppSpacing.md),
                            Expanded(
                              child: _buildTextField(
                                _cgpaController, 'CGPA (0-10)', 
                                required: true,
                                keyboardType: const TextInputType.numberWithOptions(decimal: true),
                                validator: (v) {
                                  if (v == null || v.isEmpty) return 'Required';
                                  final n = double.tryParse(v);
                                  if (n == null || n < 0 || n > 10) return '0-10 only';
                                  return null;
                                }
                              )
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: AppSpacing.xl),
                  
                  _buildSectionTitle('Contact Details', LucideIcons.contact),
                  _buildCard(
                    child: Column(
                      children: [
                        Row(
                          children: [
                            Expanded(child: _buildTextField(_phoneController, 'Phone Number')),
                            const SizedBox(width: AppSpacing.md),
                            Expanded(
                              child: DropdownButtonFormField<String>(
                                initialValue: _gender,
                                decoration: _inputDecoration('Gender'),
                                dropdownColor: AppColors.surfaceElevated,
                                items: const [
                                  DropdownMenuItem(value: 'M', child: Text('Male')),
                                  DropdownMenuItem(value: 'F', child: Text('Female')),
                                  DropdownMenuItem(value: 'O', child: Text('Other')),
                                ],
                                onChanged: (v) => setState(() => _gender = v!),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: AppSpacing.xl),
                  
                  _buildSectionTitle('Skills', LucideIcons.code),
                  _buildCard(
                    child: _buildTextField(
                      _skillsController, 
                      'Skills (Comma separated)',
                      hint: 'e.g. Flutter, Python, Django, React'
                    ),
                  ),
                  const SizedBox(height: AppSpacing.xl),
                  
                  _buildSectionTitle('Links', LucideIcons.link),
                  _buildCard(
                    child: Column(
                      children: [
                        _buildTextField(_githubController, 'GitHub URL', keyboardType: TextInputType.url),
                        const SizedBox(height: AppSpacing.md),
                        _buildTextField(_linkedinController, 'LinkedIn URL', keyboardType: TextInputType.url),
                        const SizedBox(height: AppSpacing.md),
                        _buildTextField(_portfolioController, 'Portfolio URL', keyboardType: TextInputType.url),
                      ],
                    ),
                  ),
                  const SizedBox(height: AppSpacing.xxl),
                  
                  SizedBox(
                    width: double.infinity,
                    height: 50,
                    child: ElevatedButton(
                      onPressed: _isLoading ? null : _submit,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppColors.primary,
                        foregroundColor: Colors.white,
                      ),
                      child: _isLoading 
                        ? const CircularProgressIndicator(color: Colors.white)
                        : const Text('Save Profile', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                    ),
                  ),
                  const SizedBox(height: AppSpacing.xxl),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildSectionTitle(String title, IconData icon) {
    return Padding(
      padding: const EdgeInsets.only(bottom: AppSpacing.md),
      child: Row(
        children: [
          Icon(icon, color: AppColors.primary),
          const SizedBox(width: AppSpacing.sm),
          Text(
            title,
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
              color: AppColors.textPrimary,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCard({required Widget child}) {
    return Container(
      padding: const EdgeInsets.all(AppSpacing.cardPadding),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(AppSpacing.borderRadius),
        border: Border.all(color: AppColors.border),
      ),
      child: child,
    );
  }

  InputDecoration _inputDecoration(String label, {String? hint}) {
    return InputDecoration(
      labelText: label,
      hintText: hint,
      labelStyle: const TextStyle(color: AppColors.textHint),
      enabledBorder: OutlineInputBorder(
        borderSide: const BorderSide(color: AppColors.border),
        borderRadius: BorderRadius.circular(AppSpacing.buttonRadius),
      ),
      focusedBorder: OutlineInputBorder(
        borderSide: const BorderSide(color: AppColors.primary),
        borderRadius: BorderRadius.circular(AppSpacing.buttonRadius),
      ),
      errorBorder: OutlineInputBorder(
        borderSide: const BorderSide(color: AppColors.error),
        borderRadius: BorderRadius.circular(AppSpacing.buttonRadius),
      ),
      focusedErrorBorder: OutlineInputBorder(
        borderSide: const BorderSide(color: AppColors.error),
        borderRadius: BorderRadius.circular(AppSpacing.buttonRadius),
      ),
      filled: true,
      fillColor: AppColors.background,
    );
  }

  Widget _buildTextField(
    TextEditingController controller, 
    String label, {
    bool required = false,
    TextInputType? keyboardType,
    String? hint,
    String? Function(String?)? validator,
  }) {
    return TextFormField(
      controller: controller,
      keyboardType: keyboardType,
      style: const TextStyle(color: AppColors.textPrimary),
      decoration: _inputDecoration(label, hint: hint),
      validator: validator ?? (required 
        ? (v) => v == null || v.isEmpty ? 'This field is required' : null 
        : null),
    );
  }
}

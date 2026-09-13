import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../widgets/common/primary_button.dart';
import '../../../widgets/common/custom_text_field.dart';
import '../../../core/api/api_client.dart';
import 'dart:convert';
class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLoading = false;

  void _handleLogin() async {
    if (_emailController.text.isEmpty || _passwordController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter email and password'), backgroundColor: Colors.red),
      );
      return;
    }

    setState(() => _isLoading = true);
    
    try {
      final response = await ApiClient.post('/accounts/login/', body: {
        'email': _emailController.text.trim(),
        'password': _passwordController.text,
      });

      if (!mounted) return;

      setState(() => _isLoading = false);
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final role = data['user']?['role'];
        ApiClient.setTokens(data['access'], data['refresh'], role: role);
        
        context.go('/dashboard');
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Invalid credentials'), backgroundColor: Colors.red),
        );
      }
    } catch (e) {
      if (!mounted) return;
      setState(() => _isLoading = false);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Network error. Please try again.'), backgroundColor: Colors.red),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Row(
        children: [
          // Left side branding - hidden on mobile
          if (MediaQuery.of(context).size.width > 800)
            Expanded(
              child: Container(
                color: AppColors.surface,
                child: Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(
                        LucideIcons.rocket,
                        size: 80,
                        color: AppColors.primary,
                      ),
                      const SizedBox(height: AppSpacing.lg),
                      Text(
                        'LaunchPad',
                        style: Theme.of(context).textTheme.displayLarge?.copyWith(
                          color: AppColors.primary,
                        ),
                      ),
                      const SizedBox(height: AppSpacing.sm),
                      Text(
                        'Your premium placement portal',
                        style: Theme.of(context).textTheme.bodyLarge,
                      ),
                    ],
                  ),
                ),
              ),
            ),
          
          // Right side form
          Expanded(
            child: Center(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(AppSpacing.xxl),
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 400),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      if (MediaQuery.of(context).size.width <= 800) ...[
                        const Icon(
                          LucideIcons.rocket,
                          size: 48,
                          color: AppColors.primary,
                        ),
                        const SizedBox(height: AppSpacing.lg),
                      ],
                      Text(
                        'Welcome back',
                        style: Theme.of(context).textTheme.displaySmall,
                      ),
                      const SizedBox(height: AppSpacing.sm),
                      Text(
                        'Enter your details to access your dashboard.',
                        style: Theme.of(context).textTheme.bodyMedium,
                      ),
                      const SizedBox(height: AppSpacing.xl),
                      CustomTextField(
                        labelText: 'Email',
                        hintText: 'student@college.edu',
                        controller: _emailController,
                        prefixIcon: const Icon(LucideIcons.mail, size: 20),
                      ),
                      const SizedBox(height: AppSpacing.lg),
                      CustomTextField(
                        labelText: 'Password',
                        hintText: '••••••••',
                        obscureText: true,
                        controller: _passwordController,
                        prefixIcon: const Icon(LucideIcons.lock, size: 20),
                      ),
                      const SizedBox(height: AppSpacing.lg),
                      Align(
                        alignment: Alignment.centerRight,
                        child: TextButton(
                          onPressed: () {},
                          child: Text(
                            'Forgot Password?',
                            style: Theme.of(context).textTheme.labelLarge?.copyWith(
                              color: AppColors.primary,
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(height: AppSpacing.xl),
                      PrimaryButton(
                        text: 'Sign In',
                        onPressed: _handleLogin,
                        isFullWidth: true,
                        isLoading: _isLoading,
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

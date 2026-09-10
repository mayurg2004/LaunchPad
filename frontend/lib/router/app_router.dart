import 'package:go_router/go_router.dart';
import '../core/api/api_client.dart';
import '../features/auth/presentation/login_screen.dart';
import '../features/dashboard/presentation/dashboard_layout.dart';
import '../features/interviews/presentation/interview_details_screen.dart';
import '../features/placement_drives/presentation/placement_drive_details_screen.dart';
import '../features/profile/presentation/edit_profile_screen.dart';
import '../features/resumes/presentation/resume_analysis_screen.dart';
import '../features/resumes/presentation/skill_gap_screen.dart';

final appRouter = GoRouter(
  initialLocation: '/login',
  redirect: (context, state) {
    final isLoggedIn = ApiClient.isAuthenticated;
    final isLoginRoute = state.matchedLocation == '/login';

    if (!isLoggedIn && !isLoginRoute) {
      return '/login';
    }
    
    if (isLoggedIn && isLoginRoute) {
      return '/dashboard';
    }
    
    return null;
  },
  routes: [
    GoRoute(
      path: '/login',
      builder: (context, state) => const LoginScreen(),
    ),
    GoRoute(
      path: '/dashboard',
      builder: (context, state) => const DashboardLayout(),
    ),
    GoRoute(
      path: '/placement-drives/:id',
      builder: (context, state) {
        final idStr = state.pathParameters['id']!;
        return PlacementDriveDetailsScreen(driveId: int.parse(idStr));
      },
    ),
    GoRoute(
      path: '/interviews/:id',
      builder: (context, state) {
        final idStr = state.pathParameters['id']!;
        return InterviewDetailsScreen(interviewId: int.parse(idStr));
      },
    ),
    GoRoute(
      path: '/profile/edit',
      builder: (context, state) => const EditProfileScreen(),
    ),
    GoRoute(
      path: '/resumes/:id/analysis',
      builder: (context, state) {
        final resumeId = int.parse(state.pathParameters['id']!);
        return ResumeAnalysisScreen(resumeId: resumeId);
      },
    ),
    GoRoute(
      path: '/resumes/:id/skill-gap',
      builder: (context, state) {
        final resumeId = int.parse(state.pathParameters['id']!);
        return SkillGapScreen(resumeId: resumeId);
      },
    ),
  ],
);

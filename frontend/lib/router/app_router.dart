import 'package:go_router/go_router.dart';
import '../features/auth/presentation/login_screen.dart';
import '../features/dashboard/presentation/dashboard_layout.dart';
import '../features/placement_drives/presentation/placement_drive_details_screen.dart';
import '../core/api/api_client.dart';

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
  ],
);

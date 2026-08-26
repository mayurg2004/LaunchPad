import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:launchpad/core/api/api_client.dart';
import 'package:launchpad/router/app_router.dart';
import 'package:launchpad/features/auth/presentation/login_screen.dart';
import 'package:launchpad/features/dashboard/presentation/dashboard_layout.dart';

void main() {
  Widget createTestApp() {
    return ProviderScope(
      child: MaterialApp.router(
        routerConfig: appRouter,
      ),
    );
  }

  group('Auth & Session Tests', () {
    setUp(() {
      ApiClient.clearSession();
      // Reset router manually for each test
      appRouter.go('/login');
    });

    testWidgets('logout clears session', (WidgetTester tester) async {
      ApiClient.setTokens('access', 'refresh');
      expect(ApiClient.isAuthenticated, isTrue);

      ApiClient.logout();
      expect(ApiClient.isAuthenticated, isFalse);
    });

    testWidgets('user is redirected to login on logout', (WidgetTester tester) async {
      tester.view.physicalSize = const Size(3000, 2000);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);

      ApiClient.setTokens('access', 'refresh');
      await tester.pumpWidget(createTestApp());
      await tester.pumpAndSettle();
      
      appRouter.go('/dashboard');
      await tester.pumpAndSettle();
      
      ApiClient.logout();
      await tester.pumpAndSettle();
      
      expect(find.byType(LoginScreen), findsOneWidget);
    });

    testWidgets('authenticated screens cannot be accessed after logout', (WidgetTester tester) async {
      tester.view.physicalSize = const Size(3000, 2000);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);

      await tester.pumpWidget(createTestApp());
      await tester.pumpAndSettle();
      
      // Attempt to go to dashboard directly without auth
      appRouter.go('/dashboard');
      await tester.pumpAndSettle();
      
      // Should redirect to login
      expect(find.byType(LoginScreen), findsOneWidget);
      expect(find.byType(DashboardLayout), findsNothing);
    });

    testWidgets('expired session is handled correctly (clearSession)', (WidgetTester tester) async {
      tester.view.physicalSize = const Size(3000, 2000);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);

      ApiClient.setTokens('access', 'refresh');
      await tester.pumpWidget(createTestApp());
      await tester.pumpAndSettle();
      
      appRouter.go('/dashboard');
      await tester.pumpAndSettle();
      
      expect(find.byType(DashboardLayout), findsOneWidget);
      
      // Simulating the 401 handler action
      ApiClient.clearSession();
      await tester.pumpAndSettle();
      
      expect(ApiClient.isAuthenticated, isFalse);
      expect(find.byType(LoginScreen), findsOneWidget);
    });
  });
}

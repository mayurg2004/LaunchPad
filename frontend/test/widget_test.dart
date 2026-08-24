import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:launchpad/main.dart';
import 'package:launchpad/features/auth/presentation/login_screen.dart';

void main() {
  testWidgets('LaunchPadApp renders login screen', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const ProviderScope(child: LaunchPadApp()));
    
    // Wait for the router to push the initial route
    await tester.pumpAndSettle();

    // Verify that the login screen is rendered
    expect(find.byType(LoginScreen), findsOneWidget);
  });
}

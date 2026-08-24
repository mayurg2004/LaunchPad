import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:launchpad/features/notifications/data/notification_model.dart';
import 'package:launchpad/features/notifications/providers/notification_provider.dart';
import 'package:launchpad/features/notifications/presentation/notification_panel.dart';
import 'package:launchpad/features/dashboard/presentation/dashboard_layout.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';
import 'package:launchpad/core/theme/app_theme.dart';

// Mock Notifier to override the API calls for testing
class MockNotificationNotifier extends NotificationNotifier {
  final List<NotificationModel> initialData;

  MockNotificationNotifier(this.initialData);

  @override
  Future<List<NotificationModel>> build() async {
    return initialData;
  }

  @override
  Future<void> markAsRead(int id) async {
    if (state.hasValue) {
      final updatedList = state.value!.map((n) {
        if (n.id == id) return n.copyWith(isRead: true);
        return n;
      }).toList();
      state = AsyncData(updatedList);
    }
  }

  @override
  Future<void> markAllAsRead() async {
    if (state.hasValue) {
      final updatedList = state.value!.map((n) => n.copyWith(isRead: true)).toList();
      state = AsyncData(updatedList);
    }
  }
}

void main() {
  Widget createWidgetUnderTest(List<NotificationModel> mockData) {
    return ProviderScope(
      overrides: [
        notificationProvider.overrideWith(() => MockNotificationNotifier(mockData)),
      ],
      child: MaterialApp(
        theme: AppTheme.darkTheme,
        home: const Scaffold(
          body: NotificationPanel(),
        ),
      ),
    );
  }

  testWidgets('NotificationPanel displays empty state when no notifications', (WidgetTester tester) async {
    await tester.pumpWidget(createWidgetUnderTest([]));
    await tester.pumpAndSettle();

    expect(find.text('You\'re all caught up!'), findsOneWidget);
    expect(find.byIcon(LucideIcons.bellOff), findsOneWidget);
  });

  testWidgets('NotificationPanel displays notification list and unread styles correctly', (WidgetTester tester) async {
    final mockData = [
      NotificationModel(
        id: 1,
        title: 'Interview Scheduled',
        message: 'TCS interview at 10 AM',
        notificationType: 'INTERVIEW',
        isRead: false,
        createdAt: DateTime.now().subtract(const Duration(minutes: 5)),
      ),
      NotificationModel(
        id: 2,
        title: 'New Opportunity',
        message: 'Infosys is hiring',
        notificationType: 'PLACEMENT_DRIVE',
        isRead: true,
        createdAt: DateTime.now().subtract(const Duration(hours: 2)),
      ),
    ];

    await tester.pumpWidget(createWidgetUnderTest(mockData));
    await tester.pumpAndSettle();

    // Verify both items are rendered
    expect(find.text('Interview Scheduled'), findsOneWidget);
    expect(find.text('New Opportunity'), findsOneWidget);

    // Verify unread badge in layout - we need a slightly different setup to test the badge in the app bar
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          notificationProvider.overrideWith(() => MockNotificationNotifier(mockData)),
        ],
        child: MaterialApp(
          theme: AppTheme.darkTheme,
          home: const DashboardLayout(),
        ),
      ),
    );
    await tester.pumpAndSettle();

    // One unread notification should show '1' in the badge
    final badgeWidget = find.byType(Badge);
    expect(badgeWidget, findsOneWidget);
    expect(find.descendant(of: badgeWidget, matching: find.text('1')), findsOneWidget);
  });

  testWidgets('Tapping mark all as read updates state', (WidgetTester tester) async {
    final mockData = [
      NotificationModel(
        id: 1,
        title: 'Test 1',
        message: 'Msg 1',
        notificationType: 'SYSTEM',
        isRead: false,
        createdAt: DateTime.now(),
      ),
    ];

    await tester.pumpWidget(createWidgetUnderTest(mockData));
    await tester.pumpAndSettle();

    // Verify 'Mark all as read' is visible since there is an unread notification
    final markAllButton = find.text('Mark all as read');
    expect(markAllButton, findsOneWidget);

    // Tap it
    await tester.tap(markAllButton);
    await tester.pumpAndSettle();

    // After tapping, there are no unread notifications, so 'Mark all as read' should disappear
    expect(find.text('Mark all as read'), findsNothing);
  });
}

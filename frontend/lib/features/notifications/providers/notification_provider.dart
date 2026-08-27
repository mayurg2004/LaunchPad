import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/notification_model.dart';
import '../data/notification_repository.dart';

final notificationRepositoryProvider = Provider((ref) => NotificationRepository());

class NotificationNotifier extends AsyncNotifier<List<NotificationModel>> {
  @override
  Future<List<NotificationModel>> build() async {
    return _fetchNotifications();
  }

  Future<List<NotificationModel>> _fetchNotifications() async {
    final repo = ref.read(notificationRepositoryProvider);
    return await repo.fetchNotifications();
  }

  Future<void> markAsRead(int id) async {
    // Optimistic update
    final previousState = state;
    if (state.hasValue) {
      final updatedList = state.value!.map((n) {
        if (n.id == id) return n.copyWith(isRead: true);
        return n;
      }).toList();
      state = AsyncData(updatedList);
    }

    try {
      final repo = ref.read(notificationRepositoryProvider);
      await repo.markAsRead(id);
    } catch (e, st) {
      // Revert on failure
      state = previousState;
      state = AsyncError(e, st);
    }
  }

  Future<void> markAllAsRead() async {
    final previousState = state;
    if (state.hasValue) {
      final updatedList = state.value!.map((n) => n.copyWith(isRead: true)).toList();
      state = AsyncData(updatedList);
    }

    try {
      final repo = ref.read(notificationRepositoryProvider);
      await repo.markAllAsRead();
    } catch (e, st) {
      state = previousState;
      state = AsyncError(e, st);
    }
  }

  Future<void> refresh() async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() => _fetchNotifications());
  }
}

final notificationProvider = AsyncNotifierProvider<NotificationNotifier, List<NotificationModel>>(() {
  return NotificationNotifier();
});

final unreadCountProvider = Provider<int>((ref) {
  final notificationsState = ref.watch(notificationProvider);
  return notificationsState.maybeWhen(
    data: (notifications) => notifications.where((n) => !n.isRead).length,
    orElse: () => 0,
  );
});

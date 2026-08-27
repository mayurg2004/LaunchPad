import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/models/application.dart';
import '../data/repositories/application_repository.dart';

final applicationRepositoryProvider = Provider((ref) {
  return ApplicationRepository();
});

final myApplicationsProvider = FutureProvider<List<Application>>((ref) async {
  final repo = ref.watch(applicationRepositoryProvider);
  return await repo.getMyApplications();
});

class ApplicationNotifier extends StateNotifier<AsyncValue<Application?>> {
  final ApplicationRepository _repository;
  final Ref _ref;

  ApplicationNotifier(this._repository, this._ref) : super(const AsyncValue.data(null));

  Future<bool> apply(int placementDriveId) async {
    state = const AsyncValue.loading();
    try {
      final application = await _repository.apply(placementDriveId);
      state = AsyncValue.data(application);
      // Refresh my applications list
      _ref.invalidate(myApplicationsProvider);
      return true;
    } catch (e, st) {
      state = AsyncValue.error(e, st);
      return false;
    }
  }

  void reset() {
    state = const AsyncValue.data(null);
  }
}

final applicationNotifierProvider = StateNotifierProvider<ApplicationNotifier, AsyncValue<Application?>>((ref) {
  return ApplicationNotifier(ref.watch(applicationRepositoryProvider), ref);
});

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/models/interview.dart';
import '../data/repositories/interview_repository.dart';

final interviewRepositoryProvider = Provider((ref) {
  return InterviewRepository();
});

final allInterviewsProvider = FutureProvider<List<Interview>>((ref) async {
  final repo = ref.watch(interviewRepositoryProvider);
  return await repo.getInterviews();
});

final upcomingInterviewsProvider = FutureProvider<List<Interview>>((ref) async {
  final repo = ref.watch(interviewRepositoryProvider);
  return await repo.getUpcomingInterviews();
});

final interviewDetailsProvider = FutureProvider.family<Interview, int>((ref, id) async {
  final repo = ref.watch(interviewRepositoryProvider);
  return await repo.getInterviewDetails(id);
});

import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/api/api_client.dart';
import '../../../core/api/endpoints.dart';
import '../data/models/student_profile_model.dart';

final profileProvider = StateNotifierProvider<ProfileNotifier, AsyncValue<StudentProfileModel?>>((ref) {
  return ProfileNotifier();
});

class ProfileNotifier extends StateNotifier<AsyncValue<StudentProfileModel?>> {
  ProfileNotifier() : super(const AsyncValue.loading()) {
    fetchProfile();
  }

  Future<void> fetchProfile() async {
    try {
      state = const AsyncValue.loading();
      final response = await ApiClient.get(Endpoints.studentProfile);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        state = AsyncValue.data(StudentProfileModel.fromJson(data));
      } else if (response.statusCode == 404) {
        // Profile not found - returning null allowing empty state creation
        state = const AsyncValue.data(null);
      } else {
        state = AsyncValue.error('Failed to load profile: ${response.statusCode}', StackTrace.current);
      }
    } catch (e, stackTrace) {
      state = AsyncValue.error(e, stackTrace);
    }
  }

  Future<bool> updateProfile(StudentProfileModel profile) async {
    try {
      final isCreating = state.value == null;
      final endpoint = isCreating 
          ? '/students/create/' 
          : Endpoints.studentProfileUpdate;
          
      final response = isCreating 
          ? await ApiClient.post(endpoint, body: profile.toJson())
          : await ApiClient.patch(endpoint, body: profile.toJson());

      if (response.statusCode == 200 || response.statusCode == 201) {
        final data = jsonDecode(response.body);
        state = AsyncValue.data(StudentProfileModel.fromJson(data));
        return true;
      } else {
        state = AsyncValue.error('Failed to update profile: ${response.body}', StackTrace.current);
        return false;
      }
    } catch (e, stackTrace) {
      state = AsyncValue.error(e, stackTrace);
      return false;
    }
  }
}

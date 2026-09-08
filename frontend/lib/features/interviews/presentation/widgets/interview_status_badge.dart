import 'package:flutter/material.dart';
import '../../../../widgets/common/status_badge.dart';

class InterviewStatusBadge extends StatelessWidget {
  final String status;
  final String? result;

  const InterviewStatusBadge({
    super.key,
    required this.status,
    this.result,
  });

  @override
  Widget build(BuildContext context) {
    String displayText = status;
    BadgeStatus badgeStatus = BadgeStatus.neutral;

    final upperStatus = status.toUpperCase();
    final upperResult = result?.toUpperCase() ?? 'PENDING';

    if (upperStatus == 'COMPLETED') {
      if (upperResult == 'PASSED') {
        displayText = 'Passed';
        badgeStatus = BadgeStatus.success;
      } else if (upperResult == 'FAILED') {
        displayText = 'Failed';
        badgeStatus = BadgeStatus.error;
      } else {
        displayText = 'Completed';
        badgeStatus = BadgeStatus.success;
      }
    } else if (upperStatus == 'SCHEDULED') {
      displayText = 'Scheduled';
      badgeStatus = BadgeStatus.info;
    } else if (upperStatus == 'IN_PROGRESS') {
      displayText = 'In Progress';
      badgeStatus = BadgeStatus.warning;
    } else if (upperStatus == 'CANCELLED') {
      displayText = 'Cancelled';
      badgeStatus = BadgeStatus.error;
    } else {
      displayText = status;
      badgeStatus = BadgeStatus.neutral;
    }

    // Since StatusBadge handles 'REJECTED' etc internally, it will ignore our badgeStatus if it matches its hardcoded strings,
    // but none of our displayTexts match its hardcoded strings, so it's fine.

    return StatusBadge(
      text: displayText,
      status: badgeStatus,
    );
  }
}

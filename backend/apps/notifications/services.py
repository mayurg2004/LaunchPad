from .models import Notification, NotificationPreference

class NotificationService:
    @staticmethod
    def should_send(user, notification_type):
        pref, _ = NotificationPreference.objects.get_or_create(user=user)
        if notification_type == 'APPLICATION':
            return pref.application_notifications
        elif notification_type == 'INTERVIEW':
            return pref.interview_notifications
        elif notification_type == 'OFFER':
            return pref.offer_notifications
        elif notification_type == 'PLACEMENT_DRIVE':
            return pref.placement_drive_notifications
        elif notification_type == 'SYSTEM':
            return pref.system_notifications
        return True

    @staticmethod
    def notify_application_submitted(application):
        if not NotificationService.should_send(application.student.user, 'APPLICATION'):
            return
        Notification.objects.create(
            recipient=application.student.user,
            title="Application Submitted",
            message=f"You have successfully applied to {application.placement_drive.title} at {application.placement_drive.company.company_name}.",
            notification_type='APPLICATION'
        )

    @staticmethod
    def notify_application_shortlisted(application):
        if not NotificationService.should_send(application.student.user, 'APPLICATION'):
            return
        Notification.objects.create(
            recipient=application.student.user,
            title="Application Shortlisted",
            message=f"Congratulations! Your application for {application.placement_drive.title} at {application.placement_drive.company.company_name} has been shortlisted.",
            notification_type='APPLICATION'
        )

    @staticmethod
    def notify_application_rejected(application):
        if not NotificationService.should_send(application.student.user, 'APPLICATION'):
            return
        Notification.objects.create(
            recipient=application.student.user,
            title="Application Update",
            message=f"Your application for {application.placement_drive.title} at {application.placement_drive.company.company_name} was not moved forward.",
            notification_type='APPLICATION'
        )

    @staticmethod
    def notify_interview_scheduled(interview):
        application = interview.application
        if not NotificationService.should_send(application.student.user, 'INTERVIEW'):
            return
        Notification.objects.create(
            recipient=application.student.user,
            title="Interview Scheduled",
            message=f"An interview for {application.placement_drive.company.company_name} has been scheduled for {interview.scheduled_at.strftime('%Y-%m-%d %H:%M')}.",
            notification_type='INTERVIEW'
        )

    @staticmethod
    def notify_interview_passed(interview):
        application = interview.application
        if not NotificationService.should_send(application.student.user, 'INTERVIEW'):
            return
        Notification.objects.create(
            recipient=application.student.user,
            title="Interview Passed",
            message=f"Congratulations! You passed the {interview.round_name} interview for {application.placement_drive.company.company_name}.",
            notification_type='INTERVIEW'
        )

    @staticmethod
    def notify_interview_failed(interview):
        application = interview.application
        if not NotificationService.should_send(application.student.user, 'INTERVIEW'):
            return
        Notification.objects.create(
            recipient=application.student.user,
            title="Interview Update",
            message=f"You did not pass the {interview.round_name} interview for {application.placement_drive.company.company_name}.",
            notification_type='INTERVIEW'
        )

    @staticmethod
    def notify_offer_received(offer):
        if not NotificationService.should_send(offer.student.user, 'OFFER'):
            return
        Notification.objects.create(
            recipient=offer.student.user,
            title="New Offer Received",
            message=f"You have received a new offer from {offer.company.company_name} for the position of {offer.job_title}.",
            notification_type='OFFER'
        )

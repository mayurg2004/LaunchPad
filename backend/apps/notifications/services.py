from .models import Notification

class NotificationService:
    @staticmethod
    def notify_application_submitted(application):
        Notification.objects.create(
            recipient=application.student.user,
            title="Application Submitted",
            message=f"You have successfully applied to {application.placement_drive.title} at {application.placement_drive.company.company_name}.",
            notification_type='APPLICATION'
        )

    @staticmethod
    def notify_application_shortlisted(application):
        Notification.objects.create(
            recipient=application.student.user,
            title="Application Shortlisted",
            message=f"Congratulations! Your application for {application.placement_drive.title} at {application.placement_drive.company.company_name} has been shortlisted.",
            notification_type='APPLICATION'
        )

    @staticmethod
    def notify_application_rejected(application):
        Notification.objects.create(
            recipient=application.student.user,
            title="Application Update",
            message=f"Your application for {application.placement_drive.title} at {application.placement_drive.company.company_name} was not moved forward.",
            notification_type='APPLICATION'
        )

    @staticmethod
    def notify_interview_scheduled(interview):
        application = interview.application
        Notification.objects.create(
            recipient=application.student.user,
            title="Interview Scheduled",
            message=f"An interview for {application.placement_drive.company.company_name} has been scheduled for {interview.scheduled_at.strftime('%Y-%m-%d %H:%M')}.",
            notification_type='INTERVIEW'
        )

    @staticmethod
    def notify_interview_passed(interview):
        application = interview.application
        Notification.objects.create(
            recipient=application.student.user,
            title="Interview Passed",
            message=f"Congratulations! You passed the {interview.round_name} interview for {application.placement_drive.company.company_name}.",
            notification_type='INTERVIEW'
        )

    @staticmethod
    def notify_interview_failed(interview):
        application = interview.application
        Notification.objects.create(
            recipient=application.student.user,
            title="Interview Update",
            message=f"You did not pass the {interview.round_name} interview for {application.placement_drive.company.company_name}.",
            notification_type='INTERVIEW'
        )

    @staticmethod
    def notify_offer_received(offer):
        Notification.objects.create(
            recipient=offer.student.user,
            title="New Offer Received",
            message=f"You have received a new offer from {offer.company.company_name} for the position of {offer.job_title}.",
            notification_type='OFFER'
        )

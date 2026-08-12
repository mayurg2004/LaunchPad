from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from applications.models import Application
from interviews.models import Interview
from offers.models import Offer
from .services import NotificationService

@receiver(pre_save, sender=Application)
def cache_application_status(sender, instance, **kwargs):
    if instance.id:
        try:
            old_instance = Application.objects.get(id=instance.id)
            instance._old_status = old_instance.status
        except Application.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None

@receiver(post_save, sender=Application)
def handle_application_save(sender, instance, created, **kwargs):
    if created:
        NotificationService.notify_application_submitted(instance)
    else:
        old_status = getattr(instance, '_old_status', None)
        if old_status and old_status != instance.status:
            if instance.status == 'SHORTLISTED':
                NotificationService.notify_application_shortlisted(instance)
            elif instance.status == 'REJECTED':
                NotificationService.notify_application_rejected(instance)

@receiver(pre_save, sender=Interview)
def cache_interview_result(sender, instance, **kwargs):
    if instance.id:
        try:
            old_instance = Interview.objects.get(id=instance.id)
            instance._old_result = old_instance.result
        except Interview.DoesNotExist:
            instance._old_result = None
    else:
        instance._old_result = None

@receiver(post_save, sender=Interview)
def handle_interview_save(sender, instance, created, **kwargs):
    if created:
        NotificationService.notify_interview_scheduled(instance)
    else:
        old_result = getattr(instance, '_old_result', None)
        if old_result and old_result != instance.result:
            if instance.result == 'PASSED':
                NotificationService.notify_interview_passed(instance)
            elif instance.result == 'FAILED':
                NotificationService.notify_interview_failed(instance)

@receiver(post_save, sender=Offer)
def handle_offer_save(sender, instance, created, **kwargs):
    if created:
        NotificationService.notify_offer_received(instance)

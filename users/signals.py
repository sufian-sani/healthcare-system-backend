from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import DoctorSchedule, User, DoctorDetail

@receiver(post_save, sender=User)
def create_doctor_profile(sender, instance, created, **kwargs):
    if created and instance.role == 'doctor':
        # Avoid duplicate DoctorDetail creation
        if not hasattr(instance, 'doctordetail'):
            DoctorDetail.objects.create(
                user=instance,
                license_number='',
                experience_years=0,
                consultation_fee=0
            )
        if not hasattr(instance, 'doctorschedule'):
            DoctorSchedule.objects.create(
                doctor=instance,
                date=None,
                start_time=None,
                end_time=None,
            )

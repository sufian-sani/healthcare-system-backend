from celery_app import shared_task
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from appointments.models import AppointmentBooking

@shared_task
def send_appointment_reminders():
    now = timezone.now()
    reminder_time = now + timedelta(hours=24)

    appointments = AppointmentBooking.objects.filter(
        schedule__date=reminder_time.date(),
        appointment_time__hour=reminder_time.hour,
        status__in=['pending', 'confirmed']  # Only upcoming appointments
    )

    for appointment in appointments:
        patient_email = appointment.patient.email
        doctor_name = appointment.doctor.full_name
        appointment_time = appointment.appointment_time.strftime("%I:%M %p")

        if patient_email:
            send_mail(
                subject="Appointment Reminder",
                message=(
                    f"Dear {appointment.patient.full_name},\n\n"
                    f"This is a reminder that you have an appointment with Dr. {doctor_name} "
                    f"on {appointment.schedule.date} at {appointment_time}.\n\n"
                    "Please be on time."
                ),
                from_email="no-reply@gmail.com",
                recipient_list=[patient_email],
                fail_silently=True,
            )

    return f"Reminders sent for {appointments.count()} appointments."

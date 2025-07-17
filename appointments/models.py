from django.db import models
from users.models import User, DoctorSchedule

class AppointmentBooking(models.Model):
    doctor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='doctor_appointments',
        limit_choices_to={'role': 'doctor'}
    )
    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='patient_appointments',
        limit_choices_to={'role': 'patient'}
    )
    schedule = models.ForeignKey(DoctorSchedule, on_delete=models.CASCADE, related_name='appointments')
    appointment_time = models.TimeField()  # single 30-min slot
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('confirmed', 'Confirmed'),
            ('cancelled', 'Cancelled'),
            ('completed', 'Completed')
        ],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('doctor', 'schedule', 'appointment_time')  # ✅ no double-booking

    def __str__(self):
        return f"{self.patient.full_name} with {self.doctor.full_name} at {self.appointment_time}"

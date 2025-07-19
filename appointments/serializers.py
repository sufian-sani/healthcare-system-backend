from rest_framework import serializers
from .models import AppointmentBooking
from users.models import DoctorSchedule, User
from .utils import generate_30_min_slots
from rest_framework.validators import UniqueTogetherValidator
from django.utils import timezone
from datetime import datetime, time

class AppointmentBookingSerializer(serializers.ModelSerializer):
    date = serializers.DateField(source='schedule.date', read_only=True)

    class Meta:
        model = AppointmentBooking
        fields = ['id', 'doctor', 'patient', 'date', 'schedule', 'appointment_time', 'notes', 'status']
        read_only_fields = ['id', 'status', 'patient', 'date']

        validators = [
            UniqueTogetherValidator(
                queryset=AppointmentBooking.objects.all(),
                fields=('doctor', 'schedule', 'appointment_time'),
                message="This timeslot is already booked. Please choose another."
            )
        ]

    def validate(self, data):
        doctor = data['doctor']
        schedule = data['schedule']
        appointment_time = data['appointment_time']

        # ✅ Ensure doctor has correct role
        if doctor.role != "doctor":
            raise serializers.ValidationError({"doctor": "Selected user is not a doctor."})

        # ✅ Ensure schedule belongs to doctor
        if schedule.doctor != doctor:
            raise serializers.ValidationError(
                {"schedule": "This schedule does not belong to the selected doctor."}
            )

        # ✅ Business hours validation (9 AM to 6 PM)
        BUSINESS_START = time(9, 0)
        BUSINESS_END = time(18, 0)
        if appointment_time < BUSINESS_START or appointment_time > BUSINESS_END:
            raise serializers.ValidationError({
                "appointment_time": f"Appointments are only allowed between {BUSINESS_START} and {BUSINESS_END}."
            })

        # ✅ Ensure appointment time is in the future (not past)
        appointment_datetime = datetime.combine(schedule.date, appointment_time)

        # Make timezone-aware if naive
        if timezone.is_naive(appointment_datetime):
            appointment_datetime = timezone.make_aware(appointment_datetime, timezone.get_current_timezone())

        if appointment_datetime <= timezone.now():
            raise serializers.ValidationError({
                "appointment_time": "You cannot book an appointment in the past."
            })

        # ✅ Ensure appointment time is within available slots
        valid_slots = generate_30_min_slots(schedule.start_time, schedule.end_time)
        if appointment_time not in valid_slots:
            raise serializers.ValidationError(
                {"appointment_time": "Selected time is not within the available slots for this schedule."}
            )

        return data

    def create(self, validated_data):
        validated_data['patient'] = self.context['request'].user
        return super().create(validated_data)

class AvailableSlotsSerializer(serializers.Serializer):
    schedule_id = serializers.IntegerField()
    available_slots = serializers.ListField(child=serializers.CharField())


class AppointmentStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentBooking
        fields = ["status"]

    def validate_status(self, value):
        allowed_statuses = ["confirmed", "cancelled", "completed"]
        if value not in allowed_statuses:
            raise serializers.ValidationError(f"Status must be one of: {', '.join(allowed_statuses)}")
        return value

class DoctorScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorSchedule
        fields = ['id', 'date', 'start_time', 'end_time']  # doctor auto-assigned

    def validate(self, data):
        user = self.context['request'].user
        date = data['date']
        start_time = data['start_time']
        end_time = data['end_time']

        # ✅ Ensure requester is a doctor
        if user.role != "doctor":
            raise serializers.ValidationError({"doctor": "Only doctors can create schedules."})

        # ✅ End time must be after start time
        if end_time <= start_time:
            raise serializers.ValidationError({"end_time": "End time must be after start time."})

        # ✅ No past schedules
        if date < datetime.now().date():
            raise serializers.ValidationError({"date": "You cannot create a schedule in the past."})

        # ✅ Today's schedule must be in the future
        if date == datetime.now().date() and start_time <= datetime.now().time():
            raise serializers.ValidationError({"start_time": "Start time must be in the future."})

        # ✅ Business hours (09:00 - 18:00)
        BUSINESS_START = time(9, 0)
        BUSINESS_END = time(18, 0)
        if start_time < BUSINESS_START or end_time > BUSINESS_END:
            raise serializers.ValidationError({
                "start_time": "Schedule must be within business hours (09:00 - 18:00).",
                "end_time": "Schedule must be within business hours (09:00 - 18:00)."
            })

        # ✅ Ensure unique schedule for this doctor
        if DoctorSchedule.objects.filter(
            doctor=user, date=date, start_time=start_time, end_time=end_time
        ).exists():
            raise serializers.ValidationError({
                "schedule": "This schedule already exists for this doctor."
            })

        return data

    def create(self, validated_data):
        """✅ Automatically assign logged-in doctor"""
        validated_data['doctor'] = self.context['request'].user
        return super().create(validated_data)
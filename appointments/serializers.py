from rest_framework import serializers
from .models import AppointmentBooking
from users.models import DoctorSchedule, User
from .utils import generate_30_min_slots
from rest_framework.validators import UniqueTogetherValidator

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

        # ✅ Ensure appointment time is valid
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

from rest_framework import serializers
from .models import AppointmentBooking
from users.models import DoctorSchedule
from .utils import generate_30_min_slots
from rest_framework.validators import UniqueTogetherValidator

class AppointmentBookingSerializer(serializers.ModelSerializer):
    date = serializers.DateField(source='schedule.date', read_only=True)  # Show schedule date in response
    class Meta:
        model = AppointmentBooking
        fields = ['id', 'doctor', 'patient', 'date', 'schedule', 'appointment_time', 'notes', 'status']
        read_only_fields = ['id', 'status', 'patient','date']

        validators = [
            UniqueTogetherValidator(
                queryset=AppointmentBooking.objects.all(),
                fields=('doctor', 'schedule', 'appointment_time'),
                message="This timeslot is already booked. Please choose another."
            )
        ]

    def validate(self, data):
        schedule = data['schedule']
        doctor = data['doctor']
        appointment_time = data['appointment_time']

        # ✅ Ensure doctor matches the schedule
        if schedule.doctor != doctor:
            # raise serializers.ValidationError("This schedule does not belong to the selected doctor.")
            raise serializers.ValidationError(
                {"doctor": "This schedule does not belong to the selected doctor."}
            )

        # ✅ Ensure time is valid (within start and end)
        valid_slots = generate_30_min_slots(schedule.start_time, schedule.end_time)
        if appointment_time not in valid_slots:
            # raise serializers.ValidationError("Selected time is not available in this schedule.")
            raise serializers.ValidationError(
                {"appointment_time": "Selected time is not within the available slots for this schedule."}
            )

        # # ✅ Ensure time not already booked
        # if AppointmentBooking.objects.filter(doctor=doctor, schedule=schedule, appointment_time=appointment_time).exists():
        #     # raise serializers.ValidationError("This timeslot is already booked.")
        #     raise serializers.ValidationError(
        #         {"appointment_time": "This timeslot is already booked. Please choose another."}
        #     )

        return data

    def create(self, validated_data):
        validated_data['patient'] = self.context['request'].user  # set patient automatically
        return super().create(validated_data)


class AvailableSlotsSerializer(serializers.Serializer):
    schedule_id = serializers.IntegerField()
    available_slots = serializers.ListField(child=serializers.CharField())

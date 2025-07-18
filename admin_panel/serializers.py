from rest_framework import serializers
from appointments.models import AppointmentBooking
from users.models import User, DoctorDetail, DoctorSchedule
from users.serializers import DoctorDetailSerializer, DoctorScheduleSerializer

# ✅ Appointment Serializer for Admin
class AdminAppointmentSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source="doctor.full_name", read_only=True)
    patient_name = serializers.CharField(source="patient.full_name", read_only=True)

    class Meta:
        model = AppointmentBooking
        fields = [
            "id", "doctor", "doctor_name",
            "patient", "patient_name",
            "schedule", "appointment_time",
            "notes", "status", "created_at"
        ]
        read_only_fields = ["id", "doctor_name", "patient_name", "created_at"]


# ✅ Doctor Serializer for Admin
class AdminDoctorSerializer(serializers.ModelSerializer):
    doctordetail = DoctorDetailSerializer(read_only=True)
    schedules = DoctorScheduleSerializer(source="doctorschedules", many=True, read_only=True)

    class Meta:
        model = User
        fields = ["id", "full_name", "mobile_number", "role", "doctordetail", "schedules", "is_active"]
        
        
class AppointmentStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentBooking
        fields = ['status', 'notes']
        read_only_fields = []  # ✅ allow doctor/admin to update

    def validate_status(self, value):
        """Ensure valid status values"""
        allowed_status = ['confirmed', 'cancelled', 'completed']
        if value not in allowed_status:
            raise serializers.ValidationError("Invalid status. Choose from confirmed, cancelled, completed.")
        return value


class AppointmentCRUDSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentBooking
        fields = ['id', 'doctor', 'patient', 'schedule', 'appointment_time', 'notes', 'status', 'created_at']
        read_only_fields = ['id', 'doctor', 'patient', 'schedule', 'appointment_time', 'created_at']

    def validate_status(self, value):
        allowed_status = ['confirmed', 'cancelled', 'completed']
        if value not in allowed_status:
            raise serializers.ValidationError(f"Invalid status. Choose from {allowed_status}.")
        return value


class DoctorStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'full_name', 'is_active']
        read_only_fields = ['id', 'full_name']
       
class FilteredListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        data = data.filter(role='patient')  # Filter only 'patient' roles
        return super().to_representation(data) 

class AdminUserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'full_name', 'mobile_number', 'role', 'is_active', 'created_at']
        list_serializer_class = FilteredListSerializer

        
        
class AdminUserStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'is_active']
        read_only_fields = ['id']

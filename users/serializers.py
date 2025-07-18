from rest_framework import serializers

from appointments.models import AppointmentBooking
from appointments.serializers import AppointmentBookingSerializer
from .models import DoctorDetail, DoctorSchedule, User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.hashers import make_password

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # ✅ Add custom claims to JWT
        token['role'] = user.role
        token['full_name'] = user.full_name

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # ✅ Also include these in the response body (not only inside JWT)
        data.update({
            'role': self.user.role,
            'full_name': self.user.full_name
        })
        return data



class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.CharField(required=False)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ['full_name', 'mobile_number', 'password', 'role', 'address','access', 'refresh']

    def create(self, validated_data):
        role = validated_data.get('role', 'patient')
        user = User.objects.create_user(
            full_name=validated_data['full_name'],
            mobile_number=validated_data['mobile_number'],
            password=validated_data['password'],
            role=role,
            address=validated_data.get('address', '')
        )
        # 🔑 Generate tokens
        refresh = RefreshToken.for_user(user)
        validated_data['refresh'] = str(refresh)
        validated_data['access'] = str(refresh.access_token)

        return validated_data


class DoctorDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorDetail
        fields = ['license_number', 'experience_years', 'consultation_fee', 'specialization', 'location']

class DoctorScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorSchedule
        fields = ['id', 'date', 'start_time', 'end_time']

class UserProfileSerializer(serializers.ModelSerializer):
    doctordetail = DoctorDetailSerializer(required=False)
    schedules = serializers.ListField(child=serializers.DictField(), required=False)
    booked_appointments = serializers.SerializerMethodField()
    already_booked = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'full_name', 'mobile_number', 'role', 'address', 'profile_image', 'created_at','doctordetail','schedules','booked_appointments','already_booked']
        read_only_fields = ['id', 'mobile_number', 'role', 'created_at']

    def get_booked_appointments(self, obj):
        """Return all appointments booked by this patient"""
        if obj.role != 'patient':
            return []
        appointments = AppointmentBooking.objects.filter(patient=obj).select_related('doctor', 'schedule')
        return AppointmentBookingSerializer(appointments, many=True).data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance') or (args[0] if args else None)

        # ✅ If user is NOT doctor → remove these fields from response
        if instance:
            if instance.role != 'doctor':
                self.fields.pop('doctordetail', None)
                self.fields.pop('schedules', None)
                self.fields.pop('already_booked', None)

            if instance.role != 'patient':
                self.fields.pop('booked_appointments', None)

    def get_already_booked(self, obj):
        """For doctors: show booked slots with patient info"""
        if obj.role != 'doctor':
            return []
        appointments = AppointmentBooking.objects.filter(doctor=obj).select_related('patient', 'schedule')
        return [
            {
                "appointment_id": app.id,
                "patient_name": app.patient.full_name,
                "schedule_id": app.schedule.id,
                "appointment_time": app.appointment_time.strftime("%H:%M"),
                "notes": app.notes,
                "status":app.status
            }
            for app in appointments
        ]

    def to_representation(self, instance):
        """✅ Convert schedules to readable format when retrieving"""
        data = super().to_representation(instance)
        if instance.role == 'doctor':
            schedules = DoctorSchedule.objects.filter(doctor=instance)
            data['schedules'] = DoctorScheduleSerializer(schedules, many=True).data
        # elif instance.role == 'patient':
        #     appointments = AppointmentBooking.objects.filter(patient=instance).select_related('doctor', 'schedule')
        #     data['booked_appointments'] = AppointmentBookingSerializer(appointments, many=True).data

        return data

    def update(self, instance, validated_data):
        # Extract and remove doctordetail data from validated_data
        doctor_data = validated_data.pop('doctordetail', None)
        schedules_data = validated_data.pop('schedules', None)

        # Update User fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Handle nested doctor update
        if instance.role == 'doctor' and doctor_data:
            doctor_detail, _ = DoctorDetail.objects.get_or_create(user=instance)
            # Update each field from doctor_data
            for attr, value in doctor_data.items():
                setattr(doctor_detail, attr, value)
            doctor_detail.save()

        if instance.role == 'doctor' and schedules_data:
            # Delete old schedules
            DoctorSchedule.objects.filter(doctor=instance).delete()

            # Create new schedules
            for schedule in schedules_data:
                DoctorSchedule.objects.create(
                    doctor=instance,
                    date=schedule.get('date'),
                    start_time=schedule.get('start_time'),
                    end_time=schedule.get('end_time')
                )

        return instance

class DoctorListSerializer(serializers.ModelSerializer):
    doctordetail = DoctorDetailSerializer(read_only=True)
    schedule = DoctorScheduleSerializer(source='doctorschedule_set', many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'full_name', 'mobile_number', 'role', 'address', 'profile_image', 'doctordetail','schedule']

class DoctorProfileSerializer(serializers.ModelSerializer):
    doctordetail = DoctorDetailSerializer(read_only=True)
    schedules = DoctorScheduleSerializer(source='doctorschedule_set', many=True, read_only=True)  # uses related_name='schedules'

    class Meta:
        model = User
        fields = ['id', 'full_name', 'mobile_number', 'role', 'address', 'profile_image', 'doctordetail', 'schedules']


class DoctorSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'full_name', 'mobile_number', 'password', 'role', 'address', 'profile_image']
        extra_kwargs = {
            'role': {'default': 'doctor'},
        }

    def validate_role(self, value):
        if value != 'doctor':
            raise serializers.ValidationError("Only doctor signup is allowed with this endpoint.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        # ✅ DoctorDetail will be automatically created via signal
        return user
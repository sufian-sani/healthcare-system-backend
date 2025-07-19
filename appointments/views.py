from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import AppointmentBooking
from .serializers import AppointmentBookingSerializer, AppointmentStatusUpdateSerializer, AvailableSlotsSerializer, DoctorScheduleSerializer
from users.models import DoctorSchedule
from .utils import generate_30_min_slots

# ✅ Book an appointment
class AppointmentBookingView(generics.CreateAPIView):
    queryset = AppointmentBooking.objects.all()
    serializer_class = AppointmentBookingSerializer
    permission_classes = [permissions.IsAuthenticated]


# ✅ Get available slots for a schedule
class AvailableSlotsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, doctor_id, schedule_id):
        try:
            schedule = DoctorSchedule.objects.get(id=schedule_id, doctor_id=doctor_id)
        except DoctorSchedule.DoesNotExist:
            return Response({"error": "Schedule not found"}, status=404)

        all_slots = generate_30_min_slots(schedule.start_time, schedule.end_time)
        booked_slots = AppointmentBooking.objects.filter(schedule=schedule).values_list('appointment_time', flat=True)
        free_slots = [slot.strftime("%H:%M") for slot in all_slots if slot not in booked_slots]

        return Response({
            "doctor_id": doctor_id,
            "schedule_id": schedule.id,
            "date": schedule.date,
            "available_slots": free_slots
        })


# ✅ List patient’s booked appointments
class MyAppointmentsView(generics.ListAPIView):
    serializer_class = AppointmentBookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return AppointmentBooking.objects.filter(patient=self.request.user)
    

class AppointmentStatusUpdateView(generics.UpdateAPIView):
    queryset = AppointmentBooking.objects.all()
    serializer_class = AppointmentStatusUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        appointment = super().get_object()
        if appointment.doctor != self.request.user:
            raise PermissionDenied("You are not allowed to update this appointment status.")
        return appointment
    
    

class DoctorScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = DoctorScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """✅ Doctors can only see their own schedules"""
        user = self.request.user
        if user.role == "doctor":
            return DoctorSchedule.objects.filter(doctor=user)
        return DoctorSchedule.objects.none()

    def perform_create(self, serializer):
        """✅ Automatically assign logged-in doctor"""
        user = self.request.user
        if user.role != "doctor":
            raise PermissionError("Only doctors can create schedules.")
        serializer.save(doctor=user)

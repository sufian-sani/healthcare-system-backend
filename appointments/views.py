from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import AppointmentBooking
from .serializers import AppointmentBookingSerializer, AvailableSlotsSerializer
from users.models import DoctorSchedule
from .utils import generate_30_min_slots
from rest_framework import status

# ✅ Book an appointment
class AppointmentBookingView(generics.CreateAPIView):
    queryset = AppointmentBooking.objects.all()
    serializer_class = AppointmentBookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("🔴 Field‑level errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # At this point all fields are OK and validate() will run
        print("🟢 Fields OK, now running validate()")
        return super().create(request, *args, **kwargs)


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

from rest_framework import generics, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count, Sum

from .permissions import IsAdminUserRole
from .serializers import AdminAppointmentSerializer, AdminDoctorSerializer, AppointmentCRUDSerializer
from appointments.models import AppointmentBooking
from users.models import User

# ✅ List & Search Appointments
class AdminAppointmentListView(generics.ListAPIView):
    queryset = AppointmentBooking.objects.all().select_related("doctor", "patient", "schedule")
    serializer_class = AdminAppointmentSerializer
    permission_classes = [IsAdminUserRole]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["doctor__full_name", "patient__full_name", "status"]
    ordering_fields = ["created_at", "appointment_time"]

# ✅ Update or Delete Appointment
class AdminAppointmentUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AppointmentBooking.objects.all()
    serializer_class = AdminAppointmentSerializer
    permission_classes = [IsAdminUserRole]

# ✅ List Doctors
class AdminDoctorListView(generics.ListAPIView):
    queryset = User.objects.filter(role="doctor").prefetch_related("doctorschedule_set", "doctordetail")
    serializer_class = AdminDoctorSerializer
    permission_classes = [IsAdminUserRole]

# ✅ Update Doctor
class AdminDoctorUpdateView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.filter(role="doctor")
    serializer_class = AdminDoctorSerializer
    permission_classes = [IsAdminUserRole]

# ✅ Reports (Appointments & Revenue)
class AdminReportView(APIView):
    permission_classes = [IsAdminUserRole]

    def get(self, request):
        doctor_appointments = (
            AppointmentBooking.objects.values("doctor__full_name")
            .annotate(total_appointments=Count("id"))
        )
        total_revenue = AppointmentBooking.objects.filter(status="completed").aggregate(
            total=Sum("doctor__doctordetail__consultation_fee")
        )
        return Response({
            "appointments_per_doctor": list(doctor_appointments),
            "total_revenue": total_revenue["total"] or 0
        })

class AdminAppointmentCRUDView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AppointmentBooking.objects.all()
    serializer_class = AppointmentCRUDSerializer
    permission_classes = [IsAdminUserRole]
from rest_framework import generics, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncMonth
from django.db.models import Count, Sum, Q, F, ExpressionWrapper, DecimalField

from .permissions import IsAdminUserRole
from .serializers import AdminAppointmentSerializer, AdminDoctorSerializer, AdminUserListSerializer, AdminUserStatusUpdateSerializer, AppointmentCRUDSerializer, DoctorStatusUpdateSerializer
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
        # ✅ Get query params (default: show all if not provided)
        month = request.GET.get("month")
        year = request.GET.get("year")

        queryset = AppointmentBooking.objects.all()

        # ✅ Apply filtering if month & year provided
        if month and year:
            queryset = queryset.filter(
                created_at__month=int(month),
                created_at__year=int(year)
            )

        # ✅ Ensure revenue calculated only for completed appointments
        # (Multiplying completed appointments by consultation_fee per booking)
        queryset = queryset.annotate(
            earned=ExpressionWrapper(
                F("doctor__doctordetail__consultation_fee"),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            )
        )

        monthly_report = (
            queryset.annotate(month=TruncMonth("created_at"))
            .values("month", "doctor__id", "doctor__full_name")
            .annotate(
                total_appointments=Count("id"),
                total_patient_visits=Count("patient", distinct=True),
                total_earned=Sum(
                    "earned",
                    filter=Q(status="completed")  # ✅ Count revenue only for completed appointments
                )
            )
            .order_by("month", "doctor__full_name")
        )

        report_data = [
            {
                "month": data["month"].strftime("%B %Y"),
                "doctor_id": data["doctor__id"],
                "doctor_name": data["doctor__full_name"],
                "total_patient_visits": data["total_patient_visits"],
                "total_appointments": data["total_appointments"],
                "total_earned": float(data["total_earned"] or 0)
            }
            for data in monthly_report
        ]

        return Response({"monthly_report": report_data})

class AdminAppointmentCRUDView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AppointmentBooking.objects.all()
    serializer_class = AppointmentCRUDSerializer
    permission_classes = [IsAdminUserRole]
    
    
class AdminDoctorStatusUpdateView(generics.UpdateAPIView):
    queryset = User.objects.filter(role='doctor')
    serializer_class = DoctorStatusUpdateSerializer
    permission_classes = [IsAdminUserRole]
    
    
class AdminUserListView(generics.ListAPIView):
    queryset = User.objects.all().order_by('-created_at')
    serializer_class = AdminUserListSerializer
    permission_classes = [IsAdminUserRole]
    
class AdminUserStatusUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = AdminUserStatusUpdateSerializer
    permission_classes = [IsAdminUserRole]
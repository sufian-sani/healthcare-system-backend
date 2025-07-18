from django.urls import path
from .views import (
    AdminAppointmentCRUDView, AdminAppointmentListView, AdminAppointmentUpdateDeleteView,
    AdminDoctorListView, AdminDoctorUpdateView,
    AdminReportView
)

urlpatterns = [
    path("appointments/", AdminAppointmentListView.as_view(), name="admin-appointments"),
    path("appointments/<int:pk>/", AdminAppointmentUpdateDeleteView.as_view(), name="admin-appointment-detail"),
    path("doctors/", AdminDoctorListView.as_view(), name="admin-doctors"),
    path("doctors/<int:pk>/", AdminDoctorUpdateView.as_view(), name="admin-doctor-update"),
    path("reports/", AdminReportView.as_view(), name="admin-reports"),
    path('admin/appointments/<int:pk>/', AdminAppointmentCRUDView.as_view(), name='admin-appointment-crud'),
]

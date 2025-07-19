from django.urls import path
from .views import AppointmentBookingView, AppointmentStatusUpdateView, AvailableSlotsView, DoctorScheduleViewSet, MyAppointmentsView

doctor_schedule_list = DoctorScheduleViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

doctor_schedule_detail = DoctorScheduleViewSet.as_view({
    'get': 'retrieve',
    'patch': 'partial_update',
    'delete': 'destroy'
})

urlpatterns = [
    path('book/', AppointmentBookingView.as_view(), name='book-appointment'),
    path('<int:doctor_id>/available-slots/<int:schedule_id>/', AvailableSlotsView.as_view(), name='available-slots'),
    path('my-appointments/', MyAppointmentsView.as_view(), name='my-appointments'),
    path("status/<int:pk>/", AppointmentStatusUpdateView.as_view(), name="appointment-status-update"),
    
    path('doctor/schedules/', doctor_schedule_list, name='doctor-schedule-list'),
    path('doctor/schedules/<int:pk>/', doctor_schedule_detail, name='doctor-schedule-detail'),
]

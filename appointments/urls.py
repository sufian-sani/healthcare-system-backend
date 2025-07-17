from django.urls import path
from .views import AppointmentBookingView, AppointmentStatusUpdateView, AvailableSlotsView, MyAppointmentsView

urlpatterns = [
    path('book/', AppointmentBookingView.as_view(), name='book-appointment'),
    path('<int:doctor_id>/available-slots/<int:schedule_id>/', AvailableSlotsView.as_view(), name='available-slots'),
    path('my-appointments/', MyAppointmentsView.as_view(), name='my-appointments'),
    path("status/<int:pk>/", AppointmentStatusUpdateView.as_view(), name="appointment-status-update"),
]

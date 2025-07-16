from django.urls import path
from .views import AppointmentBookingView, AvailableSlotsView, MyAppointmentsView

urlpatterns = [
    path('book/<int:doctor_id>/', AppointmentBookingView.as_view(), name='book-appointment'),
    path('<int:doctor_id>/available-slots/<int:schedule_id>/', AvailableSlotsView.as_view(), name='available-slots'),
    path('my-appointments/', MyAppointmentsView.as_view(), name='my-appointments'),
]

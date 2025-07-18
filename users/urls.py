from django.urls import path
from .views import DoctorListView, DoctorSignupView, RegisterView, UserProfileView, CustomTokenObtainPairView, DoctorDetailView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path("doctors/", DoctorListView.as_view(), name="doctor-list"),
    path('doctors/<int:pk>/', DoctorDetailView.as_view(), name='doctor-detail'),
    path("signup/doctor/", DoctorSignupView.as_view(), name="doctor-signup"),
]
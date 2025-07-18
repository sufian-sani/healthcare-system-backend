from rest_framework import generics, permissions
from rest_framework.permissions import AllowAny
from .serializers import DoctorListSerializer, DoctorProfileSerializer, DoctorSignupSerializer, RegisterSerializer, UserProfileSerializer
from .models import User
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer

# Create your views here.
# class RegisterView(generics.CreateAPIView):
#     queryset = User.objects.all()
#     permission_classes = [AllowAny]
#     serializer_class = RegisterSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.save()  # returns dict with tokens
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user  # 👈 always returns logged-in user
    

class DoctorListView(generics.ListAPIView):
    # queryset = User.objects.filter(role='doctor').select_related('doctordetail').prefetch_related('doctorschedule_set')
    serializer_class = DoctorListSerializer
    permission_classes = [permissions.AllowAny]  # anyone can view
    
    def get_queryset(self):
        queryset = User.objects.filter(role='doctor').select_related('doctordetail').prefetch_related('doctorschedule_set')

        specialization = self.request.query_params.get('specialization')
        location = self.request.query_params.get('location')
        available = self.request.query_params.get('available')

        if specialization:
            queryset = queryset.filter(doctordetail__specialization__icontains=specialization)
        if location:
            queryset = queryset.filter(doctordetail__location__icontains=location)
        if available == "true":
            queryset = queryset.filter(schedules__date__gte=now().date()).distinct()

        return queryset


class DoctorDetailView(generics.RetrieveAPIView):
    queryset = User.objects.filter(role='doctor').select_related('doctordetail').prefetch_related('doctorschedule_set')
    serializer_class = DoctorProfileSerializer
    permission_classes = [permissions.AllowAny]
    

class DoctorSignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = DoctorSignupSerializer
    permission_classes = [permissions.AllowAny]
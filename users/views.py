from rest_framework import generics, permissions
from rest_framework.permissions import AllowAny
from .serializers import DoctorListSerializer, RegisterSerializer, UserProfileSerializer
from .models import User
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

# Create your views here.
# class RegisterView(generics.CreateAPIView):
#     queryset = User.objects.all()
#     permission_classes = [AllowAny]
#     serializer_class = RegisterSerializer

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
    queryset = User.objects.filter(role='doctor').select_related('doctordetail').prefetch_related('doctorschedule_set')
    serializer_class = DoctorListSerializer
    permission_classes = [permissions.AllowAny]  # anyone can view
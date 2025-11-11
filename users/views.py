from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import authenticate
from .serializers import UserRegistrationSerializer
from .models import CustomUser


# ----------------------------------------------------
# 1. მომხმარებლის რეგისტრაცია (POST /api/register/)
# ----------------------------------------------------
class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # ავტომატური ავტორიზაცია (JWT ტოკენების გენერაცია)
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Registration successful. User created.',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_id': user.id,
                'username': user.username
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ----------------------------------------------------
# 2. მომხმარებლის ავტორიზაცია (POST /api/login/)
# ----------------------------------------------------
class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Login successful.',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_id': user.id,
                'username': user.username
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
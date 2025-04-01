from rest_framework import viewsets
from .models import SensorType, Sensor, SensorData
from .serializers import SensorTypeSerializer, SensorSerializer, SensorDataSerializer, RegisterUserSerializer
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf import settings

import logging
logger = logging.getLogger(__name__)

# Create your views here.
class SensorTypeViewSet(viewsets.ModelViewSet):
    queryset = SensorType.objects.all()
    serializer_class = SensorTypeSerializer
    permission_classes = [IsAuthenticated]

class SensorViewSet(viewsets.ModelViewSet):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer
    permission_classes = [IsAuthenticated]

class SensorDataViewSet(viewsets.ModelViewSet):
    queryset = SensorData.objects.all()
    serializer_class = SensorDataSerializer
    permission_classes = [IsAuthenticated]

class RegisterUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)

        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"Success": "Usuario registrado con éxito!"}, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f'Error registrando usuario: {e}')
                return Response({"Error": "No se pudo registrar el usuario"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            access_token = response.data.get('access')
            refresh_token = response.data.get('refresh')

            response.set_cookie(
                key=settings.SIMPLE_JWT['AUTH_COOKIE'],
                value=access_token,
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTPONLY'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                max_age=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds(),
            )

            response.set_cookie(
                key=settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
                value=refresh_token,
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTPONLY'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds(),
            )

            del response.data['access']
            del response.data['refresh']
            response.data['message'] = "Inicio de sesión exitoso!"
        
        return response

class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'])

        if not refresh_token:
            logger.warning("Intento de refrescar token sin cookie de refresh_token")
            return Response({"Error": "No se ha encontrado refresh token en las cookies"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            request.data['refresh'] = refresh_token
            response = super().post(request, *args, **kwargs)
        except Exception as e:
            logger.error(f'Error al refrescar token: {e}')
            return Response({"Error": "Token inválido o expirado"}, status=status.HTTP_401_UNAUTHORIZED)


        if response.status_code == 200:
            access_token = response.data.get('access')

            response.set_cookie(
                key=settings.SIMPLE_JWT['AUTH_COOKIE'],
                value=access_token,
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTPONLY'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                max_age=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds(),
            )

            del response.data['access']
            response.data['message'] = 'Token renovado'

        return response
    
class CustomLogoutView(APIView):
    def post(self, request):
        response = Response({"message": "Nos vemos!"}, status=status.HTTP_200_OK)

        response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE'])
        response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'])

        refresh_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'])

        if refresh_token:
            try:
                token =  RefreshToken(refresh_token)
                token.blacklist()
            except Exception as e:
                logger.error(f'Error al invalidar refresh_token: {e}')

        return response
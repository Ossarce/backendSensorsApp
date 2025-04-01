from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SensorTypeViewSet, SensorViewSet, SensorDataViewSet, RegisterUserView, CustomTokenObtainPairView,CustomTokenRefreshView, CustomLogoutView

router = DefaultRouter()
router.register(r'sensors/types', SensorTypeViewSet)
router.register(r'sensors', SensorViewSet)
router.register(r'sensors/data', SensorDataViewSet)

urlpatterns = [
    # Login JWT
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),

    # Logout JWT
    path('logout/', CustomLogoutView.as_view(), name='logout'),

    # Registro de usuarios
    path('register/', RegisterUserView.as_view(), name='register_user'),

    # Rutas router
    path('', include(router.urls))
]
from rest_framework import serializers
from .models import SensorType, Sensor, SensorData
from django.contrib.auth.models import User

class SensorTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorType
        fields = ['name']

class SensorSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    class Meta:
        model = Sensor
        fields = ['name', 'category', 'created_at', 'category_name']

class SensorDataSerializer(serializers.ModelSerializer):
    sensor_name = serializers.CharField(source='sensor.name', read_only=True)
    class Meta:
        model = SensorData
        fields = ['sensor', 'value', 'measured_at', 'sensor_name']

class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True) # La contraseña no se devuelve en response

    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name', 'email', 'is_superuser', 'is_staff', 'is_active']

    def validate(self, data):
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({"username": "Usuario ya registrado"})
        
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": "El correo ya está en uso"})
        
        return data
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            email=validated_data["email"]
        )
        user.is_superuser = validated_data.get("is_superuser", False)
        user.is_staff = validated_data.get("is_staff", True)
        user.is_active = validated_data.get("is_active", True)
        user.save()

        return user
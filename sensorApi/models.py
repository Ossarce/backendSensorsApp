from django.db import models

# Create your models here.
class SensorType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Sensor(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(SensorType, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class SensorData(models.Model):
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    value = models.CharField(max_length=100)
    measured_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sensor.name} - {self.value} at {self.measured_at}"
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.admin import site


class District(models.Model):
    location = models.CharField(max_length=255)


class User(AbstractUser):
    user_type = models.CharField(max_length=50)
    district = models.ForeignKey(District, on_delete=models.deletion.SET_NULL, null=True, blank=True)


class Clinic(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True)
    contact_info = models.CharField(max_length=255)
    services_offered = models.TextField()
    availability = models.BooleanField(default=True)
    capacity = models.IntegerField()


class Room(models.Model):
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)


class Appointment(models.Model):
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    date_time = models.IntegerField()
    status = models.CharField(max_length=50)


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


site.register(District)
site.register(User)
site.register(Clinic)
site.register(Room)
site.register(Notification)
site.register(Appointment)
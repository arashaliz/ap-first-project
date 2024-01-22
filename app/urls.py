from django.urls import path
from . import views

urlpatterns = [
    path('', views.clinic_dashboard, name='clinic_dashboard'),
    path('cancel-appointment/', views.cancel_appointment, name='cancel_appointment'),
    path('new-reservation/', views.new_reservation, name='new_reservation'),
    path('update-clinic-capacity', views.update_clinic_capacity, name='update_clinic_capacity'),
    path('available-times/<str:clinic_id>', views.available_times, name='available_times'),
    path('reserve-time/', views.reserve_time, name='reserve_time'),
]
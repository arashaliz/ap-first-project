from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
import requests
import json
from .models import Clinic, Appointment, User


@login_required
def clinic_dashboard(request):
    user = request.user

    if user.user_type == "DOCTOR":
        appointments = Appointment.objects.filter(room__user=user)
        return render(request, 'app/doctor_dashboard.html', context={'appointments': appointments})

    elif user.user_type == "ADMIN" or user.is_staff or user.is_superuser:

        api_url = 'http://127.0.0.1:5000/slots'
        response = requests.get(api_url)

        if response.status_code == 200:
            database = response.json()
        else:
            database = {}

        current_appointments = Appointment.objects.all()

        return render(request, 'app/admin_dashboard.html', {
            'current_appointments': current_appointments,
            'database': database,
        })

    else:
        future_appointments = Appointment.objects.filter(user=user)
        context = {
            'future_appointments': future_appointments,
        }
        return render(request, 'app/receptionist_dashboard.html', context=context)


@login_required
def update_clinic_capacity(request):
    if request.method == 'POST':
        clinic_id = request.POST.get('clinic_id', '')
        new_capacity = request.POST.get('new_capacity', '')
        response = requests.get('http://127.0.0.1:5000/slots')
        x = int(response.json()[clinic_id]) - int(new_capacity)
        print(x)
        api_url = 'http://127.0.0.1:5000/reserve'
        payload = {'id': clinic_id, 'reserved': x}

        response = requests.post(api_url, json=payload)

        if response.status_code == 200 and response.json().get('success'):
            return JsonResponse({'success': True, 'message': 'Clinic capacity updated successfully'})
        else:
            return JsonResponse({'success': False, 'message': 'Failed to update clinic capacity. Please try again.'},
                                status=400)

    return HttpResponseBadRequest("Invalid request method")


@login_required
def cancel_appointment(request):
    if request.method == 'POST':
        appointment_id = request.POST.get('appointment_id', '')

        try:
            appointment = Appointment.objects.get(id=appointment_id)
            clinic = appointment.clinic

            api_url = 'http://127.0.0.1:5000/reserve'
            payload = {'id': str(clinic.id), 'released': -1}

            response = requests.post(api_url, json=payload)

            if response.status_code == 200 and response.json().get('success'):
                appointment.delete()
                return JsonResponse({'success': True, 'message': 'Appointment canceled successfully'})
            else:
                return JsonResponse({'success': False, 'message': 'Failed to cancel appointment. Please try again.'},
                                    status=400)

        except Appointment.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Appointment not found'}, status=404)

    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)


def new_reservation(request):
    clinics = Clinic.objects.all()
    doctors = User.objects.filter(user_type="DOCTOR")

    search_query = request.GET.get('q', '')
    if search_query:
        clinics = clinics.filter(name__icontains=search_query)
        doctors = doctors.filter(user__username__icontains=search_query)

    return render(request, 'app/new_reservation.html', {'clinics': clinics,
                                                        'doctors': doctors,
                                                        'search_query': search_query})


@login_required
def available_times(request, clinic_id):
    api_url_slots = 'http://127.0.0.1:5000/slots'
    response_slots = requests.get(api_url_slots)

    if response_slots.status_code == 200:
        all_slots = response_slots.json()
        clinic_slots = all_slots.get(clinic_id, [])
    else:
        clinic_slots = []
    if isinstance(clinic_slots, int):
        clinic_slots = range(clinic_slots+1)
    return render(request, 'app/available_times.html', {'available_times': clinic_slots,
                                                        'clinic_id': clinic_id})


@login_required
def reserve_time(request):
    if request.method == 'POST':
        try:
            selected_time = request.POST.get('time', '')
            clinic_id = request.POST.get('clinic_id', '')
        except:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data'}, status=400)

        user = request.user

        existing_appointment = Appointment.objects.filter(user=user, date_time=selected_time).first()
        if existing_appointment:
            return JsonResponse({'success': False, 'message': 'You already have an appointment at this time.'},
                                status=400)

        api_url = 'http://127.0.0.1:5000/reserve'
        payload = {'id': str(clinic_id), 'reserved': 1}

        response = requests.post(api_url, json=payload)

        if response.status_code == 200 and response.json().get('success'):

            new_appointment = Appointment(user=user, clinic_id=clinic_id, date_time=selected_time, status='Reserved')
            new_appointment.save()

            return JsonResponse({'success': True, 'message': 'Reservation successful'})
        else:
            return JsonResponse({'success': False, 'message': 'Reservation failed. Please try again.'}, status=400)

    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)

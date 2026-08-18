from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from .forms import AppointmentForm, RegistrationForm
from .models import Appointment, Business, Service

def home(request):
    return render(request, "booking/home.html", {"business": Business.objects.first(), "services": Service.objects.filter(active=True)})

def register(request):
    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save(); login(request, user); messages.success(request, "Welcome to Fresh Fade Barbershop!"); return redirect("book")
    return render(request, "registration/register.html", {"form": form})

@login_required
def book(request):
    form = AppointmentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            appointment = Appointment(customer=request.user, staff=form.cleaned_data["staff"], service=form.cleaned_data["service"], date=form.cleaned_data["date"], start_time=form.cleaned_data["start_time"], end_time=form.cleaned_data["end_time"])
            try: appointment.full_clean(); appointment.save()
            except Exception:
                form.add_error(None, "That time was just taken. Please choose another slot.")
            else:
                messages.success(request, "Your appointment is confirmed. We look forward to seeing you!"); return redirect("my_appointments")
    return render(request, "booking/book.html", {"form": form})

@login_required
def my_appointments(request):
    appointments = request.user.appointments.exclude(status=Appointment.Status.CANCELLED)
    return render(request, "booking/my_appointments.html", {"appointments": appointments})

@login_required
def cancel_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk, customer=request.user)
    if request.method == "POST" and appointment.status in (Appointment.Status.PENDING, Appointment.Status.CONFIRMED):
        appointment.status = Appointment.Status.CANCELLED; appointment.save(update_fields=["status"]); messages.success(request, "Your appointment has been cancelled.")
    return redirect("my_appointments")

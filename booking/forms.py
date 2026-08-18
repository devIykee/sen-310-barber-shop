from datetime import datetime, timedelta
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Appointment, Customer, Service, Staff

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=30, required=False)
    class Meta:
        model = User
        fields = ("username", "email", "phone", "password1", "password2")
    def save(self, commit=True):
        user = super().save(commit=False); user.email = self.cleaned_data["email"]
        if commit:
            user.save(); Customer.objects.create(user=user, phone=self.cleaned_data["phone"])
        return user

class AppointmentForm(forms.Form):
    service = forms.ModelChoiceField(queryset=Service.objects.filter(active=True))
    staff = forms.ModelChoiceField(queryset=Staff.objects.filter(active=True))
    date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    start_time = forms.TimeField(widget=forms.TimeInput(attrs={"type": "time"}))
    def clean(self):
        data = super().clean()
        service, staff, date, start = data.get("service"), data.get("staff"), data.get("date"), data.get("start_time")
        if service and staff and not staff.services.filter(pk=service.pk).exists(): self.add_error("staff", "This barber does not provide that service.")
        if service and date and start:
            end = (datetime.combine(date, start) + timedelta(minutes=service.duration_minutes)).time()
            candidate = Appointment(staff=staff, service=service, date=date, start_time=start, end_time=end)
            try: candidate.full_clean()
            except forms.ValidationError as exc: self.add_error(None, exc)
            data["end_time"] = end
        return data

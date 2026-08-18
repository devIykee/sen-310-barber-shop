from datetime import datetime
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Business(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=255)
    working_hours = models.CharField(max_length=255, help_text="Example: Mon–Sat, 9:00–18:00")
    contact_info = models.CharField(max_length=255)
    def __str__(self): return self.name


class Service(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="services")
    name = models.CharField(max_length=100)
    duration_minutes = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    active = models.BooleanField(default=True)
    def __str__(self): return self.name


class Staff(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="staff_members")
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100, default="Barber")
    services = models.ManyToManyField(Service, related_name="staff_members")
    active = models.BooleanField(default=True)
    def __str__(self): return self.name


class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="customer_profile")
    phone = models.CharField(max_length=30, blank=True)
    def __str__(self): return self.user.get_full_name() or self.user.username


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"
        COMPLETED = "completed", "Completed"
        BLOCKED = "blocked", "Blocked"
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="appointments")
    staff = models.ForeignKey(Staff, on_delete=models.PROTECT, related_name="appointments")
    service = models.ForeignKey(Service, null=True, blank=True, on_delete=models.PROTECT, related_name="appointments")
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.CONFIRMED)
    notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date", "start_time"]

    def __str__(self): return f"{self.staff} — {self.date} {self.start_time}"

    @property
    def starts_at(self):
        return timezone.make_aware(datetime.combine(self.date, self.start_time))

    def is_conflicting(self):
        return Appointment.objects.filter(staff=self.staff, date=self.date).exclude(pk=self.pk).exclude(status=Appointment.Status.CANCELLED).filter(start_time__lt=self.end_time, end_time__gt=self.start_time).exists()

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError("End time must be after the start time.")
        if self.date and self.starts_at < timezone.now():
            raise ValidationError("Appointments cannot be booked in the past.")
        if self.staff_id and self.service_id and not self.staff.services.filter(pk=self.service_id).exists():
            raise ValidationError("This barber does not offer the selected service.")
        if self.staff_id and self.is_conflicting():
            raise ValidationError("This barber is unavailable during that time.")

from datetime import date, time, timedelta
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from booking.models import Appointment, Business, Service, Staff

class AppointmentValidationTests(TestCase):
    def setUp(self):
        business = Business.objects.create(name="Fresh Fade", address="1 Main St", working_hours="09:00–18:00", contact_info="0800")
        self.service = Service.objects.create(business=business, name="Haircut", duration_minutes=30, price=5000)
        self.staff = Staff.objects.create(business=business, name="Tunde")
        self.staff.services.add(self.service)
        self.user = User.objects.create_user("customer", password="password123")
        self.future_date = timezone.localdate() + timedelta(days=1)

    def test_overlapping_appointments_are_rejected(self):
        Appointment.objects.create(customer=self.user, staff=self.staff, service=self.service, date=self.future_date, start_time=time(10), end_time=time(10, 30))
        duplicate = Appointment(customer=self.user, staff=self.staff, service=self.service, date=self.future_date, start_time=time(10, 15), end_time=time(10, 45))
        with self.assertRaises(ValidationError): duplicate.full_clean()

    def test_past_appointment_is_rejected(self):
        past = Appointment(customer=self.user, staff=self.staff, service=self.service, date=timezone.localdate() - timedelta(days=1), start_time=time(10), end_time=time(10, 30))
        with self.assertRaises(ValidationError): past.full_clean()

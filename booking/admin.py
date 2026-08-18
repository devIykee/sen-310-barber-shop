from django.contrib import admin
from .models import Appointment, Business, Customer, Service, Staff

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("staff", "customer", "service", "date", "start_time", "status")
    list_filter = ("status", "date", "staff")
    search_fields = ("customer__username", "staff__name")
    actions = ("mark_complete",)
    @admin.action(description="Mark selected appointments complete")
    def mark_complete(self, request, queryset): queryset.update(status=Appointment.Status.COMPLETED)

admin.site.register([Business, Service, Staff, Customer])

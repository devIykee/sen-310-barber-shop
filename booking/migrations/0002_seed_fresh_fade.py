from django.db import migrations

def seed(apps, schema_editor):
    Business = apps.get_model("booking", "Business")
    Service = apps.get_model("booking", "Service")
    Staff = apps.get_model("booking", "Staff")
    business, _ = Business.objects.get_or_create(name="Fresh Fade Barbershop", defaults={"description": "Precision cuts and classic grooming in a relaxed neighbourhood barbershop.", "address": "15 Admiralty Way, Lekki, Lagos", "working_hours": "Monday–Saturday, 09:00–18:00", "contact_info": "0800 FRESHFADE"})
    haircut, _ = Service.objects.get_or_create(business=business, name="Classic Haircut", defaults={"duration_minutes": 30, "price": 5000})
    beard, _ = Service.objects.get_or_create(business=business, name="Haircut and Beard Trim", defaults={"duration_minutes": 45, "price": 7500})
    barber, _ = Staff.objects.get_or_create(business=business, name="Tunde Adeyemi", defaults={"role": "Senior Barber"})
    barber.services.add(haircut, beard)

def unseed(apps, schema_editor):
    apps.get_model("booking", "Business").objects.filter(name="Fresh Fade Barbershop").delete()

class Migration(migrations.Migration):
    dependencies = [("booking", "0001_initial")]
    operations = [migrations.RunPython(seed, unseed)]

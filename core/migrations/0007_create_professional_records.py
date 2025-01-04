from django.db import migrations

def create_professional_records(apps, schema_editor):
    User = apps.get_model('core', 'User')
    Business = apps.get_model('core', 'Business')
    ShelterClinic = apps.get_model('core', 'ShelterClinic')
    PetSitterGroomer = apps.get_model('core', 'PetSitterGroomer')
    Shop = apps.get_model('core', 'Shop')
    
    # Create shelter/clinic records
    shelter_users = User.objects.filter(
        account_type='professional',
        professional_type='shelter'
    )
    
    for user in shelter_users:
        business = Business.objects.filter(user=user).first()
        if business:
            ShelterClinic.objects.get_or_create(
                business=business,
                defaults={
                    'phone': user.phone or '',
                    'email': user.email or '',
                }
            )
    
    # Create groomer records
    groomer_users = User.objects.filter(
        account_type='professional',
        professional_type='business',
        business_type='groomer'
    )
    
    for user in groomer_users:
        business = Business.objects.filter(user=user).first()
        if business:
            PetSitterGroomer.objects.get_or_create(
                business=business,
                defaults={
                    'contact': user.phone or '',
                    'experience': 0,
                    'rating': 0.0
                }
            )
    
    # Create shop records
    shop_users = User.objects.filter(
        account_type='professional',
        professional_type='business',
        business_type='shop'
    )
    
    for user in shop_users:
        business = Business.objects.filter(user=user).first()
        if business:
            Shop.objects.get_or_create(
                business=business,
                defaults={
                    'product_name': f"{business.name}'s Products",
                    'quantity': 0,
                    'status': 'active',
                    'rating': 0.0  # Added default rating
                }
            )

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0006_alter_business_created_at'),
    ]

    operations = [
        migrations.RunPython(create_professional_records),
    ]
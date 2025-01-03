from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import *
from django.utils import timezone
import random
from decimal import Decimal

class Command(BaseCommand):
    help = 'Creates sample data for PAW SOCIAL'

    def handle(self, *args, **options):
        User = get_user_model()

        # Create Regular Users
        if not User.objects.filter(username='regular_user').exists():
            regular_user = User.objects.create_user(
                username='regular_user',
                email='regular@example.com',
                password='password123',
                account_type='regular'
            )
            self.stdout.write(self.style.SUCCESS('Created regular user'))

        # Create Professional User
        if not User.objects.filter(username='business_user').exists():
            business_user = User.objects.create_user(
                username='business_user',
                email='business@example.com',
                password='password123',
                account_type='professional'
            )
            self.stdout.write(self.style.SUCCESS('Created business user'))

        # Create Pets
        pet_names = ['Max', 'Luna', 'Charlie', 'Bella', 'Rocky']
        species = ['dog', 'cat', 'bird']
        breeds = ['Labrador', 'Persian', 'Parrot', 'Siamese', 'German Shepherd']
        
        for name in pet_names:
            if not Pet.objects.filter(name=name).exists():
                Pet.objects.create(
                    name=name,
                    species=random.choice(species),
                    breed=random.choice(breeds),
                    age=random.randint(1, 10),
                    owner=User.objects.get(username='regular_user'),
                    is_stray=random.choice([True, False])
                )
        self.stdout.write(self.style.SUCCESS('Created sample pets'))

        # Create Business
        business = Business.objects.create(
            user=User.objects.get(username='business_user'),
            name='Pet Paradise',
            rating=4.5
        )
        
        # Create Shelter/Clinic
        ShelterClinic.objects.create(
            business=business,
            phone='123-456-7890',
            email='shelter@example.com',
            review='Great service and caring staff'
        )

        # Create Events
        event_titles = ['Pet Adoption Day', 'Dog Training Workshop', 'Cat Show', 'Vet Camp']
        for title in event_titles:
            if not Event.objects.filter(title=title).exists():
                Event.objects.create(
                    title=title,
                    date=timezone.now() + timezone.timedelta(days=random.randint(1, 30)),
                    location='123 Pet Street',
                    details='Join us for this amazing event!',
                    organizer=User.objects.get(username='business_user')
                )
        self.stdout.write(self.style.SUCCESS('Created sample events'))

        # Create Fundraisers
        pets = Pet.objects.all()
        for i in range(3):
            Fundraiser.objects.create(
                title=f'Help {pets[i].name}',
                target_amount=Decimal(random.randint(1000, 5000)),
                collected_amount=Decimal(random.randint(100, 1000)),
                applicant_name='John Doe',
                created_by=User.objects.get(username='regular_user'),
                beneficiary=pets[i]
            )
        self.stdout.write(self.style.SUCCESS('Created sample fundraisers'))

        # Create Shop and Marketplace Items
        shop = Shop.objects.create(
            business=business,
            product_name='Pet Supplies',
            quantity=100,
            status='active',
            rating=4.5
        )

        products = [
            ('Premium Dog Food', 'High-quality dog food for all breeds', 49.99),
            ('Cat Tree', 'Multi-level cat tree with scratching posts', 89.99),
            ('Bird Cage', 'Spacious bird cage with accessories', 129.99),
            ('Pet Bed', 'Comfortable bed for cats and dogs', 39.99),
            ('Grooming Kit', 'Complete pet grooming set', 59.99)
        ]

        for name, desc, price in products:
            Marketplace.objects.create(
                product_name=name,
                description=desc,
                price=Decimal(price),
                status='available',
                seller=shop
            )
        self.stdout.write(self.style.SUCCESS('Created sample marketplace items'))

        self.stdout.write(self.style.SUCCESS('Successfully created all sample data'))
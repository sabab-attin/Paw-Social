from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import json

class User(AbstractUser):
    USER_TYPES = (
        ('regular', 'Regular User'),
        ('professional', 'Professional User'),
    )
    PROFESSIONAL_TYPES = (
        ('vet', 'Veterinarian'),
        ('shelter', 'Shelter/Clinic'),
        ('business', 'Business'),
    )
    BUSINESS_TYPES = (
        ('shop', 'Pet Shop'),
        ('groomer', 'Pet Groomer/Sitter'),
    )
    
    account_type = models.CharField(max_length=20, choices=USER_TYPES, default='regular')
    professional_type = models.CharField(max_length=20, choices=PROFESSIONAL_TYPES, null=True, blank=True)
    business_type = models.CharField(max_length=20, choices=BUSINESS_TYPES, null=True, blank=True)
    followers_count = models.IntegerField(default=0)
    following_count = models.IntegerField(default=0)
    phone = models.CharField(max_length=15, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    zip_code = models.CharField(max_length=10, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following', blank=True)
    follower_names = models.TextField(blank=True, default='')
    following_names = models.TextField(blank=True, default='')

    def update_follower_names(self):
        self.follower_names = ', '.join([user.username for user in self.followers.all()])
        self.following_names = ', '.join([user.username for user in self.following.all()])
        self.save()
        
    def get_profile_picture(self):
        if self.profile_picture:
            return self.profile_picture.url
        return '/static/core/images/default_profile.png'
    

class Pet(models.Model):
    # Species choices
    SPECIES_CHOICES = (
        ('dog', 'Dog'),
        ('cat', 'Cat'),
        ('bird', 'Bird'),
        ('other', 'Other'),
    )

    # Adoption status choices
    STATUS_CHOICES = (
        ('not_for_adoption', 'Not For Adoption'),
        ('available', 'Available for Adoption'),
        ('adopted', 'Adopted')
    )

    # Basic pet information
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=20, choices=SPECIES_CHOICES)
    breed = models.CharField(max_length=100)
    age = models.IntegerField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pets')
    is_stray = models.BooleanField(default=False)
    pet_picture = models.ImageField(upload_to='pet_pics/', blank=True, null=True)

    # Adoption related fields
    adoption_status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='not_for_adoption'
    )
    adopted_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='adopted_pets'
    )
    adoption_date = models.DateTimeField(null=True, blank=True)
    
    # Health and medical information
    medical_history = models.TextField(blank=True, default='')
    vaccinated = models.BooleanField(default=False)
    last_checkup = models.DateField(null=True, blank=True)
    
    # Additional details
    description = models.TextField(blank=True, default='')
    special_needs = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_pet_picture(self):
        if self.pet_picture:
            return self.pet_picture.url
        return '/static/core/images/default_pet.png'

    def mark_as_adopted(self, adopted_by_user):
        self.adoption_status = 'adopted'
        self.adopted_by = adopted_by_user
        self.adoption_date = timezone.now()
        self.save()

    def make_available_for_adoption(self):
        self.adoption_status = 'available'
        self.adopted_by = None
        self.adoption_date = None
        self.save()

    def toggle_adoption_status(self):
        if self.adoption_status == 'not_for_adoption':
            self.adoption_status = 'available'
        elif self.adoption_status == 'available':
            self.adoption_status = 'not_for_adoption'
        self.save()

    def cancel_adoption(self):
        self.adoption_status = 'not_for_adoption'
        self.adopted_by = None
        self.adoption_date = None
        self.save()

    def is_available_for_adoption(self):
        return self.adoption_status == 'available'

    def is_adopted(self):
        return self.adoption_status == 'adopted'

    def __str__(self):
        return f"{self.name} ({self.get_species_display()})"

    class Meta:
        ordering = ['-created_at']



class Business(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    rating = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    logo = models.ImageField(upload_to='business_logos/', blank=True, null=True)

    def get_logo(self):
        if self.logo:
            return self.logo.url
        return '/static/core/images/default_business.png'

class ShelterClinic(models.Model):
    business = models.OneToOneField(Business, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    review = models.TextField(blank=True)
    facility_images = models.ManyToManyField('Image', blank=True, related_name='shelter_images')

class PetSitterGroomer(models.Model):
    business = models.OneToOneField(Business, on_delete=models.CASCADE)
    experience = models.IntegerField()  # in years
    contact = models.CharField(max_length=100)
    rating = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    certificate_image = models.ImageField(upload_to='certificates/', blank=True, null=True)

class Shop(models.Model):
    business = models.OneToOneField(Business, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    status = models.CharField(max_length=20)
    rating = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    shop_image = models.ImageField(upload_to='shop_images/', blank=True, null=True)

class Marketplace(models.Model):
    product_name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='marketplace_listings')
    created_at = models.DateTimeField(auto_now_add=True, null=True)  # Added null=True
    product_images = models.ManyToManyField('Image', blank=True, related_name='product_images')
    quantity = models.PositiveIntegerField(default=1)
    def __str__(self):
        return self.product_name
    
class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled')
    )
    
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    product = models.ForeignKey(Marketplace, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    contact_number = models.CharField(max_length=15)
    delivery_address = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)


class Event(models.Model):
    CATEGORY_CHOICES = (
        ('adoption', 'Adoption Events'),
        ('training', 'Training Workshops'),
        ('show', 'Pet Shows'),
        ('vet', 'Vet Camps'),
        ('social', 'Social Meetups'),
    )
    
    title = models.CharField(max_length=200)
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    details = models.TextField()
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
    participants = models.ManyToManyField(User, related_name='participated_events')
    participant_names = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='social')

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update participant names after save
        self.participant_names = ', '.join([user.username for user in self.participants.all()])
        super().save(*args, **kwargs)


class Fundraiser(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    collected_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    applicant_name = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    beneficiary = models.ForeignKey(Pet, on_delete=models.CASCADE)
    shelter = models.ForeignKey(ShelterClinic, null=True, blank=True, on_delete=models.SET_NULL)
    campaign_image = models.ImageField(upload_to='fundraiser_images/', blank=True, null=True)
    donation_history = models.TextField(default='{}', blank=True)

    def save(self, *args, **kwargs):
        if self.target_amount is None:
            self.target_amount = 0
        if self.collected_amount is None:
            self.collected_amount = 0
        super().save(*args, **kwargs)

    def get_progress_percentage(self):
        try:
            if float(self.target_amount) > 0:
                return (float(self.collected_amount) / float(self.target_amount)) * 100
            return 0
        except (ValueError, TypeError, ZeroDivisionError):
            return 0


class Image(models.Model):
    image = models.ImageField(upload_to='images/')
    caption = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def get_url(self):
        return self.image.url if self.image else ''
    

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    dislikes = models.ManyToManyField(User, related_name='disliked_posts', blank=True)

    class Meta:
        ordering = ['-created_at']

class Service(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='services')
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    class Meta:
        ordering = ['-created_at']

        
class ProfessionalProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=200, blank=True, default='')
    average_rating = models.FloatField(default=0.0)
    total_ratings = models.IntegerField(default=0)
    
    # Fields for different professional types
    specialties = models.CharField(max_length=200, blank=True, default='')  # For both vets and groomers
    schedule = models.TextField(blank=True, default='')  # For both vets and groomers
    facilities = models.TextField(blank=True, default='')  # For shelters
    services = models.TextField(blank=True, default='')  # For groomers
    business_hours = models.TextField(blank=True, default='')  # For shops

    def __str__(self):
        return f"{self.user.username}'s Professional Profile"

class Review(models.Model):
    reviewer = models.ForeignKey(User, related_name='given_reviews', on_delete=models.CASCADE)
    professional = models.ForeignKey(User, related_name='received_reviews', on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review_text = models.TextField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['reviewer', 'professional']

class AdoptionRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    )
    
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='adoption_requests')
    requestor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='adoption_requests_made')
    contact_number = models.CharField(max_length=15)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Adoption request for {self.pet.name} by {self.requestor.username}"

    class Meta:
        ordering = ['-created_at']

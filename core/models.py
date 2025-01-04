from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import json
from decimal import Decimal


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
    
# CREATE TABLE user (
    #   id BIGINT AUTO_INCREMENT PRIMARY KEY,
    #   username VARCHAR(150) UNIQUE NOT NULL,
    #   password VARCHAR(128) NOT NULL,
    #   first_name VARCHAR(150),
    #   last_name VARCHAR(150),
    #   email VARCHAR(254) UNIQUE,
    #   is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    #   is_active BOOLEAN NOT NULL DEFAULT TRUE,
    #   date_joined DATETIME NOT NULL,
    #   account_type VARCHAR(20) DEFAULT 'regular',
    #   professional_type VARCHAR(20),
    #   business_type VARCHAR(20),
    #   followers_count INT DEFAULT 0,
    #   following_count INT DEFAULT 0,
    #   phone VARCHAR(15),
    #   address VARCHAR(255),
    #   city VARCHAR(100),
    #   zip_code VARCHAR(10),
    #   profile_picture VARCHAR(255),
    #   follower_names TEXT,
    #   following_names TEXT
    # );
    #
# CREATE TABLE user_followers (
    #   id BIGINT AUTO_INCREMENT PRIMARY KEY,
    #   from_user_id BIGINT NOT NULL,
    #   to_user_id BIGINT NOT NULL,
    #   FOREIGN KEY (from_user_id) REFERENCES user(id),
    #   FOREIGN KEY (to_user_id) REFERENCES user(id),
    #   UNIQUE KEY unique_followers (from_user_id, to_user_id)
    # );


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


# CREATE TABLE pet (
    #   id INT AUTO_INCREMENT PRIMARY KEY,
    #   name VARCHAR(100) NOT NULL,
    #   species VARCHAR(20) NOT NULL,
    #   breed VARCHAR(100) NOT NULL,
    #   age INT NOT NULL,
    #   owner_id BIGINT NOT NULL,
    #   is_stray BOOLEAN DEFAULT FALSE,
    #   pet_picture VARCHAR(255),
    #   adoption_status VARCHAR(20) DEFAULT 'not_for_adoption',
    #   adopted_by_id BIGINT,
    #   adoption_date DATETIME,
    #   medical_history TEXT,
    #   vaccinated BOOLEAN DEFAULT FALSE,
    #   last_checkup DATE,
    #   description TEXT,
    #   special_needs TEXT,
    #   created_at DATETIME NOT NULL,
    #   updated_at DATETIME NOT NULL,
    #   FOREIGN KEY (owner_id) REFERENCES user(id),
    #   FOREIGN KEY (adopted_by_id) REFERENCES user(id)
    # );


class Business(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    professional_type = models.CharField(max_length=20, choices=User.PROFESSIONAL_TYPES, null=True, blank=True)
    business_type = models.CharField(max_length=20, choices=User.BUSINESS_TYPES, null=True, blank=True)
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    zip_code = models.CharField(max_length=10, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    rating = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(5)], default=0)
    logo = models.ImageField(upload_to='business_logos/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now) 
    updated_at = models.DateTimeField(auto_now=True)

    def get_logo(self):
        if self.logo:
            return self.logo.url
        return '/static/core/images/default_business.png'
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"

# CREATE TABLE business (
    #   id BIGINT AUTO_INCREMENT PRIMARY KEY,
    #   user_id BIGINT NOT NULL UNIQUE,
    #   name VARCHAR(100) NOT NULL,
    #   professional_type VARCHAR(20),
    #   business_type VARCHAR(20),
    #   contact_number VARCHAR(15),
    #   email VARCHAR(254),
    #   address VARCHAR(255),
    #   city VARCHAR(100),
    #   zip_code VARCHAR(10),
    #   description TEXT,
    #   rating FLOAT DEFAULT 0 CHECK (rating >= 0 AND rating <= 5),
    #   logo VARCHAR(255),
    #   created_at DATETIME NOT NULL,
    #   updated_at DATETIME NOT NULL,
    #   FOREIGN KEY (user_id) REFERENCES user(id)
    # );

class ShelterClinic(models.Model):
    business = models.OneToOneField(Business, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    facilities = models.TextField(blank=True, default='')
    capacity = models.IntegerField(default=0)
    emergency_service = models.BooleanField(default=False)
    working_hours = models.TextField(blank=True, default='Monday-Friday: 9 AM - 5 PM')
    review = models.TextField(blank=True)
    facility_images = models.ManyToManyField('Image', blank=True, related_name='shelter_images')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.business.name}'s Shelter/Clinic"

# CREATE TABLE shelter_clinic (
    #   id BIGINT AUTO_INCREMENT PRIMARY KEY,
    #   business_id BIGINT NOT NULL UNIQUE,
    #   phone VARCHAR(15) NOT NULL,
    #   email VARCHAR(254) NOT NULL,
    #   facilities TEXT,
    #   capacity INT DEFAULT 0,
    #   emergency_service BOOLEAN DEFAULT FALSE,
    #   working_hours TEXT DEFAULT 'Monday-Friday: 9 AM - 5 PM',
    #   review TEXT,
    #   updated_at DATETIME NOT NULL,
    #   FOREIGN KEY (business_id) REFERENCES business(id)
    # );
    #
    # CREATE TABLE shelter_facility_images (
    #   id BIGINT AUTO_INCREMENT PRIMARY KEY,
    #   shelter_id BIGINT NOT NULL,
    #   image_id BIGINT NOT NULL,
    #   FOREIGN KEY (shelter_id) REFERENCES shelter_clinic(id),
    #   FOREIGN KEY (image_id) REFERENCES image(id)
    # );    

class PetSitterGroomer(models.Model):
    business = models.OneToOneField(Business, on_delete=models.CASCADE)
    experience = models.IntegerField(default=0)  # in years
    service_types = models.TextField(blank=True, default='')
    service_area = models.CharField(max_length=255, blank=True)
    availability = models.TextField(blank=True, default='Monday-Friday: 9 AM - 5 PM')
    contact = models.CharField(max_length=100)
    rating = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(5)], default=0)
    house_calls = models.BooleanField(default=False)
    certificate_image = models.ImageField(upload_to='certificates/', blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.business.name}'s Pet Services"


# CREATE TABLE pet_sitter_groomer (
    #   id BIGINT AUTO_INCREMENT PRIMARY KEY,
    #   business_id BIGINT NOT NULL UNIQUE,
    #   experience INT DEFAULT 0,
    #   service_types TEXT DEFAULT '',
    #   service_area VARCHAR(255) DEFAULT '',
    #   availability TEXT DEFAULT 'Monday-Friday: 9 AM - 5 PM',
    #   contact VARCHAR(100) NOT NULL,
    #   rating FLOAT DEFAULT 0 CHECK (rating >= 0 AND rating <= 5),
    #   house_calls BOOLEAN DEFAULT FALSE,
    #   certificate_image VARCHAR(255),
    #   updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    #   FOREIGN KEY (business_id) REFERENCES business(id) ON DELETE CASCADE
    # );


class Shop(models.Model):
    business = models.OneToOneField(Business, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=100, default='Shop Products')
    quantity = models.IntegerField(default=0)
    status = models.CharField(max_length=20, default='active')
    rating = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        default=0.0,  
    )
    business_hours = models.TextField(blank=True, null=True, default="Monday-Friday: 9 AM - 5 PM")
    contact_info = models.CharField(max_length=100, blank=True, null=True)
    shop_image = models.ImageField(upload_to='shop_images/', blank=True, null=True)

    def __str__(self):
        return f"{self.business.name}'s Shop"
    

# CREATE TABLE shop (
    #   id BIGINT AUTO_INCREMENT PRIMARY KEY,
    #   business_id BIGINT NOT NULL UNIQUE,
    #   product_name VARCHAR(100) DEFAULT 'Shop Products',
    #   quantity INT DEFAULT 0,
    #   status VARCHAR(20) DEFAULT 'active',
    #   rating FLOAT DEFAULT 0.0 CHECK (rating >= 0 AND rating <= 5),
    #   business_hours TEXT DEFAULT 'Monday-Friday: 9 AM - 5 PM',
    #   contact_info VARCHAR(100),
    #   shop_image VARCHAR(255),
    #   FOREIGN KEY (business_id) REFERENCES business(id) ON DELETE CASCADE
    # );


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


# CREATE TABLE marketplace (
    #   id BIGINT AUTO_INCREMENT PRIMARY KEY,
    #   product_name VARCHAR(100) NOT NULL,
    #   description TEXT NOT NULL,
    #   price DECIMAL(10,2) NOT NULL,
    #   status VARCHAR(20) NOT NULL,
    #   seller_id BIGINT NOT NULL,
    #   created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    #   quantity INT UNSIGNED DEFAULT 1,
    #   FOREIGN KEY (seller_id) REFERENCES user(id) ON DELETE CASCADE
    # );
    #
# CREATE TABLE marketplace_product_images (
    #   id BIGINT AUTO_INCREMENT PRIMARY KEY,
    #   marketplace_id BIGINT NOT NULL,
    #   image_id BIGINT NOT NULL,
    #   FOREIGN KEY (marketplace_id) REFERENCES marketplace(id) ON DELETE CASCADE,
    #   FOREIGN KEY (image_id) REFERENCES image(id) ON DELETE CASCADE,
    #   UNIQUE KEY unique_marketplace_image (marketplace_id, image_id)
    # );

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


# CREATE TABLE order (
    #   id BIGINT AUTO_INCREMENT PRIMARY KEY,
    #   buyer_id BIGINT NOT NULL,
    #   product_id BIGINT NOT NULL,
    #   quantity INT UNSIGNED NOT NULL,
    #   contact_number VARCHAR(15) NOT NULL,
    #   delivery_address TEXT NOT NULL,
    #   status VARCHAR(20) DEFAULT 'pending',
    #   created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    #   FOREIGN KEY (buyer_id) REFERENCES user(id) ON DELETE CASCADE,
    #   FOREIGN KEY (product_id) REFERENCES marketplace(id) ON DELETE CASCADE,
    #   CONSTRAINT status_check CHECK (status IN ('pending', 'confirmed', 'cancelled'))
    # );


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


# CREATE TABLE event (
    #   id BIGINT AUTO_INCREMENT PRIMARY KEY,
    #   title VARCHAR(200) NOT NULL,
    #   date DATETIME NOT NULL,
    #   location VARCHAR(255) NOT NULL,
    #   details TEXT NOT NULL,
    #   organizer_id BIGINT NOT NULL,
    #   participant_names TEXT,
    #   category VARCHAR(20) DEFAULT 'social',
    #   FOREIGN KEY (organizer_id) REFERENCES user(id)
    # );
    #
    # CREATE TABLE event_participants (
    #   id BIGINT AUTO_INCREMENT PRIMARY KEY,
    #   event_id BIGINT NOT NULL,
    #   user_id BIGINT NOT NULL,
    #   FOREIGN KEY (event_id) REFERENCES event(id),
    #   FOREIGN KEY (user_id) REFERENCES user(id)
    # );


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


# CREATE TABLE fundraiser (
    #   id BIGINT AUTO_INCREMENT PRIMARY KEY,
    #   title VARCHAR(200) NOT NULL,
    #   description TEXT,
    #   target_amount DECIMAL(10,2) NOT NULL,
    #   collected_amount DECIMAL(10,2) DEFAULT 0,
    #   applicant_name VARCHAR(100) NOT NULL,
    #   created_by_id BIGINT NOT NULL,
    #   beneficiary_id BIGINT NOT NULL,
    #   shelter_id BIGINT,
    #   campaign_image VARCHAR(255),
    #   donation_history TEXT DEFAULT '{}',
    #   FOREIGN KEY (created_by_id) REFERENCES user(id),
    #   FOREIGN KEY (beneficiary_id) REFERENCES pet(id),
    #   FOREIGN KEY (shelter_id) REFERENCES shelter_clinic(id)
    # );


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


# CREATE TABLE post (
    #   id BIGINT AUTO_INCREMENT PRIMARY KEY,
    #   user_id BIGINT NOT NULL,
    #   content TEXT NOT NULL,
    #   image VARCHAR(255),
    #   created_at DATETIME NOT NULL,
    #   updated_at DATETIME NOT NULL,
    #   FOREIGN KEY (user_id) REFERENCES user(id)
    # );
    #
    # CREATE TABLE post_likes (
    #   id BIGINT AUTO_INCREMENT PRIMARY KEY,
    #   post_id BIGINT NOT NULL,
    #   user_id BIGINT NOT NULL,
    #   FOREIGN KEY (post_id) REFERENCES post(id),
    #   FOREIGN KEY (user_id) REFERENCES user(id)
    # );
    #
    # CREATE TABLE post_dislikes (
    #   id BIGINT AUTO_INCREMENT PRIMARY KEY,
    #   post_id BIGINT NOT NULL,
    #   user_id BIGINT NOT NULL,
    #   FOREIGN KEY (post_id) REFERENCES post(id),
    #   FOREIGN KEY (user_id) REFERENCES user(id)
    # );


class Service(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='services')
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    created_at = models.DateTimeField(auto_now_add=True)

        
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


# CREATE TABLE review (
    #   id BIGINT AUTO_INCREMENT PRIMARY KEY,
    #   reviewer_id BIGINT NOT NULL,
    #   professional_id BIGINT NOT NULL,
    #   rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    #   review_text TEXT NOT NULL,
    #   created_at DATETIME NOT NULL,
    #   FOREIGN KEY (reviewer_id) REFERENCES user(id),
    #   FOREIGN KEY (professional_id) REFERENCES user(id),
    #   UNIQUE KEY unique_review (reviewer_id, professional_id)
    # );


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


# CREATE TABLE adoption_request (
    #   id BIGINT AUTO_INCREMENT PRIMARY KEY,
    #   pet_id BIGINT NOT NULL,
    #   requestor_id BIGINT NOT NULL,
    #   contact_number VARCHAR(15) NOT NULL,
    #   message TEXT NOT NULL,
    #   status VARCHAR(20) DEFAULT 'pending',
    #   created_at DATETIME NOT NULL,
    #   FOREIGN KEY (pet_id) REFERENCES pet(id),
    #   FOREIGN KEY (requestor_id) REFERENCES user(id)
    # );
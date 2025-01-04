from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *
from decimal import Decimal, InvalidOperation


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'account_type', 'phone', 'address', 'city', 'zip_code', 'profile_picture']
        widgets = {
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class PetForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = ['name', 'species', 'breed', 'age', 'is_stray', 'adoption_status', 'pet_picture']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'species': forms.Select(attrs={'class': 'form-control'}),
            'breed': forms.TextInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_stray': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'adoption_status': forms.Select(attrs={'class': 'form-control'}),
            'pet_picture': forms.FileInput(attrs={'class': 'form-control'})
        }

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'category', 'date', 'location', 'details']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter event title'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter event location'
            }),
            'details': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter event details'
            })
        }


class FundraiserForm(forms.ModelForm):
    class Meta:
        model = Fundraiser
        fields = ['title', 'description', 'target_amount', 'applicant_name', 'beneficiary', 'campaign_image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'target_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'applicant_name': forms.TextInput(attrs={'class': 'form-control'}),
            'beneficiary': forms.Select(attrs={'class': 'form-control'}),
            'campaign_image': forms.FileInput(attrs={'class': 'form-control'})
        }

class MarketplaceForm(forms.ModelForm):
    class Meta:
        model = Marketplace
        fields = ['product_name', 'description', 'price', 'status']
        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'min': '0.01', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('available', 'Available'),
                ('sold', 'Sold'),
                ('reserved', 'Reserved')
            ]),
        }

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'})
        }

class ShopForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = ['product_name', 'quantity', 'status', 'rating', 'shop_image']
        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'status': forms.TextInput(attrs={'class': 'form-control'}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '5', 'step': '0.1'}),
            'shop_image': forms.FileInput(attrs={'class': 'form-control'})
        }

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['quantity', 'contact_number', 'delivery_address']
        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'delivery_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image', 'caption']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'caption': forms.TextInput(attrs={'class': 'form-control'})
        }


class UserRegistrationForm(UserCreationForm):
    PROFESSIONAL_TYPES = (
        ('vet', 'Veterinarian'),
        ('shelter', 'Shelter/Clinic'),
        ('business', 'Business'),
    )
    BUSINESS_TYPES = (
        ('shop', 'Pet Shop'),
        ('groomer', 'Pet Groomer/Sitter'),
    )
    
    professional_type = forms.ChoiceField(choices=PROFESSIONAL_TYPES, required=False)
    business_type = forms.ChoiceField(choices=BUSINESS_TYPES, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'account_type', 'professional_type', 'business_type', 
                 'phone', 'address', 'city', 'zip_code', 'profile_picture']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control'})
        }

# In forms.py
class ServiceForm(forms.ModelForm):
    title = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter service title'
        }),
        required=True
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Describe your service'
        }),
        required=True
    )
    price = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '0.01',
            'step': '0.01',
            'placeholder': 'Enter price'
        }),
        required=True,
        min_value=0.01
    )

    class Meta:
        model = Service
        fields = ['title', 'description', 'price']

class ProfessionalProfileForm(forms.ModelForm):
    class Meta:
        model = ProfessionalProfile
        fields = ['description']
        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'maxlength': 200,
                'placeholder': 'Write a brief description about your professional services...'
            })
        }

    def __init__(self, *args, professional_type=None, **kwargs):
        super().__init__(*args, **kwargs)
        if professional_type == 'vet':
            self.fields['specialties'] = forms.CharField(
                widget=forms.TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter your specialties (e.g., Surgery, Dentistry, etc.)'
                }),
                required=False
            )
            self.fields['schedule'] = forms.CharField(
                widget=forms.Textarea(attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Enter your working hours and availability'
                }),
                required=False
            )
            self.Meta.fields.extend(['specialties', 'schedule'])
        elif professional_type == 'groomer':
            self.fields['specialties'] = forms.CharField(
                widget=forms.TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter your specialties (e.g., Dog Grooming, Cat Grooming, etc.)'
                }),
                required=False
            )
            self.fields['services'] = forms.CharField(
                widget=forms.Textarea(attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'List your services and prices'
                }),
                required=False
            )
            self.fields['schedule'] = forms.CharField(
                widget=forms.Textarea(attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Enter your working hours and availability'
                }),
                required=False
            )
            self.Meta.fields.extend(['specialties', 'services', 'schedule'])

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'review_text']
        widgets = {
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'review_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'maxlength': 100})
        }

class AdoptionRequestForm(forms.ModelForm):
    class Meta:
        model = AdoptionRequest
        fields = ['contact_number', 'message']
        widgets = {
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

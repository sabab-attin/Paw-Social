from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'account_type', 'date_joined')
    list_filter = ('account_type', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('account_type', 'phone', 'address', 'city', 'zip_code', 'profile_picture')}),
    )

@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('name', 'species', 'breed', 'age', 'owner', 'is_stray')
    list_filter = ('species', 'is_stray')
    search_fields = ('name', 'owner__username')

@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'rating')
    search_fields = ('name', 'user__username')

@admin.register(ShelterClinic)
class ShelterClinicAdmin(admin.ModelAdmin):
    list_display = ('business', 'phone', 'email')
    search_fields = ('business__name', 'email')

@admin.register(PetSitterGroomer)
class PetSitterGroomerAdmin(admin.ModelAdmin):
    list_display = ('business', 'experience', 'rating')
    list_filter = ('rating',)

@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('business', 'product_name', 'quantity', 'status')
    list_filter = ('status',)

@admin.register(Marketplace)
class MarketplaceAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'status', 'seller')
    list_filter = ('status',)
    search_fields = ('product_name',)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'location', 'organizer')
    list_filter = ('date',)
    search_fields = ('title', 'location')
    filter_horizontal = ('participants',)

@admin.register(Fundraiser)
class FundraiserAdmin(admin.ModelAdmin):
    list_display = ('title', 'target_amount', 'collected_amount', 'created_by')
    search_fields = ('title', 'applicant_name')

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('caption', 'uploaded_at')
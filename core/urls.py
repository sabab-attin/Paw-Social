from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Profile URLs
    path('profile/', views.profile, name='profile'),
    path('profile/update-picture/', views.update_profile_picture, name='update_profile_picture'),
    path('profile/delete-account/', views.delete_account, name='delete_account'),  # Delete account URL
    path('profile/<str:username>/', views.profile, name='profile'),
    path('user/<str:username>/', views.profile_public, name='user_profile'),
    
    # Pet URLs
    path('pets/', views.pet_list, name='pets'),
    path('pets/<int:pet_id>/edit/', views.edit_pet, name='edit_pet'),
    path('pets/<int:pet_id>/update-picture/', views.update_pet_picture, name='update_pet_picture'),
    path('pets/<int:pet_id>/delete/', views.delete_pet, name='delete_pet'),
    path('adoptions/', views.available_adoptions, name='available_adoptions'),

    # Professional URLs
    path('professional/<str:username>/', views.professional_dashboard, name='professional_dashboard'),
    path('professional/<str:username>/review/', views.add_review, name='add_review'),

    # Event URLs
    path('event/', views.event_list, name='events'),
    
    # Fundraiser URLs
    path('fundraisers/', views.fundraiser_list, name='fundraisers'),
    path('fundraisers/<int:fundraiser_id>/donate/', views.donate, name='donate'),
    path('fundraisers/delete/<int:fundraiser_id>/', views.delete_fundraiser, name='delete_fundraiser'),
    
    # Marketplace URLs
    path('marketplace/', views.marketplace, name='marketplace'),
    path('marketplace/delete/<int:listing_id>/', views.delete_listing, name='delete_listing'),
    path('marketplace/contact/<int:listing_id>/', views.contact_seller, name='contact_seller'),
    path('marketplace/buy/<int:listing_id>/', views.buy_product, name='buy_product'),
    path('marketplace/order/<int:listing_id>/', views.create_order, name='create_order'),
    path('orders/', views.my_orders, name='my_orders'),
    
    # Post URLs
    path('post/<int:post_id>/like/', views.like_post, name='like_post'),
    path('post/<int:post_id>/dislike/', views.dislike_post, name='dislike_post'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    
    # Service URLs
    path('service/add/', views.add_service, name='add_service'),
    path('service/<int:service_id>/delete/', views.delete_service, name='delete_service'),
    
    # User URLs
    path('user/<str:username>/', views.profile, name='user_profile'),
    path('user/<int:user_id>/posts/', views.user_posts, name='user_posts'),
    path('search/', views.search_users, name='search_users'),
    path('follow/<str:username>/', views.follow_user, name='follow_user'),

    # Adoption URLs
    path('pets/<int:pet_id>/request-adoption/', views.request_adoption, name='request_adoption'),
    path('pets/<int:pet_id>/toggle-adoption/', views.toggle_pet_adoption, name='toggle_pet_adoption'),
    path('pets/<int:pet_id>/manage-requests/', views.manage_adoption_requests, name='manage_adoption_requests'),
    path('adoption/approve/<int:request_id>/', views.approve_adoption, name='approve_adoption'),
    path('adoption/reject/<int:request_id>/', views.reject_adoption, name='reject_adoption'),
    path('pets/<int:pet_id>/adoption-requests/', views.view_adoption_requests, name='view_adoption_requests'),

]

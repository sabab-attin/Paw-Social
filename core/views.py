from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import *
from .forms import *
from decimal import Decimal
from django.db.models import Q
from django.db.models import Avg
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db import transaction




@login_required
def home(request):
    # Show all posts
    posts = Post.objects.all().order_by('-created_at')
    adoptable_pets = Pet.objects.filter(adoption_status='available').order_by('-id')[:5]
    
    # Initialize forms
    post_form = PostForm()
    service_form = ServiceForm()
    
    if request.method == 'POST':
        if 'service_form' in request.POST:
            service_form = ServiceForm(request.POST)
            if service_form.is_valid():
                service = service_form.save(commit=False)
                service.user = request.user
                service.save()
                messages.success(request, 'Service added successfully!')
                return redirect('home')
        else:
            post_form = PostForm(request.POST, request.FILES)
            if post_form.is_valid():
                post = post_form.save(commit=False)
                post.user = request.user
                post.save()
                messages.success(request, 'Post created successfully!')
                return redirect('home')
    
    context = {
        'posts': posts,
        'form': post_form,
        'adoptable_pets': adoptable_pets,
        'service_form': service_form
    }
    
    # Add services if user is a groomer/sitter
    if hasattr(request.user, 'professional_type') and request.user.professional_type == 'business' and request.user.business_type == 'groomer':
        services = Service.objects.filter(user=request.user)
        context.update({
            'services': services,
        })
    
    return render(request, 'core/home.html', context)


# SELECT * FROM post ORDER BY created_at DESC;
# SELECT * FROM pet 
# WHERE adoption_status = 'available' 
# ORDER BY id DESC 
# LIMIT 5;
# SELECT professional_type, business_type 
# FROM user 
# WHERE id = [user_id] 
# AND professional_type = 'business' 
# AND business_type = 'groomer';
# SELECT * FROM service 
# WHERE user_id = [user_id];
# INSERT INTO service (title, description, price, user_id, created_at) 
# VALUES (--, --,--, [user_id], CURRENT_TIMESTAMP);
# INSERT INTO post (content, image, user_id, created_at, updated_at) 
# VALUES (--,--, [user_id], CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);


@transaction.atomic
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()        # -- MySQL: INSERT INTO user (username, email, ...) VALUES (...);
            
            # If this is a professional account, create a business record
            if user.account_type == 'professional':
                business = Business.objects.create(    # -- MySQL: INSERT INTO business (user_id, name, ...) VALUES (...);
                    user=user,
                    name=form.cleaned_data.get('username'),
                    professional_type=form.cleaned_data.get('professional_type'),
                    business_type=form.cleaned_data.get('business_type'),
                    contact_number=form.cleaned_data.get('phone'),
                    email=user.email,
                    address=form.cleaned_data.get('address'),
                    city=form.cleaned_data.get('city'),
                    zip_code=form.cleaned_data.get('zip_code')
                )
                
                # Create appropriate professional record based on type
                if user.professional_type == 'shelter':   # -- MySQL: INSERT INTO shelter_clinic (business_id, phone, ...) VALUES (...);
                    ShelterClinic.objects.create(
                        business=business,
                        phone=form.cleaned_data.get('phone'),
                        email=user.email,
                        working_hours="Monday-Friday: 9 AM - 5 PM"
                    )
                elif user.professional_type == 'business' and user.business_type == 'groomer':   # -- MySQL: INSERT INTO pet_sitter_groomer (business_id, contact, ...) VALUES (...);
                    PetSitterGroomer.objects.create(
                        business=business,
                        contact=form.cleaned_data.get('phone'),
                        experience=0,
                        service_types="Basic Grooming, Pet Sitting",
                        availability="Monday-Friday: 9 AM - 5 PM"
                    )
                elif user.professional_type == 'business' and user.business_type == 'shop':    # -- MySQL: INSERT INTO shop (business_id, contact_info, ...) VALUES (...);
                    Shop.objects.create(
                        business=business,
                        contact_info=form.cleaned_data.get('phone'),
                        business_hours="Monday-Friday: 9 AM - 5 PM"
                    )
            
            messages.success(request, 'Registration successful!')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})



@login_required
def profile(request, username=None):     # -- MySQL: SELECT * FROM user WHERE username = '...' LIMIT 1;
    if username:
        viewed_user = get_object_or_404(User, username=username)
        is_own_profile = request.user == viewed_user
    else:
        viewed_user = request.user
        is_own_profile = True
    
    if request.method == 'POST' and is_own_profile:
        form = UserRegistrationForm(request.POST, request.FILES, instance=viewed_user)
        if form.is_valid():
            user = form.save()      # -- MySQL: UPDATE user SET ... WHERE id = ...;
            
            if user.account_type == 'professional':
                business, _ = Business.objects.get_or_create(user=user)  # -- MySQL: INSERT INTO business (...) VALUES (...) ON DUPLICATE KEY UPDATE ...;
                business.name = form.cleaned_data.get('username')
                business.professional_type = form.cleaned_data.get('professional_type')
                business.business_type = form.cleaned_data.get('business_type')
                business.contact_number = form.cleaned_data.get('phone')
                business.email = user.email
                business.address = form.cleaned_data.get('address')
                business.city = form.cleaned_data.get('city')
                business.zip_code = form.cleaned_data.get('zip_code')
                business.save()         # -- MySQL: UPDATE business SET ... WHERE id = ...;
                
                # Update or create professional record based on type
                if user.professional_type == 'shelter':
                    shelter, created = ShelterClinic.objects.get_or_create(         # -- MySQL: INSERT INTO shelter_clinic (...) VALUES (...) ON DUPLICATE KEY UPDATE ...;
                        business=business,
                        defaults={
                            'phone': form.cleaned_data.get('phone'),
                            'email': user.email,
                            'working_hours': "Monday-Friday: 9 AM - 5 PM"
                        }
                    )
                    if not created:
                        shelter.phone = form.cleaned_data.get('phone')
                        shelter.email = user.email
                        shelter.save()                      # -- MySQL: UPDATE shelter_clinic SET phone = '...', email = '...' WHERE id = ...;
                        
                elif user.professional_type == 'business':
                    if user.business_type == 'groomer':
                        groomer, created = PetSitterGroomer.objects.get_or_create(
                            business=business,
                            defaults={
                                'contact': form.cleaned_data.get('phone'),
                                'availability': "Monday-Friday: 9 AM - 5 PM"
                            }
                        )
                        if not created:
                            groomer.contact = form.cleaned_data.get('phone')
                            groomer.save()
                            
                    elif user.business_type == 'shop':
                        shop, created = Shop.objects.get_or_create(
                            business=business,
                            defaults={
                                'contact_info': form.cleaned_data.get('phone'),
                                'business_hours': "Monday-Friday: 9 AM - 5 PM"
                            }
                        )
                        if not created:
                            shop.contact_info = form.cleaned_data.get('phone')
                            shop.save()
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserRegistrationForm(instance=viewed_user) if is_own_profile else None

    context = {
        'viewed_user': viewed_user,
        'is_own_profile': is_own_profile,
        'posts': Post.objects.filter(user=viewed_user).order_by('-created_at'),
        'form': form,
    }
    
    # Add professional information to context if applicable
    if viewed_user.account_type == 'professional':
        try:
            business = Business.objects.get(user=viewed_user)
            if viewed_user.professional_type == 'shelter':
                context['shelter'] = ShelterClinic.objects.get(business=business)
            elif viewed_user.professional_type == 'business':
                if viewed_user.business_type == 'groomer':
                    context['groomer'] = PetSitterGroomer.objects.get(business=business)
                elif viewed_user.business_type == 'shop':
                    context['shop'] = Shop.objects.get(business=business)
        except (Business.DoesNotExist, ShelterClinic.DoesNotExist, 
                PetSitterGroomer.DoesNotExist, Shop.DoesNotExist):
            pass
    
    return render(request, 'core/profile.html', context)

@login_required
def update_profile_picture(request):
    if request.method == 'POST' and request.FILES.get('profile_picture'):
        request.user.profile_picture = request.FILES['profile_picture']
        request.user.save()
        messages.success(request, 'Profile picture updated successfully!')
    return redirect('profile')

@login_required
def pet_list(request):
    pets = Pet.objects.filter(owner=request.user)
    if request.method == 'POST':
        form = PetForm(request.POST, request.FILES)
        if form.is_valid():
            pet = form.save(commit=False)
            pet.owner = request.user
            pet.save()
            messages.success(request, 'Pet added successfully!')
            return redirect('pets')
    else:
        form = PetForm()
    return render(request, 'core/pet_list.html', {'pets': pets, 'form': form})

@login_required
def update_pet_picture(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, owner=request.user)
    if request.method == 'POST' and request.FILES.get('pet_picture'):
        pet.pet_picture = request.FILES['pet_picture']
        pet.save()
        messages.success(request, 'Pet picture updated successfully!')
    return redirect('pets')

@login_required
def edit_pet(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, owner=request.user)
    if request.method == 'POST':
        form = PetForm(request.POST, request.FILES, instance=pet)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pet information updated successfully!')
    return redirect('pets')

@login_required
def fundraiser_list(request):
    fundraisers = Fundraiser.objects.all().order_by('-id')
    if request.method == 'POST':
        form = FundraiserForm(request.POST, request.FILES)
        if form.is_valid():
            fundraiser = form.save(commit=False)
            fundraiser.created_by = request.user
            fundraiser.collected_amount = 0
            fundraiser.save()
            messages.success(request, 'Fundraiser created successfully!')
            return redirect('fundraisers')
    else:
        form = FundraiserForm()
    
    return render(request, 'core/fundraisers.html', {
        'fundraisers': fundraisers,
        'form': form
    })

@login_required
def donate(request, fundraiser_id):
    from decimal import Decimal
    fundraiser = get_object_or_404(Fundraiser, id=fundraiser_id)        # -- MySQL: SELECT * FROM fundraiser WHERE id = ... LIMIT 1;
    
    if request.method == 'POST':
        try:
            amount = Decimal(request.POST.get('amount', '0'))
            if amount > 0:
                # For debugging
                old_amount = fundraiser.collected_amount
                
                # Update donation history
                import json
                try:
                    current_donations = json.loads(fundraiser.donation_history)
                except json.JSONDecodeError:
                    current_donations = {}
                
                current_donations[request.user.username] = str(amount)
                fundraiser.donation_history = json.dumps(current_donations)
                
                # Update collected amount
                fundraiser.collected_amount += amount
                fundraiser.save()                           # -- MySQL: UPDATE fundraiser 
                                                            #           SET collected_amount = collected_amount + ...,
                                                            #               donation_history = '...'
                                                            #           WHERE id = ...;
                
                # For debugging
                messages.success(request, 
                    f'Thank you for donating ${amount}! (Previous total: ${old_amount}, New total: ${fundraiser.collected_amount})')
            else:
                messages.error(request, 'Please enter a valid amount.')
        except (ValueError, TypeError) as e:
            messages.error(request, f'Please enter a valid amount. Error: {str(e)}')
    
    return redirect('fundraisers')


@login_required
def marketplace(request):                # -- MySQL: SELECT * FROM marketplace;
    listings = Marketplace.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        listings = listings.filter(                     # -- MySQL: SELECT * FROM marketplace
            Q(product_name__icontains=search_query) |   #        WHERE product_name LIKE '%...%
            Q(description__icontains=search_query)      #        OR description LIKE '%...%';
        )

    # Price filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        listings = listings.filter(price__gte=min_price)    # -- MySQL: ... AND price >= ...;
    if max_price:
        listings = listings.filter(price__lte=max_price)    # -- MySQL: ... AND price <= ...;

    # Status filter 
    status = request.GET.get('status')
    if status:
        if status == 'in_stock':
            listings = listings.filter(quantity__gt=0)     # -- MySQL: ... AND quantity > 0; 
        elif status == 'out_of_stock':
            listings = listings.filter(quantity=0)          # -- MySQL: ... AND quantity = 0;

    # Sorting
    sort = request.GET.get('sort')
    if sort:
        if sort == 'price_low':
            listings = listings.order_by('price')           # -- MySQL: ... ORDER BY price ASC;
        elif sort == 'price_high':
            listings = listings.order_by('-price')          # -- MySQL: ... ORDER BY price DESC;
        elif sort == 'latest':
            listings = listings.order_by('-created_at')     # -- MySQL: ... ORDER BY created_at DESC;
        elif sort == 'oldest':
            listings = listings.order_by('created_at')      # -- MySQL: ... ORDER BY created_at ASC;

    # Handle POST requests
    if request.method == 'POST':
        if 'update_quantity' in request.POST:
            listing_id = request.POST.get('listing_id')
            new_quantity = int(request.POST.get('quantity'))
            listing = get_object_or_404(Marketplace, id=listing_id, seller=request.user)
            listing.quantity = new_quantity
            listing.status = 'out_of_stock' if new_quantity == 0 else 'available'
            listing.save()
            messages.success(request, 'Quantity updated successfully!')
            return redirect('marketplace')
            
        elif 'delete' in request.POST:
            listing_id = request.POST.get('listing_id')
            listing = get_object_or_404(Marketplace, id=listing_id, seller=request.user)
            listing.delete()
            messages.success(request, 'Listing deleted successfully!')
            return redirect('marketplace')
        
        else:
            # Create new listing
            product_name = request.POST.get('product_name')
            description = request.POST.get('description')
            price = request.POST.get('price')
            quantity = request.POST.get('quantity')
            
            # Create the listing
            listing = Marketplace.objects.create(
                seller=request.user,
                product_name=product_name,
                description=description,
                price=price,
                quantity=quantity,
                status='available' if int(quantity) > 0 else 'out_of_stock'
            )
            
            # Handle the product image
            if request.FILES.get('product_image'):
                image = Image.objects.create(
                    image=request.FILES['product_image'],
                    caption=f"Product image for {product_name}"
                )
                listing.product_images.add(image)
            
            messages.success(request, 'Product listed successfully!')
            return redirect('marketplace')

    context = {
        'listings': listings,
        'search_query': search_query,
        'min_price': min_price,
        'max_price': max_price,
        'selected_sort': sort,
        'selected_status': status,
    }
    
    return render(request, 'core/marketplace.html', context)

@login_required
def delete_listing(request, listing_id):
    listing = get_object_or_404(Marketplace, id=listing_id)
    if request.user == listing.seller:
        listing.delete()
        messages.success(request, 'Listing deleted successfully!')
    else:
        messages.error(request, 'You are not authorized to delete this listing!')
    return redirect('marketplace')

@login_required
def contact_seller(request, listing_id):
    listing = get_object_or_404(Marketplace, id=listing_id)
    messages.success(request, f"Seller's contact: {listing.seller.email}")
    return redirect('marketplace')

@login_required
def buy_product(request, listing_id):
    listing = get_object_or_404(Marketplace, id=listing_id)
    if listing.seller.account_type == 'professional' and listing.seller.professional_type == 'business':
        messages.success(request, f'Purchase request sent to {listing.seller.username}. They will contact you at {request.user.email}')
    return redirect('marketplace')


@login_required
def event_list(request):
    events = Event.objects.all().order_by('-date')              # -- MySQL: SELECT * FROM event ORDER BY date DESC;
    category = request.GET.get('category')
    form = EventForm()  # Initialize form at the start
    
    if category:
        events = events.filter(category=category)               # -- MySQL: SELECT * FROM event WHERE category = '...' ORDER BY date DESC;

    if request.method == 'POST':
        if 'join_event' in request.POST:
            event_id = request.POST.get('event_id')
            event = get_object_or_404(Event, id=event_id)               # -- MySQL: SELECT * FROM event WHERE id = ... LIMIT 1;
            if request.user not in event.participants.all():
                event.participants.add(request.user)                    # -- MySQL: INSERT INTO event_participants (event_id, user_id) VALUES (..., ...);
                messages.success(request, 'Joined event successfully!')
            else:
                event.participants.remove(request.user)                 # -- MySQL: DELETE FROM event_participants WHERE event_id = ... AND user_id = ...;
                messages.info(request, 'Left event successfully!')
            event.save()                                                # -- MySQL: UPDATE event SET participant_names = ... WHERE id = ...;
            return redirect('events')
            
        elif 'create_event' in request.POST:
            form = EventForm(request.POST)
            if form.is_valid():
                event = form.save(commit=False)
                event.organizer = request.user
                event.save()
                messages.success(request, 'Event created successfully!')
                return redirect('events')
        
        elif 'delete_event' in request.POST:
            event_id = request.POST.get('event_id')
            event = get_object_or_404(Event, id=event_id, organizer=request.user)
            event.delete()
            messages.success(request, 'Event deleted successfully!')
            return redirect('events')
    
    context = {
        'events': events,
        'form': form,
        'current_category': category
    }
    
    return render(request, 'core/event_list.html', context)


@login_required
def home(request):
    # Show all posts
    posts = Post.objects.all().order_by('-created_at')
    adoptable_pets = Pet.objects.filter(adoption_status='available').order_by('-id')[:5]
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            messages.success(request, 'Post created successfully!')
            return redirect('home')
    else:
        form = PostForm()
    
    context = {
        'posts': posts,
        'form': form,
        'adoptable_pets': adoptable_pets
    }
    
    # Add services if user is a groomer/sitter
    if hasattr(request.user, 'professional_type') and request.user.professional_type == 'business' and request.user.business_type == 'groomer':
        services = Service.objects.filter(user=request.user)
        service_form = ServiceForm()
        context.update({
            'services': services,
            'service_form': service_form
        })
    
    return render(request, 'core/home.html', context)



@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.dislikes.all():
        post.dislikes.remove(request.user)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return redirect('home')

@login_required
def dislike_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    if request.user in post.dislikes.all():
        post.dislikes.remove(request.user)
    else:
        post.dislikes.add(request.user)
    return redirect('home')

@login_required
def add_service(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            try:
                service = form.save(commit=False)
                service.user = request.user
                
                # Ensure description is not empty
                if not service.description:
                    service.description = "No description provided"
                    
                service.save()
                messages.success(request, 'Service added successfully!')
                return redirect('home')
                
            except Exception as e:
                messages.error(request, f'Error adding service: {str(e)}')
                return render(request, 'core/add_service.html', {'form': form})
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ServiceForm()
    
    return render(request, 'core/add_service.html', {'form': form})

def search_users(request):
    query = request.GET.get('q', '')
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )
    else:
        users = []
    
    return render(request, 'core/search_results.html', {
        'users': users,
        'query': query
    })

@login_required
def user_posts(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)
    posts = Post.objects.filter(user=profile_user).order_by('-created_at')
    
    context = {
        'profile_user': profile_user,
        'posts': posts,
    }
    
    # Add professional profile context if applicable
    if profile_user.account_type == 'professional':
        professional_profile, created = ProfessionalProfile.objects.get_or_create(
            user=profile_user,
            defaults={
                'description': '',
                'average_rating': 0.0,
                'total_ratings': 0
            }
        )
        
        reviews = Review.objects.filter(professional=profile_user).order_by('-created_at')
        
        # Get services for groomer/shelter
        services = None
        if profile_user.professional_type in ['business', 'shelter']:
            if profile_user.professional_type == 'business' and profile_user.business_type != 'shop':
                services = Service.objects.filter(user=profile_user)
            elif profile_user.professional_type == 'shelter':
                services = Service.objects.filter(user=profile_user)
        
        # Add review form if user hasn't reviewed yet
        review_form = None
        if request.user != profile_user:
            user_review = Review.objects.filter(reviewer=request.user, professional=profile_user).first()
            if not user_review:
                review_form = ReviewForm()
        
        context.update({
            'professional_profile': professional_profile,
            'reviews': reviews,
            'review_form': review_form,
            'services': services,
            'user_review': Review.objects.filter(reviewer=request.user, professional=profile_user).first() if request.user.is_authenticated else None
        })
    
    return render(request, 'core/user_posts.html', context)

@login_required
def add_service(request):
    if request.method == 'POST':
        service = Service(
            user=request.user,
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            price=request.POST.get('price')
        )
        service.save()
        messages.success(request, 'Service added successfully!')
    return redirect('user_posts', user_id=request.user.id)


@login_required
def create_order(request, listing_id):
    listing = get_object_or_404(Marketplace, id=listing_id)
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            if quantity <= listing.quantity:
                order = form.save(commit=False)
                order.buyer = request.user
                order.product = listing
                order.save()
                
                # Decrease product quantity
                listing.quantity -= quantity
                listing.save()
                
                messages.success(request, 'Order placed successfully!')
                return redirect('marketplace')
            else:
                messages.error(request, 'Requested quantity not available!')
    else:
        form = OrderForm()
    
    return render(request, 'core/create_order.html', {
        'form': form,
        'listing': listing
    })

@login_required
def create_order(request, listing_id):
    listing = get_object_or_404(Marketplace, id=listing_id)
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            if quantity <= listing.quantity:
                order = form.save(commit=False)
                order.buyer = request.user
                order.product = listing
                order.save()
                
                # Decrease product quantity
                listing.quantity -= quantity
                listing.save()
                
                messages.success(request, 'Order placed successfully!')
                return redirect('marketplace')
            else:
                messages.error(request, 'Requested quantity not available!')
    else:
        form = OrderForm()
    
    return render(request, 'core/create_order.html', {
        'form': form,
        'listing': listing
    })


@login_required
def my_orders(request):
    # For buyers
    orders = Order.objects.filter(buyer=request.user).order_by('-created_at')
    # For sellers
    seller_orders = Order.objects.filter(product__seller=request.user).order_by('-created_at')
    
    return render(request, 'core/my_orders.html', {
        'buyer_orders': orders,
        'seller_orders': seller_orders
    })

@login_required
def professional_dashboard(request, username):
    professional = get_object_or_404(User, username=username, account_type='professional')
    profile, created = ProfessionalProfile.objects.get_or_create(user=professional)
    reviews = Review.objects.filter(professional=professional).order_by('-created_at')
    
    if request.user == professional:
        if request.method == 'POST':
            form = ProfessionalProfileForm(
                request.POST, 
                instance=profile,
                professional_type=professional.professional_type
            )
            if form.is_valid():
                profile = form.save(commit=False)
                profile.specialties = form.cleaned_data.get('specialties', '')
                profile.schedule = form.cleaned_data.get('schedule', '')
                profile.services = form.cleaned_data.get('services', '')
                profile.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('professional_dashboard', username=username)
        else:
            form = ProfessionalProfileForm(
                instance=profile,
                professional_type=professional.professional_type
            )
    else:
        form = None

    return render(request, 'core/professional_dashboard.html', {
        'professional': professional,
        'profile': profile,
        'form': form,
        'reviews': reviews
    })

@login_required
def add_review(request, username):
    professional = get_object_or_404(User, username=username, account_type='professional')          # -- MySQL: SELECT * FROM user WHERE username = '...' AND account_type = 'professional' LIMIT 1;
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review, created = Review.objects.get_or_create(                                         # -- MySQL: INSERT INTO review (...) VALUES (...) ON DUPLICATE KEY UPDATE ...;
                reviewer=request.user,
                professional=professional,
                defaults={
                    'rating': form.cleaned_data['rating'],
                    'review_text': form.cleaned_data['review_text']
                }
            )
            
            if not created:
                review.rating = form.cleaned_data['rating']
                review.review_text = form.cleaned_data['review_text']
                review.save()                                           # -- MySQL: UPDATE review SET rating = ..., review_text = '...' WHERE id = ...;
            
            # Update average rating
            avg_rating = Review.objects.filter(professional=professional).aggregate(Avg('rating'))          # -- MySQL: SELECT AVG(rating) as rating__avg FROM review WHERE professional_id = ...;
            profile = professional.professionalprofile
            profile.average_rating = avg_rating['rating__avg'] or 0.0
            profile.total_ratings = Review.objects.filter(professional=professional).count()            # -- MySQL: SELECT COUNT(*) FROM review WHERE professional_id = ...;
            profile.save()                                                                  # -- MySQL: UPDATE professional_profile SET average_rating = ..., total_ratings = ... WHERE id = ...;
            
            messages.success(request, 'Review submitted successfully!')
    
    return redirect('user_posts', user_id=professional.id)

@login_required
def delete_service(request, service_id):
    service = get_object_or_404(Service, id=service_id, user=request.user)
    service.delete()
    messages.success(request, 'Service deleted successfully!')
    return redirect('user_posts', user_id=request.user.id)

@login_required
def delete_fundraiser(request, fundraiser_id):
    fundraiser = get_object_or_404(Fundraiser, id=fundraiser_id)
    
    # Check if user is the creator of the fundraiser
    if request.user == fundraiser.created_by:
        fundraiser.delete()
        messages.success(request, 'Fundraiser deleted successfully!')
    else:
        messages.error(request, 'You are not authorized to delete this fundraiser!')
        
    return redirect('fundraisers')

@login_required
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)         # -- MySQL: SELECT * FROM user WHERE username = ... LIMIT 1;
    
    if request.user != user_to_follow:
        if request.user in user_to_follow.followers.all():              # -- MySQL: SELECT EXISTS(SELECT 1 FROM user_followers WHERE from_user_id = ... AND to_user_id = ...);
            user_to_follow.followers.remove(request.user)               # -- MySQL: DELETE FROM user_followers WHERE from_user_id = ... AND to_user_id = ...;
            messages.info(request, f'Unfollowed {user_to_follow.username}')
        else:
            user_to_follow.followers.add(request.user)                   # -- MySQL: INSERT INTO user_followers (from_user_id, to_user_id) VALUES (..., ...);
            messages.success(request, f'Following {user_to_follow.username}')
        
        user_to_follow.update_follower_names()                           # -- MySQL: UPDATE user
        request.user.update_follower_names()                             #          SET follower_names = (SELECT GROUP_CONCAT(username)
                                                                         #                                FROM user WHERE id IN
                                                                         #                                (SELECT from_user_id FROM user_followers WHERE to_user_id = ...))
                                                                         #          WHERE id = ...;
    return redirect('user_posts', user_id=user_to_follow.id)

@login_required
def home(request):                                                                  # -- MySQL: SELECT * FROM user
                                                                                    #          WHERE id IN (SELECT to_user_id
                                                                                    #                        FROM user_followers
                                                                                    #                        WHERE from_user_id = ...);  
    followed_users = request.user.following.all()
    posts = Post.objects.filter(user__in=followed_users).order_by('-created_at')    # -- MySQL: SELECT * FROM post
                                                                                    #          WHERE user_id IN (SELECT to_user_id
                                                                                    #                           FROM user_followers
                                                                                    #                           WHERE from_user_id = ...)
                                                                                    #          ORDER BY created_at DESC;
 
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()                                                             # -- MySQL: INSERT INTO post (content, image, user_id, created_at, updated_at)
            messages.success(request, 'Post created successfully!')                 #          VALUES (--, --, --, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
            return redirect('home')
    else:
        form = PostForm()
    
    return render(request, 'core/home.html', {
        'posts': posts,
        'form': form
    })

@login_required
def delete_account(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        user = request.user
        
        if user.check_password(password):
            # Store username for message
            username = user.username
            
            # Logout the user
            logout(request)
            
            # Delete the user account
            user.delete()                   # -- MySQL: DELETE FROM user WHERE id = ...;
                                            # (This will cascade delete all related records based on foreign key constraints)
            
            messages.success(request, f'Account "{username}" has been deleted successfully.')
            return redirect('home')
        else:
            messages.error(request, 'Incorrect password. Please try again.')
    
    return redirect('profile')

@login_required
def delete_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id, user=request.user)
        post.delete()
        messages.success(request, 'Post deleted successfully!')
    except Post.DoesNotExist:
        messages.error(request, 'Post not found or you do not have permission to delete it.')
    return redirect('home')

@login_required
def profile_public(request, username):
    viewed_user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(user=viewed_user).order_by('-created_at')
    pets = Pet.objects.filter(owner=viewed_user)

    context = {
        'viewed_user': viewed_user,
        'posts': posts,
        'pets': pets,
        'is_own_profile': request.user == viewed_user,
    }
    
    return render(request, 'core/profile_public.html', context)

@login_required
def request_adoption(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)                 # -- MySQL: SELECT * FROM pet WHERE id = ... LIMIT 1;
    
    # Check if user is not the owner
    if request.user == pet.owner:
        messages.error(request, "You can't request to adopt your own pet.")
        return redirect('available_adoptions')
        
    # Check if pet is available for adoption
    if pet.adoption_status != 'available':
        messages.error(request, 'This pet is not available for adoption.')
        return redirect('available_adoptions')
    
    # Check if user already has a pending request
    existing_request = AdoptionRequest.objects.filter(
        pet=pet,
        requestor=request.user,
        status='pending'
    ).exists()                      # -- MySQL: SELECT EXISTS(
                                    #             SELECT 1 FROM adoption_request
                                    #             WHERE pet_id = ... AND requestor_id = ... AND status = 'pending'
                                    #           );
    if existing_request:
        messages.error(request, 'You already have a pending request for this pet.')
        return redirect('available_adoptions')
    
    if request.method == 'POST':
        AdoptionRequest.objects.create(                                 # -- MySQL: INSERT INTO adoption_request
            pet=pet,                                                    #          (pet_id, requestor_id, contact_number, message, status)
            requestor=request.user,                                     #          VALUES (..., ..., '...', '...', 'pending');
            contact_number=request.POST.get('contact_number'),
            message=request.POST.get('message'),
            status='pending'
        )
        messages.success(request, f'Adoption request sent for {pet.name}!')
        return redirect('available_adoptions')
    
    context = {
        'pet': pet
    }
    return render(request, 'core/request_adoption.html', context)

@login_required
def manage_adoption_requests(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, owner=request.user)             # -- MySQL: SELECT * FROM pet WHERE id = ... AND owner_id = ... LIMIT 1;
    adoption_requests = pet.adoption_requests.filter(status='pending')
    
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')
        
        adoption_request = get_object_or_404(AdoptionRequest, id=request_id)        # -- MySQL: SELECT * FROM adoption_request WHERE pet_id = ... AND status = 'pending';
        
        if action == 'approve':
            # Update pet ownership
            pet.owner = adoption_request.requestor
            pet.adoption_status = 'adopted'
            pet.adopted_by = adoption_request.requestor
            pet.save()                                          # -- MySQL: UPDATE pet
                                                                #           SET owner_id = ..., adoption_status = 'adopted', adopted_by_id = ...
                                                                #           WHERE id = ...;

            # Update request status
            adoption_request.status = 'approved'
            adoption_request.save()                             # -- MySQL: UPDATE adoption_request SET status = 'approved' WHERE id = ...;
            
            # Reject other requests
            pet.adoption_requests.exclude(id=request_id).update(status='rejected')          # -- MySQL: UPDATE adoption_request
                                                                                            #           SET status = 'rejected'
                                                                                            #           WHERE pet_id = ...
                                                                                            #           AND id != ...;
            
            messages.success(request, f'Pet successfully adopted by {adoption_request.requestor.username}!')
        elif action == 'reject':
            adoption_request.status = 'rejected'
            adoption_request.save()
            messages.success(request, 'Adoption request rejected.')
            
    return render(request, 'core/manage_adoption_requests.html', {
        'pet': pet,
        'adoption_requests': adoption_requests
    })

@login_required
def toggle_pet_adoption(request, pet_id):                               # -- MySQL: SELECT * FROM pet WHERE id = ... AND owner_id = ... LIMIT 1;
    pet = get_object_or_404(Pet, id=pet_id, owner=request.user)  # Ensure owner access
    pet.toggle_adoption_status()                                            # -- MySQL: UPDATE pet                                             
    messages.success(request, f'Updated adoption status for {pet.name}')    #          SET adoption_status = CASE
    return redirect('available_adoptions')                                  #              WHEN adoption_status = 'not_for_adoption' THEN 'available'
                                                                            #              ELSE 'not_for_adoption'
                                                                            #          END
                                                                            #          WHERE id = ...;

@login_required
def delete_pet(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, owner=request.user)  # Ensure owner access          # -- MySQL: SELECT * FROM pet WHERE id = ... AND owner_id = ... LIMIT 1;
    pet_name = pet.name
    pet.delete()                                                                                # -- MySQL: DELETE FROM pet WHERE id = ...;                                                                                
    messages.success(request, f'{pet_name} has been removed from your pets.')
    return redirect('available_adoptions')


@login_required
def available_adoptions(request):
    # Get all pets available for adoption
    available_pets = Pet.objects.filter(adoption_status='available').select_related('owner')
    # -- MySQL: SELECT p.*, u.* 
    #          FROM pet p 
    #          INNER JOIN user u ON p.owner_id = u.id 
    #          WHERE p.adoption_status = 'available';


    # Filter by species if requested
    species = request.GET.get('species')
    if species:
        available_pets = available_pets.filter(species=species)         # -- MySQL: ... AND p.species = '...';
    
    # Handle adoption requests
    if request.method == 'POST':
        pet_id = request.POST.get('pet_id')                             # -- MySQL: SELECT * FROM pet WHERE id = ... LIMIT 1;
        pet = get_object_or_404(Pet, id=pet_id)
        if request.user != pet.owner:
            adoption_request = AdoptionRequest.objects.create(
                pet=pet,
                requestor=request.user,
                contact_number=request.POST.get('contact_number'),
                message=request.POST.get('message')
            )
            messages.success(request, 'Adoption request sent successfully!')
            return redirect('available_adoptions')
    
    context = {
        'pets': available_pets,
        'selected_species': species,
        'species_choices': Pet.SPECIES_CHOICES,
    }
    
    return render(request, 'core/available_adoptions.html', context)


@login_required
def view_adoption_requests(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, owner=request.user)  # Ensure owner access
    adoption_requests = AdoptionRequest.objects.filter(pet=pet).order_by('-created_at')
    return render(request, 'core/manage_adoption_requests.html', {
        'pet': pet,
        'adoption_requests': adoption_requests
    })


@login_required
def approve_adoption(request, request_id):
    adoption_request = get_object_or_404(AdoptionRequest, id=request_id)                # -- MySQL: SELECT * FROM adoption_request WHERE id = ... LIMIT 1;
    pet = adoption_request.pet                                                          # -- MySQL: SELECT * FROM pet WHERE id = adoption_request.pet_id;
    
    # Verify ownership
    if pet.owner != request.user:
        messages.error(request, 'You are not authorized to approve this request.')
        return redirect('pets')

    # Process adoption
    if pet.adoption_status == 'available':
        # Update pet ownership and status
        pet.owner = adoption_request.requestor
        pet.adoption_status = 'not_for_adoption'
        pet.is_stray = False                                                             # -- MySQL: UPDATE pet
        pet.save()                                                                       #          SET owner_id = ...,
                                                                                         #              adoption_status = 'not_for_adoption',
                                                                                         #              is_stray = FALSE
                                                                                         #          WHERE id = ...;
        
        # Update request status
        adoption_request.status = 'approved'                                            # -- MySQL: UPDATE adoption_request
        adoption_request.save()                                                         #          SET status = 'approved'
                                                                                        #          WHERE id = ...; 
        
        # Reject other pending requests
        AdoptionRequest.objects.filter(pet=pet, status='pending').exclude(id=request_id).update(status='rejected')
        
        messages.success(request, f'{pet.name} has been successfully adopted by {adoption_request.requestor.username}!')
    else:
        messages.error(request, 'This pet is not available for adoption.')
    
    return redirect('pets')

@login_required
def reject_adoption(request, request_id):
    adoption_request = get_object_or_404(AdoptionRequest, id=request_id)                    # -- MySQL: SELECT * FROM adoption_request WHERE id = ... LIMIT 1;
    pet = adoption_request.pet                                                              # -- MySQL: SELECT * FROM pet WHERE id = adoption_request.pet_id;
    
    # Verify ownership
    if pet.owner != request.user:
        messages.error(request, 'You are not authorized to reject this request.')
        return redirect('pets')
    
    adoption_request.status = 'rejected'
    adoption_request.save()                                                                 # -- MySQL: UPDATE adoption_request
                                                                                            #          SET status = 'rejected'
                                                                                            #          WHERE id = ...;
    messages.success(request, 'Adoption request rejected.')
    return redirect('view_adoption_requests', pet_id=pet.id)
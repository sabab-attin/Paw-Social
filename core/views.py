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

def home(request):
    events = Event.objects.order_by('-date')[:5]
    fundraisers = Fundraiser.objects.all()[:5]
    return render(request, 'core/home.html', {
        'events': events,
        'fundraisers': fundraisers
    })

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful!')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile(request, username=None):
    # If username is provided, we're viewing someone else's profile
    if username:
        viewed_user = get_object_or_404(User, username=username)
        is_own_profile = request.user == viewed_user
    else:
        viewed_user = request.user
        is_own_profile = True
    
    # Get user's posts
    posts = Post.objects.filter(user=viewed_user).order_by('-created_at')
    
    context = {
        'viewed_user': viewed_user,
        'is_own_profile': is_own_profile,
        'posts': posts,
    }
    
    if request.method == 'POST' and is_own_profile:
        form = UserRegistrationForm(request.POST, request.FILES, instance=viewed_user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserRegistrationForm(instance=viewed_user) if is_own_profile else None
    
    context['form'] = form
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
    fundraiser = get_object_or_404(Fundraiser, id=fundraiser_id)
    
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
                fundraiser.save()
                
                # For debugging
                messages.success(request, 
                    f'Thank you for donating ${amount}! (Previous total: ${old_amount}, New total: ${fundraiser.collected_amount})')
            else:
                messages.error(request, 'Please enter a valid amount.')
        except (ValueError, TypeError) as e:
            messages.error(request, f'Please enter a valid amount. Error: {str(e)}')
    
    return redirect('fundraisers')


@login_required
def marketplace(request):
    listings = Marketplace.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        listings = listings.filter(
            Q(product_name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Price filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        listings = listings.filter(price__gte=min_price)
    if max_price:
        listings = listings.filter(price__lte=max_price)

    # Status filter 
    status = request.GET.get('status')
    if status:
        if status == 'in_stock':
            listings = listings.filter(quantity__gt=0)
        elif status == 'out_of_stock':
            listings = listings.filter(quantity=0)

    # Sorting
    sort = request.GET.get('sort')
    if sort:
        if sort == 'price_low':
            listings = listings.order_by('price')
        elif sort == 'price_high':
            listings = listings.order_by('-price')
        elif sort == 'latest':
            listings = listings.order_by('-created_at')
        elif sort == 'oldest':
            listings = listings.order_by('created_at')

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
    events = Event.objects.all().order_by('-date')
    category = request.GET.get('category')
    form = EventForm()  # Initialize form at the start
    
    if category:
        events = events.filter(category=category)

    if request.method == 'POST':
        if 'join_event' in request.POST:
            event_id = request.POST.get('event_id')
            event = get_object_or_404(Event, id=event_id)
            if request.user not in event.participants.all():
                event.participants.add(request.user)
                messages.success(request, 'Joined event successfully!')
            else:
                event.participants.remove(request.user)
                messages.info(request, 'Left event successfully!')
            event.save()
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
        service = Service(
            user=request.user,
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            price=request.POST.get('price')
        )
        service.save()
        messages.success(request, 'Service added successfully!')
    return redirect('user_posts', user_id=request.user.id)

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
    professional = get_object_or_404(User, username=username, account_type='professional')
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review, created = Review.objects.get_or_create(
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
                review.save()
            
            # Update average rating
            avg_rating = Review.objects.filter(professional=professional).aggregate(Avg('rating'))
            profile = professional.professionalprofile
            profile.average_rating = avg_rating['rating__avg'] or 0.0
            profile.total_ratings = Review.objects.filter(professional=professional).count()
            profile.save()
            
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
    user_to_follow = get_object_or_404(User, username=username)
    
    if request.user != user_to_follow:
        if request.user in user_to_follow.followers.all():
            user_to_follow.followers.remove(request.user)
            messages.info(request, f'Unfollowed {user_to_follow.username}')
        else:
            user_to_follow.followers.add(request.user)
            messages.success(request, f'Following {user_to_follow.username}')
        
        user_to_follow.update_follower_names()
        request.user.update_follower_names()
    
    return redirect('user_posts', user_id=user_to_follow.id)

@login_required
def home(request):
    followed_users = request.user.following.all()
    posts = Post.objects.filter(user__in=followed_users).order_by('-created_at')
    
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
            user.delete()
            
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
    pet = get_object_or_404(Pet, id=pet_id)
    
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
    ).exists()
    
    if existing_request:
        messages.error(request, 'You already have a pending request for this pet.')
        return redirect('available_adoptions')
    
    if request.method == 'POST':
        AdoptionRequest.objects.create(
            pet=pet,
            requestor=request.user,
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
    pet = get_object_or_404(Pet, id=pet_id, owner=request.user)
    adoption_requests = pet.adoption_requests.filter(status='pending')
    
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')
        
        adoption_request = get_object_or_404(AdoptionRequest, id=request_id)
        
        if action == 'approve':
            # Update pet ownership
            pet.owner = adoption_request.requestor
            pet.adoption_status = 'adopted'
            pet.adopted_by = adoption_request.requestor
            pet.save()
            
            # Update request status
            adoption_request.status = 'approved'
            adoption_request.save()
            
            # Reject other requests
            pet.adoption_requests.exclude(id=request_id).update(status='rejected')
            
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
def toggle_pet_adoption(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, owner=request.user)  # Ensure owner access
    pet.toggle_adoption_status()
    messages.success(request, f'Updated adoption status for {pet.name}')
    return redirect('available_adoptions')

@login_required
def delete_pet(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, owner=request.user)  # Ensure owner access
    pet_name = pet.name
    pet.delete()
    messages.success(request, f'{pet_name} has been removed from your pets.')
    return redirect('available_adoptions')


@login_required
def available_adoptions(request):
    # Get all pets available for adoption
    available_pets = Pet.objects.filter(adoption_status='available').select_related('owner')
    
    # Filter by species if requested
    species = request.GET.get('species')
    if species:
        available_pets = available_pets.filter(species=species)
    
    # Handle adoption requests
    if request.method == 'POST':
        pet_id = request.POST.get('pet_id')
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
    adoption_request = get_object_or_404(AdoptionRequest, id=request_id)
    pet = adoption_request.pet
    
    # Verify ownership
    if pet.owner != request.user:
        messages.error(request, 'You are not authorized to approve this request.')
        return redirect('pets')

    # Process adoption
    if pet.adoption_status == 'available':
        # Update pet ownership and status
        pet.owner = adoption_request.requestor
        pet.adoption_status = 'not_for_adoption'
        pet.is_stray = False
        pet.save()
        
        # Update request status
        adoption_request.status = 'approved'
        adoption_request.save()
        
        # Reject other pending requests
        AdoptionRequest.objects.filter(pet=pet, status='pending').exclude(id=request_id).update(status='rejected')
        
        messages.success(request, f'{pet.name} has been successfully adopted by {adoption_request.requestor.username}!')
    else:
        messages.error(request, 'This pet is not available for adoption.')
    
    return redirect('pets')

@login_required
def reject_adoption(request, request_id):
    adoption_request = get_object_or_404(AdoptionRequest, id=request_id)
    pet = adoption_request.pet
    
    # Verify ownership
    if pet.owner != request.user:
        messages.error(request, 'You are not authorized to reject this request.')
        return redirect('pets')
    
    adoption_request.status = 'rejected'
    adoption_request.save()
    
    messages.success(request, 'Adoption request rejected.')
    return redirect('view_adoption_requests', pet_id=pet.id)
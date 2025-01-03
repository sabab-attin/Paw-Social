# Generated by Django 4.2.9 on 2025-01-03 06:38

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('account_type', models.CharField(choices=[('regular', 'Regular User'), ('professional', 'Professional User')], default='regular', max_length=20)),
                ('professional_type', models.CharField(blank=True, choices=[('vet', 'Veterinarian'), ('shelter', 'Shelter/Clinic'), ('business', 'Business')], max_length=20, null=True)),
                ('business_type', models.CharField(blank=True, choices=[('shop', 'Pet Shop'), ('groomer', 'Pet Groomer/Sitter')], max_length=20, null=True)),
                ('followers_count', models.IntegerField(default=0)),
                ('following_count', models.IntegerField(default=0)),
                ('phone', models.CharField(blank=True, max_length=15, null=True)),
                ('address', models.CharField(blank=True, max_length=255, null=True)),
                ('city', models.CharField(blank=True, max_length=100, null=True)),
                ('zip_code', models.CharField(blank=True, max_length=10, null=True)),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='profile_pics/')),
                ('follower_names', models.TextField(blank=True, default='')),
                ('following_names', models.TextField(blank=True, default='')),
                ('followers', models.ManyToManyField(blank=True, related_name='following', to=settings.AUTH_USER_MODEL)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Business',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('rating', models.FloatField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)])),
                ('logo', models.ImageField(blank=True, null=True, upload_to='business_logos/')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='images/')),
                ('caption', models.CharField(blank=True, max_length=200)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Marketplace',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('product_images', models.ManyToManyField(blank=True, related_name='product_images', to='core.image')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='marketplace_listings', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Shop',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=100)),
                ('quantity', models.IntegerField()),
                ('status', models.CharField(max_length=20)),
                ('rating', models.FloatField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)])),
                ('shop_image', models.ImageField(blank=True, null=True, upload_to='shop_images/')),
                ('business', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.business')),
            ],
        ),
        migrations.CreateModel(
            name='ShelterClinic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(max_length=15)),
                ('email', models.EmailField(max_length=254)),
                ('review', models.TextField(blank=True)),
                ('business', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.business')),
                ('facility_images', models.ManyToManyField(blank=True, related_name='shelter_images', to='core.image')),
            ],
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='services', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ProfessionalProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, default='', max_length=200)),
                ('average_rating', models.FloatField(default=0.0)),
                ('total_ratings', models.IntegerField(default=0)),
                ('specialties', models.CharField(blank=True, default='', max_length=200)),
                ('schedule', models.TextField(blank=True, default='')),
                ('facilities', models.TextField(blank=True, default='')),
                ('services', models.TextField(blank=True, default='')),
                ('business_hours', models.TextField(blank=True, default='')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('image', models.ImageField(blank=True, null=True, upload_to='post_images/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('dislikes', models.ManyToManyField(blank=True, related_name='disliked_posts', to=settings.AUTH_USER_MODEL)),
                ('likes', models.ManyToManyField(blank=True, related_name='liked_posts', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='PetSitterGroomer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('experience', models.IntegerField()),
                ('contact', models.CharField(max_length=100)),
                ('rating', models.FloatField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)])),
                ('certificate_image', models.ImageField(blank=True, null=True, upload_to='certificates/')),
                ('business', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.business')),
            ],
        ),
        migrations.CreateModel(
            name='Pet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('species', models.CharField(choices=[('dog', 'Dog'), ('cat', 'Cat'), ('bird', 'Bird'), ('other', 'Other')], max_length=20)),
                ('breed', models.CharField(max_length=100)),
                ('age', models.IntegerField()),
                ('is_stray', models.BooleanField(default=False)),
                ('pet_picture', models.ImageField(blank=True, null=True, upload_to='pet_pics/')),
                ('adoption_status', models.CharField(choices=[('not_for_adoption', 'Not For Adoption'), ('available', 'Available for Adoption'), ('adopted', 'Adopted')], default='not_for_adoption', max_length=20)),
                ('adoption_date', models.DateTimeField(blank=True, null=True)),
                ('medical_history', models.TextField(blank=True, default='')),
                ('vaccinated', models.BooleanField(default=False)),
                ('last_checkup', models.DateField(blank=True, null=True)),
                ('description', models.TextField(blank=True, default='')),
                ('special_needs', models.TextField(blank=True, default='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('adopted_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='adopted_pets', to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pets', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('contact_number', models.CharField(max_length=15)),
                ('delivery_address', models.TextField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('buyer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to=settings.AUTH_USER_MODEL)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.marketplace')),
            ],
        ),
        migrations.CreateModel(
            name='Fundraiser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('target_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('collected_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('applicant_name', models.CharField(max_length=100)),
                ('campaign_image', models.ImageField(blank=True, null=True, upload_to='fundraiser_images/')),
                ('beneficiary', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.pet')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('shelter', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.shelterclinic')),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('date', models.DateTimeField()),
                ('location', models.CharField(max_length=255)),
                ('details', models.TextField()),
                ('category', models.CharField(choices=[('adoption', 'Adoption Events'), ('training', 'Training Workshops'), ('show', 'Pet Shows'), ('vet', 'Vet Camps'), ('social', 'Social Meetups')], max_length=20)),
                ('participant_names', models.TextField(blank=True)),
                ('organizer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='organized_events', to=settings.AUTH_USER_MODEL)),
                ('participants', models.ManyToManyField(related_name='participated_events', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AdoptionRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contact_number', models.CharField(max_length=15)),
                ('message', models.TextField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('pet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='adoption_requests', to='core.pet')),
                ('requestor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='adoption_requests_made', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('review_text', models.TextField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('professional', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_reviews', to=settings.AUTH_USER_MODEL)),
                ('reviewer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='given_reviews', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('reviewer', 'professional')},
            },
        ),
    ]
# Generated by Django 5.2.4 on 2025-07-17 09:54

import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


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
            name='Buyer',
            fields=[
                ('buyer_id', models.AutoField(primary_key=True, serialize=False)),
                ('profile_picture', models.ImageField(default='default.jpg', upload_to='buyers/')),
                ('mobile_no', models.CharField(max_length=10, unique=True)),
                ('address', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='buyer_created_by', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='buyer_updated_by', to=settings.AUTH_USER_MODEL)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('cart_id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('buyer', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='myapp.buyer')),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('category_id', models.AutoField(primary_key=True, serialize=False)),
                ('category_name', models.CharField(max_length=20, unique=True)),
                ('category_detail', models.CharField(max_length=100, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='category_created_by', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='category_updated_by', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('payment_id', models.AutoField(primary_key=True, serialize=False)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_method', models.CharField(choices=[('COD', 'Cash on Delivery'), ('CREDIT_CARD', 'Credit Card'), ('DEBIT_CARD', 'Debit Card'), ('NET_BANKING', 'Net Banking'), ('UPI', 'UPI'), ('WALLET', 'Wallet')], max_length=20)),
                ('transaction_id', models.CharField(max_length=100, unique=True)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed'), ('REFUNDED', 'Refunded')], default='PENDING', max_length=20)),
                ('payment_date', models.DateTimeField(auto_now_add=True)),
                ('refund_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('refund_date', models.DateTimeField(blank=True, null=True)),
                ('buyer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.buyer')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('order_id', models.AutoField(primary_key=True, serialize=False)),
                ('order_number', models.CharField(max_length=20, unique=True)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('PROCESSING', 'Processing'), ('SHIPPED', 'Shipped'), ('DELIVERED', 'Delivered'), ('CANCELLED', 'Cancelled'), ('REFUNDED', 'Refunded')], default='PENDING', max_length=20)),
                ('total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('order_date', models.DateTimeField(auto_now_add=True)),
                ('dispatch_date', models.DateTimeField(blank=True, null=True)),
                ('delivery_date', models.DateTimeField(blank=True, null=True)),
                ('tracking_number', models.CharField(blank=True, max_length=50)),
                ('shipping_company', models.CharField(blank=True, max_length=50)),
                ('buyer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.buyer')),
                ('payment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='myapp.payment')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('product_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('images', models.ImageField(upload_to='')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('sale_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, validators=[django.core.validators.MinValueValidator(0.01)])),
                ('quantity', models.PositiveIntegerField()),
                ('brand', models.CharField(max_length=50)),
                ('tags', models.CharField(blank=True, max_length=255)),
                ('size', models.CharField(blank=True, max_length=20)),
                ('color', models.CharField(blank=True, max_length=20)),
                ('fabric', models.CharField(blank=True, max_length=50)),
                ('in_stock', models.BooleanField(default=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.category')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_created_by', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_updated_by', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('color', models.CharField(blank=True, max_length=50)),
                ('size', models.CharField(blank=True, max_length=50)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.product')),
            ],
        ),
        migrations.CreateModel(
            name='Seller',
            fields=[
                ('seller_id', models.AutoField(primary_key=True, serialize=False)),
                ('profile_picture', models.ImageField(default='default.jpg', upload_to='sellers/')),
                ('mobile_no', models.CharField(max_length=10, unique=True)),
                ('address', models.TextField()),
                ('is_verified', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='seller_created_by', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='seller_updated_by', to=settings.AUTH_USER_MODEL)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='seller',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.seller'),
        ),
        migrations.CreateModel(
            name='SubCategory',
            fields=[
                ('subcategory_id', models.AutoField(primary_key=True, serialize=False)),
                ('subcategory_name', models.CharField(max_length=50)),
                ('subcategory_detail', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.category')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subcategory_created_by', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subcategory_updated_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('category', 'subcategory_name')},
            },
        ),
        migrations.AddField(
            model_name='product',
            name='sub_category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.subcategory'),
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('selected_color', models.CharField(blank=True, max_length=50)),
                ('selected_size', models.CharField(blank=True, max_length=50)),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='myapp.cart')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.product')),
            ],
            options={
                'unique_together': {('cart', 'product', 'selected_color', 'selected_size')},
            },
        ),
    ]

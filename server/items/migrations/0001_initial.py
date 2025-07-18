# Generated by Django 4.2.7 on 2025-07-12 05:41

import cloudinary.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('icon', cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='image')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
                'db_table': 'categories',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Favorite',
                'verbose_name_plural': 'Favorites',
                'db_table': 'favorites',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('story', models.TextField(blank=True, help_text='Optional background story of the item')),
                ('tags', models.CharField(blank=True, help_text='Comma-separated tags', max_length=500)),
                ('size', models.CharField(choices=[('xs', 'Extra Small'), ('s', 'Small'), ('m', 'Medium'), ('l', 'Large'), ('xl', 'Extra Large'), ('xxl', 'XXL'), ('3xl', '3XL'), ('one_size', 'One Size')], max_length=10)),
                ('condition', models.CharField(choices=[('new', 'New'), ('like_new', 'Like New'), ('gently_used', 'Gently Used'), ('worn', 'Worn')], max_length=15)),
                ('brand', models.CharField(blank=True, max_length=100)),
                ('color', models.CharField(blank=True, max_length=50)),
                ('material', models.CharField(blank=True, max_length=100)),
                ('primary_image', cloudinary.models.CloudinaryField(max_length=255, verbose_name='image')),
                ('image_2', cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='image')),
                ('image_3', cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='image')),
                ('image_4', cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='image')),
                ('status', models.CharField(choices=[('pending', 'Pending Approval'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('swapped', 'Swapped'), ('redeemed', 'Redeemed')], default='pending', max_length=15)),
                ('is_available', models.BooleanField(default=True)),
                ('points_value', models.PositiveIntegerField(default=0, help_text='Points required for redemption')),
                ('allow_redemption', models.BooleanField(default=True)),
                ('rejection_reason', models.TextField(blank=True)),
                ('admin_notes', models.TextField(blank=True)),
                ('approved_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Item',
                'verbose_name_plural': 'Items',
                'db_table': 'items',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ItemView',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='views', to='items.item')),
            ],
            options={
                'verbose_name': 'Item View',
                'verbose_name_plural': 'Item Views',
                'db_table': 'item_views',
            },
        ),
    ]

from django.db import models
from django.conf import settings
from cloudinary.models import CloudinaryField


class Category(models.Model):
    """
    Clothing categories
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = CloudinaryField('image', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Item(models.Model):
    """
    Clothing items for exchange
    """
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('like_new', 'Like New'),
        ('gently_used', 'Gently Used'),
        ('worn', 'Worn'),
    ]
    
    SIZE_CHOICES = [
        ('xs', 'Extra Small'),
        ('s', 'Small'),
        ('m', 'Medium'),
        ('l', 'Large'),
        ('xl', 'Extra Large'),
        ('xxl', 'XXL'),
        ('3xl', '3XL'),
        ('one_size', 'One Size'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('swapped', 'Swapped'),
        ('redeemed', 'Redeemed'),
    ]
    
    # Basic information
    title = models.CharField(max_length=200)
    description = models.TextField()
    story = models.TextField(blank=True, help_text="Optional background story of the item")
    
    # Categorization
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    
    # Physical attributes
    size = models.CharField(max_length=10, choices=SIZE_CHOICES)
    condition = models.CharField(max_length=15, choices=CONDITION_CHOICES)
    brand = models.CharField(max_length=100, blank=True)
    color = models.CharField(max_length=50, blank=True)
    material = models.CharField(max_length=100, blank=True)
    
    # Images
    primary_image = CloudinaryField('image')
    image_2 = CloudinaryField('image', null=True, blank=True)
    image_3 = CloudinaryField('image', null=True, blank=True)
    image_4 = CloudinaryField('image', null=True, blank=True)
    
    # Ownership and status
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='items')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    is_available = models.BooleanField(default=True)
    
    # Redemption settings
    points_value = models.PositiveIntegerField(default=0, help_text="Points required for redemption")
    allow_redemption = models.BooleanField(default=True)
    
    # Admin fields
    rejection_reason = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='approved_items'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'items'
        verbose_name = 'Item'
        verbose_name_plural = 'Items'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'is_available']),
            models.Index(fields=['category', 'size']),
            models.Index(fields=['owner']),
        ]
    
    def __str__(self):
        return f"{self.title} by {self.owner.full_name}"
    
    @property
    def tag_list(self):
        """Return tags as a list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []
    
    @property
    def image_urls(self):
        """Return all image URLs"""
        images = []
        if self.primary_image:
            images.append(self.primary_image.url)
        if self.image_2:
            images.append(self.image_2.url)
        if self.image_3:
            images.append(self.image_3.url)
        if self.image_4:
            images.append(self.image_4.url)
        return images
    
    def save(self, *args, **kwargs):
        # Set default points value based on condition
        if not self.points_value:
            points_map = {
                'new': 100,
                'like_new': 75,
                'gently_used': 50,
                'worn': 25,
            }
            self.points_value = points_map.get(self.condition, 50)
        
        super().save(*args, **kwargs)


class ItemView(models.Model):
    """
    Track item views for analytics
    """
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='item_views'
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'item_views'
        verbose_name = 'Item View'
        verbose_name_plural = 'Item Views'
        indexes = [
            models.Index(fields=['item', 'created_at']),
        ]
    
    def __str__(self):
        return f"View of {self.item.title}"


class Favorite(models.Model):
    """
    User favorites/wishlist
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='favorited_by')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'favorites'
        unique_together = ['user', 'item']
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.full_name} favorites {self.item.title}"

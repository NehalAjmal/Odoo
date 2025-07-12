from django.contrib.auth.models import AbstractUser
from django.db import models
from cloudinary.models import CloudinaryField


class User(AbstractUser):
    """
    Custom User model for ReWear platform
    """
    email = models.EmailField(unique=True)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    profile_picture = CloudinaryField('image', null=True, blank=True)
    
    # Gamification fields
    points = models.PositiveIntegerField(default=0)
    green_score = models.FloatField(default=0.0)
    items_listed_count = models.PositiveIntegerField(default=0)
    swaps_completed_count = models.PositiveIntegerField(default=0)
    
    # Settings
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    mystery_box_enabled = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def calculate_green_score(self):
        """Calculate user's environmental impact score"""
        from django.conf import settings
        multiplier = settings.REWEAR_SETTINGS.get('GREEN_SCORE_MULTIPLIER', 1.5)
        
        # Simple formula: items listed + swaps completed * multiplier
        score = (self.items_listed_count + (self.swaps_completed_count * multiplier))
        self.green_score = round(score, 2)
        self.save(update_fields=['green_score'])
        return self.green_score


class Badge(models.Model):
    """
    Achievement badges for users
    """
    BADGE_TYPES = [
        ('first_swap', 'First Swap'),
        ('eco_hero', 'Eco Hero'),
        ('five_items', '5 Items Listed'),
        ('mystery_master', 'Mystery Match Completed'),
        ('green_warrior', 'Green Warrior'),
        ('community_champion', 'Community Champion'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    badge_type = models.CharField(max_length=20, choices=BADGE_TYPES, unique=True)
    icon = CloudinaryField('image', null=True, blank=True)
    points_required = models.PositiveIntegerField(default=0)
    swaps_required = models.PositiveIntegerField(default=0)
    items_required = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'badges'
        verbose_name = 'Badge'
        verbose_name_plural = 'Badges'
    
    def __str__(self):
        return self.name


class UserBadge(models.Model):
    """
    Junction table for user badges
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_badges'
        unique_together = ['user', 'badge']
        verbose_name = 'User Badge'
        verbose_name_plural = 'User Badges'
    
    def __str__(self):
        return f"{self.user.full_name} - {self.badge.name}"


class Notification(models.Model):
    """
    User notifications
    """
    NOTIFICATION_TYPES = [
        ('swap_request', 'Swap Request'),
        ('swap_accepted', 'Swap Accepted'),
        ('swap_rejected', 'Swap Rejected'),
        ('swap_completed', 'Swap Completed'),
        ('item_approved', 'Item Approved'),
        ('item_rejected', 'Item Rejected'),
        ('badge_earned', 'Badge Earned'),
        ('mystery_box', 'Mystery Box'),
        ('general', 'General'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    is_read = models.BooleanField(default=False)
    
    # Optional foreign key references
    related_item_id = models.PositiveIntegerField(null=True, blank=True)
    related_swap_id = models.PositiveIntegerField(null=True, blank=True)
    related_user_id = models.PositiveIntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
    
    def __str__(self):
        return f"{self.user.full_name} - {self.title}"

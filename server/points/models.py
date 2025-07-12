from django.db import models
from django.conf import settings
from django.utils import timezone


class PointTransaction(models.Model):
    """
    Track all point transactions for users
    """
    TRANSACTION_TYPES = [
        ('earned_listing', 'Earned from Item Listing'),
        ('earned_swap', 'Earned from Completed Swap'),
        ('earned_referral', 'Earned from Referral'),
        ('earned_badge', 'Earned from Badge Achievement'),
        ('earned_bonus', 'Bonus Points'),
        ('spent_redemption', 'Spent on Item Redemption'),
        ('spent_premium', 'Spent on Premium Features'),
        ('admin_adjustment', 'Admin Adjustment'),
        ('expired', 'Points Expired'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='point_transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    points = models.IntegerField()  # Can be negative for spending
    description = models.CharField(max_length=500)
    
    # Optional references
    related_item_id = models.PositiveIntegerField(null=True, blank=True)
    related_swap_id = models.PositiveIntegerField(null=True, blank=True)
    related_badge_id = models.PositiveIntegerField(null=True, blank=True)
    
    # Balance tracking
    balance_before = models.PositiveIntegerField()
    balance_after = models.PositiveIntegerField()
    
    # Admin fields
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='created_transactions'
    )
    admin_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'point_transactions'
        verbose_name = 'Point Transaction'
        verbose_name_plural = 'Point Transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['transaction_type']),
        ]
    
    def __str__(self):
        action = "earned" if self.points > 0 else "spent"
        return f"{self.user.full_name} {action} {abs(self.points)} points"
    
    @classmethod
    def award_points(cls, user, points, transaction_type, description, **kwargs):
        """
        Award points to a user and create transaction record
        """
        balance_before = user.points
        user.points += points
        user.save(update_fields=['points'])
        
        return cls.objects.create(
            user=user,
            transaction_type=transaction_type,
            points=points,
            description=description,
            balance_before=balance_before,
            balance_after=user.points,
            **kwargs
        )
    
    @classmethod
    def spend_points(cls, user, points, transaction_type, description, **kwargs):
        """
        Spend user's points and create transaction record
        """
        if user.points < points:
            raise ValueError("Insufficient points")
        
        balance_before = user.points
        user.points -= points
        user.save(update_fields=['points'])
        
        return cls.objects.create(
            user=user,
            transaction_type=transaction_type,
            points=-points,  # Negative for spending
            description=description,
            balance_before=balance_before,
            balance_after=user.points,
            **kwargs
        )


class PointsRedemption(models.Model):
    """
    Track point redemptions for items
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('fulfilled', 'Fulfilled'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='redemptions')
    item = models.ForeignKey('items.Item', on_delete=models.CASCADE, related_name='redemptions')
    points_spent = models.PositiveIntegerField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    
    # Admin fields
    rejection_reason = models.TextField(blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='approved_redemptions'
    )
    admin_notes = models.TextField(blank=True)
    
    # Related transaction
    transaction = models.OneToOneField(
        PointTransaction, 
        on_delete=models.CASCADE, 
        related_name='redemption'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'points_redemptions'
        verbose_name = 'Points Redemption'
        verbose_name_plural = 'Points Redemptions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['item']),
        ]
    
    def __str__(self):
        return f"{self.user.full_name} redeemed {self.item.title} for {self.points_spent} points"


class PointsSettings(models.Model):
    """
    Global points system settings (admin configurable)
    """
    SETTING_TYPES = [
        ('listing_reward', 'Points for Listing Item'),
        ('swap_reward', 'Points for Completing Swap'),
        ('referral_reward', 'Points for Successful Referral'),
        ('badge_bonus', 'Bonus Points for Badge'),
        ('daily_login', 'Daily Login Bonus'),
        ('review_bonus', 'Points for Leaving Review'),
    ]
    
    setting_type = models.CharField(max_length=20, choices=SETTING_TYPES, unique=True)
    points_value = models.PositiveIntegerField()
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    
    # Optional conditions
    conditions = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'points_settings'
        verbose_name = 'Points Setting'
        verbose_name_plural = 'Points Settings'
    
    def __str__(self):
        return f"{self.get_setting_type_display()}: {self.points_value} points"


class ReferralCode(models.Model):
    """
    Referral codes for earning bonus points
    """
    code = models.CharField(max_length=20, unique=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='referral_codes')
    uses_count = models.PositiveIntegerField(default=0)
    max_uses = models.PositiveIntegerField(default=10)
    
    points_for_referrer = models.PositiveIntegerField(default=50)
    points_for_referee = models.PositiveIntegerField(default=25)
    
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'referral_codes'
        verbose_name = 'Referral Code'
        verbose_name_plural = 'Referral Codes'
    
    def __str__(self):
        return f"Referral code: {self.code} by {self.owner.full_name}"
    
    def is_valid(self):
        """Check if referral code is still valid"""
        if not self.is_active:
            return False
        if self.uses_count >= self.max_uses:
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        return True


class ReferralUse(models.Model):
    """
    Track referral code usage
    """
    referral_code = models.ForeignKey(ReferralCode, on_delete=models.CASCADE, related_name='uses')
    referred_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='referral_used')
    
    # Points awarded
    referrer_transaction = models.ForeignKey(
        PointTransaction, 
        on_delete=models.CASCADE, 
        related_name='referrer_referral'
    )
    referee_transaction = models.ForeignKey(
        PointTransaction, 
        on_delete=models.CASCADE, 
        related_name='referee_referral'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'referral_uses'
        unique_together = ['referral_code', 'referred_user']
        verbose_name = 'Referral Use'
        verbose_name_plural = 'Referral Uses'
    
    def __str__(self):
        return f"{self.referred_user.full_name} used {self.referral_code.code}"

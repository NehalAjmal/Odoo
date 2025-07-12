from django.db import models
from django.conf import settings


class Swap(models.Model):
    """
    Clothing swap requests and transactions
    """
    STATUS_CHOICES = [
        ('requested', 'Requested'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('in_transit', 'In Transit'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    SWAP_TYPES = [
        ('item_swap', 'Item for Item'),
        ('point_redemption', 'Point Redemption'),
        ('mystery_box', 'Mystery Box'),
    ]
    
    # Basic swap information
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='sent_swaps'
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='received_swaps'
    )
    
    # Items involved
    requested_item = models.ForeignKey(
        'items.Item', 
        on_delete=models.CASCADE, 
        related_name='swap_requests'
    )
    offered_item = models.ForeignKey(
        'items.Item', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='swap_offers'
    )
    
    # Swap details
    swap_type = models.CharField(max_length=20, choices=SWAP_TYPES, default='item_swap')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='requested')
    points_used = models.PositiveIntegerField(default=0)
    
    # Messages
    request_message = models.TextField(blank=True)
    response_message = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)
    
    # Tracking information
    shipping_info = models.JSONField(default=dict, blank=True)
    tracking_number = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'swaps'
        verbose_name = 'Swap'
        verbose_name_plural = 'Swaps'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['requester', 'status']),
            models.Index(fields=['owner', 'status']),
            models.Index(fields=['requested_item']),
        ]
    
    def __str__(self):
        return f"Swap: {self.requester.full_name} → {self.owner.full_name} ({self.requested_item.title})"
    
    @property
    def is_point_redemption(self):
        return self.swap_type == 'point_redemption'
    
    @property
    def is_mystery_box(self):
        return self.swap_type == 'mystery_box'
    
    def can_be_accepted(self):
        """Check if swap can be accepted"""
        return self.status == 'requested'
    
    def can_be_cancelled(self):
        """Check if swap can be cancelled"""
        return self.status in ['requested', 'accepted', 'in_transit']


class SwapFeedback(models.Model):
    """
    Feedback for completed swaps
    """
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    
    swap = models.ForeignKey(Swap, on_delete=models.CASCADE, related_name='feedback')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reviewed_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='received_feedback'
    )
    
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    
    # Specific feedback categories
    item_condition_rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    communication_rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    shipping_rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'swap_feedback'
        unique_together = ['swap', 'reviewer']
        verbose_name = 'Swap Feedback'
        verbose_name_plural = 'Swap Feedback'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Feedback: {self.reviewer.full_name} → {self.reviewed_user.full_name} ({self.rating}★)"


class MysteryBox(models.Model):
    """
    Mystery box events and matching
    """
    MYSTERY_BOX_STATUS = [
        ('active', 'Active'),
        ('matching', 'Matching in Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Participation criteria
    min_items = models.PositiveIntegerField(default=1)
    max_participants = models.PositiveIntegerField(default=100)
    
    # Timing
    registration_deadline = models.DateTimeField()
    matching_date = models.DateTimeField()
    
    status = models.CharField(max_length=15, choices=MYSTERY_BOX_STATUS, default='active')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'mystery_boxes'
        verbose_name = 'Mystery Box'
        verbose_name_plural = 'Mystery Boxes'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class MysteryBoxParticipant(models.Model):
    """
    Users participating in mystery box events
    """
    mystery_box = models.ForeignKey(MysteryBox, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ManyToManyField('items.Item', related_name='mystery_box_entries')
    
    preferences = models.JSONField(default=dict, blank=True)  # Size, style, color preferences
    notes = models.TextField(blank=True)
    
    # Matching results
    matched_with = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='mystery_box_matches'
    )
    match_score = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'mystery_box_participants'
        unique_together = ['mystery_box', 'user']
        verbose_name = 'Mystery Box Participant'
        verbose_name_plural = 'Mystery Box Participants'
    
    def __str__(self):
        return f"{self.user.full_name} in {self.mystery_box.title}"


class SwapMessage(models.Model):
    """
    Messages between users during swap negotiations
    """
    swap = models.ForeignKey(Swap, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'swap_messages'
        verbose_name = 'Swap Message'
        verbose_name_plural = 'Swap Messages'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message from {self.sender.full_name} in swap #{self.swap.id}"

# Yeh app DONORS aur RECIPIENTS ko aapas mein match karega - jaise shaadi.com mein ladka-ladki ko match karte hain, waise hi organ donation ke liye.


from django.db import models
from django.contrib.auth import get_user_model
from profiles.models import DonorProfile, RecipientProfile

CustomUser = get_user_model()

class OrganMatch(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    )
    
    donor = models.ForeignKey(DonorProfile, on_delete=models.CASCADE, related_name='matches')
    recipient = models.ForeignKey(RecipientProfile, on_delete=models.CASCADE, related_name='matches')
    match_score = models.FloatField(help_text="ML-generated compatibility score (0-100)")
    organs_matched = models.JSONField(help_text="List of organs that match")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(help_text="Match expiration date")
    
    class Meta:
        unique_together = ('donor', 'recipient')
        ordering = ['-match_score', '-created_at']
    
    def __str__(self):
        return f"Match: {self.donor.user.username} -> {self.recipient.user.username} ({self.match_score}%)"
    
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at

class MatchMessage(models.Model):
    match = models.ForeignKey(OrganMatch, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"Message from {self.sender.username}"

class MatchPreference(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    max_distance = models.IntegerField(default=100, help_text="Maximum distance in miles")
    min_match_score = models.IntegerField(default=70, help_text="Minimum match score to show")
    notify_new_matches = models.BooleanField(default=True)
    notify_messages = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Preferences for {self.user.username}"
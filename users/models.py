from django.db import models
from django.utils import timezone
from datetime import timedelta

class UserProfile(models.Model):
    wallet_address = models.CharField(max_length=100, unique=True)
    has_nft = models.BooleanField(default=False)
    points = models.IntegerField(default=0)
    access_start_time = models.DateTimeField(null=True, blank=True)
    access_expiry_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    personality_notes = models.TextField(blank=True, null=True) 

    def __str__(self):
        return self.wallet_address

    def grant_access(self):
        """Grant 24-hour access starting now."""
        now = timezone.now()
        self.access_start_time = now
        self.access_expiry_time = now + timedelta(hours=24)
        self.save()

    def has_active_access(self):
        """Check if user has valid active access."""
        if self.access_expiry_time and timezone.now() < self.access_expiry_time:
            return True
        return False

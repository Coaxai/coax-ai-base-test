from django.db import models
from users.models import UserProfile

class ChatSession(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    active = models.BooleanField(default=True)

    def _str_(self):
        return f"Session for {self.user.wallet_address} ({self.started_at})"


class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE)
    sender = models.CharField(max_length=10, default='user')  # 'user' or 'ai'
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"{self.sender.upper()}: {self.content[:30]}"


class PrizeConfig(models.Model):
    prize_name = models.CharField(
        max_length=255,
        help_text="Title or description of the prize (e.g., 100 $BERA, NFT, Whitelist)"
    )
    prize_description = models.TextField(
        blank=True,
        null=True,
        help_text="Optional detailed description of the prize."
    )
    trigger_phrases = models.TextField(
        help_text="List of specific phrases that trigger a win, separated by commas."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def _str_(self):
        return self.prize_name


class Winner(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    prize = models.ForeignKey(PrizeConfig, on_delete=models.CASCADE)
    won_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"{self.user.wallet_address} won {self.prize.prize_name}"
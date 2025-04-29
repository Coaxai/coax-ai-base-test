from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('wallet_address', 'has_nft', 'points', 'access_start_time', 'access_expiry_time', 'created_at')
    search_fields = ('wallet_address',)
    list_filter = ('has_nft',)
    ordering = ('-created_at',)

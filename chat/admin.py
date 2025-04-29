from django.contrib import admin
from .models import ChatSession, ChatMessage, PrizeConfig, Winner


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'started_at', 'expires_at', 'active')
    list_filter = ('active', 'started_at')
    search_fields = ('user__wallet_address',)
    ordering = ('-started_at',)


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'sender', 'created_at')
    list_filter = ('sender', 'created_at')
    search_fields = ('session_user_wallet_address', 'content')
    ordering = ('-created_at',)


@admin.register(PrizeConfig)
class PrizeConfigAdmin(admin.ModelAdmin):
    list_display = ('prize_name', 'prize_amount', 'active', 'created_at')
    list_filter = ('active', 'created_at')
    search_fields = ('prize_name', 'trigger_phrases')
    ordering = ('-created_at',)
    actions = ['deactivate_all']

    def deactivate_all(self, request, queryset):
        queryset.update(active=False)
    deactivate_all.short_description = "Deactivate selected prizes"


@admin.register(Winner)
class WinnerAdmin(admin.ModelAdmin):
    list_display = ('user', 'prize', 'won_at')
    list_filter = ('won_at', 'prize')
    search_fields = ('user_wallet_address', 'prize_prize_name')
    ordering = ('-won_at',)
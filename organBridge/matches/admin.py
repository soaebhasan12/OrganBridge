from django.contrib import admin
from .models import OrganMatch, MatchMessage, MatchPreference

@admin.register(OrganMatch)
class OrganMatchAdmin(admin.ModelAdmin):
    list_display = ('donor', 'recipient', 'match_score', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('donor__user__username', 'recipient__user__username')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(MatchMessage)
class MatchMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'match', 'timestamp', 'is_read')
    list_filter = ('timestamp', 'is_read')
    search_fields = ('sender__username', 'message')

@admin.register(MatchPreference)
class MatchPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'max_distance', 'min_match_score')
    search_fields = ('user__username',)
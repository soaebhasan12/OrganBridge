from django.contrib import admin
from .models import DonorProfile, RecipientProfile

@admin.register(DonorProfile)
class DonorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'health_status', 'is_available', 'organs_donating_list', 'created_at')
    list_filter = ('health_status', 'is_available', 'smoking_status', 'alcohol_use', 'created_at')
    search_fields = ('user__username', 'user__email', 'medical_history')
    readonly_fields = ('created_at', 'updated_at', 'bmi')
    
    def organs_donating_list(self, obj):
        return ", ".join(obj.get_organs_list())
    organs_donating_list.short_description = 'Organs Donating'

@admin.register(RecipientProfile)
class RecipientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'urgency_level', 'organs_needed_list', 'insurance_coverage', 'created_at')
    list_filter = ('urgency_level', 'insurance_coverage', 'created_at')
    search_fields = ('user__username', 'user__email', 'medical_condition', 'current_hospital')
    readonly_fields = ('created_at', 'updated_at')
    
    def organs_needed_list(self, obj):
        return ", ".join(obj.get_organs_list())
    organs_needed_list.short_description = 'Organs Needed'
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    
    list_display = ('username', 'email', 'user_type', 'blood_type', 'city', 'state', 'is_staff')
    list_filter = ('user_type', 'blood_type', 'is_staff', 'is_superuser', 'is_active')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('email', 'phone_number', 'date_of_birth', 'blood_type')}),
        ('Location', {'fields': ('city', 'state', 'zip_code', 'location')}),
        ('Permissions', {'fields': ('user_type', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'user_type', 'password1', 'password2', 
                      'phone_number', 'blood_type', 'city', 'state')}
        ),
    )
    
    search_fields = ('username', 'email', 'city', 'state')
    ordering = ('-created_at',)

admin.site.register(CustomUser, CustomUserAdmin)
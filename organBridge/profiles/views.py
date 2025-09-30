from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from accounts.models import CustomUser
from .models import DonorProfile, RecipientProfile
from .forms import DonorProfileForm, RecipientProfileForm

@login_required
def profile_dashboard(request):
    """User ka main dashboard based on their type"""
    user = request.user
    
    if user.is_donor():
        return donor_dashboard(request)
    elif user.is_recipient():
        return recipient_dashboard(request)
    else:
        messages.error(request, 'Please complete your profile setup first.')
        return redirect('profile_setup')

@login_required
def donor_dashboard(request):
    """Donor-specific dashboard"""
    if not request.user.is_donor():
        messages.error(request, 'Access denied. This page is for donors only.')
        return redirect('profile_dashboard')
    
    donor_profile = get_object_or_404(DonorProfile, user=request.user)
    
    # Dashboard statistics
    context = {
        'donor': donor_profile,
        'profile_complete': True,
        'organs_count': len(donor_profile.organs_donating),
        'last_update': donor_profile.updated_at,
    }
    
    return render(request, 'profiles/donor_dashboard.html', context)


@login_required
def recipient_dashboard(request):
    """Recipient-specific dashboard"""
    if not request.user.is_recipient():
        messages.error(request, 'Access denied. This page is for recipients only.')
        return redirect('profiles:profile_dashboard')
    
    recipient_profile = get_object_or_404(RecipientProfile, user=request.user)
    
    context = {
        'recipient': recipient_profile,
        'profile_complete': True,
        'urgency_color': recipient_profile.get_urgency_display_color(),
        'last_update': recipient_profile.updated_at,
    }
    
    return render(request, 'profiles/recipient_dashboard.html', context)

@login_required
def profile_setup(request):
    """Initial profile setup based on user type"""
    user = request.user
    
    if hasattr(user, 'donor_profile') or hasattr(user, 'recipient_profile'):
        messages.info(request, 'Your profile is already set up.')
        return redirect('profile_dashboard')
    
    if request.method == 'POST':
        if user.is_donor():
            form = DonorProfileForm(request.POST)
        else:
            form = RecipientProfileForm(request.POST)
        
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = user
            profile.save()
            
            messages.success(request, 'Profile setup completed successfully!')
            return redirect('profile_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        if user.is_donor():
            form = DonorProfileForm()
        else:
            form = RecipientProfileForm()
    
    return render(request, 'profiles/profile_setup.html', {
        'form': form,
        'user_type': user.get_user_type_display()
    })

@login_required
def edit_profile(request):
    """Edit existing profile"""
    user = request.user
    
    if user.is_donor():
        profile = get_object_or_404(DonorProfile, user=user)
        form_class = DonorProfileForm
        template = 'profiles/edit_donor_profile.html'
    else:
        profile = get_object_or_404(RecipientProfile, user=user)
        form_class = RecipientProfileForm
        template = 'profiles/edit_recipient_profile.html'
    
    if request.method == 'POST':
        form = form_class(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = form_class(instance=profile)
    
    return render(request, template, {
        'form': form,
        'profile': profile
    })

@login_required
def profile_view(request, user_id=None):
    """Public profile view (for matching)"""
    if user_id:
        user = get_object_or_404(CustomUser, id=user_id)
    else:
        user = request.user
    
    # Check if user can view this profile
    if user != request.user and not (
        (request.user.is_donor() and user.is_recipient()) or 
        (request.user.is_recipient() and user.is_donor())
    ):
        messages.error(request, 'You cannot view this profile.')
        return redirect('profile_dashboard')
    
    context = {}
    if user.is_donor():
        context['profile'] = get_object_or_404(DonorProfile, user=user)
        context['profile_type'] = 'donor'
    else:
        context['profile'] = get_object_or_404(RecipientProfile, user=user)
        context['profile_type'] = 'recipient'
    
    context['viewed_user'] = user
    return render(request, 'profiles/public_profile.html', context)

@login_required
def toggle_availability(request):
    """Donor availability toggle (AJAX)"""
    if not request.user.is_donor():
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        donor_profile = get_object_or_404(DonorProfile, user=request.user)
        donor_profile.is_available = not donor_profile.is_available
        donor_profile.save()
        
        return JsonResponse({
            'success': True,
            'is_available': donor_profile.is_available,
            'message': 'Availability updated successfully!'
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
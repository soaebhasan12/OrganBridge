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
    
    # Use direct database queries instead of hasattr()
    try:
        # Check if donor profile exists
        if user.user_type == 'donor':
            if DonorProfile.objects.filter(user=user).exists():
                return donor_dashboard(request)
            else:
                messages.info(request, 'Please complete your donor profile setup first.')
                return redirect('profiles:profile_setup')
        
        # Check if recipient profile exists  
        elif user.user_type == 'recipient':
            if RecipientProfile.objects.filter(user=user).exists():
                return recipient_dashboard(request)
            else:
                messages.info(request, 'Please complete your recipient profile setup first.')
                return redirect('profiles:profile_setup')
        
        # If user type is not set or invalid
        else:
            messages.error(request, 'User type not set. Please contact support.')
            return redirect('profiles:profile_setup')
            
    except Exception as e:
        # If there's any error, redirect to profile setup
        messages.error(request, 'Profile not found. Please complete your profile setup.')
        return redirect('profiles:profile_setup')
    

@login_required
def donor_dashboard(request):
    """Donor-specific dashboard"""
    if not request.user.is_donor():
        messages.error(request, 'Access denied. This page is for donors only.')
        return redirect('profiles:profile_dashboard')
    
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
    
    # Check if profile already exists using database query
    try:
        if DonorProfile.objects.filter(user=user).exists() or RecipientProfile.objects.filter(user=user).exists():
            messages.info(request, 'Your profile is already set up.')
            return redirect('profiles:profile_dashboard')
    except Exception:
        # Handle any database errors
        pass
    
    organ_choices = DonorProfile.ORGANS_CHOICES
    
    if request.method == 'POST':
        # Determine user type safely
        if hasattr(user, 'user_type') and user.user_type == 'donor':
            form = DonorProfileForm(request.POST)
            profile_model = DonorProfile
        elif hasattr(user, 'user_type') and user.user_type == 'recipient':
            form = RecipientProfileForm(request.POST)
            profile_model = RecipientProfile
        elif hasattr(user, 'is_donor') and user.is_donor():
            form = DonorProfileForm(request.POST)
            profile_model = DonorProfile
        elif hasattr(user, 'is_recipient') and user.is_recipient():
            form = RecipientProfileForm(request.POST)
            profile_model = RecipientProfile
        else:
            messages.error(request, 'Unable to determine user type.')
            return redirect('profiles:profile_dashboard')
        
        if form.is_valid():
            try:
                # Final database check to prevent duplicates
                if DonorProfile.objects.filter(user=user).exists() or RecipientProfile.objects.filter(user=user).exists():
                    messages.info(request, 'Your profile is already set up.')
                    return redirect('profiles:profile_dashboard')
                
                # Create profile using get_or_create to handle race conditions
                profile, created = profile_model.objects.get_or_create(
                    user=user,
                    defaults=form.cleaned_data
                )
                
                if not created:
                    # Update existing profile
                    for field, value in form.cleaned_data.items():
                        setattr(profile, field, value)
                    profile.save()
                    messages.info(request, 'Profile updated successfully!')
                else:
                    messages.success(request, 'Profile setup completed successfully!')
                
                return redirect('profiles:profile_dashboard')
                
            except Exception as e:
                messages.error(request, f'Error creating profile: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Pre-fill form if profile exists, otherwise create empty form
        try:
            if hasattr(user, 'user_type') and user.user_type == 'donor':
                profile = DonorProfile.objects.get(user=user)
                form = DonorProfileForm(instance=profile)
            elif hasattr(user, 'user_type') and user.user_type == 'recipient':
                profile = RecipientProfile.objects.get(user=user)
                form = RecipientProfileForm(instance=profile)
            elif hasattr(user, 'is_donor') and user.is_donor():
                profile = DonorProfile.objects.get(user=user)
                form = DonorProfileForm(instance=profile)
            elif hasattr(user, 'is_recipient') and user.is_recipient():
                profile = RecipientProfile.objects.get(user=user)
                form = RecipientProfileForm(instance=profile)
            else:
                # Create empty form for new profile
                if hasattr(user, 'user_type') and user.user_type == 'donor':
                    form = DonorProfileForm()
                else:
                    form = RecipientProfileForm()
        except (DonorProfile.DoesNotExist, RecipientProfile.DoesNotExist):
            # Create empty form for new profile
            if hasattr(user, 'user_type') and user.user_type == 'donor':
                form = DonorProfileForm()
            else:
                form = RecipientProfileForm()
    
    return render(request, 'profiles/profile_setup.html', {
        'form': form,
        'user_type': getattr(user, 'user_type', 'recipient'),  # Default to recipient if not set
        'organ_choices': organ_choices,
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
            return redirect('profiles:profile_dashboard')
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
        return redirect('profiles:profile_dashboard')
    
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
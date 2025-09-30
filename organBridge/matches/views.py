from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from profiles.models import DonorProfile, RecipientProfile
from ml_model.matching_algorithm import OrganMatchingEngine
from .models import OrganMatch, MatchMessage, MatchPreference
from .forms import MatchPreferenceForm, MessageForm

@login_required
def find_matches(request):
    """Find matches for the current user (recipient)"""
    if not request.user.is_recipient():
        messages.error(request, 'Only organ recipients can search for matches.')
        return redirect('profile')
    
    try:
        recipient = RecipientProfile.objects.get(user=request.user)
    except RecipientProfile.DoesNotExist:
        messages.error(request, 'Please complete your recipient profile first.')
        return redirect('edit_profile')  # You'll need to create this view
    
    # Get available donors
    donors = DonorProfile.objects.filter(is_available=True)
    
    if not donors:
        messages.info(request, 'No available donors at the moment. Please check back later.')
        return render(request, 'matches/find_matches.html', {'matches': []})
    
    # Use ML matching engine
    matching_engine = OrganMatchingEngine()
    matches_data = matching_engine.find_matches(recipient, donors)
    
    # Create or update match records
    matches = []
    for match_data in matches_data:
        match, created = OrganMatch.objects.update_or_create(
            donor=match_data['donor'],
            recipient=recipient,
            defaults={
                'match_score': match_data['score'],
                'organs_matched': list(set(match_data['donor'].organs_donating) & set(recipient.organs_needed)),
                'expires_at': timezone.now() + timedelta(days=30),  # 30-day expiration
                'status': 'pending'
            }
        )
        matches.append(match)
    
    return render(request, 'matches/find_matches.html', {
        'matches': matches,
        'recipient': recipient
    })


@login_required
def match_detail(request, match_id):
    """View match details and messages"""
    match = get_object_or_404(OrganMatch, id=match_id)
    
    # Check if user is part of this match
    if request.user not in [match.donor.user, match.recipient.user]:
        messages.error(request, 'You do not have permission to view this match.')
        return redirect('find_matches')
    
    messages_list = MatchMessage.objects.filter(match=match)
    message_form = MessageForm()
    
    if request.method == 'POST' and 'send_message' in request.POST:
        message_form = MessageForm(request.POST)
        if message_form.is_valid():
            new_message = message_form.save(commit=False)
            new_message.match = match
            new_message.sender = request.user
            new_message.save()
            messages.success(request, 'Message sent successfully!')
            return redirect('match_detail', match_id=match_id)
    
    return render(request, 'matches/match_detail.html', {
        'match': match,
        'messages': messages_list,
        'message_form': message_form,
        'other_user': match.recipient.user if request.user == match.donor.user else match.donor.user
    })


@login_required
def update_match_status(request, match_id, status):
    """Update match status (accept/reject)"""
    match = get_object_or_404(OrganMatch, id=match_id)
    
    if request.user not in [match.donor.user, match.recipient.user]:
        messages.error(request, 'You do not have permission to update this match.')
        return redirect('find_matches')
    
    valid_statuses = ['accepted', 'rejected']
    if status not in valid_statuses:
        messages.error(request, 'Invalid status update.')
        return redirect('match_detail', match_id=match_id)
    
    match.status = status
    match.save()
    
    messages.success(request, f'Match {status} successfully!')
    return redirect('match_detail', match_id=match_id)



@login_required
def my_matches(request):
    """Show user's current matches"""
    user_matches = OrganMatch.objects.none()
    
    if request.user.is_donor():
        user_matches = OrganMatch.objects.filter(donor__user=request.user)
    elif request.user.is_recipient():
        user_matches = OrganMatch.objects.filter(recipient__user=request.user)
    
    # Separate matches by status
    active_matches = user_matches.filter(status__in=['pending', 'accepted']).exclude(expires_at__lt=timezone.now())
    expired_matches = user_matches.filter(status='expired') | user_matches.filter(expires_at__lt=timezone.now())
    rejected_matches = user_matches.filter(status='rejected')
    
    return render(request, 'matches/my_matches.html', {
        'active_matches': active_matches,
        'expired_matches': expired_matches,
        'rejected_matches': rejected_matches
    })


@login_required
def match_preferences(request):
    """Update user's matching preferences"""
    preference, created = MatchPreference.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = MatchPreferenceForm(request.POST, instance=preference)
        if form.is_valid():
            form.save()
            messages.success(request, 'Preferences updated successfully!')
            return redirect('match_preferences')
    else:
        form = MatchPreferenceForm(instance=preference)
    
    return render(request, 'matches/preferences.html', {'form': form})


@login_required
def send_message_ajax(request, match_id):
    """AJAX endpoint for sending messages"""
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        match = get_object_or_404(OrganMatch, id=match_id)
        
        if request.user not in [match.donor.user, match.recipient.user]:
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        message_form = MessageForm(request.POST)
        if message_form.is_valid():
            new_message = message_form.save(commit=False)
            new_message.match = match
            new_message.sender = request.user
            new_message.save()
            
            return JsonResponse({
                'success': True,
                'message': new_message.message,
                'sender': new_message.sender.username,
                'timestamp': new_message.timestamp.strftime('%Y-%m-%d %H:%M')
            })
        else:
            return JsonResponse({'error': 'Invalid message'}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
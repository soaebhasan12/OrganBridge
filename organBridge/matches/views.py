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
    """
    Find matches for recipient using ML algorithm
    """
    if not request.user.is_recipient():
        messages.error(request, 'Only recipients can search for matches.')
        return redirect('profiles:profile_dashboard')
    
    try:
        # Get recipient profile
        recipient = get_object_or_404(RecipientProfile, user=request.user)
        
        # Get all available donors
        donors = DonorProfile.objects.filter(is_available=True)
        
        if not donors.exists():
            messages.warning(request, 'No donors are currently available.')
            return render(request, 'matches/find_matches.html', {
                'recipient': recipient,
                'matches': []
            })
        
        # Use ML matching engine to find best matches
        matching_engine = OrganMatchingEngine()
        matches_data = matching_engine.find_matches(recipient, donors, top_n=10)
        
        # Format matches for template - FIXED: Create OrganMatch objects or pass proper data
        formatted_matches = []
        for match_data in matches_data:
            # Check if OrganMatch already exists, if not create one
            organ_match, created = OrganMatch.objects.get_or_create(
                donor=match_data['donor'],
                recipient=recipient,
                defaults={
                    'match_score': match_data['final_score'],
                    'organs_matched': match_data['compatibility_details']['organs_matched'],
                    'expires_at': timezone.now() + timedelta(days=30),
                    'status': 'pending'
                }
            )
            
            formatted_matches.append({
                'match_id': organ_match.id,  # FIXED: Add match_id for URL generation
                'donor': match_data['donor'],
                'match_score': match_data['final_score'],
                'ml_score': match_data['ml_score'],
                'compatibility': get_compatibility_level(match_data['final_score']),
                'blood_compatible': match_data['compatibility_details']['blood_match'],
                'organs_matched': match_data['compatibility_details']['organs_matched'],
                'same_location': match_data['compatibility_details']['location_same'],
            })
        
        context = {
            'recipient': recipient,
            'matches': formatted_matches,
            'total_matches': len(formatted_matches),
        }
        
        return render(request, 'matches/find_matches.html', context)
        
    except Exception as e:
        messages.error(request, f'Error finding matches: {str(e)}')
        return redirect('profiles:recipient_dashboard')

# Utility Function
def get_compatibility_level(score):
    """
    Convert numerical score to compatibility level
    WHY: Score ko human-readable format mein convert karne ke liye
    WHERE: Template mein display ke liye use hoga
    HOW: Score range ke basis par level return karega
    """
    if score >= 90:
        return 'Excellent'
    elif score >= 75:
        return 'Good'
    elif score >= 60:
        return 'Fair'
    elif score >= 40:
        return 'Poor'
    else:
        return 'Not Compatible'


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
        
        message_text = request.POST.get('message', '').strip()
        if message_text:
            new_message = MatchMessage.objects.create(
                match=match,
                sender=request.user,
                message=message_text
            )
            
            # Return updated messages list HTML
            messages_list = MatchMessage.objects.filter(match=match)
            return render(request, 'matches/_messages_list.html', {
                'messages': messages_list
            })
        else:
            return JsonResponse({'error': 'Empty message'}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)











"""
HACKATHON INTERVIEW QUESTIONS:

1. Q: How does the ML matching algorithm work in your organ matching system?
   A: We use TF-IDF vectorization on donor/recipient features (location, blood type, 
      health status, etc.) and calculate cosine similarity to find compatible matches.
      Business rules are then applied for blood type compatibility, urgency, and distance.

2. Q: How do you handle the case when multiple recipients need the same organ?
   A: The system prioritizes based on:
      - Urgency level (critical > high > medium > low)
      - Compatibility score from ML algorithm
      - Blood type compatibility
      - Geographic proximity
      
3. Q: What happens if no donors are available?
   A: The system displays a message to the recipient and allows them to save their 
      search criteria and get notified when new donors register.

4. Q: How do you ensure data privacy in the matching process?
   A: - Matches are only visible to involved parties (donor/recipient)
      - Permission checks on every view
      - Personal contact info hidden until match acceptance
      - Login required for all matching operations

5. Q: What optimization would you add to scale this to millions of users?
   A: - Cache frequently accessed donor/recipient profiles
      - Use database indexing on search fields (blood_type, organs, location)
      - Implement async task queues (Celery) for ML calculations
      - Add pagination for large result sets
      - Use Redis for real-time match notifications
"""
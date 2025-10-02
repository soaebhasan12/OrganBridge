import random
from accounts.models import CustomUser
from matches.models import MatchPreference

def create_preferences():
    # Clear existing
    MatchPreference.objects.all().delete()
    print('Cleared existing preferences...')
    
    users = CustomUser.objects.all()
    created = 0
    
    for user in users:
        try:
            # Different logic for donors vs recipients
            if user.user_type == 'donor':
                max_distance = random.randint(50, 200)
                min_match_score = random.randint(70, 90)
            else:  # recipient
                max_distance = random.randint(100, 500)
                min_match_score = random.randint(60, 85)
            
            MatchPreference.objects.create(
                user=user,
                max_distance=max_distance,
                min_match_score=min_match_score,
                notify_new_matches=random.choice([True, True, True, False]),  # 75% True
                notify_messages=random.choice([True, False, True, True]),     # 75% True
            )
            created += 1
            print(f'Created preference for {user.username}')
            
        except Exception as e:
            print(f'Error for {user.username}: {e}')
    
    print(f'Created {created} preferences total')

create_preferences()
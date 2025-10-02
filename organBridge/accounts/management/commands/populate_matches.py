import random
from django.core.management.base import BaseCommand
from accounts.models import CustomUser
from matches.models import Match  # Adjust import based on your actual model name

class Command(BaseCommand):
    help = 'Populate matches table based on existing users'

    def handle(self, *args, **options):
        # Get all users
        all_users = list(CustomUser.objects.all())
        donors = [user for user in all_users if user.is_donor()]
        recipients = [user for user in all_users if user.is_recipient()]
        
        self.stdout.write(f'Found {len(donors)} donors and {len(recipients)} recipients')
        
        matches_created = 0
        
        # Create matches between compatible donors and recipients
        for recipient in recipients:
            # Find compatible donors based on blood type and location
            compatible_donors = self.find_compatible_donors(recipient, donors)
            
            if compatible_donors:
                # Create 1-3 matches for each recipient
                num_matches = min(random.randint(1, 3), len(compatible_donors))
                selected_donors = random.sample(compatible_donors, num_matches)
                
                for donor in selected_donors:
                    try:
                        # Create match - adjust fields based on your actual model
                        match = Match(
                            donor=donor,
                            recipient=recipient,
                            match_score=random.randint(50, 100),
                            status=random.choice(['pending', 'approved', 'rejected']),
                            organ_type=random.choice(['kidney', 'liver', 'heart', 'lung']),
                            # Add other fields as per your model
                            created_at=recipient.created_at  # or use timezone.now()
                        )
                        match.save()
                        matches_created += 1
                        
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Match created: {donor.username} -> {recipient.username} '
                                f'({match.organ_type}, Score: {match.match_score}%)'
                            )
                        )
                        
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f'Error creating match {donor.username} -> {recipient.username}: {str(e)}'
                            )
                        )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {matches_created} matches!')
        )
    
    def find_compatible_donors(self, recipient, donors):
        """Find donors compatible with the recipient based on blood type"""
        compatible_donors = []
        
        # Blood type compatibility rules
        compatibility_rules = {
            'A+': ['A+', 'A-', 'O+', 'O-'],
            'A-': ['A-', 'O-'],
            'B+': ['B+', 'B-', 'O+', 'O-'],
            'B-': ['B-', 'O-'],
            'AB+': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],  # Universal recipient
            'AB-': ['A-', 'B-', 'AB-', 'O-'],
            'O+': ['O+', 'O-'],
            'O-': ['O-']  # Universal donor
        }
        
        recipient_blood_type = recipient.blood_type
        compatible_blood_types = compatibility_rules.get(recipient_blood_type, [])
        
        for donor in donors:
            if (donor.blood_type in compatible_blood_types and 
                donor.city == recipient.city):  # Same city for better matching
                compatible_donors.append(donor)
        
        return compatible_donors
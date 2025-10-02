import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import CustomUser
from matches.models import Match

class Command(BaseCommand):
    help = 'Populate matches table based on existing users'

    def handle(self, *args, **options):
        # Clear existing matches
        Match.objects.all().delete()
        self.stdout.write('Cleared existing matches...')
        
        # Get all users
        all_users = list(CustomUser.objects.all())
        donors = [user for user in all_users if user.is_donor()]
        recipients = [user for user in all_users if user.is_recipient()]
        
        self.stdout.write(f'Found {len(donors)} donors and {len(recipients)} recipients')
        
        matches_created = 0
        
        # Blood type compatibility rules (simplified)
        compatibility_rules = {
            'A+': ['A+', 'A-', 'O+', 'O-'],
            'A-': ['A-', 'O-'],
            'B+': ['B+', 'B-', 'O+', 'O-'],
            'B-': ['B-', 'O-'],
            'AB+': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],
            'AB-': ['A-', 'B-', 'AB-', 'O-'],
            'O+': ['O+', 'O-'],
            'O-': ['O-']
        }
        
        # Common organ types with weights (more common organs appear more frequently)
        organ_types = ['kidney'] * 5 + ['liver'] * 3 + ['cornea'] * 4 + ['bone_marrow'] * 2 + ['heart', 'lung', 'pancreas']
        
        for recipient in recipients:
            # Find compatible donors based on blood type
            compatible_blood_types = compatibility_rules.get(recipient.blood_type, [])
            compatible_donors = [
                donor for donor in donors 
                if donor.blood_type in compatible_blood_types
            ]
            
            if compatible_donors:
                # Create 1-2 matches for each recipient
                num_matches = min(random.randint(1, 2), len(compatible_donors))
                selected_donors = random.sample(compatible_donors, num_matches)
                
                for donor in selected_donors:
                    try:
                        # Calculate match score based on various factors
                        base_score = random.randint(60, 85)
                        
                        # Bonus points for same city
                        if donor.city == recipient.city:
                            base_score += 10
                        
                        # Bonus points for age compatibility (simplified)
                        if donor.date_of_birth and recipient.date_of_birth:
                            age_diff = abs((donor.date_of_birth - recipient.date_of_birth).days) / 365
                            if age_diff < 10:
                                base_score += 5
                        
                        match_score = min(100, base_score)
                        
                        # Create match
                        match = Match(
                            donor=donor,
                            recipient=recipient,
                            organ_type=random.choice(organ_types),
                            match_score=match_score,
                            status=random.choices(
                                ['pending', 'approved', 'rejected'],
                                weights=[70, 20, 10]  # 70% pending, 20% approved, 10% rejected
                            )[0],
                            is_urgent=random.choice([True, False, False, False]),  # 25% urgent
                            notes=random.choice([
                                "Good compatibility match",
                                "Potential match based on location",
                                "Blood type compatible",
                                "Urgent case - high priority",
                                "Regular priority match",
                                ""
                            ])
                        )
                        match.save()
                        matches_created += 1
                        
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Match {matches_created}: {donor.username} -> {recipient.username} '
                                f'({match.organ_type}, Blood: {donor.blood_type}->{recipient.blood_type}, '
                                f'Score: {match_score}%, Status: {match.status})'
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
        
        # Display summary
        matches = Match.objects.all()
        status_counts = matches.values('status').annotate(count=models.Count('status'))
        organ_counts = matches.values('organ_type').annotate(count=models.Count('organ_type'))
        
        self.stdout.write("\nMatch Summary:")
        self.stdout.write("Status distribution:")
        for status in status_counts:
            self.stdout.write(f"  {status['status']}: {status['count']}")
        
        self.stdout.write("\nOrgan type distribution:")
        for organ in organ_counts:
            self.stdout.write(f"  {organ['organ_type']}: {organ['count']}")
import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import CustomUser
from matches.models import OrganMatch

class Command(BaseCommand):
    help = 'Populate OrganMatch table with realistic matches between donors and recipients'

    def handle(self, *args, **options):
        # Clear existing matches
        OrganMatch.objects.all().delete()
        self.stdout.write('Cleared existing organ matches...')

        # Get all users
        donors = CustomUser.objects.filter(user_type='donor')
        recipients = CustomUser.objects.filter(user_type='recipient')

        self.stdout.write(f'Found {donors.count()} donors and {recipients.count()} recipients')

        if donors.count() == 0 or recipients.count() == 0:
            self.stdout.write(
                self.style.ERROR('Need both donors and recipients to create matches. Run populate_users first.')
            )
            return

        matches_created = 0
        
        # Common organs for matching
        all_organs = ['kidney', 'liver', 'heart', 'lung', 'pancreas', 'cornea', 'bone_marrow']
        
        # Blood type compatibility rules
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

        for recipient in recipients:
            compatible_donors = []

            # Find compatible donors based on blood type
            compatible_blood_types = compatibility_rules.get(recipient.blood_type, [])
            for donor in donors:
                # Skip if same user (shouldn't happen but just in case)
                if donor.id == recipient.id:
                    continue
                
                # Check blood type compatibility
                if donor.blood_type in compatible_blood_types:
                    compatible_donors.append(donor)

            if compatible_donors:
                # Create 1-3 matches for each recipient
                num_matches = min(random.randint(1, 3), len(compatible_donors))
                selected_donors = random.sample(compatible_donors, num_matches)

                for donor in selected_donors:
                    try:
                        # Calculate base match score
                        base_score = random.uniform(60.0, 95.0)
                        
                        # Bonus for same city (15 points)
                        if donor.city == recipient.city and donor.city:
                            base_score += 15.0
                        # Bonus for same state (10 points)  
                        elif donor.state == recipient.state and donor.state:
                            base_score += 10.0
                        
                        # Bonus for age compatibility (within 15 years)
                        if donor.date_of_birth and recipient.date_of_birth:
                            donor_age = self.calculate_age(donor.date_of_birth)
                            recipient_age = self.calculate_age(recipient.date_of_birth)
                            age_diff = abs(donor_age - recipient_age)
                            if age_diff <= 15:
                                base_score += random.uniform(5.0, 12.0)
                        
                        # Ensure score doesn't exceed 100
                        match_score = min(100.0, round(base_score, 2))
                        
                        # Determine organs matched (1-3 organs)
                        num_organs = random.randint(1, 3)
                        organs_matched = random.sample(all_organs, num_organs)
                        
                        # Set expiration date (30-90 days from now)
                        days_until_expiry = random.randint(30, 90)
                        expires_at = timezone.now() + timedelta(days=days_until_expiry)
                        
                        # Determine status with weighted probabilities
                        status = random.choices(
                            ['pending', 'accepted', 'rejected', 'expired'],
                            weights=[60, 20, 15, 5]  # 60% pending, 20% accepted, etc.
                        )[0]
                        
                        # If status is expired, set expiration in past
                        if status == 'expired':
                            expires_at = timezone.now() - timedelta(days=random.randint(1, 30))
                        
                        # Create the organ match
                        organ_match = OrganMatch(
                            donor=donor,
                            recipient=recipient,
                            match_score=match_score,
                            organs_matched=organs_matched,
                            status=status,
                            expires_at=expires_at
                        )
                        
                        organ_match.save()
                        matches_created += 1

                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Match {matches_created}: {donor.username} → {recipient.username} '
                                f'(Score: {match_score}%, Organs: {", ".join(organs_matched)}, '
                                f'Status: {status})'
                            )
                        )

                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f'Error creating match {donor.username} → {recipient.username}: {str(e)}'
                            )
                        )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {matches_created} organ matches!')
        )
        
        # Display summary statistics
        self.display_summary()

    def calculate_age(self, birth_date):
        """Calculate age from date of birth"""
        today = timezone.now().date()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

    def display_summary(self):
        """Display summary statistics of created matches"""
        matches = OrganMatch.objects.all()
        
        if matches.count() == 0:
            self.stdout.write(self.style.WARNING('No matches were created.'))
            return
            
        self.stdout.write("\n" + "="*50)
        self.stdout.write("ORGAN MATCHES SUMMARY")
        self.stdout.write("="*50)
        
        # Status distribution
        status_counts = {}
        for status in ['pending', 'accepted', 'rejected', 'expired']:
            count = matches.filter(status=status).count()
            status_counts[status] = count
        
        self.stdout.write("\nStatus Distribution:")
        for status, count in status_counts.items():
            percentage = (count / matches.count() * 100)
            self.stdout.write(f"  {status.capitalize()}: {count} ({percentage:.1f}%)")
        
        # Score ranges
        score_ranges = {
            'Excellent (90-100)': (90, 100),
            'Good (75-89)': (75, 90),
            'Fair (60-74)': (60, 75),
            'Poor (<60)': (0, 60)
        }
        
        self.stdout.write("\nMatch Score Distribution:")
        for range_name, (min_score, max_score) in score_ranges.items():
            if max_score == 100:
                count = matches.filter(match_score__gte=min_score).count()
            else:
                count = matches.filter(match_score__gte=min_score, match_score__lt=max_score).count()
            percentage = (count / matches.count() * 100)
            self.stdout.write(f"  {range_name}: {count} ({percentage:.1f}%)")
        
        # Organ distribution
        organ_counts = {}
        for match in matches:
            for organ in match.organs_matched:
                organ_counts[organ] = organ_counts.get(organ, 0) + 1
        
        self.stdout.write("\nOrgan Type Distribution:")
        for organ, count in sorted(organ_counts.items(), key=lambda x: x[1], reverse=True):
            self.stdout.write(f"  {organ.capitalize()}: {count} matches")
        
        self.stdout.write(f"\nTotal matches created: {matches.count()}")
        self.stdout.write("="*50)
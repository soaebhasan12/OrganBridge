import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import CustomUser
from profiles.models import RecipientProfile, DonorProfile

class Command(BaseCommand):
    help = 'Populate RecipientProfile table for existing recipient users'

    def handle(self, *args, **options):
        # Clear existing recipient profiles
        RecipientProfile.objects.all().delete()
        self.stdout.write('Cleared existing recipient profiles...')

        # Get all recipient users from ID 1 to last
        recipients = CustomUser.objects.filter(user_type='recipient').order_by('id')
        
        self.stdout.write(f'Found {recipients.count()} recipient users')

        profiles_created = 0
        
        # Common medical conditions for organ recipients
        medical_conditions = [
            "End-stage renal disease requiring kidney transplant",
            "Chronic liver failure due to hepatitis C",
            "Alcoholic liver disease with cirrhosis",
            "Primary biliary cholangitis with liver failure",
            "Congestive heart failure - ischemic cardiomyopathy",
            "Dilated cardiomyopathy with severe LV dysfunction",
            "Chronic obstructive pulmonary disease with respiratory failure",
            "Idiopathic pulmonary fibrosis",
            "Cystic fibrosis with end-stage lung disease",
            "Type 1 diabetes with pancreatic failure",
            "Short bowel syndrome requiring intestinal transplant",
            "Corneal blindness due to injury",
            "Keratoconus with corneal scarring",
            "Bone marrow failure - aplastic anemia",
            "Acute myeloid leukemia requiring bone marrow transplant"
        ]
        
        # Current treatments
        current_treatments = [
            "Dialysis three times per week",
            "Diuretics and beta-blockers for heart failure",
            "Insulin therapy for diabetes management",
            "Oxygen therapy at 2L/min",
            "Immunosuppressant therapy",
            "Pulmonary rehabilitation program",
            "Nutritional support with TPN",
            "Antiviral therapy for hepatitis",
            "Bronchodilators and corticosteroids",
            "Waiting for suitable donor match"
        ]
        
        # Indian hospitals
        hospitals = [
            "AIIMS Delhi", "Apollo Hospital", "Fortis Hospital", "Max Super Specialty",
            "Medanta - The Medicity", "Sir Ganga Ram Hospital", "Kokilaben Dhirubhai Ambani Hospital",
            "Artemis Hospital", "Narayana Health", "Columbia Asia Hospital",
            "Manipal Hospital", "Global Hospital", "Jaslok Hospital", "Lilavati Hospital"
        ]
        
        # Insurance providers
        insurance_providers = [
            "Star Health Insurance", "HDFC ERGO", "ICICI Lombard", "Bajaj Allianz",
            "New India Assurance", "United India Insurance", "National Insurance",
            "Oriental Insurance", "Reliance General Insurance", "None"
        ]

        for recipient in recipients:
            try:
                # Determine organs needed (1-2 organs typically)
                all_organs = ['kidney', 'liver', 'heart', 'lungs', 'pancreas', 'intestine', 'cornea', 'bone']
                num_organs = random.randint(1, 2)
                organs_needed = random.sample(all_organs, num_organs)
                
                # Urgency level with realistic distribution
                urgency_level = random.choices(
                    ['low', 'medium', 'high', 'critical'],
                    weights=[20, 40, 30, 10]  # 20% low, 40% medium, 30% high, 10% critical
                )[0]
                
                # Diagnosis date (6 months to 10 years ago)
                years_ago = random.randint(1, 10)
                months_ago = random.randint(0, 11)
                diagnosis_date = timezone.now().date() - timedelta(days=(years_ago * 365 + months_ago * 30))
                
                # Preferred hospitals (1-3 hospitals)
                num_hospitals = random.randint(1, 3)
                preferred_hospitals = random.sample(hospitals, num_hospitals)
                
                # Previous transplants (mostly 0, some 1, rarely 2)
                previous_transplants = random.choices([0, 1, 2], weights=[80, 18, 2])[0]
                
                # Insurance coverage (60% have coverage)
                insurance_coverage = random.choices([True, False], weights=[60, 40])[0]
                
                # Lifestyle factors
                smoking_status = random.choices([True, False], weights=[25, 75])[0]
                alcohol_use = random.choices([True, False], weights=[30, 70])[0]
                drug_use = random.choices([True, False], weights=[10, 90])[0]
                
                # Sleep patterns (often disturbed due to medical condition)
                avg_sleep = round(random.uniform(4.0, 8.0), 1)
                
                # Travel preferences based on urgency
                if urgency_level in ['high', 'critical']:
                    max_travel_distance = random.randint(500, 2000)  # Willing to travel far
                    willing_to_relocate = random.choices([True, False], weights=[70, 30])[0]
                else:
                    max_travel_distance = random.randint(50, 300)   # Prefer local
                    willing_to_relocate = random.choices([True, False], weights=[20, 80])[0]
                
                # Create the recipient profile
                recipient_profile = RecipientProfile(
                    user=recipient,
                    organs_needed=organs_needed,
                    urgency_level=urgency_level,
                    medical_condition=random.choice(medical_conditions),
                    diagnosis_date=diagnosis_date,
                    current_treatment=random.choice(current_treatments),
                    preferred_hospitals=preferred_hospitals,
                    current_hospital=random.choice(hospitals),
                    previous_transplants=previous_transplants,
                    insurance_coverage=insurance_coverage,
                    max_travel_distance=max_travel_distance,
                    willing_to_relocate=willing_to_relocate,
                    smoking_status=smoking_status,
                    alcohol_use=alcohol_use,
                    drug_use=drug_use,
                    avg_sleep=avg_sleep,
                    preferred_hospital=random.choice(hospitals),
                    insurance_provider=random.choice(insurance_providers) if insurance_coverage else "None"
                )
                
                recipient_profile.save()
                profiles_created += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Profile {profiles_created}: {recipient.username} - '
                        f'Organs: {", ".join(organs_needed)}, '
                        f'Urgency: {urgency_level}, '
                        f'Diagnosed: {diagnosis_date.strftime("%Y-%m-%d")}'
                    )
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating profile for {recipient.username}: {str(e)}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {profiles_created} recipient profiles!')
        )
        
        # Display summary statistics
        self.display_summary()

    def display_summary(self):
        """Display summary statistics of created recipient profiles"""
        profiles = RecipientProfile.objects.all()
        
        if profiles.count() == 0:
            self.stdout.write(self.style.WARNING('No recipient profiles were created.'))
            return
            
        self.stdout.write("\n" + "="*50)
        self.stdout.write("RECIPIENT PROFILES SUMMARY")
        self.stdout.write("="*50)
        
        # Urgency level distribution
        self.stdout.write("\nUrgency Level Distribution:")
        for urgency in ['low', 'medium', 'high', 'critical']:
            count = profiles.filter(urgency_level=urgency).count()
            percentage = (count / profiles.count() * 100)
            self.stdout.write(f"  {urgency.capitalize()}: {count} ({percentage:.1f}%)")
        
        # Organ needs distribution
        organ_counts = {}
        for profile in profiles:
            for organ in profile.organs_needed:
                organ_counts[organ] = organ_counts.get(organ, 0) + 1
        
        self.stdout.write("\nOrgan Needs Distribution:")
        for organ, count in sorted(organ_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / profiles.count() * 100)
            self.stdout.write(f"  {organ.capitalize()}: {count} ({percentage:.1f}%)")
        
        # Insurance coverage
        insured_count = profiles.filter(insurance_coverage=True).count()
        uninsured_count = profiles.filter(insurance_coverage=False).count()
        self.stdout.write(f"\nInsurance Coverage:")
        self.stdout.write(f"  Insured: {insured_count} ({insured_count/profiles.count()*100:.1f}%)")
        self.stdout.write(f"  Uninsured: {uninsured_count} ({uninsured_count/profiles.count()*100:.1f}%)")
        
        # Previous transplants
        transplant_counts = {}
        for i in range(0, 3):  # 0, 1, 2 previous transplants
            count = profiles.filter(previous_transplants=i).count()
            transplant_counts[i] = count
        
        self.stdout.write(f"\nPrevious Transplants:")
        for count, num in transplant_counts.items():
            percentage = (num / profiles.count() * 100)
            self.stdout.write(f"  {count} previous: {num} ({percentage:.1f}%)")
        
        # Willing to relocate
        relocate_count = profiles.filter(willing_to_relocate=True).count()
        no_relocate_count = profiles.filter(willing_to_relocate=False).count()
        self.stdout.write(f"\nWilling to Relocate:")
        self.stdout.write(f"  Yes: {relocate_count} ({relocate_count/profiles.count()*100:.1f}%)")
        self.stdout.write(f"  No: {no_relocate_count} ({no_relocate_count/profiles.count()*100:.1f}%)")
        
        # Lifestyle factors
        smoking_count = profiles.filter(smoking_status=True).count()
        alcohol_count = profiles.filter(alcohol_use=True).count()
        drug_count = profiles.filter(drug_use=True).count()
        
        self.stdout.write(f"\nLifestyle Factors:")
        self.stdout.write(f"  Smokers: {smoking_count} ({smoking_count/profiles.count()*100:.1f}%)")
        self.stdout.write(f"  Alcohol Users: {alcohol_count} ({alcohol_count/profiles.count()*100:.1f}%)")
        self.stdout.write(f"  Drug Users: {drug_count} ({drug_count/profiles.count()*100:.1f}%)")
        
        # Travel distance ranges
        distance_ranges = {
            'Local (0-100mi)': (0, 100),
            'Regional (101-300mi)': (101, 300),
            'State-wide (301-500mi)': (301, 500),
            'National (500+mi)': (501, 2000)
        }
        
        self.stdout.write("\nMax Travel Distance:")
        for range_name, (min_dist, max_dist) in distance_ranges.items():
            count = profiles.filter(max_travel_distance__gte=min_dist, max_travel_distance__lte=max_dist).count()
            percentage = (count / profiles.count() * 100)
            self.stdout.write(f"  {range_name}: {count} ({percentage:.1f}%)")
        
        # Sleep patterns
        sleep_ranges = {
            'Poor (<5 hours)': (0, 5),
            'Fair (5-6 hours)': (5, 6),
            'Good (6-7 hours)': (6, 7),
            'Very Good (7+ hours)': (7, 10)
        }
        
        self.stdout.write("\nAverage Sleep Patterns:")
        for range_name, (min_sleep, max_sleep) in sleep_ranges.items():
            count = profiles.filter(avg_sleep__gte=min_sleep, avg_sleep__lt=max_sleep).count()
            percentage = (count / profiles.count() * 100)
            self.stdout.write(f"  {range_name}: {count} ({percentage:.1f}%)")
        
        self.stdout.write(f"\nTotal recipient profiles created: {profiles.count()}")
        self.stdout.write("="*50)
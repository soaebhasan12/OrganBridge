import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import CustomUser
from profiles.models import DonorProfile

class Command(BaseCommand):
    help = 'Populate DonorProfile table for existing donor users'

    def handle(self, *args, **options):
        # Clear existing donor profiles
        DonorProfile.objects.all().delete()
        self.stdout.write('Cleared existing donor profiles...')

        # Get all donor users
        donors = CustomUser.objects.filter(user_type='donor')
        
        self.stdout.write(f'Found {donors.count()} donor users')

        profiles_created = 0
        
        # Common Indian hospitals
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

        for donor in donors:
            try:
                # Determine organs donating (1-4 organs)
                all_organs = ['kidney', 'liver', 'cornea', 'bone', 'skin', 'pancreas']
                num_organs = random.randint(1, 4)
                organs_donating = random.sample(all_organs, num_organs)
                
                # Generate realistic health data
                height = random.uniform(150, 190)  # cm
                weight = random.uniform(50, 100)   # kg
                
                # Calculate BMI
                bmi = round(weight / ((height/100) ** 2), 2)
                
                # Health status based on BMI and random factors
                if bmi < 18.5:
                    health_status = random.choice(['fair', 'poor'])
                elif bmi > 30:
                    health_status = random.choice(['fair', 'good'])
                else:
                    health_status = random.choices(
                        ['excellent', 'good', 'fair'], 
                        weights=[30, 50, 20]
                    )[0]
                
                # Smoking status with realistic distribution
                smoking_status = random.choices(
                    ['never', 'former', 'current'],
                    weights=[70, 20, 10]  # 70% never, 20% former, 10% current
                )[0]
                
                # Alcohol use with realistic distribution
                alcohol_use = random.choices(
                    ['never', 'occasional', 'regular'],
                    weights=[50, 40, 10]  # 50% never, 40% occasional, 10% regular
                )[0]
                
                # Drug use - mostly false
                drug_use = random.choices([True, False], weights=[5, 95])[0]
                
                # Last medical check (within 1-24 months)
                months_ago = random.randint(1, 24)
                last_medical_check = timezone.now().date() - timedelta(days=30 * months_ago)
                
                # Average sleep (5-9 hours)
                avg_sleep = round(random.uniform(5.0, 9.0), 1)
                
                # Create the donor profile
                donor_profile = DonorProfile(
                    user=donor,
                    organs_donating=organs_donating,
                    health_status=health_status,
                    smoking_status=smoking_status,
                    alcohol_use=alcohol_use,
                    drug_use=drug_use,
                    height=height,
                    weight=weight,
                    bmi=bmi,
                    last_medical_check=last_medical_check,
                    avg_sleep=avg_sleep,
                    preferred_hospital=random.choice(hospitals),
                    insurance_provider=random.choice(insurance_providers),
                    is_available=random.choices([True, False], weights=[80, 20])[0],
                    last_medical_checkup=last_medical_check,
                    medical_history=random.choice([
                        "No significant medical history",
                        "Hypertension controlled with medication",
                        "Type 2 Diabetes well controlled",
                        "Asthma in childhood",
                        "Appendectomy in 2015",
                        "Minor allergies to pollen",
                        "Family history of heart disease",
                        "Previous fracture in left arm",
                        ""
                    ]),
                    willing_to_travel=random.choices([True, False], weights=[70, 30])[0],
                    max_travel_distance=random.randint(50, 500)
                )
                
                donor_profile.save()
                profiles_created += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Profile {profiles_created}: {donor.username} - '
                        f'Organs: {", ".join(organs_donating)}, '
                        f'Health: {health_status}, BMI: {bmi}, '
                        f'Available: {donor_profile.is_available}'
                    )
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating profile for {donor.username}: {str(e)}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {profiles_created} donor profiles!')
        )
        
        # Display summary statistics
        self.display_summary()

    def display_summary(self):
        """Display summary statistics of created donor profiles"""
        profiles = DonorProfile.objects.all()
        
        if profiles.count() == 0:
            self.stdout.write(self.style.WARNING('No donor profiles were created.'))
            return
            
        self.stdout.write("\n" + "="*50)
        self.stdout.write("DONOR PROFILES SUMMARY")
        self.stdout.write("="*50)
        
        # Health status distribution
        self.stdout.write("\nHealth Status Distribution:")
        for status in ['excellent', 'good', 'fair', 'poor']:
            count = profiles.filter(health_status=status).count()
            percentage = (count / profiles.count() * 100)
            self.stdout.write(f"  {status.capitalize()}: {count} ({percentage:.1f}%)")
        
        # Smoking status
        self.stdout.write("\nSmoking Status:")
        for status in ['never', 'former', 'current']:
            count = profiles.filter(smoking_status=status).count()
            percentage = (count / profiles.count() * 100)
            self.stdout.write(f"  {status.capitalize()}: {count} ({percentage:.1f}%)")
        
        # Alcohol use
        self.stdout.write("\nAlcohol Use:")
        for use in ['never', 'occasional', 'regular']:
            count = profiles.filter(alcohol_use=use).count()
            percentage = (count / profiles.count() * 100)
            self.stdout.write(f"  {use.capitalize()}: {count} ({percentage:.1f}%)")
        
        # Availability
        available_count = profiles.filter(is_available=True).count()
        unavailable_count = profiles.filter(is_available=False).count()
        self.stdout.write(f"\nAvailability:")
        self.stdout.write(f"  Available: {available_count} ({available_count/profiles.count()*100:.1f}%)")
        self.stdout.write(f"  Unavailable: {unavailable_count} ({unavailable_count/profiles.count()*100:.1f}%)")
        
        # Willing to travel
        travel_count = profiles.filter(willing_to_travel=True).count()
        no_travel_count = profiles.filter(willing_to_travel=False).count()
        self.stdout.write(f"\nWilling to Travel:")
        self.stdout.write(f"  Yes: {travel_count} ({travel_count/profiles.count()*100:.1f}%)")
        self.stdout.write(f"  No: {no_travel_count} ({no_travel_count/profiles.count()*100:.1f}%)")
        
        # Organ distribution
        organ_counts = {}
        for profile in profiles:
            for organ in profile.organs_donating:
                organ_counts[organ] = organ_counts.get(organ, 0) + 1
        
        self.stdout.write("\nOrgan Donation Distribution:")
        for organ, count in sorted(organ_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / profiles.count() * 100)
            self.stdout.write(f"  {organ.capitalize()}: {count} ({percentage:.1f}%)")
        
        # BMI ranges
        bmi_ranges = {
            'Underweight (<18.5)': (0, 18.5),
            'Normal (18.5-25)': (18.5, 25),
            'Overweight (25-30)': (25, 30),
            'Obese (30+)': (30, 100)
        }
        
        self.stdout.write("\nBMI Distribution:")
        for range_name, (min_bmi, max_bmi) in bmi_ranges.items():
            count = profiles.filter(bmi__gte=min_bmi, bmi__lt=max_bmi).count()
            percentage = (count / profiles.count() * 100)
            self.stdout.write(f"  {range_name}: {count} ({percentage:.1f}%)")
        
        # Travel distance ranges
        distance_ranges = {
            'Local (0-100mi)': (0, 100),
            'Regional (101-250mi)': (101, 250),
            'State-wide (251-500mi)': (251, 500),
            'National (500+mi)': (501, 1000)
        }
        
        self.stdout.write("\nMax Travel Distance:")
        for range_name, (min_dist, max_dist) in distance_ranges.items():
            count = profiles.filter(max_travel_distance__gte=min_dist, max_travel_distance__lte=max_dist).count()
            percentage = (count / profiles.count() * 100)
            self.stdout.write(f"  {range_name}: {count} ({percentage:.1f}%)")
        
        self.stdout.write(f"\nTotal donor profiles created: {profiles.count()}")
        self.stdout.write("="*50)
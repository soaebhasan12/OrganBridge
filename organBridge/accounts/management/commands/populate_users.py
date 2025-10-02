import os
import sys
import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from accounts.models import CustomUser

class Command(BaseCommand):
    help = 'Populate the database with 40 sample users'

    def handle(self, *args, **options):
        # Indian Muslim and Hindu names
        muslim_first_names = [
            'Mohammad', 'Ahmad', 'Ali', 'Omar', 'Yusuf', 'Ibrahim', 'Hamza', 'Bilal', 
            'Zain', 'Abdullah', 'Fatima', 'Aisha', 'Zainab', 'Maryam', 'Khadija', 
            'Safia', 'Hafsa', 'Sumaiya', 'Ayesha', 'Rukhsar'
        ]
        
        hindu_first_names = [
            'Aarav', 'Vihaan', 'Vivaan', 'Ananya', 'Diya', 'Advik', 'Kabir', 'Anaya',
            'Aaradhya', 'Reyansh', 'Sai', 'Arjun', 'Ishaan', 'Ayaan', 'Rohan', 'Priya',
            'Sania', 'Riya', 'Sara', 'Neha'
        ]
        
        last_names = [
            'Khan', 'Ali', 'Ahmed', 'Hussain', 'Malik', 'Patel', 'Sharma', 'Kumar',
            'Singh', 'Verma', 'Gupta', 'Yadav', 'Jain', 'Mehta', 'Reddy', 'Mishra',
            'Choudhary', 'Shah', 'Rao', 'Pandey'
        ]
        
        # Uttarakhand cities and locations
        uttarakhand_cities = [
            'Dehradun', 'Haridwar', 'Roorkee', 'Haldwani', 'Rudrapur', 'Kashipur',
            'Rishikesh', 'Ramnagar', 'Pithoragarh', 'Almora', 'Ranikhet', 'Nainital',
            'Mussoorie', 'Tehri', 'Uttarkashi', 'Chamoli', 'Pauri', 'Bageshwar',
            'Champawat', 'Kotdwar'
        ]
        
        locations = [
            'Civil Lines', 'Rajpur Road', 'Clement Town', 'Ballupur', 'Dharampur',
            'Jwalapur', 'Bahadrabad', 'Laksar', 'Bhagwanpur', 'Sultanpur', 'Jaspur',
            'Bazpur', 'Gadarpur', 'Kichha', 'Sitarganj', 'Khatima', 'Mahua Dabra'
        ]
        
        blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        
        users_created = 0
        
        for i in range(40):
            # Randomly choose between Muslim and Hindu names
            if random.choice([True, False]):
                first_name = random.choice(muslim_first_names)
            else:
                first_name = random.choice(hindu_first_names)
            
            last_name = random.choice(last_names)
            username = f"{first_name.lower()}{last_name.lower()}{i+1}"
            email = f"{username}@example.com"
            
            # Create user
            user = CustomUser(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                user_type=random.choice(['donor', 'recipient']),
                phone_number=f"9{random.randint(100000000, 999999999)}",
                date_of_birth=self.get_random_date(),
                blood_type=random.choice(blood_types),
                location=f"{random.choice(locations)}",
                city=random.choice(uttarakhand_cities),
                state="Uttarakhand",
                zip_code=f"{random.randint(248000, 249999)}",
                password=make_password('password123')  # Default password
            )
            
            try:
                user.save()
                users_created += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created user: {username}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating user {username}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {users_created} users!')
        )
    
    def get_random_date(self):
        """Generate a random date between 1950 and 2005"""
        start_date = datetime(1950, 1, 1)
        end_date = datetime(2005, 12, 31)
        
        time_between_dates = end_date - start_date
        days_between_dates = time_between_dates.days
        random_number_of_days = random.randrange(days_between_dates)
        
        random_date = start_date + timedelta(days=random_number_of_days)
        return random_date.date()
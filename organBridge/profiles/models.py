from django.db import models
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class BaseProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='%(class)s_profile')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True



class DonorProfile(BaseProfile):
    ORGANS_CHOICES = [
        ('kidney', 'Kidney'),
        ('liver', 'Liver'),
        ('heart', 'Heart'),
        ('lungs', 'Lungs'),
        ('pancreas', 'Pancreas'),
        ('intestine', 'Intestine'),
        ('cornea', 'Cornea'),
        ('skin', 'Skin'),
        ('bone', 'Bone'),
    ]
    
    HEALTH_STATUS_CHOICES = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ]
    
    SMOKING_CHOICES = [
        ('never', 'Never Smoked'),
        ('former', 'Former Smoker'),
        ('current', 'Current Smoker'),
    ]
    
    ALCOHOL_CHOICES = [
        ('never', 'Never'),
        ('occasional', 'Occasional'),
        ('regular', 'Regular'),
    ]
    
    # Organ donation specific fields
    organs_donating = models.JSONField(default=list, help_text="Organs willing to donate")
    health_status = models.CharField(max_length=20, choices=HEALTH_STATUS_CHOICES, default='good')
    smoking_status = models.CharField(max_length=20, choices=SMOKING_CHOICES, default='never')
    alcohol_use = models.CharField(max_length=20, choices=ALCOHOL_CHOICES, default='never')
    drug_use = models.BooleanField(default=False, help_text="History of drug use")
    
    # Medical information
    height = models.FloatField(help_text="Height in cm", null=True, blank=True)
    weight = models.FloatField(help_text="Weight in kg", null=True, blank=True)
    bmi = models.FloatField(null=True, blank=True, help_text="Body Mass Index")
    
    # Availability
    is_available = models.BooleanField(default=True, help_text="Currently available for donation")
    last_medical_checkup = models.DateField(null=True, blank=True)
    medical_history = models.TextField(blank=True, help_text="Any significant medical history")
    
    # Contact preferences
    willing_to_travel = models.BooleanField(default=True)
    max_travel_distance = models.IntegerField(default=100, help_text="Maximum travel distance in miles")
    
    def save(self, *args, **kwargs):
        # Calculate BMI automatically
        if self.height and self.weight and self.height > 0:
            self.bmi = round(self.weight / ((self.height/100) ** 2), 2)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Donor: {self.user.username}"
    
    def get_organs_list(self):
        """Return organs as readable list"""
        return [dict(self.ORGANS_CHOICES).get(organ, organ) for organ in self.organs_donating]



class RecipientProfile(BaseProfile):
    URGENCY_CHOICES = [
        ('low', 'Low - Can wait months'),
        ('medium', 'Medium - Needs within weeks'),
        ('high', 'High - Needs within days'),
        ('critical', 'Critical - Immediate need'),
    ]
    
    # Organ needs
    organs_needed = models.JSONField(default=list, help_text="Organs required")
    urgency_level = models.CharField(max_length=20, choices=URGENCY_CHOICES, default='medium')
    
    # Medical information
    medical_condition = models.TextField(help_text="Current medical condition")
    diagnosis_date = models.DateField(null=True, blank=True)
    current_treatment = models.TextField(blank=True, help_text="Current treatment plan")
    
    # Hospital preferences
    preferred_hospitals = models.JSONField(default=list, help_text="Preferred hospitals for transplant")
    current_hospital = models.CharField(max_length=100, blank=True)
    
    # Transplant history
    previous_transplants = models.IntegerField(default=0)
    insurance_coverage = models.BooleanField(default=False)
    
    # Search preferences
    max_travel_distance = models.IntegerField(default=100, help_text="Maximum willing to travel in miles")
    willing_to_relocate = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Recipient: {self.user.username}"
    
    def get_organs_list(self):
        """Return needed organs as readable list"""
        return [dict(DonorProfile.ORGANS_CHOICES).get(organ, organ) for organ in self.organs_needed]
    
    def get_urgency_display_color(self):
        """Return CSS color based on urgency"""
        colors = {
            'low': 'green',
            'medium': 'orange', 
            'high': 'red',
            'critical': 'darkred'
        }
        return colors.get(self.urgency_level, 'black')
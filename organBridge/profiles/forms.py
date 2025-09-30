from django import forms
from .models import DonorProfile, RecipientProfile

class DonorProfileForm(forms.ModelForm):
    class Meta:
        model = DonorProfile
        fields = [
            'organs_donating', 'health_status', 'smoking_status', 'alcohol_use', 'drug_use',
            'height', 'weight', 'is_available', 'last_medical_checkup', 'medical_history',
            'willing_to_travel', 'max_travel_distance'
        ]
        widgets = {
            'organs_donating': forms.CheckboxSelectMultiple(choices=DonorProfile.ORGANS_CHOICES),
            'medical_history': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe any significant medical history...'}),
            'last_medical_checkup': forms.DateInput(attrs={'type': 'date'}),
            'height': forms.NumberInput(attrs={'placeholder': 'Height in cm'}),
            'weight': forms.NumberInput(attrs={'placeholder': 'Weight in kg'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            
        # Special styling for checkboxes
        self.fields['organs_donating'].widget.attrs['class'] = 'form-check-input'
        self.fields['drug_use'].widget.attrs['class'] = 'form-check-input'

class RecipientProfileForm(forms.ModelForm):
    class Meta:
        model = RecipientProfile
        fields = [
            'organs_needed', 'urgency_level', 'medical_condition', 'diagnosis_date',
            'current_treatment', 'preferred_hospitals', 'current_hospital',
            'previous_transplants', 'insurance_coverage', 'max_travel_distance',
            'willing_to_relocate'
        ]
        widgets = {
            'organs_needed': forms.CheckboxSelectMultiple(choices=DonorProfile.ORGANS_CHOICES),
            'medical_condition': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your medical condition...'}),
            'current_treatment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Current treatment plan...'}),
            'diagnosis_date': forms.DateInput(attrs={'type': 'date'}),
            'preferred_hospitals': forms.TextInput(attrs={'placeholder': 'Hospital names separated by commas'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            
        self.fields['organs_needed'].widget.attrs['class'] = 'form-check-input'
        self.fields['willing_to_relocate'].widget.attrs['class'] = 'form-check-input'
        self.fields['insurance_coverage'].widget.attrs['class'] = 'form-check-input'
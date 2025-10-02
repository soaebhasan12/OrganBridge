from django import forms
from .models import DonorProfile, RecipientProfile

class DonorProfileForm(forms.ModelForm):
    # Remove the custom organs field and use the original one
    class Meta:
        model = DonorProfile
        fields = [
            'organs_donating', 'health_status', 'smoking_status', 'alcohol_use', 'drug_use',
            'height', 'weight', 'is_available', 'last_medical_checkup', 'medical_history',
            'willing_to_travel', 'max_travel_distance'
        ]
        widgets = {
            'organs_donating': forms.SelectMultiple(attrs={
                'class': 'form-control multiselect-dropdown',
                'multiple': 'multiple'
            }),
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
        self.fields['drug_use'].widget.attrs['class'] = 'form-check-input'

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            profile.save()
        return profile

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
            'organs_needed': forms.SelectMultiple(attrs={
                'class': 'form-control multiselect-dropdown',
                'multiple': 'multiple'
            }),
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
                
            self.fields['willing_to_relocate'].widget.attrs['class'] = 'form-check-input'
            self.fields['insurance_coverage'].widget.attrs['class'] = 'form-check-input'

        def save(self, commit=True):
            profile = super().save(commit=False)
            if commit:
                profile.save()
            return profile








# from django import forms
# from .models import DonorProfile, RecipientProfile

# class DonorProfileForm(forms.ModelForm):
#     # Custom field for template compatibility
#     organs = forms.MultipleChoiceField(
#         choices=DonorProfile.ORGANS_CHOICES,
#         widget=forms.CheckboxSelectMultiple,
#         required=True,
#         label="Organs Willing to Donate"
#     )
    
#     class Meta:
#         model = DonorProfile
#         fields = [
#             'organs_donating', 'health_status', 'smoking_status', 'alcohol_use', 'drug_use',
#             'height', 'weight', 'is_available', 'last_medical_checkup', 'medical_history',
#             'willing_to_travel', 'max_travel_distance'
#         ]
#         widgets = {
#             'organs_donating': forms.HiddenInput(),  # Hide the original field
#             'medical_history': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe any significant medical history...'}),
#             'last_medical_checkup': forms.DateInput(attrs={'type': 'date'}),
#             'height': forms.NumberInput(attrs={'placeholder': 'Height in cm'}),
#             'weight': forms.NumberInput(attrs={'placeholder': 'Weight in kg'}),
#         }
    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Add CSS classes to all fields
#         for field_name, field in self.fields.items():
#             if field_name != 'organs_donating':  # Don't add class to hidden field
#                 field.widget.attrs['class'] = 'form-control'
            
#         # Special styling for checkboxes
#         self.fields['drug_use'].widget.attrs['class'] = 'form-check-input'
        
#         # Set initial value for custom organs field
#         if self.instance and self.instance.pk:
#             self.fields['organs'].initial = self.instance.organs_donating

#     def save(self, commit=True):
#         # Map custom 'organs' field to model's 'organs_donating' field
#         profile = super().save(commit=False)
#         profile.organs_donating = self.cleaned_data.get('organs', [])
#         if commit:
#             profile.save()
#         return profile

# class RecipientProfileForm(forms.ModelForm):
#     # Custom fields for template compatibility
#     organs = forms.MultipleChoiceField(
#         choices=DonorProfile.ORGANS_CHOICES,
#         widget=forms.CheckboxSelectMultiple,
#         required=False,
#         label="Organs Needed"
#     )
    
#     preferred_hospital = forms.CharField(
#         required=False,
#         label="Preferred Hospital"
#     )
    
#     insurance_provider = forms.CharField(
#         required=False,
#         label="Insurance Provider"
#     )
    
#     avg_sleep = forms.FloatField(
#         required=False,
#         min_value=0,
#         max_value=24,
#         label="Average Sleep Hours"
#     )
    
#     class Meta:
#         model = RecipientProfile
#         fields = [
#             'organs_needed', 'urgency_level', 'medical_condition', 'diagnosis_date',
#             'current_treatment', 'preferred_hospitals', 'current_hospital',
#             'previous_transplants', 'insurance_coverage', 'max_travel_distance',
#             'willing_to_relocate'
#         ]
#         widgets = {
#             'organs_needed': forms.HiddenInput(),  # Hide the original field
#             'preferred_hospitals': forms.HiddenInput(),  # Hide the original field
#             'medical_condition': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your medical condition...'}),
#             'current_treatment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Current treatment plan...'}),
#             'diagnosis_date': forms.DateInput(attrs={'type': 'date'}),
#         }
    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Add CSS classes to all fields
#         for field_name, field in self.fields.items():
#             if field_name not in ['organs_needed', 'preferred_hospitals']:  # Don't add class to hidden fields
#                 field.widget.attrs['class'] = 'form-control'
            
#         self.fields['willing_to_relocate'].widget.attrs['class'] = 'form-check-input'
#         self.fields['insurance_coverage'].widget.attrs['class'] = 'form-check-input'
        
#         # Set initial values for custom fields
#         if self.instance and self.instance.pk:
#             self.fields['organs'].initial = self.instance.organs_needed
#             if self.instance.preferred_hospitals:
#                 self.fields['preferred_hospital'].initial = ', '.join(self.instance.preferred_hospitals)

#     def save(self, commit=True):
#         # Map custom fields to model fields
#         profile = super().save(commit=False)
#         profile.organs_needed = self.cleaned_data.get('organs', [])
        
#         # Convert preferred_hospital string to list for JSONField
#         preferred_hospital = self.cleaned_data.get('preferred_hospital', '')
#         if preferred_hospital:
#             profile.preferred_hospitals = [h.strip() for h in preferred_hospital.split(',') if h.strip()]
#         else:
#             profile.preferred_hospitals = []
            
#         if commit:
#             profile.save()
#         return profile
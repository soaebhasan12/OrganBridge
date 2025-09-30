from django import forms
from .models import MatchPreference, MatchMessage

class MatchPreferenceForm(forms.ModelForm):
    class Meta:
        model = MatchPreference
        fields = ['max_distance', 'min_match_score', 'notify_new_matches', 'notify_messages']
        widgets = {
            'max_distance': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 10,
                'max': 1000
            }),
            'min_match_score': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100
            }),
            'notify_new_matches': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notify_messages': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class MessageForm(forms.ModelForm):
    class Meta:
        model = MatchMessage
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Type your message here...'
            })
        }
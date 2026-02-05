from django import forms
from .models import MealPlan


class MealPlanForm(forms.ModelForm):
    """Form for meal plan management"""
    class Meta:
        model = MealPlan
        fields = ['date', 'breakfast', 'lunch', 'dinner', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'breakfast': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Breakfast items...'}),
            'lunch': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Lunch items...'}),
            'dinner': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Dinner items...'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Additional notes...'}),
        }

from django import forms
from .models import *


class ComplaintForms(forms.ModelForm):

    class Meta:
        model = Complaint
        # fields = ['district', 'police_station', 'location', 'image', 'note']
        fields = ['location', 'image', 'note']


class ComplaintNextStepsForms(forms.Form):
    email_or_start_date = forms.CharField()

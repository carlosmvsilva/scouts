from django import forms

from .models import StationComponentTeamPoints

class ContactForm(forms.Form):
	name = forms.CharField(max_length=100)
	sender = forms.EmailField()
	subject = forms.CharField(max_length=100)
	message = forms.CharField(widget=forms.Textarea)
	cc_myself = forms.BooleanField(required=False)

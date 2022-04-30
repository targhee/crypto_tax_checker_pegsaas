from django import forms
from django.contrib.auth.models import User
from .models import Historyfile

class CryptoHistoryUploadForm(forms.ModelForm):
    class Meta:
        model = Historyfile
        #fields = ['user', 'upload_file']
        fields = ['upload_file']
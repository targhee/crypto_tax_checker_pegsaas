from django.forms import BaseForm, ModelForm
from .models import Historyfile


def set_form_fields_disabled(form: BaseForm, disabled: bool = True) -> None:
    """
    For a given form, disable (or enable) all fields.
    """
    for field in form.fields:
        form.fields[field].disabled = disabled

class CryptoHistoryUploadForm(ModelForm):
    class Meta:
        model = Historyfile
        fields = ['upload_file']

from django import forms
from django.db.models.functions import Substr
from .models import ModelResult

class HistoryForm(forms.Form):
    models = forms.ModelMultipleChoiceField(
        queryset=ModelResult.objects.values_list('model_name', flat=True).distinct(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    questions = forms.ModelMultipleChoiceField(
        queryset=ModelResult.objects.order_by('question', '-timestamp').distinct('question').values_list('question', flat=True),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

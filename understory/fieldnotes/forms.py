from django import forms
from .models import ForagingReport

class ForagingReportForm(forms.ModelForm):
    """
    A ModelForm for creating a foraging report.
    'user' and 'created' are handled by the view/code, not the user.
    """

    class Meta:
        model = ForagingReport
        fields = ['location', 'date_foraged', 'notes']

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

# Fields included in each per-species form. 'species' and 'quantity' are
# rendered as hidden inputs (pre-populated from the basket); the remaining
# fields are observation details the user fills in on the report page.
SPECIES_FORMSET_FIELDS = ['species', 'quantity', 'growth_stage', 'condition', 'habitat_context']
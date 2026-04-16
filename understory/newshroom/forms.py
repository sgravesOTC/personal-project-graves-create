from django import forms

# ================== NEWSHROOM FORMS ==================

class SearchForm(forms.Form):
    """Simple search form for full-text article search.
    
    Fields:
        query: Search terms to find in article titles and bodies
    """
    query = forms.CharField()
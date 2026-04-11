from django import forms
from .models import Request

# ================== NEWSHROOM FORMS ==================
# Forms for articles: newslet sharing, requests, and search


class NewsLetterForm(forms.Form):
    """Form to share an article via email recommendation.
    
    Fields:
        name: Recommender's name
        email: Recipient's email address
    """
    name = forms.CharField(max_length=25)
    email = forms.EmailField()


class RequestBoundForm(forms.BoundField):
    """Custom BoundField to add CSS classes to request form fields."""
    request_class = "request"
    def css_classes(self, extra_classes=None):
        result = super().css_classes(extra_classes)
        if self.request_class not in result:
            result += f' {self.request_class}'
        return result.strip()
    

class RequestForm(forms.ModelForm):
    """Form for submitting article requests/suggestions from readers.
    
    Saves to Request model. Uses custom BoundField for styling.
    """
    bound_field_class = RequestBoundForm

    class Meta:
        model = Request
        fields = ['name','email','body']


class SearchForm(forms.Form):
    """Simple search form for full-text article search.
    
    Fields:
        query: Search terms to find in article titles and bodies
    """
    query = forms.CharField()
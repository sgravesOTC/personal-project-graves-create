from django import forms
from .models import Request

class NewsLetterForm(forms.Form):
    name = forms.CharField(max_length=25)
    email = forms.EmailField()

class RequestBoundForm(forms.BoundField):
    request_class = "request"
    def css_classes(self, extra_classes=None):
        result = super().css_classes(extra_classes)
        if self.request_class not in result:
            result += f' {self.request_class}'
        return result.strip()
    
class RequestForm(forms.ModelForm):
    bound_field_class = RequestBoundForm

    class Meta:
        model = Request
        fields = ['name','email','body']

class SearchForm(forms.Form):
    query = forms.CharField()
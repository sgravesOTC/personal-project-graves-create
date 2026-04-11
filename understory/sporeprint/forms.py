from django import forms
from .models import Specimen

# ================== SPOREPRINT FORMS ==================
# Forms for creating and editing specimen collection entries
# Supports both local uploads and external image URLs


class SpecimenCreateForm(forms.ModelForm):
    """Form to create a new specimen collection entry.
    
    Supports two image input methods:
    - Local upload: User provides image file directly
    - URL source: User provides image URL (image is downloaded)
    
    Validates that exactly one image source is provided (not both, not neither).
    """
    upload_image = forms.ImageField(
        required=False,
        label='Upload Photo',
    )

    class Meta:
        model = Specimen
        fields = ['title', 'source_url', 'description']
        labels = {
            'source_url': 'Image URL',
            'description': 'Notes (optional)',
        }
        widgets = {
            'source_url': forms.URLInput(attrs={'class': 'sporeprint-url-input'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make source_url optional - either upload or URL is required
        self.fields['source_url'].required = False

    def clean(self):
        """Validate that exactly one image source is provided."""
        cleaned_data = super().clean()
        source_url = cleaned_data.get('source_url')
        upload_image = cleaned_data.get('upload_image')
        
        # Must have at least one image source
        if not source_url and not upload_image:
            raise forms.ValidationError('Please provide either an image URL or upload a photo.')
        
        # Cannot have both image sources
        if source_url and upload_image:
            raise forms.ValidationError('Please provide an image URL or upload a photo, not both.')
        return cleaned_data


class SpecimenEditForm(forms.ModelForm):
    """Form to edit an existing specimen entry.
    
    Allows updating title, description, and image.
    Image can be replaced via upload or URL (same validation as create form).
    """
    upload_image = forms.ImageField(
        required=False,
        label='Replace Photo (upload)',
    )

    class Meta:
        model = Specimen
        fields = ['title', 'source_url', 'description']
        labels = {
            'source_url': 'Replace Photo (URL)',
            'description': 'Notes (optional)',
        }
        widgets = {
            'source_url': forms.URLInput(attrs={'class': 'sporeprint-url-input'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['source_url'].required = False

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('source_url') and cleaned_data.get('upload_image'):
            raise forms.ValidationError('Please provide a URL or upload a photo, not both.')
        return cleaned_data

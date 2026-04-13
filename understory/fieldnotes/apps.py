from django.apps import AppConfig


class FieldnotesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fieldnotes'
    
    def ready(self):
        import fieldnotes.signals
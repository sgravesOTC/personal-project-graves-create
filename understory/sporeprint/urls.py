from django.urls import path
from . import views

# URL namespace for the Sporeprint specimen collection app
app_name = 'sporeprint'

# ================== SPECIMEN URL PATTERNS ==================
# All specimen URLs require authentication for create/edit/delete
# Detail and collection views are public

urlpatterns = [
    # Create new specimen entry - form to upload/add mushroom photo
    path('create/', views.specimen_create, name='specimen_create'),
    
    # View specimen details - public, shows collector info and description
    # Example: /sporeprint/123/specimen-name/
    path('<int:id>/<slug:slug>/', views.specimen_detail, name='specimen_detail'),
    
    # Edit specimen - only original collector can edit
    path('<int:id>/<slug:slug>/edit/', views.specimen_edit, name='specimen_edit'),
    
    # Delete specimen - only original collector can delete, requires confirmation
    path('<int:id>/<slug:slug>/delete/', views.specimen_delete, name='specimen_delete'),
    
    # AJAX endpoint - spot/unspot specimens (requires login)
    path('like/', views.specimen_like, name='specimen_like'),
    
    # Collection gallery - paginated grid of all specimens with AJAX support
    path('collection/', views.specimen_list, name='specimen_list'),
]
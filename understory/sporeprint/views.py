import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SpecimenCreateForm, SpecimenEditForm
from .models import Specimen
from .recommender import SpecimenRecommender
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from mycelium.utils import create_action

# ================== SPOREPRINT VIEWS ==================
# Views for managing user mushroom collections and field notes.


@login_required
def specimen_create(request):
    """Create a new specimen entry with local image upload or URL source.
    
    Supports two upload methods:
    - Direct image upload from user's device
    - Image URL: downloads and stores image from external source
    
    Auto-generates slug from title.
    Creates activity log entry when saved.
    """
    form = SpecimenCreateForm(data=request.POST or None, files=request.FILES or None)

    if request.method == 'POST' and form.is_valid():

        specimen = form.save(commit=False)
        specimen.collector = request.user  # Set the current user as collector

        upload_image = form.cleaned_data.get('upload_image')
        source_url = form.cleaned_data.get('source_url')

        if upload_image:
            # Handle direct file upload
            ext = upload_image.name.rsplit('.', 1)[-1].lower()
            specimen.image.save(
                f'{specimen.slug}.{ext}',
                upload_image,
                save=False,
            )
        else:
            # Handle image URL - download and store the image
            image_name = f'{specimen.slug}.{source_url.rsplit(".", 1)[-1].lower()}'
            try:
                response = requests.get(source_url)
                specimen.image.save(
                    image_name,
                    ContentFile(response.content),
                    save=False,
                )
            except Exception:
                messages.error(request, 'There was a problem fetching that image. Please check the URL and try again.')
                return render(request, 'sporeprint/create.html', {'form': form})

        specimen.save()
        create_action(request.user, 'collected', specimen)  # Log activity
        messages.success(request, f'"{specimen.title}" has been added to your field notes.')
        return redirect(specimen.get_absolute_url())
    return render(request, 'sporeprint/create.html', {'form': form, 'section': 'sporeprint'})


def specimen_detail(request, id, slug):
    """Display a single specimen entry with collector information.

    Checks if current user has spotted this specimen.
    Tracks session history and records co-occurrence for recommendations.
    """
    specimen = get_object_or_404(
        Specimen.objects.select_related('collector'), id=id, slug=slug
    )
    user_has_spotted = (
        request.user.is_authenticated and
        specimen.spotted_by.filter(id=request.user.id).exists()
    )

    # Track specimen in session history
    history = request.session.get('specimen_history', [])
    if specimen.id not in history:
        history.append(specimen.id)
        request.session['specimen_history'] = history

    # Record co-occurrence with previously viewed specimens
    try:
        r = SpecimenRecommender()
        if len(history) > 1:
            previously_viewed = Specimen.objects.filter(
                id__in=history
            ).exclude(id=specimen.id)
            r.specimens_viewed([specimen] + list(previously_viewed))
        recommended_specimens = r.suggest_specimens_for(specimen)
    except Exception:
        recommended_specimens = []

    return render(request, 'sporeprint/detail.html', {
        'specimen': specimen,
        'user_has_spotted': user_has_spotted,
        'section': 'sporeprint',
        'recommended_specimens': recommended_specimens,
    })


@login_required
def specimen_edit(request, id, slug):
    """Edit an existing specimen entry (title, description, image).
    
    Only the original collector can edit.
    Supports same image upload options as create view.
    """
    # Ensure user only edits their own specimens
    specimen = get_object_or_404(Specimen, id=id, slug=slug, collector=request.user)
    form = SpecimenEditForm(
        data=request.POST or None,
        files=request.FILES or None,
        instance=specimen,
    )
    if request.method == 'POST' and form.is_valid():
        specimen = form.save(commit=False)

        upload_image = form.cleaned_data.get('upload_image')
        source_url = form.cleaned_data.get('source_url')

        if upload_image:
            # Handle direct file upload
            ext = upload_image.name.rsplit('.', 1)[-1].lower()
            specimen.image.save(f'{specimen.slug}.{ext}', upload_image, save=False)
        elif source_url:
            # Handle image URL - download and store the image
            image_name = f'{specimen.slug}.{source_url.rsplit(".", 1)[-1].lower()}'
            try:
                response = requests.get(source_url)
                specimen.image.save(image_name, ContentFile(response.content), save=False)
            except Exception:
                messages.error(request, 'There was a problem fetching that image. Please check the URL and try again.')
                return render(request, 'sporeprint/edit.html', {'form': form, 'specimen': specimen, 'section': 'sporeprint'})

        specimen.save()
        create_action(request.user, 'updated', specimen)  # Log activity
        messages.success(request, f'"{specimen.title}" has been updated.')
        return redirect(specimen.get_absolute_url())
    return render(request, 'sporeprint/edit.html', {'form': form, 'specimen': specimen, 'section': 'sporeprint'})


@login_required
def specimen_delete(request, id, slug):
    """Delete a specimen entry (only available to original collector).
    
    Requires POST confirmation.
    """
    # Ensure user only deletes their own specimens
    specimen = get_object_or_404(Specimen, id=id, slug=slug, collector=request.user)
    if request.method == 'POST':
        specimen.delete()
        messages.success(request, f'"{specimen.title}" has been deleted.')
        return redirect('fairy_ring:fairy_ring')
    return render(request, 'sporeprint/delete.html', {'specimen': specimen, 'section': 'sporeprint'})

@login_required
@require_POST
def specimen_like(request):
    """Handle AJAX requests to spot/unspot specimens.
    
    Requires: authenticated user and POST method.
    Returns: JSON with updated spot count.
    Updates total_spots counter for database persistence.
    """
    specimen_id = request.POST.get('id')
    action = request.POST.get('action')  # 'spot' or 'unspot'

    if specimen_id and action:
        specimen = get_object_or_404(Specimen, id = specimen_id)

        if action == 'spot':
            # User is spotting the specimen
            specimen.spotted_by.add(request.user)
            specimen.total_spots += 1
            # Record this action for activity feed
            create_action(request.user, 'spotted', specimen)

        elif action == 'unspot':
            # User is removing their spot
            specimen.spotted_by.remove(request.user)
            specimen.total_spots -= 1
        
        specimen.save()

        return JsonResponse({'status':'ok','total_spots':specimen.total_spots})
    
    # Invalid request parameters
    return JsonResponse({'status':'error'}, status=400)


def specimen_list(request):
    """Display paginated collection of all specimens with AJAX support.
    
    Supports AJAX requests for infinite scroll / load more functionality.
    Returns empty response if AJAX request gets empty page.
    Tracks which specimens current user has spotted.
    """
    all_specimens = Specimen.objects.select_related('collector').all()
    paginator = Paginator(all_specimens, 8)  # 8 specimens per page
    page = request.GET.get('page',1)

    try:
        specimens = paginator.page(page)
    except EmptyPage:
        # For AJAX requests, return empty response when no more pages
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return HttpResponse('')
        # For regular requests, show last page
        specimens = paginator.page(paginator.num_pages)

    # Get IDs of specimens this user has spotted
    spotted_ids = (
        set(request.user.sporeprint_spotted.values_list('id', flat=True))
        if request.user.is_authenticated else set()
    )

    context = {'specimens': specimens, 'spotted_ids': spotted_ids}

    # Return different templates based on request type (AJAX vs regular)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # AJAX request: return just the items for appending
        return render(request, 'sporeprint/specimen_list_ajax.html', context)

    # Regular request: return full page with sidebar/header
    return render(request, 'sporeprint/collection.html', {
        **context,
        'section': 'sporeprint',
    })
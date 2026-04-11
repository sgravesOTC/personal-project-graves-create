import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SpecimenCreateForm, SpecimenEditForm
from .models import Specimen
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from mycelium.utils import create_action

# Create your views here.

@login_required
def specimen_create(request):

    form = SpecimenCreateForm(data=request.POST or None, files=request.FILES or None)

    if request.method == 'POST' and form.is_valid():

        specimen = form.save(commit=False)
        specimen.collector = request.user

        upload_image = form.cleaned_data.get('upload_image')
        source_url = form.cleaned_data.get('source_url')

        if upload_image:
            ext = upload_image.name.rsplit('.', 1)[-1].lower()
            specimen.image.save(
                f'{specimen.slug}.{ext}',
                upload_image,
                save=False,
            )
        else:
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
        create_action(request.user, 'collected', specimen)
        messages.success(request, f'"{specimen.title}" has been added to your field notes.')
        return redirect(specimen.get_absolute_url())
    return render(request, 'sporeprint/create.html', {'form': form, 'section': 'create'})


def specimen_detail(request, id, slug):
    specimen = get_object_or_404(Specimen.objects.select_related('collector'), id=id, slug=slug)
    user_has_spotted = (
        request.user.is_authenticated and specimen.spotted_by.filter(id=request.user.id).exists()
    )
    return render(request, 'sporeprint/detail.html', {'specimen': specimen, 'user_has_spotted':user_has_spotted, 'section':'collection'})


@login_required
def specimen_edit(request, id, slug):
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
            ext = upload_image.name.rsplit('.', 1)[-1].lower()
            specimen.image.save(f'{specimen.slug}.{ext}', upload_image, save=False)
        elif source_url:
            image_name = f'{specimen.slug}.{source_url.rsplit(".", 1)[-1].lower()}'
            try:
                response = requests.get(source_url)
                specimen.image.save(image_name, ContentFile(response.content), save=False)
            except Exception:
                messages.error(request, 'There was a problem fetching that image. Please check the URL and try again.')
                return render(request, 'sporeprint/edit.html', {'form': form, 'specimen': specimen})

        specimen.save()
        create_action(request.user, 'updated', specimen)
        messages.success(request, f'"{specimen.title}" has been updated.')
        return redirect(specimen.get_absolute_url())
    return render(request, 'sporeprint/edit.html', {'form': form, 'specimen': specimen})


@login_required
def specimen_delete(request, id, slug):
    specimen = get_object_or_404(Specimen, id=id, slug=slug, collector=request.user)
    if request.method == 'POST':
        specimen.delete()
        messages.success(request, f'"{specimen.title}" has been deleted.')
        return redirect('fairy_ring:fairy_ring')
    return render(request, 'sporeprint/delete.html', {'specimen': specimen})

@login_required
@require_POST
def specimen_like(request):

    specimen_id = request.POST.get('id')
    action = request.POST.get('action')

    if specimen_id and action:
        specimen = get_object_or_404(Specimen, id = specimen_id)

        if action == 'spot':
            specimen.spotted_by.add(request.user)
            specimen.total_spots += 1
            create_action(request.user, 'spotted', specimen)

        elif action == 'unspot':
            specimen.spotted_by.remove(request.user)
            specimen.total_spots -= 1
        
        specimen.save()

        return JsonResponse({'status':'ok','total_spots':specimen.total_spots})
    
    return JsonResponse({'status':'error'}, status=400)

def specimen_list(request):
    all_specimens = Specimen.objects.select_related('collector').all()
    paginator = Paginator(all_specimens, 8)
    page = request.GET.get('page',1)

    try:
        specimens = paginator.page(page)
    except EmptyPage:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return HttpResponse('')
        specimens = paginator.page(paginator.num_pages)

    spotted_ids = (
        set(request.user.sporeprint_spotted.values_list('id', flat=True))
        if request.user.is_authenticated else set()
    )

    context = {'specimens': specimens, 'spotted_ids': spotted_ids}

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'sporeprint/specimen_list_ajax.html', context)

    return render(request, 'sporeprint/collection.html', {
        **context,
        'section': 'collection',
    })
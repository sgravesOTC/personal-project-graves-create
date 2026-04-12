from django.shortcuts import render, get_object_or_404
from .models import MushroomGenus, MushroomSpecies
# Create your views here.

def species_list(request, genus_slug = None):
    """
    Displays all available species.
    If a genus_slug is provided, filters by that genus.
    """

    genus = None
    genera = MushroomGenus.objects.all()
    species = MushroomSpecies.objects.filter(available=True)

    if genus_slug:
        genus = get_object_or_404(MushroomGenus, slug=genus_slug)
        species = species.filter(genus = genus)
    
    return render(
        request,
        'mycoguide/species/list.html',
        {
            'genus':genus,
            'genera':genera,
            'species':species,
        }
    )

def species_detail(request, id, slug):
    """
    Displays a single species Page.
    """

    species = get_object_or_404(
        MushroomSpecies,
        id=id,
        slug=slug,
        available=True
    )
    return render(
        request,
        'mycoguide/species/detail.html',
        {'species':species}
    )
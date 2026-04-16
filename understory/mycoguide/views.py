from django.shortcuts import render, get_object_or_404
from .models import MushroomGenus, MushroomSpecies
import requests


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
            'section': 'mycoguide',
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
    # Fetch species data from iNaturalist's taxa endpoint

    response = requests.get(
        'https://api.inaturalist.org/v1/taxa',
        params = {
            'q': species.scientific_name,
            'peer_page': 1,
        }
    )

    if response.status_code == 200:
        results = response.json().get('results', [])
        if results:
            taxon_id = results[0]['id']
            detail_response = response = requests.get(f'https://api.inaturalist.org/v1/taxa/{taxon_id}')
            if detail_response.status_code == 200:
                detail_results = detail_response.json().get('results',[])
                inat_data = detail_results[0] if detail_results else None
            else: 
                inat_data = None
        else:
            inat_data = None
    else:
        inat_data = None

    return render(
        request,
        'mycoguide/species/detail.html',
        {
            'species':species,
            'inat_data':inat_data,
            'section': 'mycoguide',
        }
    )
   
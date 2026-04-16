from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from mycoguide.models import MushroomSpecies
from .basket import Basket

# Create your views here.
@require_POST
def basket_add(request, species_id):
    """
    Add a species to the basket. Only accepts POST requests.
    """

    basket = Basket(request)
    species = get_object_or_404(MushroomSpecies, id = species_id)
    basket.add(species=species)
    return redirect('basket:basket_detail')

@require_POST
def basket_update(request, species_id):
    """
    Update the quantity of a species already in the basket.
    """
    basket = Basket(request)
    species = get_object_or_404(MushroomSpecies, id=species_id)
    try:
        quantity = int(request.POST.get('quantity', 1))
    except ValueError:
        quantity = 1
    basket.update_quantity(species, quantity)
    return redirect('basket:basket_detail')

@require_POST
def basket_remove(request, species_id):
    """
    Remove a species from the basket.
    """
    basket = Basket(request)
    species = get_object_or_404(MushroomSpecies, id=species_id)
    basket.remove(species)
    return redirect('basket:basket_detail')

def basket_detail(request):
    """
    Display the current conrtents of the basket.
    """

    basket = Basket(request)
    return render(request, 'basket/detail.html', {'basket':basket})

from django.conf import settings
from mycoguide.models import MushroomSpecies

class Basket:
    """
    A session-based forageing basket.
    Stores species the user wants to study across requests.
    """

    def __init__(self, request):
        """
        Initialize the basket form the current session.
        If no basket exists yet, create an empty one and save it.
        """

        self.session = request.session
        basket = self.session.get(settings.BASKET_SESSION_ID)
        if not basket:
            basket = self.session[settings.BASKET_SESSION_ID] = {}
        self.basket = basket
        
    def add(self, species, quantity=1):
        """
        Add a species to the basket, or update its quantity if already present.
        We store species IDs as strings because JSON (used by sessions) requires string keys.
        """

        species_id = str(species.id)
        if species_id not in self.basket:
            self.basket[species_id] = {'quantity': quantity}
        else:
            self.basket[species_id]['quantity'] = quantity
        self.save()

    def update_quantity(self, species, quantity):
        """
        Update the quantity of an existing basket item.
        """
        species_id = str(species.id)
        if species_id in self.basket:
            self.basket[species_id]['quantity'] = max(1, quantity)
            self.save()

    def save(self):
        """
        Mark the session as modified so django knows to save it.
        Without this, changes to nested objects won't be persisted.
        """
        self.session.modified = True
    
    def remove(self, species):
        """
        Remove a species from the basket.
        """
        species_id = str(species.id)
        if species_id in self.basket:
            del self.basket[species_id]
            self.save()

    def __iter__(self):
        """
        Iterate over basket items and fetch the actual MushroomSpecies from the DB.
        """

        species_ids = self.basket.keys()
        species_objects = MushroomSpecies.objects.filter(id__in=species_ids)
        basket = self.basket.copy()
        for species in species_objects:
            basket[str(species.id)]['species'] = species
        
        for item in basket.values():
            item.setdefault('quantity', 1)
            yield item

    def __contains__(self, species):
        """
        Return True if the given species is already in the basket.
        """
        return str(species.id) in self.basket

    def __len__(self):
        """
        Return the total number of species in the basket.
        """

        return len(self.basket)
    
    def clear(self):
        """
        Remove the basket from the session entirely.
        """

        del self.session[settings.BASKET_SESSION_ID]
        self.save()
        
from .basket import Basket

def basket(request):
    """
    Makes the basket available in ever template automatically.
    """

    return{'basket': Basket(request)}
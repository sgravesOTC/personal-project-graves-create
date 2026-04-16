import redis
from django.conf import settings
from .models import Specimen

r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)

class SpecimenRecommender:

    def get_specimen_key(self,id):
        return f'specime:{id}:viewed_with'
    
    def specimens_viewed(self,specimen_list):
        """
        Records co-occurence between this specimen and other specimens viewed in the same session
        """
        specimen_ids = [s.id for s in specimen_list]
        for specimen_id in specimen_ids:
            for with_id in specimen_ids:
                if specimen_id != with_id:
                    r.zincrby(self.get_specimen_key(specimen_id), 1, with_id)

    def suggest_specimens_for(self, specimen, max_results=4):
        """
        Returns specimens frequently viewed alongside this one.
        """
        suggestions = r.zrange(
            self.get_specimen_key(specimen.id), 0, -1, desc=True
        )[:max_results]

        suggested_ids = [int(id) for id in suggestions]
        suggested_specimens = list(
            Specimen.objects.select_related('collector').filter(id__in = suggested_ids)
        )
        suggested_specimens.sort(key=lambda x: suggested_ids.index(x.id))
        return suggested_specimens
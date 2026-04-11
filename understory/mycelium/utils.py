import datetime
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from .models import Action

def create_action(user, verb, target=None):

    now = timezone.now()
    one_minute_ago = now - datetime.timedelta(seconds=60)

    recent_actions = Action.objects.filter(
        user = user,
        verb = verb,
        created__gte = one_minute_ago
    )

    if target:
        target_content_type = ContentType.objects.get_for_model(target)
        recent_actions = recent_actions.filter(
            content_type = target_content_type,
            object_id = target.pk
        )

    if not recent_actions.exists():
        action = Action(user=user, verb = verb , target = target)
        action.save()
        return True
    
    return False
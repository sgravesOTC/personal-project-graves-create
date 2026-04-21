import datetime
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from .models import Action


def create_action(user, verb, target=None):
    """Log a user action (e.g., 'spotted', 'collected', 'updated').
    
    Prevents duplicate actions for the same user, verb, and target within 60 seconds.
    This deduplication prevents activity feeds from being cluttered with repeated
    rapid-click actions.
    
    Args:
        user: The user performing the action
        verb: String describing the action ('spotted', 'collected', 'updated', etc.)
        target: Optional object (Article, Specimen, etc.) that action is about
    
    Returns:
        True if action was created, False if a recent duplicate was found
    """
    now = timezone.now()
    # Check for identical actions within the last 60 seconds
    one_minute_ago = now - datetime.timedelta(seconds=60)

    # Start with actions from this user with this verb
    recent_actions = Action.objects.filter(
        user = user,
        verb = verb,
        created__gte = one_minute_ago
    )

    # If target is specified, also check it matches (using generic foreign key)
    if target:
        target_content_type = ContentType.objects.get_for_model(target)
        recent_actions = recent_actions.filter(
            content_type = target_content_type,
            object_id = target.pk
        )

    # Only create action if no recent duplicate exists
    if not recent_actions.exists():
        action = Action(user=user, verb = verb , target = target)
        action.save()
        return True
    
    # Duplicate action ignored
    return False
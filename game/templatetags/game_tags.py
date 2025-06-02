from django import template
from game.models import GameSession

register = template.Library()

@register.filter
def get_item(lst, index):
    try:
        return lst.index(index)
    except (ValueError, TypeError):
        return 0

@register.filter
def multiply(value, arg):
    return value * arg

@register.filter
def format_time(seconds):
    if seconds is None:
        return "N/A"
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    if minutes > 0:
        return f"{minutes} minute{'s' if minutes != 1 else ''} {remaining_seconds:.2f} seconds"
    return f"{seconds:.2f} seconds"

@register.filter
def stage_progress(stage):
    stages = [s[0] for s in GameSession.STAGES]
    try:
        current_index = stages.index(stage)
        return ((current_index + 1) / len(stages)) * 100
    except ValueError:
        return 0 
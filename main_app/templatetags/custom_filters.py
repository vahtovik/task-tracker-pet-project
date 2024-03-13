from django import template

register = template.Library()


@register.filter
def format_time_interval(task_time_interval):
    if task_time_interval.startswith("0 ч "):
        return task_time_interval[4:]
    else:
        return task_time_interval

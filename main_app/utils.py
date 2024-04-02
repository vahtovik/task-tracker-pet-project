from datetime import datetime
from django.utils import timezone

today = timezone.now()


def timedelta_to_minutes_and_seconds(td):
    minutes = td.seconds // 60
    seconds = td.seconds % 60
    return '{:02}:{:02}'.format(minutes, seconds)


def format_timedelta(td):
    hours, remainder = divmod(td.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return '{:02}:{:02}'.format(hours, minutes)


def get_completed_tasks_total_time(completed_tasks):
    total_seconds = sum(
        (task.completed_task_end_time - task.completed_task_start_time).total_seconds()
        for task in completed_tasks
    )
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    return f'{int(hours)} ч {int(minutes)} м' if hours > 0 else f'{int(minutes)} м'


def get_today_date_with_specified_time(time):
    if not time:
        return None
    current_date = datetime.now().date()
    hours, minutes = map(int, time.split(':'))
    return timezone.make_aware(datetime(current_date.year, current_date.month, current_date.day, hours, minutes),
                               timezone.get_current_timezone())


MONTHS = {
    1: 'января',
    2: 'февраля',
    3: 'марта',
    4: 'апреля',
    5: 'мая',
    6: 'июня',
    7: 'июля',
    8: 'августа',
    9: 'сентября',
    10: 'октября',
    11: 'ноября',
    12: 'декабря'
}

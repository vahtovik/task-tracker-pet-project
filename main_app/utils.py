from datetime import datetime
from django.utils import timezone

today = timezone.now()


def timedelta_to_minutes_and_seconds(td):
    minutes = td.seconds // 60
    seconds = td.seconds % 60
    return '{:02}:{:02}'.format(minutes, seconds)


def get_completed_tasks_total_time(completed_tasks):
    total_seconds = sum(
        (task.completed_task_end_time - task.completed_task_start_time).total_seconds()
        for task in completed_tasks
    )
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    return f'{int(hours)} ч {int(minutes)} м' if hours > 0 else f'{int(minutes)} м'


def get_time_difference(start, end):
    return (end - start).seconds // 60


def get_today_date_with_specified_time(time):
    if not time:
        return None
    current_date = datetime.now().date()
    hours, minutes = map(int, time.split(':'))
    return timezone.make_aware(datetime(current_date.year, current_date.month, current_date.day, hours, minutes),
                               timezone.get_current_timezone())


def parse_date(date_string):
    year = datetime.now().year
    day_str, month_str = date_string.split()
    day, month = int(day_str), MONTHS_DAY.get(month_str)
    return timezone.make_aware(datetime(year, month, day), timezone.get_current_timezone())


def date_to_day_month_weekday(date):
    day = date.day
    month = MONTHS.get(date.month)
    weekday = DAYS.get(date.weekday())
    return f'{day} {month}, {weekday}'


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

MONTHS_DAY = {
    'января': 1,
    'февраля': 2,
    'марта': 3,
    'апреля': 4,
    'мая': 5,
    'июня': 6,
    'июля': 7,
    'августа': 8,
    'сентября': 9,
    'октября': 10,
    'ноября': 11,
    'декабря': 12
}

DAYS = {
    0: 'пн',
    1: 'вт',
    2: 'ср',
    3: 'чт',
    4: 'пт',
    5: 'сб',
    6: 'вс'
}

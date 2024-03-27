from django.utils import timezone


def time_to_minutes(time_str):
    hours, minutes = map(int, time_str.split(':'))
    return hours * 60 + minutes


def timedelta_to_minutes_and_seconds(td):
    minutes = td.seconds // 60
    seconds = td.seconds % 60
    return '{:02}:{:02}'.format(minutes, seconds)


def format_timedelta(td):
    hours, remainder = divmod(td.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return '{:02}:{:02}'.format(hours, minutes)


def get_completed_tasks_total_time(completed_tasks):
    total_minutes = sum(time_to_minutes(task.task_time_interval) for task in completed_tasks)
    hours = total_minutes // 60
    minutes = total_minutes % 60
    return f'{hours} ч {minutes} м' if hours > 0 else f'{minutes} м'


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

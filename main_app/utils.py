def time_to_minutes(time_str):
    hours, minutes = map(int, time_str.split(':'))
    return hours * 60 + minutes


def timedelta_to_mmss(td):
    minutes = td.seconds // 60
    seconds = td.seconds % 60
    return '{:02}:{:02}'.format(minutes, seconds)


def format_timedelta(td):
    hours, remainder = divmod(td.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return '{:02}:{:02}'.format(hours, minutes)

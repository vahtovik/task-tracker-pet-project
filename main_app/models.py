from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from main_app.utils import timedelta_to_minutes_and_seconds


class TaskList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    task_name = models.CharField(max_length=255)
    creation_time = models.DateTimeField(auto_now_add=True)
    task_current_time = models.DateTimeField(null=True)
    is_active = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    order = models.IntegerField(default=100000)
    completed_task_start_time = models.DateTimeField(null=True)
    completed_task_end_time = models.DateTimeField(null=True)
    task_time_interval = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.task_name

    def get_active_task_start_time(self):
        local_time = timezone.localtime(self.creation_time, timezone=timezone.get_current_timezone())
        return local_time.strftime('%H:%M')

    @staticmethod
    def get_active_task_current_time():
        return datetime.now().strftime('%H:%M')

    def get_active_task_time_difference(self):
        time_difference = timezone.now() - self.creation_time
        return timedelta_to_minutes_and_seconds(time_difference)

    def get_completed_task_start_time(self):
        local_time = timezone.localtime(self.completed_task_start_time, timezone=timezone.get_current_timezone())
        return local_time.strftime('%H:%M')

    def get_completed_task_end_time(self):
        local_time = timezone.localtime(self.completed_task_end_time, timezone=timezone.get_current_timezone())
        return local_time.strftime('%H:%M')

    def get_completed_task_time_difference(self):
        total_seconds = (self.completed_task_end_time - self.completed_task_start_time).total_seconds()
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f'{int(hours)} ч {int(minutes)} м' if hours > 0 else f'{int(minutes)} м'

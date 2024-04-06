from datetime import timedelta, datetime
from typing import Optional

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class TaskList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    task_name = models.CharField(max_length=255)
    creation_time = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    order = models.IntegerField(default=100000)
    completed_task_start_time = models.DateTimeField(null=True, blank=True)
    completed_task_end_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.task_name

    class Meta:
        verbose_name = 'Список задач'
        verbose_name_plural = 'Список задач'

    @staticmethod
    def timedelta_to_minutes_and_seconds(td: timedelta) -> str:
        """
        Возвращает строку формата MM:SS
        """
        minutes = td.seconds // 60
        seconds = td.seconds % 60
        return '{:02}:{:02}'.format(minutes, seconds)

    def get_active_task_start_time(self) -> str:
        """
        Возвращает время начала активной задачи в формате HH:MM
        """
        local_time = timezone.localtime(self.creation_time, timezone=timezone.get_current_timezone())
        return local_time.strftime('%H:%M')

    @staticmethod
    def get_active_task_current_time() -> str:
        """
        Возвращает текущее время активной задачи в формате HH:MM
        """
        return datetime.now().strftime('%H:%M')

    def get_active_task_time_difference(self) -> str:
        """
        Возвращает разницу во времени между текущим временем и временем начала активной задачи
        """
        time_difference = timezone.now() - self.creation_time
        return self.timedelta_to_minutes_and_seconds(time_difference)

    def get_completed_task_start_time(self) -> Optional[str]:
        """
        Возвращает время начала завершенной задачи в формате HH:MM, если оно определено
        """
        if self.completed_task_start_time:
            local_time = timezone.localtime(self.completed_task_start_time, timezone=timezone.get_current_timezone())
            return local_time.strftime('%H:%M')
        return None

    def get_completed_task_end_time(self) -> Optional[str]:
        """
        Возвращает время окончания завершенной задачи в формате HH:MM, если оно определено
        """
        if self.completed_task_end_time:
            local_time = timezone.localtime(self.completed_task_end_time, timezone=timezone.get_current_timezone())
            return local_time.strftime('%H:%M')
        return None

    def get_completed_task_time_difference(self) -> Optional[str]:
        """
        Возвращает разницу во времени между окончанием и началом завершенной задачи в часах и минутах
        """
        if self.completed_task_start_time and self.completed_task_end_time:
            total_seconds = (self.completed_task_end_time - self.completed_task_start_time).total_seconds()
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f'{int(hours)} ч {int(minutes)} м' if hours > 0 else f'{int(minutes)} м'
        return None

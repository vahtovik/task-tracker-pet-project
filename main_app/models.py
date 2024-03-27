from django.contrib.auth.models import User
from django.db import models


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

from django.db import models


class TaskList(models.Model):
    session_key = models.CharField(max_length=40, null=True, blank=True)
    task = models.CharField(max_length=255)
    # task_id = models.CharField(max_length=50)

    def __str__(self):
        return self.task

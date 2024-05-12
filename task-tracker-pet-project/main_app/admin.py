from django.contrib import admin
from .models import TaskList


@admin.register(TaskList)
class TaskListAdmin(admin.ModelAdmin):
    list_display = ('user', 'task_name', 'is_active', 'is_completed',
                    'completed_task_start_time', 'completed_task_end_time')
    list_display_links = ('user', 'task_name')
    fields = ('user', 'task_name', 'is_active', 'is_completed', 'completed_task_start_time', 'completed_task_end_time')

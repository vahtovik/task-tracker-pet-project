from django import forms

from .models import TaskList


class TaskListForm(forms.ModelForm):
    class Meta:
        model = TaskList
        fields = ('task_name',)
        labels = {
            'task_name': ''
        }


class ActiveTaskForm(forms.Form):
    task_name = forms.CharField(max_length=255)


class GetPendingTaskForm(forms.Form):
    task_name = forms.CharField(max_length=255)


class EditCompletedTaskForm(forms.Form):
    task_name = forms.CharField(max_length=255)
    task_start_time = forms.DateTimeField()
    task_current_time = forms.DateTimeField()


class AddCompletedTaskForm(forms.Form):
    task_name = forms.CharField(max_length=255)
    task_start_time = forms.DateTimeField()
    task_current_time = forms.DateTimeField()

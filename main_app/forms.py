from django import forms


class TaskForm(forms.Form):
    task_name = forms.CharField(max_length=255)


class CompletedTaskForm(forms.Form):
    task_name = forms.CharField(max_length=255)
    task_start_time = forms.DateTimeField(required=False)
    task_current_time = forms.DateTimeField(required=False)

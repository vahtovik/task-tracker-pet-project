from django import forms

from .models import TaskList


class TaskListForm(forms.ModelForm):
    class Meta:
        model = TaskList
        fields = ('task',)
        labels = {
            'task': ''
        }

    def save(self, commit=True):
        instance = super(TaskListForm, self).save(commit=False)
        if 'session_key' in self.initial:
            instance.session_key = self.initial['session_key']
        if commit:
            instance.save()
        return instance

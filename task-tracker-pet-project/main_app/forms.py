from django import forms


class TaskForm(forms.Form):
    task_name = forms.CharField(max_length=255)


class CompletedTaskForm(forms.Form):
    task_name = forms.CharField(max_length=255)
    task_start = forms.CharField(required=False)
    task_end = forms.CharField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        task_start = cleaned_data.get('task_start')
        task_end = cleaned_data.get('task_end')
        # Проверяем, что если было предоставлено task_start или task_end, то должны быть предоставлены оба поля
        if (task_start and not task_end) or (not task_start and task_end):
            raise forms.ValidationError('Provide both task start and end time')

        # Проверяем, что время окончания задачи превышает время начала
        if task_start > task_end:
            raise forms.ValidationError('End time must be greater than start time')

        return cleaned_data

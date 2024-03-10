from django.shortcuts import render
from django.http import JsonResponse

from .forms import TaskListForm
from .models import TaskList


def index(request):
    if not request.session.session_key:
        request.session.save()
    session_key = request.session.session_key
    user_tasklist = TaskList.objects.filter(session_key=session_key)
    if request.method == 'POST':
        form = TaskListForm(request.POST, initial={'session_key': session_key})
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = TaskListForm()
    return render(request, 'main_app/index.html', {'form': form, 'user_tasklist': user_tasklist})

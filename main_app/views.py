import json
from datetime import datetime

from django.db import IntegrityError
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_POST

from users.forms import ChangeLoginAndPasswordForm
from .forms import TaskListForm, GetPendingTaskForm
from .models import TaskList
from .utils import get_completed_tasks_total_time, MONTHS, get_today_date_with_specified_time, today, parse_date, \
    date_to_day_month_weekday


@require_GET
@login_required
def index(request):
    # Получаем активную задачу на таймере
    active_task = TaskList.objects.filter(user=request.user, is_active=True).first()

    # Получаем активные задачи не на таймере
    pending_tasks = TaskList.objects.filter(user=request.user, is_active=False, is_completed=False).order_by('order')

    # Получаем выполненные задачи с временными интервалами
    completed_tasks_with_time = TaskList.objects.filter(
        user=request.user,
        is_completed=True,
        completed_task_start_time__date=today.date()
    ).order_by('-completed_task_start_time')

    # Вычисляем суммарное время выполненных задач с временными интервалами
    completed_tasks_total_time = get_completed_tasks_total_time(completed_tasks_with_time)

    # Получаем выполненные задачи без временных интервалов
    completed_tasks_no_time = TaskList.objects.filter(
        user=request.user,
        is_completed=True,
        creation_time__date=today.date(),
        completed_task_start_time__isnull=True
    )

    # Форма смены логина и пароля
    form = ChangeLoginAndPasswordForm(request.POST)

    return render(request, 'main_app/index.html', {
        'active_task': active_task,
        'pending_tasks': pending_tasks,
        'completed_tasks_with_time': completed_tasks_with_time,
        'completed_tasks_total_time': completed_tasks_total_time,
        'completed_tasks_no_time': completed_tasks_no_time,
        'month_day': today.date().day,
        'month': MONTHS.get(today.date().month),
        'form': form,
    })


@require_POST
@login_required
def add_active_task(request):
    form = TaskListForm(request.POST)
    active_task = TaskList.objects.filter(user=request.user, is_active=True).first()
    if not active_task:
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.is_active = True
            task.save()
            start = datetime.now().strftime('%H:%M')
            return JsonResponse({'success': True, 'task_id': task.id, 'start': start})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        return JsonResponse({'success': False, 'task_already_present': True})


@require_POST
@login_required
def add_pending_task(request):
    form = TaskListForm(request.POST)
    if form.is_valid():
        task = form.save(commit=False)
        task.user = request.user
        task.is_active = False
        task.save()
        return JsonResponse({'success': True, 'task_id': task.pk})
    else:
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@require_POST
@login_required
def finish_active_task(request):
    body_unicode = request.body.decode('utf-8')
    pk = json.loads(body_unicode).get('taskId')
    if pk:
        try:
            task = TaskList.objects.get(pk=pk)
            task.is_active = False
            task.is_completed = True
            task.completed_task_start_time = task.creation_time
            task.completed_task_end_time = today
            task.save()
            return JsonResponse({
                'success': True,
                'task_duration': (task.completed_task_end_time - task.task_current_time).seconds // 60,
            })
        except TaskList.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Task does not exist'}, status=400)
    else:
        return JsonResponse({'success': False, 'errors': 'Provide task pk'}, status=400)


@require_POST
@login_required
def edit_pending_task(request):
    form = GetPendingTaskForm(request.POST)
    if form.is_valid():
        pk = request.POST.get('taskId')
        try:
            task = TaskList.objects.get(pk=pk)
            task.task_name = request.POST['task_name']
            task.save()
            return JsonResponse({'success': True, 'task_id': pk})
        except TaskList.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Task does not exist'}, status=400)
    else:
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@require_POST
@login_required
def remove_pending_task(request):
    pk = request.POST.get('task_id')
    if pk:
        try:
            task = TaskList.objects.get(pk=pk)
            task.delete()
            return JsonResponse({'success': True, 'task_id': pk})
        except TaskList.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Task does not exist'}, status=400)
    else:
        return JsonResponse({'success': False, 'errors': 'Provide task pk'}, status=400)


@require_POST
@login_required
def add_completed_task(request):
    task_name = request.POST.get('task_name')
    task_start_time = request.POST.get('task_start')
    task_end_time = request.POST.get('task_end')
    try:
        new_task = TaskList.objects.create(
            user=request.user,
            task_name=task_name,
            is_completed=True,
            completed_task_start_time=get_today_date_with_specified_time(task_start_time),
            completed_task_end_time=get_today_date_with_specified_time(task_end_time),
        )

        if task_start_time and task_end_time:
            task_duration = (new_task.completed_task_end_time - new_task.completed_task_start_time).seconds // 60
        else:
            task_duration = None

        return JsonResponse({
            'success': True,
            'task_id': new_task.pk,
            'task_start_time': new_task.completed_task_start_time,
            'task_end_time': new_task.completed_task_end_time,
            'task_duration': task_duration,
        })
    except IntegrityError as e:
        return JsonResponse({'success': False, 'errors': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'errors': 'Error in task creating'}, status=400)


@require_POST
@login_required
def edit_completed_task(request):
    pk = request.POST.get('task_id')
    if pk:
        task_name = request.POST.get('task_name')
        task_start_time = request.POST.get('task_start')
        task_end_time = request.POST.get('task_end')
        try:
            task = TaskList.objects.get(pk=pk)
            task.task_name = task_name
            task.completed_task_start_time = get_today_date_with_specified_time(task_start_time)
            task.completed_task_end_time = get_today_date_with_specified_time(task_end_time)
            task.save()
        except TaskList.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Task does not exist'}, status=400)

        if task_start_time and task_end_time:
            task_duration = (task.completed_task_end_time - task.completed_task_start_time).seconds // 60
        else:
            task_duration = None

        return JsonResponse({
            'success': True,
            'task_id': pk,
            'start_time': task.completed_task_start_time,
            'end_time': task.completed_task_end_time,
            'task_duration': task_duration,
        })
    else:
        return JsonResponse({'success': False, 'errors': 'Provide task pk'}, status=400)


@require_POST
@login_required
def delete_completed_task(request):
    pk = request.POST.get('task_id')
    if pk:
        try:
            task = TaskList.objects.get(pk=pk)
            task.delete()
            return JsonResponse({'success': True, 'task_id': pk})
        except TaskList.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Task does not exist'}, status=400)
    else:
        return JsonResponse({'success': False, 'errors': 'Provide task pk'}, status=400)


@require_POST
@login_required
def make_pending_task_active(request):
    body_unicode = request.body.decode('utf-8')
    pk = json.loads(body_unicode).get('itemId')
    if pk:
        try:
            task = TaskList.objects.get(pk=pk)
            task.is_active = True
            task_name = task.task_name
            task.save()
            return JsonResponse({
                'success': True,
                'task_name': task_name,
                'task_id': pk,
                'start': datetime.now().strftime('%H:%M'),
            })
        except TaskList.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Task does not exist'}, status=400)
    else:
        return JsonResponse({'success': False, 'errors': 'Provide task pk'}, status=400)


@require_POST
@login_required
def change_pending_tasks_order(request):
    body_unicode = request.body.decode('utf-8')
    id_list = json.loads(body_unicode).get('idList')
    for item in id_list:
        pk, order = item['id'], item['orderNum']
        task = TaskList.objects.get(pk=pk)
        task.order = order
        task.save()

    return JsonResponse({'success': True})


@require_POST
@login_required
def load_next_completed_tasks(request):
    body_unicode = request.body.decode('utf-8')
    date_to_parse = json.loads(body_unicode).get('date')
    if date_to_parse:
        date = parse_date(date_to_parse)

        # Получаем дату для следующих задач
        next_tasks_date = (
            TaskList.objects
            .filter(creation_time__lt=date)
            .order_by('-creation_time')
            .first()
        ).creation_time.date()

        # Получаем выполненные задачи с временными интервалами
        completed_tasks_with_time = TaskList.objects.filter(
            user=request.user,
            is_completed=True,
            completed_task_start_time__date=next_tasks_date
        ).order_by('-completed_task_start_time')

        # Вычисляем суммарное время выполненных задач с временными интервалами
        completed_tasks_total_time = get_completed_tasks_total_time(completed_tasks_with_time)

        # Форматируем время начала и конца в нужный формат
        formatted_completed_tasks_with_time = []
        for task in completed_tasks_with_time:
            formatted_task = {
                'task_name': task.task_name,
                'completed_task_start_time': task.get_completed_task_start_time(),
                'completed_task_end_time': task.get_completed_task_end_time(),
                'completed_task_time_difference': task.get_completed_task_time_difference()
            }
            formatted_completed_tasks_with_time.append(formatted_task)

        # Получаем выполненные задачи без временных интервалов
        completed_tasks_no_time = TaskList.objects.filter(
            user=request.user,
            is_completed=True,
            creation_time__date=next_tasks_date,
            completed_task_start_time__isnull=True
        ).values('task_name')

        return JsonResponse({
            'success': True,
            'title_date': date_to_day_month_weekday(next_tasks_date),
            'completed_tasks_with_time': formatted_completed_tasks_with_time,
            'completed_tasks_total_time': completed_tasks_total_time,
            'completed_tasks_no_time': list(completed_tasks_no_time)
        })
    else:
        return JsonResponse({'success': False, 'errors': 'Provide date'}, status=400)

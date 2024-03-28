import json
from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import Max
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .forms import TaskListForm, GetPendingTaskForm
from .models import TaskList
from .utils import time_to_minutes, format_timedelta, get_completed_tasks_total_time, MONTHS


@require_GET
@login_required
def index(request):
    form = TaskListForm()
    today = timezone.now().date()

    # Получаем активную задачу на таймере
    active_task = TaskList.objects.filter(user=request.user, is_active=True).first()

    # Получаем активные задачи не на таймере
    pending_tasks = TaskList.objects.filter(user=request.user, is_active=False, is_completed=False).order_by('order')

    # Получаем выполненные задачи с временными интервалами
    completed_tasks_with_time = TaskList.objects.filter(
        user=request.user,
        is_completed=True,
        completed_task_start_time__date=today
    ).order_by('-task_current_time')

    # Вычисляем суммарное время выполненных задач с временными интервалами
    completed_tasks_total_time = get_completed_tasks_total_time(completed_tasks_with_time)

    # Получаем выполненные задачи без временных интервалов
    completed_tasks_no_time = TaskList.objects.filter(
        user=request.user,
        is_completed=True,
        completed_task_start_time__date=None,
    )
    return render(request, 'main_app/index.html', {
        'form': form,
        'active_task': active_task,
        'pending_tasks': pending_tasks,
        'completed_tasks_with_time': completed_tasks_with_time,
        'completed_tasks_total_time': completed_tasks_total_time,
        'completed_tasks_no_time': completed_tasks_no_time,
        'month_day': today.day,
        'month': MONTHS.get(today.month),
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
            task.task_current_time = timezone.now()
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
            task.completed_task_end_time = timezone.now()
            task.task_time_interval = format_timedelta(task.completed_task_end_time - task.task_current_time)
            task.save()
            return JsonResponse({
                'success': True,
                'task_duration': (task.completed_task_end_time - task.task_current_time).seconds // 60,
            })
        except TaskList.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Task does not exist'}, status=400)
    else:
        return JsonResponse({'success': False, 'errors': 'Provide task pk'}, status=400)


@login_required
@csrf_exempt
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


@login_required
@csrf_exempt
def remove_pending_task(request):
    pk = request.POST.get('taskId')
    if pk:
        try:
            task = TaskList.objects.get(pk=pk)
            task.delete()
            return JsonResponse({'success': True, 'task_id': pk})
        except TaskList.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Task does not exist'}, status=400)
    else:
        return JsonResponse({'success': False, 'errors': 'Provide task pk'}, status=400)


@login_required
@csrf_exempt
def add_completed_task(request):
    if request.method == 'POST':
        user = request.user
        task_name = request.POST.get('task_name')
        # task_start_time = request.POST.get('task_start_time')
        task_start_time = request.POST.get('task_start_time')
        task_end_time = request.POST.get('task_end_time')
        if not task_start_time or not task_end_time:
            start_time_obj, end_time_obj = None, None
        else:
            today = timezone.now().date()
            start_hours, start_minutes = map(int, task_start_time.split(':'))
            end_hours, end_minutes = map(int, task_end_time.split(':'))
            start_time_obj = datetime(today.year, today.month, today.day, start_hours, start_minutes)
            end_time_obj = datetime(today.year, today.month, today.day, end_hours, end_minutes)
        try:
            new_task = TaskList.objects.create(
                user=user,
                task_name=task_name,
                is_completed=True,
            )
            task_duration = None
            if start_time_obj is not None and end_time_obj is not None:
                new_task.task_current_time = start_time_obj
                new_task.completed_task_start_time = end_time_obj
                new_task.completed_task_end_time = end_time_obj

                time_difference = end_time_obj - start_time_obj
                hours = time_difference.seconds // 3600
                minutes = (time_difference.seconds % 3600) // 60
                formatted_time_difference = '{:02}:{:02}'.format(hours, minutes)
                new_task.task_time_interval = formatted_time_difference
                task_duration = (new_task.completed_task_end_time - new_task.task_current_time).seconds // 60
                new_task.save()
            return JsonResponse({
                'success': True,
                'task_id': new_task.pk,
                # 'task_start_time': new_task.task_current_time,
                'task_start_time': new_task.creation_time,
                'task_end_time': new_task.completed_task_end_time,
                'task_duration': task_duration,
            })
        except IntegrityError as e:
            return JsonResponse({'success': False, 'errors': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'errors': 'Error in task creating'}, status=400)


@login_required
@csrf_exempt
def edit_completed_task(request):
    pk = request.POST.get('taskId')
    if pk:
        try:
            task = TaskList.objects.get(pk=pk)
            task.task_name = request.POST.get('task_name')
            today_date = datetime.now().date()
            # task_start_time = request.POST.get('task_start_time')
            creation_time = request.POST.get('task_start_time')
            task_end_time = request.POST.get('task_end_time')
            if creation_time and task_end_time:
                start_hours, start_minutes = map(int, task_start_time.split(':'))
                end_hours, end_minutes = map(int, task_end_time.split(':'))
                start_time = datetime(today_date.year, today_date.month, today_date.day, start_hours, start_minutes)
                end_time = datetime(today_date.year, today_date.month, today_date.day, end_hours, end_minutes)
                task.completed_task_start_time = start_time
                task.completed_task_end_time = end_time
                task.task_time_interval = format_timedelta(end_time - start_time)
                # нужно добавить корректное значение в поле
                task.task_current_time = start_time
                # task_duration = (task.completed_task_end_time - task.completed_task_start_time).seconds // 60
                task_duration = (task.completed_task_end_time - task.task_current_time).seconds // 60
            else:
                task.completed_task_start_time = None
                task.completed_task_end_time = None
                task.task_time_interval = None
                task_duration = None

            task.save()
            return JsonResponse({
                'success': True,
                'task_id': pk,
                # 'start_time': task_start_time,
                'start_time': creation_time,
                'end_time': task_end_time,
                'task_duration': task_duration,
            })
        except TaskList.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Task does not exist'}, status=400)
    else:
        return JsonResponse({'success': False, 'errors': 'Provide task pk'}, status=400)


@login_required
@csrf_exempt
def delete_completed_task(request):
    pk = request.POST.get('taskId')
    if pk:
        try:
            task = TaskList.objects.get(pk=pk)
            task.delete()
            return JsonResponse({'success': True, 'task_id': pk})
        except TaskList.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Task does not exist'}, status=400)
    else:
        return JsonResponse({'success': False, 'errors': 'Provide task pk'}, status=400)


@login_required
@csrf_exempt
def change_pending_tasks_order(request):
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        id_list = json.loads(body_unicode).get('idList')
        for item in id_list:
            pk = item['id']
            order = item['orderNum']
            task = TaskList.objects.get(pk=pk)
            task.order = order
            task.save()

        return JsonResponse({'message': 'Success'})  # Ответ в формате JSON
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
@csrf_exempt
def make_pending_task_active(request):
    body_unicode = request.body.decode('utf-8')
    pk = json.loads(body_unicode).get('item_id')
    if pk:
        task = TaskList.objects.get(pk=pk)
        task.is_active = True
        task_name = task.task_name
        task.task_current_time = timezone.now()
        task.save()
        return JsonResponse({
            'success': True,
            'task_name': task_name,
            'task_id': pk,
            'start': datetime.now().strftime('%H:%M'),
        })


@login_required
@csrf_exempt
def load_next_completed_tasks(request):
    body_unicode = request.body.decode('utf-8')
    date_to_decode = json.loads(body_unicode).get('date')
    date = datetime.fromisoformat(date_to_decode.replace('Z', '+00:00'))
    user = request.user

    return JsonResponse({'success': False})
    # next_smallest_date = TaskList.objects.filter(
    #     completed_task_start_time__lt=date,
    #     user=user,
    # ).aggregate(next_smallest_date=Max('completed_task_start_time__lt'))
    #
    # next_smallest_date = next_smallest_date.get('next_smallest_date', None)
    #
    # if next_smallest_date:
    #     next_smallest_date = next_smallest_date.date()  # Если вам нужна только дата без времени
    #
    #     # Определяем начало и конец дня для next_smallest_date
    #     start_of_day = datetime.combine(next_smallest_date, datetime.min.time())
    #     end_of_day = start_of_day + timedelta(days=1)  # Следующий день
    #
    #     # Запрос для получения записей за один день
    #     tasks_in_day = TaskList.objects.filter(
    #         task_start_time__range=(start_of_day, end_of_day),
    #         user=request.user
    #     )
    #
    #     # теперь у вас есть записи tasks_in_day, содержащие все задачи,
    #     # выполненные в тот же день, что и next_smallest_date
    # else:
    #     # Обработка случая, когда next_smallest_date не был найден
    #     pass
    #
    #
    # return JsonResponse({'success': True})

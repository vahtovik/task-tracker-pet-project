from django.urls import path
from . import views

app_name = 'main_app'
urlpatterns = [
    path('', views.index, name='index'),
    path('add-pending-task/', views.add_pending_task, name='add-pending-task'),
    path('edit-pending-task/', views.edit_pending_task, name='edit-pending-task'),
    path('remove-pending-task/', views.remove_pending_task, name='remove-pending-task'),
    path('finish-active-task/', views.finish_active_task, name='finish-active-task'),
    path('add-completed-task/', views.add_completed_task, name='add-completed-task'),
    path('edit-completed-task/', views.edit_completed_task, name='edit-completed-task'),
    path('delete-completed-task/', views.delete_completed_task, name='delete-completed-task'),
    path('change-pending-tasks-order/', views.change_pending_tasks_order, name='change-pending-tasks-order'),
    path('make-pending-task-active/', views.make_pending_task_active, name='make-pending-task-active'),
    path('load-next-completed-tasks/', views.load_next_completed_tasks, name='load-next-completed-tasks'),
]

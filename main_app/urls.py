from django.urls import path
from . import views

app_name = 'main_app'
urlpatterns = [
    path('', views.index, name='index'),
    path('add-active-task/', views.add_active_task, name='add-active-task'),
    path('add-pending-task/', views.add_pending_task, name='add-pending-task'),
    path('finish-active-task/', views.finish_active_task, name='finish-active-task'),
    path('edit-active-task/<int:task_id>/', views.edit_active_task, name='edit-active-task'),
    path('make-active-task-pending/', views.make_active_task_pending, name='make-active-task-pending'),
    path('edit-pending-task/<int:task_id>/', views.edit_pending_task, name='edit-pending-task'),
    path('remove-pending-task/<int:task_id>/', views.remove_pending_task, name='remove-pending-task'),
    path('make-pending-task-active/', views.make_pending_task_active, name='make-pending-task-active'),
    path('add-completed-task/', views.add_completed_task, name='add-completed-task'),
    path('edit-completed-task/<int:task_id>/', views.edit_completed_task, name='edit-completed-task'),
    path('remove-completed-task/<int:task_id>/', views.remove_completed_task, name='remove-completed-task'),
    path('change-pending-tasks-order/', views.change_pending_tasks_order, name='change-pending-tasks-order'),
    path('load-next-completed-tasks/', views.load_next_completed_tasks, name='load-next-completed-tasks'),
]

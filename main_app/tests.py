from http import HTTPStatus

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main_app.models import TaskList


class IndexViewTests(TestCase):
    fixtures = ['user.json', 'active_task.json', 'pending_tasks.json']

    def setUp(self):
        self.user = User.objects.get(username='root')
        self.client.login(username='root', password='root_password')

    def test_redirect_if_not_logged_in(self):
        self.client.logout()
        path = reverse('main_app:index')
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, '/login/?next=/', target_status_code=200)

    def test_index_view_with_logged_in_user(self):
        path = reverse('main_app:index')
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'main_app/index.html')

    def test_active_task_displayed(self):
        active_task = TaskList.objects.filter(user=self.user, is_active=True).first()
        path = reverse('main_app:index')
        response = self.client.get(path)
        self.assertContains(response, active_task.task_name)

    def test_pending_tasks_displayed(self):
        pending_tasks = TaskList.objects.filter(user=self.user, is_active=False, is_completed=False).order_by('order')
        path = reverse('main_app:index')
        response = self.client.get(path)
        self.assertQuerysetEqual(response.context['pending_tasks'], pending_tasks, ordered=True)

    def test_completed_tasks_with_time_displayed(self):
        path = reverse('main_app:add-completed-task')
        self.client.post(path, {
            'task_name': 'выполненная задача со временем 1',
            'task_start': '12:20',
            'task_end': '14:40',
        })
        self.client.post(path, {
            'task_name': 'выполненная задача со временем 2',
            'task_start': '15:00',
            'task_end': '15:50',
        })
        completed_tasks_with_time = TaskList.objects.filter(
            user=self.user,
            is_completed=True,
            completed_task_start_time__date=timezone.now().date()
        ).order_by('-completed_task_start_time')
        path = reverse('main_app:index')
        response = self.client.get(path)
        self.assertQuerysetEqual(
            response.context['completed_tasks_with_time'],
            completed_tasks_with_time,
            ordered=True
        )

    def test_completed_tasks_without_time_displayed(self):
        path = reverse('main_app:add-completed-task')
        self.client.post(path, {
            'task_name': 'выполненная задача без времени 1',
            'task_start': '',
            'task_end': '',
        })
        self.client.post(path, {
            'task_name': 'выполненная задача без времени 2',
            'task_start': '',
            'task_end': '',
        })
        completed_tasks_without_time = TaskList.objects.filter(
            user=self.user,
            is_completed=True,
            creation_time__date=timezone.now().date(),
            completed_task_start_time__isnull=True
        )
        path = reverse('main_app:index')
        response = self.client.get(path)
        self.assertQuerysetEqual(
            response.context['completed_tasks_without_time'],
            completed_tasks_without_time,
            ordered=False
        )

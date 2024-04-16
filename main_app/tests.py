import json
from http import HTTPStatus

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main_app.models import TaskList
from main_app.views import add_pending_task


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


class AddActiveTaskTestCase(TestCase):
    fixtures = ['user.json']

    def setUp(self):
        self.user = User.objects.get(username='root')
        self.client.login(username='root', password='root_password')

    def test_add_active_task_with_valid_data(self):
        path = reverse('main_app:add-active-task')
        response = self.client.post(path, {'task_name': 'Test Task'})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue('success' in response.json())
        self.assertTrue(response.json()['success'])
        self.assertTrue('task_id' in response.json())
        self.assertTrue('start' in response.json())

    def test_add_active_task_with_invalid_data(self):
        path = reverse('main_app:add-active-task')
        response = self.client.post(path, {'task_name': ''})
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertTrue('success' in response.json())
        self.assertFalse(response.json()['success'])
        self.assertTrue('errors' in response.json())
        self.assertEqual(response.json()['errors']['task_name'], ['Обязательное поле.'])

    def test_add_active_task_when_active_task_already_exists(self):
        path = reverse('main_app:add-active-task')
        self.client.post(path, {'task_name': 'Existing Task'})
        response = self.client.post(path, {'task_name': 'New Task'})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue('success' in response.json())
        self.assertFalse(response.json()['success'])
        self.assertTrue('message' in response.json())
        self.assertEqual(response.json()['message'], 'There is already an active task')

    def test_add_active_task_requires_post_method(self):
        path = reverse('main_app:add-active-task')
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_add_active_task_requires_authentication(self):
        self.client.logout()
        path = reverse('main_app:add-active-task')
        response = self.client.post(path, {'task_name': 'Test Task'})
        self.assertEqual(response.status_code, HTTPStatus.FOUND)


class AddPendingTaskTestCase(TestCase):
    fixtures = ['user.json']

    def setUp(self):
        self.user = User.objects.get(username='root')
        self.client.login(username='root', password='root_password')

    def test_add_pending_task_with_valid_data(self):
        path = reverse('main_app:add-pending-task')
        response = self.client.post(path, {'task_name': 'Test Task'})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(response.json()['success'])
        self.assertTrue(TaskList.objects.filter(user=self.user, task_name='Test Task', is_active=False).exists())

    def test_add_pending_task_with_invalid_data(self):
        path = reverse('main_app:add-pending-task')
        response = self.client.post(path, {'task_name': ''})
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertFalse(response.json()['success'])
        self.assertEqual(response.json()['errors']['task_name'], ['Обязательное поле.'])

    def test_add_pending_task_requires_post_method(self):
        path = reverse('main_app:add-pending-task')
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_add_pending_task_requires_authentication(self):
        self.client.logout()
        path = reverse('main_app:add-pending-task')
        response = self.client.post(path, {'task_name': 'Test Task'})
        self.assertEqual(response.status_code, HTTPStatus.FOUND)


class FinishActiveTaskTestCase(TestCase):
    fixtures = ['user.json', 'active_task.json']

    def setUp(self):
        self.user = User.objects.get(username='root')
        self.client.login(username='root', password='root_password')
        self.active_task = TaskList.objects.filter(user=self.user, is_active=True).first()

    def test_finish_active_task_success(self):
        path = reverse('main_app:finish-active-task')
        response = self.client.post(path, json.dumps({'taskId': self.active_task.pk}), content_type='application/json')
        self.active_task.refresh_from_db()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(response.json()['success'])
        self.assertFalse(self.active_task.is_active)
        self.assertTrue(self.active_task.is_completed)

    def test_finish_inactive_task(self):
        self.active_task.is_active = False
        self.active_task.save()
        path = reverse('main_app:finish-active-task')
        response = self.client.post(path, json.dumps({'taskId': self.active_task.pk}), content_type='application/json')
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertFalse(response.json()['success'])
        self.assertEqual(response.json()['message'], 'Provide id of an active task')

    def test_finish_active_task_with_invalid_id(self):
        path = reverse('main_app:finish-active-task')
        response = self.client.post(path, json.dumps({'taskId': 999}), content_type='application/json')
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertFalse(response.json()['success'])
        self.assertEqual(response.json()['message'], 'Task with id 999 does not exist')

    def test_finish_active_task_no_task_id(self):
        path = reverse('main_app:finish-active-task')
        response = self.client.post(path, content_type='application/json')
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertFalse(response.json()['success'])
        self.assertEqual(response.json()['message'], 'Provide task pk')


class EditActiveTaskTestCase(TestCase):
    fixtures = ['user.json', 'active_task.json']

    def setUp(self):
        self.user = User.objects.get(username='root')
        self.client.login(username='root', password='root_password')
        self.active_task = TaskList.objects.filter(user=self.user, is_active=True).first()

    def test_edit_active_task_success(self):
        path = reverse('main_app:edit-active-task', args=[self.active_task.pk])
        response = self.client.post(path, {'task_name': 'Updated Task'})
        self.active_task.refresh_from_db()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(response.json()['success'])
        self.assertEqual(self.active_task.task_name, 'Updated Task')

    def test_edit_active_task_with_invalid_id(self):
        path = reverse('main_app:edit-active-task', args=[999])
        response = self.client.post(path, {'task_name': 'Updated Task'})
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertFalse(response.json()['success'])
        self.assertEqual(response.json()['message'], 'Task with id 999 does not exist')

    def test_edit_inactive_task(self):
        self.active_task.is_active = False
        self.active_task.save()
        path = reverse('main_app:edit-active-task', args=[self.active_task.pk])
        response = self.client.post(path, {'task_name': 'Updated Task'})
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertFalse(response.json()['success'])
        self.assertEqual(response.json()['message'], 'Provide id of an active task')

    def test_edit_active_task_with_invalid_data(self):
        path = reverse('main_app:edit-active-task', args=[self.active_task.pk])
        response = self.client.post(path, {})
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertFalse(response.json()['success'])
        self.assertEqual(response.json()['errors']['task_name'], ['Обязательное поле.'])

from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class RegistrationTestCase(TestCase):
    def setUp(self):
        self.data = {
            'username': 'test_user',
            'password1': 'test_password',
            'password2': 'test_password',
        }

    def test_get_register_page(self):
        path = reverse('users:register')
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'users/register.html')

    def test_register_user(self):
        path = reverse('users:register')
        response = self.client.post(path, self.data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('main_app:index'))
        self.assertTrue(User.objects.filter(username=self.data.get('username')).exists())

    def test_empty_fields(self):
        path = reverse('users:register')
        response = self.client.post(path, {})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, 'Обязательное поле')

    def test_duplicate_username(self):
        User.objects.create_user(username='test_user', password='test_password')
        path = reverse('users:register')
        response = self.client.post(path, self.data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, 'Пользователь с таким именем уже существует')

    def test_bad_password(self):
        self.data['password1'] = '1234'
        self.data['password2'] = '1234'
        path = reverse('users:register')
        response = self.client.post(path, self.data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        error_messages = (
            'Введённый пароль слишком короткий',
            'Введённый пароль слишком широко распространён',
            'Введённый пароль состоит только из цифр'
        )
        for error_message in error_messages:
            self.assertContains(response, error_message)

    def test_password_missmatch(self):
        self.data['password2'] = 'test_password_to_fail'
        path = reverse('users:register')
        response = self.client.post(path, self.data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, 'Пароли не совпадают')


class AuthenticationTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test_user', password='test_password')

    def test_get_login_page(self):
        path = reverse('users:login')
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'users/login.html')

    def test_login(self):
        path = reverse('users:login')
        response = self.client.post(path, {'username': 'test_user', 'password': 'test_password'})
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('main_app:index'))

    def test_failed_login(self):
        path = reverse('users:login')
        response = self.client.post(path, {'username': 'test_user', 'password': 'wrong_password'})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, 'Неверный логин или пароль')

    def test_logout(self):
        self.client.login(username='test_user', password='test_password')
        path = reverse('users:logout')
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('users:login'))

    def test_login_required_page_access(self):
        self.client.login(username='test_user', password='test_password')
        path = reverse('main_app:index')
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.OK)


class EditCredentialsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test_user', password='test_password')
        self.client.login(username='test_user', password='test_password')

    def test_access_via_get(self):
        path = reverse('users:edit-credentials')
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_edit_of_all_credentials(self):
        path = reverse('users:edit-credentials')
        response = self.client.post(path, {
            'username': 'new_test_user',
            'new_password1': 'new_test_password',
            'new_password2': 'new_test_password',
        })
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(response.json().get('success'))
        self.assertEqual(self.user.username, 'new_test_user')
        self.assertTrue(self.user.check_password('new_test_password'))

    def test_edit_of_username(self):
        path = reverse('users:edit-credentials')
        response = self.client.post(path, {'username': 'new_test_user'})
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(response.json().get('success'))
        self.assertEqual(self.user.username, 'new_test_user')

    def test_edit_of_password(self):
        path = reverse('users:edit-credentials')
        response = self.client.post(path, {
            'new_password1': 'new_test_password',
            'new_password2': 'new_test_password',
        })
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(response.json().get('success'))
        self.assertTrue(self.user.check_password('new_test_password'))

    def test_duplicate_username(self):
        path = reverse('users:edit-credentials')
        response = self.client.post(path, {'username': 'test_user'})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFalse(response.json().get('success'))
        self.assertIn('Пользователь с таким именем уже существует', response.json()['errors']['username'])

    def test_bad_password(self):
        path = reverse('users:edit-credentials')
        response = self.client.post(path, {
            'new_password1': '1234',
            'new_password2': '1234',
        })
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('Введённый пароль слишком короткий', response.json()['errors']['new_password2'])

    def test_password_missmatch(self):
        path = reverse('users:edit-credentials')
        response = self.client.post(path, {
            'new_password1': 'test_password_1',
            'new_password2': 'test_password_2',
        })
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('Пароли не совпадают', response.json()['errors']['new_password2'])

    def test_password_first_field_empty(self):
        path = reverse('users:edit-credentials')
        response = self.client.post(path, {'new_password2': 'test_password_2'})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('Обязательное поле', response.json()['errors']['new_password1'])

    def test_password_second_field_empty(self):
        path = reverse('users:edit-credentials')
        response = self.client.post(path, {'new_password1': 'test_password_1'})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('Обязательное поле', response.json()['errors']['new_password2'])

from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client

User = get_user_model()


class UserURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Stepan')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_users_url_exists_at_desired_location(self):
        """Страницы доступные любому пользователю."""
        users_urls = [
            ('/auth/signup/', HTTPStatus.OK, self.guest_client),
            ('/auth/login/', HTTPStatus.OK, self.guest_client),
            ('/auth/password_change/', HTTPStatus.OK,
             self.authorized_client),
            ('/auth/password_change/done/', HTTPStatus.OK,
             self.authorized_client),
            ('/auth/logout/', HTTPStatus.OK, self.guest_client),
            ('/auth/password_reset/', HTTPStatus.OK,
             self.guest_client),
            ('/auth/password_reset/done/', HTTPStatus.OK,
             self.guest_client),
            ('/auth/reset/<uidb64>/<token>/', HTTPStatus.OK,
             self.guest_client),
            ('/auth/reset/done/', HTTPStatus.OK, self.guest_client),
            ('/auth/unexisting_page/', HTTPStatus.NOT_FOUND,
             self.guest_client),
        ]
        for address, status, user_status in users_urls:
            with self.subTest(address=address):
                response = user_status.get(address)
                self.assertEqual(response.status_code, status)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/logout/': 'users/logged_out.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/<uidb64>/<token>/':
                'users/password_reset_confirm.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

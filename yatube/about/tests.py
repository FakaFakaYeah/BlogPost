from http import HTTPStatus

from django.test import TestCase, Client


class StaticPagesURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_url_exists_at_desired_location(self):
        """Проверка доступности статичных страниц."""
        about_urls = [
            ('/about/author/', HTTPStatus.OK),
            ('/about/tech/', HTTPStatus.OK),
            ('/about/unexisting_page/', HTTPStatus.NOT_FOUND),
        ]
        for address, status in about_urls:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, status)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

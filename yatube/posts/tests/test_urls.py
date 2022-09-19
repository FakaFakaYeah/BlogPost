from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache

from ..models import Post, Group, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Stepan')
        cls.authorized_user = User.objects.create_user(username='Sergei')
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.author,
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)
        cache.clear()

    def test_post_url_equal_post_name(self):
        """Cоответствие фактических адресов страниц с их именами"""
        posts_urls = [
            ('/', reverse('posts:index')),
            (f'/group/{self.group.slug}/',
                reverse('posts:group_list', kwargs={'slug': self.group.slug})),
            (f'/profile/{self.post.author}/',
                reverse('posts:profile',
                        kwargs={'username': self.post.author})),
            (f'/posts/{self.post.id}/',
                reverse('posts:post_detail',
                        kwargs={'post_id': self.post.id})),
            ('/create/', reverse('posts:post_create')),
            (f'/posts/{self.post.id}/edit/',
                reverse('posts:post_edit', kwargs={'post_id': self.post.id})),
        ]
        for address, reverse_name in posts_urls:
            with self.subTest(address=address):
                self.assertEqual(address, reverse_name)

    def test_post_url_exists_at_desired_location(self):
        """Проверка статуса страниц приложения posts."""
        posts_page_info = [
            (reverse('posts:index'), HTTPStatus.OK, self.guest_client),
            (reverse('posts:group_list', kwargs={'slug': self.group.slug}),
             HTTPStatus.OK, self.guest_client),
            (reverse('posts:profile', kwargs={'username': self.post.author}),
             HTTPStatus.OK, self.guest_client),
            (reverse('posts:post_detail', kwargs={'post_id': self.post.id}),
             HTTPStatus.OK, self.guest_client),
            (reverse('posts:post_create'), HTTPStatus.OK,
             self.authorized_client),
            (reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
             HTTPStatus.OK, self.authorized_client),
            ('/unexisting_page/', HTTPStatus.NOT_FOUND, self.guest_client),
        ]
        for address, status, client in posts_page_info:
            with self.subTest(address=address):
                response = client.get(address)
                self.assertEqual(response.status_code, status)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        templates_url_names = [
            (reverse('posts:index'), 'posts/index.html'),
            (reverse('posts:group_list', kwargs={'slug': self.group.slug}),
             'posts/group_list.html'),
            (reverse('posts:profile', kwargs={'username': self.post.author}),
             'posts/profile.html'),
            (reverse('posts:post_detail', kwargs={'post_id': self.post.id}),
             'posts/post_detail.html'),
            (reverse('posts:post_create'), 'posts/create_post.html'),
            (reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
             'posts/create_post.html'),
            ('/unexisting_page/', 'core/404.html')
        ]
        for address, template in templates_url_names:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_post_redirect_anonymous_and_no_author(self):
        """Проверка редиректов анонимных пользователей и не автора поста
        на страница создания, редактирования поста и комментария"""
        self.authorized_client.force_login(self.authorized_user)
        posts_page_info = [
            (reverse('posts:post_create'),
             f"{reverse('users:login')}?next={reverse('posts:post_create')}",
             self.guest_client),
            (reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
             f"{reverse('users:login')}?next="
             f"{reverse('posts:post_edit', kwargs={'post_id': self.post.id})}",
             self.guest_client),
            (reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
             reverse('posts:post_detail', kwargs={'post_id': self.post.id}),
             self.authorized_client),
            (reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
             f"{reverse('users:login')}?next="
             f"{reverse('posts:add_comment',kwargs={'post_id':self.post.id})}",
             self.guest_client),
            (reverse('posts:follow_index'),
             f"{reverse('users:login')}?next={reverse('posts:follow_index')}",
             self.guest_client),
        ]
        for address, redirect_address, client in posts_page_info:
            with self.subTest(address=address):
                response = client.get(address, follow=True)
                self.assertRedirects(response, redirect_address)

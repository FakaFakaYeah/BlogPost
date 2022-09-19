from math import ceil

from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings

from ..models import Post, Group, User


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.TEST_POSTS = 65  # Общее кол-во постов
        cls.NUMBER_OF_PAGES = ceil(cls.TEST_POSTS / settings.POSTS_IN_PAGE)
        cls.PAGE_COEF = 1  # Коэффициент для подсчета страниц
        cls.user = User.objects.create_user(username='Stepan')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        test_posts = []
        for number_of_posts in range(cls.TEST_POSTS):
            test_posts.append(Post(text=f'Текст поста № {number_of_posts}',
                                   group=cls.group,
                                   author=cls.user))
        Post.objects.bulk_create(test_posts)

    def setUp(self):
        self.guest_client = Client()

    def test_paginator_post_in_page(self):
        """Проверка количества постов на первой и второй страницах index,
        group_list, profile.
        """
        pages_address = (
            reverse('posts:index'),
            reverse('posts:group_list',
                    kwargs={'slug': f'{self.group.slug}'}),
            reverse('posts:profile',
                    kwargs={'username': f'{self.user.username}'}),
        )
        for address in pages_address:
            response_first_page = self.guest_client.get(address)
            response_last_page = (
                self.guest_client.get(
                    address + f'?page={self.NUMBER_OF_PAGES}')
            )
            if self.TEST_POSTS > settings.POSTS_IN_PAGE:
                posts = settings.POSTS_IN_PAGE
            else:
                posts = self.TEST_POSTS
            with self.subTest(address=address):
                self.assertEqual(
                    len(response_first_page.context['page_obj']),
                    posts)
            with self.subTest(address=address):
                self.assertEqual(
                    len(response_last_page.context['page_obj']),
                    self.TEST_POSTS - (self.NUMBER_OF_PAGES - self.PAGE_COEF)
                    * settings.POSTS_IN_PAGE)

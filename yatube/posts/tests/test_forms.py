import shutil
import tempfile

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import Post, User, Group, Comment

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.small_new_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small_new.gif',
            content=cls.small_new_gif,
            content_type='image/gif'
        )
        cls.uploaded_new = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.ID_COEF = 1  # Колличество идентификатор в some_post_id
        cls.user = User.objects.create_user(username='Stepan')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Простой пост',
            author=cls.user,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает в Post."""
        all_posts = set(Post.objects.values_list('id', flat=True))
        posts_page_info = (reverse('posts:post_create'),
                           reverse('posts:profile',
                                   kwargs={'username': self.user}))
        form_data = {
            'text': 'Новый текст',
            'group': self.group.id,
            'image': self.uploaded
        }
        address, redirect_page = posts_page_info
        response = self.authorized_client.post(
            address,
            data=form_data,
            follow=True,
        )
        some_post_id = (
            list(set(Post.objects.values_list('id', flat=True))
                 - all_posts))
        self.assertEqual(len(some_post_id), self.ID_COEF)
        some_post = Post.objects.get(id=some_post_id[0])
        post_objects = [
            (some_post.text, form_data['text']),
            (some_post.author, self.user),
            (some_post.group.id, form_data['group']),
            (some_post.image, f'posts/{self.uploaded.name}'),
        ]
        for reverse_name, response_name in post_objects:
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(response_name, reverse_name)
            self.assertRedirects(response, redirect_page)

    def test_edit_post(self):
        """Валидная форма изменяет запись в Post."""
        post = Post.objects.create(
            text='Тестовый текст',
            author=self.user,
            group=self.group,
            image=self.uploaded
        )
        posts_page_info = (reverse('posts:post_edit',
                                   kwargs={'post_id': post.id}),
                           reverse('posts:post_detail',
                                   kwargs={'post_id': post.id}))
        form_data = {
            'text': 'Отредактированный текст',
            'group': self.group.id,
            'image': self.uploaded_new
        }
        address, redirect_page = posts_page_info
        response = self.authorized_client.post(
            address,
            data=form_data,
            follow=True,
        )
        edit_post = Post.objects.get(id=post.id)
        post_edit_objects = [
            (edit_post.text, form_data['text']),
            (edit_post.author, self.user),
            (edit_post.group.id, form_data['group']),
            (edit_post.image, f'posts/{self.uploaded_new.name}')
        ]
        for reverse_name, response_name in post_edit_objects:
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(response_name, reverse_name)
            self.assertRedirects(response, redirect_page)

    def test_comment_add_in_post_page_correctly(self):
        """После отправки комментария, он появляется
        на странице поста"""
        all_comments = set(Comment.objects.values_list('id', flat=True))
        posts_page_info = (reverse('posts:add_comment',
                                   kwargs={'post_id': self.post.id}),
                           reverse('posts:post_detail',
                                   kwargs={'post_id': self.post.id}))
        address, redirect_page = posts_page_info
        form_data = {
            'text': 'Крутой пост',
        }
        response = self.authorized_client.post(
            address,
            data=form_data,
            follow=True,
        )
        some_comment_id = (
            list(set(Comment.objects.values_list('id', flat=True))
                 - all_comments))
        self.assertEqual(len(some_comment_id), self.ID_COEF)
        comment = Comment.objects.get(id=some_comment_id[0])
        self.assertEqual(comment.text, form_data['text'])
        self.assertRedirects(response, redirect_page)

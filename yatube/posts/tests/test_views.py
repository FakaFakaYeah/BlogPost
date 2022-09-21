import shutil
import tempfile

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache

from ..models import Post, Group, User, Comment, Follow
from ..forms import PostForm

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.FOLLOW_COEF = 1
        cls.SMALL_GIF = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.SMALL_GIF,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(username='Stepan')
        cls.authorized_user = User.objects.create_user(username='Sergei')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.sports_group = Group.objects.create(
            title='Спортивная группа',
            slug='sports-group',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
            image=cls.uploaded,
        )
        cls.comment = Comment.objects.create(
            author=cls.authorized_user,
            text='Простой комментарий',
            post=cls.post
        )
        cls.follower = Follow.objects.create(
            user=cls.authorized_user,
            author=cls.user
        )
        cls.form = PostForm

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_index_group_profile_page_show_correct_cont(self):
        """Проверка Context страниц index, group, profile
        и проверяем правильное добавление поста при создании."""
        posts_page_info = [
            (reverse('posts:index'), 'page_obj'),
            (reverse('posts:group_list', kwargs={'slug': self.group.slug}),
             'page_obj'),
            (reverse('posts:profile', kwargs={'username': self.post.author}),
             'page_obj'),
        ]
        for address, context_key in posts_page_info:
            response = (
                self.authorized_client.get(address).context[context_key][0]
            )
            first_objects = [
                (self.post.author, response.author),
                (self.post.text, response.text),
                (self.group.slug, response.group.slug),
                (self.post.image, response.image)
            ]
            for reverse_name, response_name in first_objects:
                with self.subTest(reverse_name=reverse_name):
                    self.assertEqual(response_name, reverse_name)

    def test_post_create_show_correct_context(self):
        """Проверка Context страниц post_create, post_edit"""
        posts_page_info = (
            reverse('posts:post_create'),
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
        )
        for address in posts_page_info:
            response = (
                self.authorized_client.get(address).context.get(
                    'form'))
            with self.subTest(response=response):
                self.assertIsInstance(response, self.form)

    def test_post_not_added_group_correctly(self):
        """Правильное добавление поста при создании,
        проверка, что оне не попадает в другую группу."""
        address = reverse('posts:group_list',
                          kwargs={'slug': self.sports_group.slug})
        response = self.authorized_client.get(address).context['page_obj']
        self.assertNotIn(self.post, response)

    def test_in_form_post_edit_transfer_correctly_post(self):
        """В форму поста на редактирования передается правильный пост"""
        address = reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        self.assertEqual(
            self.authorized_client.get
            (address).context.get('form').instance.id,
            self.post.id)

    def test_author_and_group_and_post_detail_objects_transfer_in_page(self):
        """На страницу автора, группы и поста передаются правильные объекты"""
        posts_page_info = [
            (reverse('posts:group_list', kwargs={'slug': self.group.slug}),
             self.post.group, 'group'),
            (reverse('posts:profile', kwargs={'username': self.post.author}),
             self.post.author, 'author'),
            (reverse('posts:post_detail', kwargs={'post_id': self.post.id}),
             self.post, 'post'),
        ]
        for address, need_object, context_key in posts_page_info:
            response = self.authorized_client.get(address).context[context_key]
            with self.subTest(address=address):
                self.assertEqual(need_object, response)

    def test_add_comment_correctly_context(self):
        """На страницу поста передается правильный контекст комментария"""
        self.authorized_client.force_login(self.authorized_user)
        posts_page_info = (reverse('posts:post_detail',
                                   kwargs={'post_id': self.post.id}),
                           self.comment, 'comments')
        address, need_object, context_key = posts_page_info
        response = self.authorized_client.get(address).context[context_key][0]
        first_objects = [
            (self.comment.text, response.text),
            (self.comment.author, response.author)
        ]
        for reverse_name, response_name in first_objects:
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(response_name, reverse_name)

    def test_cache_index_page(self):
        """Проверка кэширования главное страницы"""
        address = reverse('posts:index')
        posts = self.guest_client.get(address).content
        Post.objects.get(id=self.post.id).delete()
        old_posts = self.guest_client.get(address).content
        self.assertEqual(posts, old_posts)
        cache.clear()
        new_posts = self.guest_client.get(address).content
        self.assertNotEqual(new_posts, old_posts)

    def test_authorized_user_follow_correctly(self):
        """Проверка подписки авторизованного пользователя """
        all_follow = Follow.objects.count()
        self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.authorized_user}))
        self.assertEqual(Follow.objects.count(), all_follow + self.FOLLOW_COEF)

    def test_authorized_user_unfollow_correctly(self):
        """Проверка отписки авторизованного пользователя """
        self.authorized_client.force_login(self.authorized_user)
        all_follow = Follow.objects.count()
        self.authorized_client.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.user}))
        self.assertEqual(Follow.objects.count(), all_follow - self.FOLLOW_COEF)

    def test_new_post_in_follow(self):
        """Новый пост появляется в ленте подписчиков и
         не появляется в ленте тех, кто не подписан"""
        address = reverse('posts:follow_index')
        self.authorized_client.force_login(self.authorized_user)
        response = self.authorized_client.get(address).context['page_obj']
        self.assertIn(self.post, response)
        self.authorized_client.force_login(self.user)
        response = self.authorized_client.get(address).context['page_obj']
        self.assertNotIn(self.post, response)

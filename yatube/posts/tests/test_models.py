from django.test import TestCase

from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        str_models = [
            (self.group.title, str(self.group)),
            (self.post.text[:Post.FIRST_POST_CHAR], str(self.post))
        ]
        for str_model in str_models:
            value, expected_value = str_model
            with self.subTest(value=value):
                self.assertEqual(value, expected_value)

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        fields_verboses = [
            ('text', 'Текст статьи'),
            ('pub_date', 'Дата публикации'),
            ('author', 'Автор статьи'),
            ('group', 'Группа'),
        ]
        for field_verboses in fields_verboses:
            field, expected_value = field_verboses
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name,
                    expected_value)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        fields_help_texts = [
            ('text', 'Напишите вашу статью.'),
            ('author', 'Укажите автора'),
            ('group', 'Укажите группу'),
        ]
        for field_help_texts in fields_help_texts:
            field, expected_value = field_help_texts
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).help_text,
                    expected_value)

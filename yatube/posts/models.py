from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Post(models.Model):

    FIRST_POST_CHAR = 15  # первые 15 символов для метода STR

    text = models.TextField(
        verbose_name='Текст статьи',
        help_text='Напишите вашу статью.'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор статьи',
        help_text='Укажите автора'
    )
    group = models.ForeignKey(
        'Group',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Группа',
        help_text='Укажите группу'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:self.FIRST_POST_CHAR]


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Группа',
        help_text='Укажите название группы'
    )
    slug = models.SlugField(
        max_length=250,
        unique=True,
        verbose_name='URL',
        help_text='Укажите адрес группы'
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Укажите описание группы'
    )

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Напишите ваш комментарий'
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации комментария'
    )

    def __str__(self):
        return self.post


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

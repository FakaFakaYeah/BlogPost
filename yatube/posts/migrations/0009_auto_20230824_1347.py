# Generated by Django 2.2.16 on 2023-08-24 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0008_auto_20230824_1344'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, height_field='1800', upload_to='posts/', verbose_name='Картинка', width_field='900'),
        ),
    ]

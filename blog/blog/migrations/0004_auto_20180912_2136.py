# Generated by Django 2.1 on 2018-09-12 14:36

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_auto_20180912_1213'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='approved_comments',
            new_name='approved_comment',
        ),
        migrations.AlterField(
            model_name='comment',
            name='created_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='post',
            name='created_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]

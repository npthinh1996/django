# Generated by Django 2.1.3 on 2018-11-26 17:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='contact',
            old_name='used_id',
            new_name='user_id',
        ),
    ]

# Generated by Django 5.0.3 on 2024-03-10 21:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0008_alter_tasklist_task_current_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='tasklist',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
    ]

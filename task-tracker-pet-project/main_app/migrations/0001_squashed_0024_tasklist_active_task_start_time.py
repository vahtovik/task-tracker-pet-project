# Generated by Django 5.0.3 on 2024-05-15 17:07

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [('main_app', '0001_initial'), ('main_app', '0002_tasklist_task_current_time_tasklist_task_start_time_and_more'), ('main_app', '0003_alter_tasklist_task_current_time_and_more'), ('main_app', '0004_alter_tasklist_task_current_time_and_more'), ('main_app', '0005_remove_tasklist_session_key_tasklist_user'), ('main_app', '0006_alter_tasklist_user'), ('main_app', '0007_alter_tasklist_task_current_time'), ('main_app', '0008_alter_tasklist_task_current_time'), ('main_app', '0009_tasklist_is_active'), ('main_app', '0010_tasklist_order'), ('main_app', '0011_rename_task_tasklist_task_name'), ('main_app', '0012_tasklist_is_completed'), ('main_app', '0013_alter_tasklist_task_current_time'), ('main_app', '0014_alter_tasklist_task_current_time'), ('main_app', '0015_alter_tasklist_task_current_time'), ('main_app', '0016_tasklist_completed_task_end_time_and_more'), ('main_app', '0017_tasklist_task_time_interval'), ('main_app', '0018_alter_tasklist_task_time_interval'), ('main_app', '0019_alter_tasklist_order'), ('main_app', '0020_rename_task_start_time_tasklist_creation_time'), ('main_app', '0021_alter_tasklist_options_and_more'), ('main_app', '0022_alter_tasklist_completed_task_end_time_and_more'), ('main_app', '0023_remove_tasklist_task_current_time'), ('main_app', '0024_tasklist_active_task_start_time')]

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_name', models.CharField(max_length=255)),
                ('creation_time', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to=settings.AUTH_USER_MODEL)),
                ('is_active', models.BooleanField(default=False)),
                ('order', models.IntegerField(default=100000)),
                ('is_completed', models.BooleanField(default=False)),
                ('completed_task_end_time', models.DateTimeField(blank=True, null=True)),
                ('completed_task_start_time', models.DateTimeField(blank=True, null=True)),
                ('active_task_start_time', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Список задач',
                'verbose_name_plural': 'Список задач',
            },
        ),
    ]

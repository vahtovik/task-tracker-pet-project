# Generated by Django 5.0.3 on 2024-03-10 23:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0009_tasklist_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='tasklist',
            name='order',
            field=models.IntegerField(default=0),
        ),
    ]

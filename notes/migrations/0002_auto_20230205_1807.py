# Generated by Django 3.2.16 on 2023-02-05 18:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reference',
            name='length',
        ),
        migrations.RemoveField(
            model_name='reference',
            name='offset',
        ),
    ]

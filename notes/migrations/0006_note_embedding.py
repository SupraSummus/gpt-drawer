# Generated by Django 4.2.10 on 2024-03-24 21:31

import pgvector.django
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0005_alter_note_options_alter_note_unique_together_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='note',
            name='embedding',
            field=pgvector.django.VectorField(blank=True, dimensions=3072, null=True, verbose_name='embedding'),
        ),
    ]

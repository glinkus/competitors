# Generated by Django 5.1.3 on 2025-04-06 18:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0011_page_analyzed_page_raw_html'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='content_hash',
            field=models.CharField(blank=True, max_length=42, null=True),
        ),
        migrations.AddField(
            model_name='page',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='page',
            name='keywords',
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AddField(
            model_name='page',
            name='links',
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AddField(
            model_name='page',
            name='structured_data',
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AddField(
            model_name='page',
            name='warnings',
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
    ]

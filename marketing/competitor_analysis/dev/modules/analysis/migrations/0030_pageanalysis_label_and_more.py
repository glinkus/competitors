# Generated by Django 5.1.3 on 2025-04-23 19:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0029_remove_page_analyzed_remove_page_content_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='pageanalysis',
            name='label',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='pageanalysis',
            name='positioning_classification',
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
    ]

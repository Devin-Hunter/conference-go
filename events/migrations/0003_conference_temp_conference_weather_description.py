# Generated by Django 4.0.3 on 2024-01-12 02:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_location_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='conference',
            name='temp',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='conference',
            name='weather_description',
            field=models.TextField(null=True),
        ),
    ]
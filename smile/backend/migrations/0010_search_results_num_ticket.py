# Generated by Django 4.2.19 on 2025-06-20 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0009_search_results_user_temp_seat"),
    ]

    operations = [
        migrations.AddField(
            model_name="search_results",
            name="num_ticket",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]

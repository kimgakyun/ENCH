# Generated by Django 5.0.4 on 2024-10-03 18:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_mealrecord_weeklyplan'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weeklyplan',
            name='plan_content',
            field=models.JSONField(),
        ),
    ]

# Generated by Django 5.0.4 on 2024-10-04 09:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_weeklyplan_nutrition_info'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mealrecord',
            name='calorie_difference',
        ),
    ]

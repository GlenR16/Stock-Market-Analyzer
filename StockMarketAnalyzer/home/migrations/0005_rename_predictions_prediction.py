# Generated by Django 4.1.7 on 2023-05-05 10:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_remove_predictions_high_remove_predictions_low_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Predictions',
            new_name='Prediction',
        ),
    ]

# Generated by Django 4.1.2 on 2023-03-15 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='new',
            name='date',
            field=models.DateField(default='2023-02-02'),
            preserve_default=False,
        ),
    ]

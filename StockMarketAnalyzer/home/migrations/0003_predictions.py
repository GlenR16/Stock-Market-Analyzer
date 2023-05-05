# Generated by Django 4.1.7 on 2023-05-05 09:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_data_high_data_low_data_volume_output'),
    ]

    operations = [
        migrations.CreateModel(
            name='Predictions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('open', models.FloatField(blank=True, default=0, null=True)),
                ('close', models.FloatField(default=0)),
                ('high', models.FloatField(blank=True, default=0, null=True)),
                ('low', models.FloatField(blank=True, default=0, null=True)),
                ('volume', models.FloatField(blank=True, default=0, null=True)),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.stock')),
            ],
        ),
    ]

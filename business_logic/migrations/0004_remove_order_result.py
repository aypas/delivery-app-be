# Generated by Django 3.0.2 on 2020-07-16 22:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('business_logic', '0003_auto_20200703_1333'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='result',
        ),
    ]
# Generated by Django 3.0.2 on 2020-07-16 22:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('business_logic', '0006_order_error_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='error_detail',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]

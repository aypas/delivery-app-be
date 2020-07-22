# Generated by Django 3.0.2 on 2020-07-16 22:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('business_logic', '0007_order_error_detail'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='last_edited_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='last_edited_by', to=settings.AUTH_USER_MODEL),
        ),
    ]

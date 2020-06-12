# Generated by Django 3.0.2 on 2020-05-16 03:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=255)),
                ('code', models.IntegerField()),
                ('managers', models.ManyToManyField(limit_choices_to={'is_manager': True}, related_name='managers', to=settings.AUTH_USER_MODEL)),
                ('owner', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='owner', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Partner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('street_address', models.CharField(max_length=255)),
                ('active', models.BooleanField(default=True)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('of_node_partner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='business_logic.Node')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('html', models.TextField(blank=True)),
                ('result', models.CharField(blank=True, max_length=20)),
                ('source', models.CharField(blank=True, max_length=30)),
                ('customer_phone', models.CharField(max_length=30)),
                ('order_number', models.CharField(max_length=200, unique=True)),
                ('name', models.CharField(max_length=200)),
                ('address', models.CharField(max_length=300)),
                ('deliver_by', models.CharField(max_length=200)),
                ('entry_date', models.DateTimeField(auto_now_add=True)),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=6)),
                ('tip', models.DecimalField(decimal_places=2, max_digits=6)),
                ('delivery_fee', models.DecimalField(decimal_places=2, max_digits=6)),
                ('note', models.CharField(blank=True, max_length=300)),
                ('in_progress', models.BooleanField(default=False)),
                ('complete', models.BooleanField(default=False)),
                ('completed_time', models.DateTimeField(blank=True, null=True)),
                ('assigned_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_user', to=settings.AUTH_USER_MODEL)),
                ('store', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='store', to='business_logic.Partner')),
            ],
        ),
    ]

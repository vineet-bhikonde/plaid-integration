# Generated by Django 3.2 on 2021-04-17 09:21

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
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_id', models.CharField(max_length=100, unique=True)),
                ('mask', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=50)),
                ('official_name', models.CharField(max_length=100, null=True)),
                ('subtype', models.CharField(max_length=100)),
                ('type', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='AvailableProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='BilledProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Balance',
            fields=[
                ('available', models.FloatField(default=0.0, null=True)),
                ('current', models.FloatField(default=0.0, null=True)),
                ('iso_currency_code', models.CharField(max_length=10)),
                ('limit', models.FloatField(null=True)),
                ('unofficial_currency_code', models.CharField(blank=True, max_length=10, null=True)),
                ('account', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='item.account')),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item', models.CharField(max_length=100)),
                ('access_token', models.CharField(max_length=200)),
                ('consent_expiration_time', models.DateTimeField(null=True)),
                ('error', models.CharField(max_length=100, null=True)),
                ('institution_id', models.CharField(max_length=10, null=True)),
                ('update_type', models.CharField(max_length=50, null=True)),
                ('webhook', models.CharField(max_length=100, null=True)),
                ('available_products', models.ManyToManyField(to='item.AvailableProduct')),
                ('billed_products', models.ManyToManyField(to='item.BilledProduct')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='account',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='item.item'),
        ),
    ]

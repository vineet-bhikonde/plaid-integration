# Generated by Django 3.2 on 2021-04-18 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('item', '0004_alter_transactiondetail_transaction_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='webhook',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]

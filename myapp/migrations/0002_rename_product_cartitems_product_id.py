# Generated by Django 5.2.4 on 2025-07-09 10:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cartitems',
            old_name='product',
            new_name='product_id',
        ),
    ]

# Generated by Django 4.1.7 on 2023-04-18 11:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('admin_side', '0002_category_is_disabe'),
    ]

    operations = [
        migrations.RenameField(
            model_name='category',
            old_name='is_disabe',
            new_name='is_disable',
        ),
    ]

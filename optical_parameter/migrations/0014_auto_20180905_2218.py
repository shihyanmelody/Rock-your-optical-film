# Generated by Django 2.0.7 on 2018-09-06 03:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('optical_parameter', '0013_auto_20180905_1718'),
    ]

    operations = [
        migrations.AlterOrderWithRespectTo(
            name='film',
            order_with_respect_to='layer_sequence',
        ),
    ]

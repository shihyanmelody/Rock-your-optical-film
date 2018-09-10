# Generated by Django 2.0.7 on 2018-09-05 22:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('optical_parameter', '0009_auto_20180905_1501'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='testfilm',
            name='id',
        ),
        migrations.AlterField(
            model_name='testfilm',
            name='layer_sequence',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='testfilm',
            name='material',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='testfilm',
            name='type',
            field=models.CharField(max_length=50, null=True),
        ),
    ]

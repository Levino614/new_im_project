# Generated by Django 3.2 on 2021-04-30 17:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('erpapp', '0004_auto_20210430_1954'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='MonthYear',
            new_name='Month',
        ),
        migrations.RenameField(
            model_name='assignmentonmonth',
            old_name='month_year',
            new_name='month',
        ),
    ]

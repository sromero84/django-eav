# Generated by Django 2.0 on 2018-08-24 14:56

from django.db import migrations, models
import eav.fields


class Migration(migrations.Migration):

    dependencies = [
        ('eav', '0003_auto_20180824_2334'),
    ]

    operations = [
        migrations.AddField(
            model_name='value',
            name='value_decimal',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='attribute',
            name='datatype',
            field=eav.fields.EavDatatypeField(choices=[('text', 'Text'), ('decimal', 'Decimal'), ('float', 'Float'), ('int', 'Integer'), ('date', 'Date'), ('bool', 'True / False'), ('object', 'Django Object'), ('enum', 'Multiple Choice')], max_length=7, verbose_name='data type'),
        ),
        migrations.AlterUniqueTogether(
            name='attribute',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='attribute',
            name='content_type',
        ),
    ]
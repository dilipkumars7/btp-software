# Generated by Django 5.0 on 2024-01-08 10:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('btporders', '0003_cachedata_frontbinpresent'),
    ]

    operations = [
        migrations.AddField(
            model_name='masterdata',
            name='sample',
            field=models.CharField(default=False, max_length=255),
        ),
    ]

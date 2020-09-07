# Generated by Django 2.2.9 on 2020-07-28 17:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_auto_20200728_1607'),
    ]

    operations = [
        migrations.RenameField(
            model_name='group',
            old_name='slug',
            new_name='slug_name',
        ),
        migrations.AlterField(
            model_name='group',
            name='title',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='post',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='post', to='posts.Group'),
        ),
    ]

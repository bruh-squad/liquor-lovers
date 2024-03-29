# Generated by Django 4.1.6 on 2023-03-14 11:04

import LiquorLovers.utils
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('party', '0004_alter_party_image_partyinvitation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='party',
            name='image',
            field=models.ImageField(default='defaults/parties/default.png', upload_to=LiquorLovers.utils.uuid_upload_to),
        ),
        migrations.CreateModel(
            name='PartyRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('party', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requests', to='party.party')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='party_requests', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

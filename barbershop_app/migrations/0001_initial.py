# Generated by Django 3.1.1 on 2020-09-02 15:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Barber',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avatar', models.CharField(max_length=500)),
                ('phone', models.CharField(blank=True, max_length=500)),
                ('address', models.CharField(blank=True, max_length=500)),
                ('location', models.CharField(blank=True, max_length=500)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='barber', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=500)),
                ('total', models.IntegerField()),
                ('status', models.IntegerField(choices=[(1, 'Waiting for barber'), (2, 'Ready to move'), (3, 'On the way'), (4, 'Service done')])),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('picked_at', models.DateTimeField(blank=True, null=True)),
                ('barber', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='barbershop_app.barber')),
            ],
        ),
        migrations.CreateModel(
            name='Branches',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=500)),
                ('phone', models.CharField(max_length=500)),
                ('address', models.CharField(max_length=500)),
                ('logo', models.ImageField(upload_to='branch_logo/')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='branch', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=500)),
                ('short_description', models.CharField(max_length=500)),
                ('image', models.ImageField(upload_to='service_images/')),
                ('price', models.IntegerField(default=0)),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='barbershop_app.branches')),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avatar', models.CharField(max_length=500)),
                ('phone', models.CharField(blank=True, max_length=500)),
                ('address', models.CharField(blank=True, max_length=500)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='customer', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='BookingDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('sub_total', models.IntegerField()),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='booking_details', to='barbershop_app.booking')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='barbershop_app.service')),
            ],
        ),
        migrations.AddField(
            model_name='booking',
            name='branch',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='barbershop_app.branches'),
        ),
        migrations.AddField(
            model_name='booking',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='barbershop_app.customer'),
        ),
    ]

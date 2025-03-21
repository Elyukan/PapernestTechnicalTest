# Generated by Django 4.1 on 2025-03-16 16:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="NetworkProviderModel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="NetworkProviderTowerModel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("x_coordinate", models.IntegerField()),
                ("y_coordinate", models.IntegerField()),
                ("postcode", models.CharField(max_length=5)),
                ("is_2G", models.BooleanField()),
                ("is_3G", models.BooleanField()),
                ("is_4G", models.BooleanField()),
                (
                    "network_provider",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="towers",
                        to="api.networkprovidermodel",
                    ),
                ),
            ],
        ),
    ]

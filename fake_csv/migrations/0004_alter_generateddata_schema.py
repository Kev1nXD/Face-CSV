# Generated by Django 4.1.7 on 2023-03-12 12:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("fake_csv", "0003_alter_column_range_from_alter_column_range_to"),
    ]

    operations = [
        migrations.AlterField(
            model_name="generateddata",
            name="schema",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="datasets",
                to="fake_csv.dataschema",
            ),
        ),
    ]

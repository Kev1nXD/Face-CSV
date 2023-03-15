from django.core.exceptions import ValidationError
from django.db import models

from fake_csv_service import settings


class DataSchema(models.Model):
    COLUMN_SEPARATORS = (
        (",", "Comma (,)"),
        (";", "Semicolon (;)")
    )

    STRING_CHARACTER = (
        ("“", "Double-quote (“)"),
        ("‘", "Apostrophes (‘)")
    )
    name = models.CharField(max_length=255)
    column_separator = models.CharField(choices=COLUMN_SEPARATORS, max_length=1)
    string_character = models.CharField(choices=STRING_CHARACTER, max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)


class Column(models.Model):
    TYPES = (
        ('Full name', 'Full name'),
        ('Job', 'Job'),
        ('Email', 'Email'),
        ('Domain name', 'Domain name'),
        ('Phone number', 'Phone number'),
        ('Company name', 'Company name'),
        ('Text', 'Text'),
        ('Integer', 'Integer'),
        ('Address', 'Address'),
        ('Date', 'Date'),
    )

    schema = models.ForeignKey(DataSchema, on_delete=models.CASCADE, related_name='columns')
    name = models.CharField(max_length=255)
    data_type = models.CharField(choices=TYPES, max_length=255)
    range_from = models.IntegerField(null=True, blank=True)
    range_to = models.IntegerField(null=True, blank=True)
    order = models.IntegerField()

    def clean(self):
        super().clean()
        if self.range_from and self.range_to and self.range_from > self.range_to:
            raise ValidationError({'range_from': 'Range from must be less than or equal to range to.'})


class DataSet(models.Model):
    schema = models.ForeignKey(DataSchema, on_delete=models.CASCADE, related_name="datasets")
    rows = models.IntegerField()
    status = models.CharField(max_length=20, choices=(
        ('PROCESSING', 'Processing'),
        ('READY', 'Ready')
    ), default='PROCESSING')
    file = models.FileField(upload_to=settings.MEDIA_ROOT, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

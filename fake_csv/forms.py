from django import forms

from .models import Column, DataSchema, DataSet


class SchemasForm(forms.ModelForm):
    class Meta:
        model = DataSchema
        fields = ["name", "column_separator", "string_character"]


class SchemasColumnForm(forms.ModelForm):
    class Meta:
        model = Column
        fields = ["name", "data_type", "range_from", "range_to", "order"]
        labels = {
            "range_from": "From",
            "range_to": "To",
        }


class DataschemaForm(forms.ModelForm):
    class Meta:
        model = DataSet
        fields = ["rows"]
        labels = {
            "rows": "Rows"
        }

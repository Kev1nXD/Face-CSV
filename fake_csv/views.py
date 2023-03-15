import csv
import os
import random
import uuid
from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import modelformset_factory
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, UpdateView, ListView, DetailView
from faker import Faker
from slugify import slugify

from fake_csv_service import settings
from .forms import SchemasForm, SchemasColumnForm, DataschemaForm
from .models import Column, DataSchema


class CreateSchemaView(CreateView, LoginRequiredMixin):
    template_name = "fake_csv/schemas/schema_create.html"
    form_class = SchemasForm
    success_url = reverse_lazy("schemas:schemas-list")

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['formset'] = modelformset_factory(Column, form=SchemasColumnForm, extra=0)(self.request.POST)
        else:
            data['formset'] = modelformset_factory(Column, form=SchemasColumnForm, extra=0)()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            self.object = form.save(commit=False)
            self.object.save()
            for form in formset:
                child = form.save(commit=False)
                child.schema = self.object
                child.save()
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))


class UpdateSchemaView(UpdateView, LoginRequiredMixin):
    template_name = "fake_csv/schemas/schema_edit.html"
    form_class = SchemasForm
    success_url = reverse_lazy("schemas:schemas-list")

    # def post(self):
    #     pass
        # $(document).on('click', '.delete-column-btn', function(e)
        # {
        #     e.preventDefault();
        # var
        # btn = $(this);
        # var
        # url = btn.attr('href');
        # $.ajax({
        #     url: url,
        #     method: 'DELETE',
        #     success: function(response) {
        #         btn.closest('tr').remove();
        # },
        # error: function(response)
        # {
        #     console.log(response);
        # }
        # });
        # });

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        return get_object_or_404(DataSchema, pk=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = modelformset_factory(Column, form=SchemasColumnForm, extra=0)(
                self.request.POST, queryset=self.object.columns.all()
            )
            context['object'] = self.get_object()
        else:
            context['formset'] = modelformset_factory(Column, form=SchemasColumnForm, extra=0)(
                queryset=self.object.columns.all()
            )
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            self.object = form.save(commit=False)
            self.object.save()
            for form in formset:
                child = form.save(commit=False)
                child.schema = self.object
                child.save()
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))


class DeleteColumnView(View, LoginRequiredMixin):
    def get(self, request, pk, *args, **kwargs):
        column = Column.objects.get(pk=pk)
        column.delete()


class SchemasListView(ListView, LoginRequiredMixin):
    model = DataSchema
    ordering = ['-created_at']
    context_object_name = "schemas_list"
    template_name = "fake_csv/schemas/schemas_list.html"
    paginate_by = 5


class DeleteSchemaView(View, LoginRequiredMixin):
    @csrf_exempt
    def get(self, request, pk, *args, **kwargs):
        schema = DataSchema.objects.get(pk=pk)
        schema.delete()


class DatasetView(DetailView, LoginRequiredMixin):
    model = DataSchema
    context_object_name = "schema"
    form_class = DataschemaForm
    template_name = "fake_csv/data_sets/dataset_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class()
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    @staticmethod
    def generate_csv(schema, rows):
        fake = Faker()
        columns = schema.columns.all()
        field_order = {column.order: column.name for column in columns}
        fieldnames = [field_order[order] for order in sorted(field_order.keys())]
        data = []

        for _ in range(rows):
            row = {}
            for column in columns:
                data_type = column.data_type
                range_from = column.range_from
                range_to = column.range_to
                if data_type == 'Full name':
                    row[column.name] = fake.name()
                elif data_type == 'Job':
                    row[column.name] = fake.job()
                elif data_type == 'Email':
                    row[column.name] = fake.email()
                elif data_type == 'Domain name':
                    row[column.name] = fake.domain_name()
                elif data_type == 'Phone number':
                    row[column.name] = fake.phone_number()
                elif data_type == 'Company name':
                    row[column.name] = fake.company()
                elif data_type == 'Text':
                    sentences_number = random.randint(range_from, range_to)
                    row[column.name] = fake.paragraph(variable_nb_sentences=True, nb_sentences=sentences_number)
                elif data_type == 'Integer':
                    row[column.name] = fake.random_int(min=range_from, max=range_to)
                elif data_type == 'Address':
                    row[column.name] = fake.address()
                elif data_type == 'Date':
                    row[column.name] = fake.date()

            data.append(row)
        filename = f"{slugify(fake.word())}-{uuid.uuid4()}.csv"
        filepath = os.path.join(settings.MEDIA_ROOT, filename)

        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.DictWriter(
                csvfile,
                fieldnames=fieldnames,
                quotechar=schema.string_character,
                delimiter=schema.column_separator
            )
            writer.writeheader()
            for row in data:
                writer.writerow(row)

        return filepath

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.form_class(request.POST)
        if form.is_valid():
            dataset = form.save(commit=False)
            dataset.schema = self.object
            dataset.file = self.generate_csv(
                DataSchema.objects.get(pk=dataset.schema.pk),
                form.cleaned_data["rows"]
            )
            dataset.status = "READY"
            dataset.save()
            created_at = datetime.fromisoformat(str(dataset.created_at))
            return JsonResponse({
                "id": dataset.pk,
                "created_at": created_at.strftime("%B %d, %Y, %I:%M %p").replace(" 0", " ").replace("AM", "a.m.").replace("PM", "p.m."),
                "status": dataset.status,
                "file_url": dataset.file.url,
                "filename": "dataset.csv",
            })
        else:
            context = self.get_context_data(object=self.object, form=form)
            return self.render_to_response(context)

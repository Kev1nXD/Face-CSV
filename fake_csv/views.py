from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.forms import modelformset_factory
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView, ListView, DetailView

from .forms import SchemasForm, SchemasColumnForm, DataschemaForm
from .models import Column, DataSchema, DataSet

from .utils import generate_csv


class CreateSchemaView(LoginRequiredMixin, CreateView):
    template_name = "fake_csv/schemas/schema_create.html"
    form_class = SchemasForm
    success_url = reverse_lazy("schemas:schemas-list")

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data["formset"] = modelformset_factory(
                Column, form=SchemasColumnForm, extra=0
            )(self.request.POST)
        else:
            data["formset"] = modelformset_factory(
                Column, form=SchemasColumnForm, extra=0
            )()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["formset"]
        if all([formset.is_valid(), form.is_valid()]):
            self.object = form.save(commit=False)
            self.object.user = self.request.user
            self.object.save()
            for form in formset:
                child = form.save(commit=False)
                child.schema = self.object
                child.save()
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))


class UpdateSchemaView(LoginRequiredMixin, UpdateView):
    template_name = "fake_csv/schemas/schema_edit.html"
    form_class = SchemasForm
    success_url = reverse_lazy("schemas:schemas-list")

    def get_object(self, queryset=None):
        pk = self.kwargs.get("pk")
        user = self.request.user
        return get_object_or_404(DataSchema, pk=pk, user=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["formset"] = modelformset_factory(
                Column, form=SchemasColumnForm, extra=0
            )(self.request.POST, queryset=self.object.columns.all())
        else:
            context["formset"] = modelformset_factory(
                Column, form=SchemasColumnForm, extra=0
            )(queryset=self.object.columns.all())
            columns = self.object.columns.all()
            context["columns"] = [i for i in columns]
            context["nested"] = zip(context["formset"], context["columns"])
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["formset"]
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


class DeleteColumnView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        column = Column.objects.get(pk=pk)
        column.delete()
        return HttpResponse(status=200)


class SchemasListView(LoginRequiredMixin, ListView):
    model = DataSchema
    ordering = ["-created_at"]
    context_object_name = "schemas_list"
    template_name = "fake_csv/schemas/schemas_list.html"
    paginate_by = 5

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user.id)


class DeleteSchemaView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        schema = DataSchema.objects.get(pk=pk)
        schema.delete()
        return HttpResponse(status=200)


class DatasetView(LoginRequiredMixin, DetailView):
    model = DataSchema
    context_object_name = "schema"
    form_class = DataschemaForm
    template_name = "fake_csv/data_sets/dataset_detail.html"

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.form_class()
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.form_class(request.POST)
        if form.is_valid():
            dataset = form.save(commit=False)
            dataset.schema = self.object
            dataset.save()
            created_at = datetime.fromisoformat(str(dataset.created_at))
            return JsonResponse(
                {
                    "id": dataset.pk,
                    "created_at": created_at.strftime("%B %d, %Y, %I:%M %p")
                    .replace(" 0", " ")
                    .replace("AM", "a.m.")
                    .replace("PM", "p.m."),
                    "status": dataset.status,
                }
            )
        else:
            context = self.get_context_data(object=self.object, form=form)
            return self.render_to_response(context)


class GenerateFileView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        dataset = DataSet.objects.get(pk=pk)
        with transaction.atomic():
            dataset.file = generate_csv(
                DataSchema.objects.get(pk=dataset.schema.pk), dataset.rows
            )
            dataset.status = "READY"
            dataset.save()
        return JsonResponse(
            {
                "id": dataset.pk,
                "status": dataset.status,
                "file_url": dataset.file.url
            }
        )

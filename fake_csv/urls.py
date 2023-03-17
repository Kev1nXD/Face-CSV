from django.urls import path

from fake_csv.views import (
    CreateSchemaView,
    UpdateSchemaView,
    SchemasListView,
    DatasetView,
    DeleteSchemaView,
    DeleteColumnView,
    GenerateFileView,
)

urlpatterns = [
    path("schema/create/", CreateSchemaView.as_view(), name="schema-create"),
    path("schema/<int:pk>/edit/", UpdateSchemaView.as_view(), name="schema-edit"),
    path("", SchemasListView.as_view(), name="schemas-list"),
    path("datasets/<int:pk>/", DatasetView.as_view(), name="datasets"),
    path(
        "schema/delete/schema/<int:pk>",
        DeleteSchemaView.as_view(),
        name="schema-delete",
    ),
    path(
        "schema/delete/column/<int:pk>",
        DeleteColumnView.as_view(),
        name="column-delete",
    ),
    path("datasets/<int:pk>/update/", GenerateFileView.as_view(), name="generate-file"),
]

app_name = "schemas"

from django.conf.urls.static import static
from django.urls import path

from fake_csv.views import CreateSchemaView, UpdateSchemaView, SchemasListView, DatasetView, DeleteSchemaView, DeleteColumnView
from fake_csv_service import settings

urlpatterns = [
    path("schema/create/", CreateSchemaView.as_view(), name="schema-create"),
    path("schema/<int:pk>/edit/", UpdateSchemaView.as_view(), name="schema-edit"),
    path("schemas/", SchemasListView.as_view(), name="schemas-list"),
    path("datasets/<int:pk>/", DatasetView.as_view(), name="datasets"),
    path("schema/delete/schema/<int:pk>", DeleteSchemaView.as_view(), name="schema-delete"),
    path("schema/delete/column/<int:pk>", DeleteColumnView.as_view(), name="column-delete")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

app_name = "schemas"

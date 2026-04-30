from wagtail.search.backends.database.postgres.postgres import (
    PostgresSearchResults,
    PostgresSearchBackend,
)
from django.db.models import Q


class CustomPostgresSearchResults(PostgresSearchResults):
    def get_queryset(self):
        # Get the default queryset
        qs = super().get_queryset()

        # Run a LIKE query against the title and file properties of models
        # that have those properties (e.g., Documents & Images)
        if hasattr(self.model, "title") and hasattr(self.model, "file"):
            like_results = self.model.objects.filter(
                Q(title__icontains=self.query_compiler.query.query_string)
                | Q(file__icontains=self.query_compiler.query.query_string)
            )

            # Combine results into a list of primary keys from the objects in each queryset
            fts_ids = list(qs.values_list("pk", flat=True))
            like_ids = list(like_results.values_list("pk", flat=True))
            combined_ids = set(fts_ids + like_ids)

            # Create a fresh QuerySet matching the combined IDs (the "in" portion of this query
            # removes duplicates)
            qs = self.model.objects.filter(pk__in=combined_ids)

        return qs


class CustomPostgresSearchBackend(PostgresSearchBackend):
    results_class = CustomPostgresSearchResults


SearchBackend = CustomPostgresSearchBackend

from modelsearch.backends.database.postgres.postgres import (
    PostgresSearchResults,
    PostgresSearchBackend,
)
from django.db.models import Q


class CustomPostgresSearchResults(PostgresSearchResults):
    def get_queryset(self):
        like_results = self.model.objects.none()

        # Run a LIKE query against the title and file properties of models
        # that have those properties (e.g., Documents & Images)
        if hasattr(self.model, "title") and hasattr(self.model, "file"):
            like_results = self.model.objects.filter(
                Q(title__icontains=self.query_compiler.query.query_string)
                | Q(file__icontains=self.query_compiler.query.query_string)
            )

        # Get the default queryset
        qs = super().get_queryset()

        # Combine results (union removes duplicates)
        qs = (like_results | qs).distinct()

        return qs


class CustomPostgresSearchBackend(PostgresSearchBackend):
    results_class = CustomPostgresSearchResults

    def autocomplete(
        self,
        query,
        model_or_queryset,
        fields=None,
        operator=None,
        order_by_relevance=True,
    ):
        """
        Performs an autocomplete (partial word match) search.

        :param query: The search query string.
        :param model_or_queryset: The model class or queryset to search within.
        :param fields: An optional list of field names to restrict the search to.
        :param operator: The operator to use when combining search terms (``"and"`` or ``"or"``).
        :param order_by_relevance: Whether to order results by relevance.
        """
        if self.autocomplete_query_compiler_class is None:
            raise NotImplementedError(
                "This search backend does not support the autocomplete API"
            )

        return self._search(
            self.autocomplete_query_compiler_class,
            query,
            model_or_queryset,
            fields=fields,
            operator=operator,
            order_by_relevance=order_by_relevance,
        )


SearchBackend = CustomPostgresSearchBackend

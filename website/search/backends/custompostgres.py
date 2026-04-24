from modelsearch.backends.database.postgres.postgres import (
    PostgresSearchResults,
    PostgresSearchBackend,
)
import logging
from django.db.models import Q


class CustomPostgresSearchResults(PostgresSearchResults):
    def get_queryset(self):
        logger = logging.getLogger(__name__)

        like_results = set()

        # all_objects = self.model.objects.all()

        like_results = self.model.objects.filter(
            Q(title__icontains=self.query_compiler.query.query_string)
            | Q(file__icontains=self.query_compiler.query.query_string)
        )

        logger.error(f"like_results: {like_results}")

        # Start with the default queryset
        qs = super().get_queryset()
        logger.error(f"qs: {qs}")

        # # Get the search term from request
        # search_term = self.request.GET.get("q", "").strip()

        # if search_term:
        #     # Perform default Wagtail search
        #     wagtail_results = qs.search(PlainText(search_term))

        #     # Perform LIKE search on title and file name
        #     like_results = qs.filter(
        #         Q(title__icontains=search_term) | Q(file__icontains=search_term)
        #     )

        # Combine results (union removes duplicates)
        qs = (like_results | qs).distinct()

        return qs


class CustomPostgresSearchBackend(PostgresSearchBackend):
    results_class = CustomPostgresSearchResults
    ###comment for sandbox deploy
    logger = logging.getLogger(__name__)
    logger.error("Called CustomPostgresSearchBackend constructor")
    print("print Called CustomPostgresSearchBackend constructor")

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
        logger = logging.getLogger(__name__)
        logger.error("Called CustomPostgresSearchBackend.autocomplete")

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

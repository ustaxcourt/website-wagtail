from django.db import models
from wagtail.search.utils import normalise_query_string

MAX_DEFINITION_QUERY_LENGTH: int = 255


class DefinitionsQuery(models.Model):
    query_string = models.CharField(max_length=MAX_DEFINITION_QUERY_LENGTH, unique=True)

    number_of_hits = models.IntegerField(default=0)

    def add_hit(self, date=None):
        self.number_of_hits += 1
        self.save()

    @classmethod
    def get(cls, query_string):
        return cls.objects.get_or_create(
            query_string=normalise_query_string(query_string)
        )[0]

    class Meta:
        verbose_name = "Definition Search Query"
        verbose_name_plural = "Definition Search Queries"

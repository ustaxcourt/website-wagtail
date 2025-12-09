from django.db import models
from django.utils import timezone
from wagtail.contrib.search_promotions.models import QueryDailyHits
from wagtail.search.utils import normalise_query_string

MAX_DEFINITION_QUERY_LENGTH: int = 255


class DefinitionsQuery(models.Model):
    query_string = models.CharField(max_length=MAX_DEFINITION_QUERY_LENGTH, unique=True)

    def add_hit(self, date=None):
        if date is None:
            date = timezone.now().date()
        daily_hits, created = QueryDailyHits.objects.get_or_create(
            query=self, date=date
        )
        daily_hits.hits = models.F("hits") + 1
        daily_hits.save()

    @classmethod
    def get(cls, query_string):
        return cls.objects.get_or_create(
            query_string=normalise_query_string(query_string)
        )[0]

from django.db import models
from wagtail.search.utils import normalise_query_string

MAX_DEFINITION_QUERY_LENGTH: int = 255


class DefinitionsQuery(models.Model):
    query_string = models.CharField(max_length=MAX_DEFINITION_QUERY_LENGTH, unique=True)

    number_of_hits = models.IntegerField(default=0)

    def add_hit(self, date=None):
        self.number_of_hits += 1
        self.save()

        # DefinitionsQuery.objects.filter(id=self.id).update(number_of_hits=models.F('number_of_hits') + 1)
        # DefinitionsQuery.objects.get_or_create(
        #     query_string=normalise_query_string(self.query_string)
        # )
        # hit = DefinitionsQuery.objects.get_or_create()
        # if date is None:
        #     date = timezone.now().date()
        # daily_hits, created = QueryDailyHits.objects.get_or_create(
        #     query=self, date=date
        # )
        # daily_hits.hits = models.F("hits") + 1
        # daily_hits.save()

    @classmethod
    def get(cls, query_string):
        return cls.objects.get_or_create(
            query_string=normalise_query_string(query_string)
        )[0]

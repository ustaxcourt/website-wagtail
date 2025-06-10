from django.db import models


class IconCategories(models.TextChoices):
    NONE = ("",)
    BOOK = "fa-solid fa-book"
    BUILDING_BANK = "fa-solid fa-building-columns"
    CALENDAR_MONTH = "fa-solid fa-calendar"
    CHEVRON_RIGHT = "fa-solid fa-chevron-right"
    FILE = "fa-solid fa-file"
    HAMMER = "fa-solid fa-gavel"
    INFO = "fa-solid fa-circle-info"
    CHECK = "fa-solid fa-check"
    LINK = "fa-solid fa-link"
    EXCLAMATION_MARK = "fa-solid fa-exclamation"
    PDF = "fa-solid fa-file-pdf"
    SCALE = "fa-solid fa-scale-balanced"
    USER = "fa-solid fa-user"
    VIDEO = "fa-solid fa-video"
    SETTINGS = "fa-solid fa-gear"
    BRIEFCASE = "fa-solid fa-briefcase"
    SEARCH = "fa-solid fa-magnifying-glass"

from django.db import models


# Additions or changes to this list should also be made to the CSS line
# in base.html of link beginning with "https://fonts.googleapis.com/css2"
class IconCategories(models.TextChoices):
    NONE = ("",)
    BOOK = "book_3"
    BUILDING_BANK = "account_balance"
    CALENDAR_MONTH = "calendar_today"
    CHEVRON_RIGHT = "chevron_right"
    FILE = "draft"
    HAMMER = "gavel"
    INFO = "info"
    CHECK = "check"
    LINK = "link_2"
    EXCLAMATION_MARK = "exclamation"
    PDF = "description"
    SCALE = "balance"
    USER = "person"
    VIDEO = "videocam"
    SETTINGS = "settings"
    BRIEFCASE = "work"
    SEARCH = "search"
    SIGNPOST = "signpost"
    TIMELINE = "timeline"
    NOTES = "note_stack"
    FORMS = "article"
    HELP = "help"
    DAWSON = "dawson"

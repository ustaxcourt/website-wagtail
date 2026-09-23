from django.db import models


# Additions or changes to either of these lists should also be made to the CSS line
# in base.html of link beginning with "https://fonts.googleapis.com/css2"
class NumberedIconCategories(models.TextChoices):
    NONE = ("",)
    ONE = "1"
    TWO = "2"
    THREE = "3"
    CHECK = "check"
    EXCLAMATION = "exclamation"


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
    SELECT_CHECK_BOX = "select_check_box"
    OUTBOUND = "outbound"
